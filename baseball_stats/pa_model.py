"""
ML model for plate appearance outcomes: Walk, HBP, Single, Double, Triple, HR, Strikeout, Out.
Uses Statcast PA-level data; trains a classifier and exports probabilities for the simulator.

Model choice (accuracy-focused, no compute limits):
- Random Forest: Fast, robust baseline. Averages many shallow trees; good but rarely best on tabular.
- XGBoost (used here): Gradient boosting—builds trees that correct previous errors. Typically
  best accuracy on tabular data; used in most ML competitions. More capacity than RF with
  early stopping to avoid overfitting.
- Logistic regression: Simple, interpretable; usually worse when count/platoon interactions matter.
- Neural net: Can match or beat boosting with lots of data and tuning; for this dataset size
  and feature set, XGBoost is usually the best tradeoff.
"""
import json
import pickle
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from xgboost import XGBClassifier

# Suppress FutureWarnings from pybaseball's deprecated pandas usage
warnings.filterwarnings('ignore', category=FutureWarning, module='pybaseball')

import pybaseball
from pa_data import load_pa_dataset, OUTCOME_ORDER


def build_features(pas: pd.DataFrame):
    """Build feature matrix from PA data. Returns (X, y)."""
    df = pas.copy()
    # Count: 0-0 through 3-2
    df["balls"] = pd.to_numeric(df["balls"], errors="coerce").fillna(0).astype(int)
    df["strikes"] = pd.to_numeric(df["strikes"], errors="coerce").fillna(0).astype(int)
    df["count_id"] = df["balls"] * 4 + df["strikes"]
    # Platoon: same hand = 1, opposite = 0
    same_hand = (df["stand"].str.upper() == df["p_throws"].str.upper())
    df["platoon_same"] = same_hand.astype(int)
    feature_cols = ["count_id", "platoon_same"]
    for c in ["inning", "outs_when_up"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)
            feature_cols.append(c)
    X = df[[c for c in feature_cols if c in df.columns]]
    return X, df["outcome"]


def train_model(pas: pd.DataFrame, test_size: float = 0.2, random_state: int = 42):
    """Train XGBoost classifier for PA outcome (best accuracy for tabular multiclass)."""
    X, y = build_features(pas)
    valid = y.isin(OUTCOME_ORDER)
    X, y = X[valid], y[valid]
    if X.empty or y.empty:
        raise ValueError("No valid rows after building features. Check PA data and outcome mapping.")
    le = LabelEncoder()
    y_enc = le.fit_transform(y)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_enc, test_size=test_size, random_state=random_state, stratify=y_enc
    )
    clf = XGBClassifier(
        n_estimators=400,
        max_depth=8,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=random_state,
        early_stopping_rounds=25,
        eval_metric="mlogloss",
    )
    clf.fit(
        X_train, y_train,
        eval_set=[(X_test, y_test)],
        verbose=False,
    )
    acc = (clf.predict(X_test) == y_test).mean()
    meta = {"accuracy": float(acc), "classes": list(le.classes_), "feature_names": list(X_train.columns)}
    return clf, le, meta


def outcome_probs_for_sim(clf, le, count_id: int, platoon_same: int, inning: int = 5, outs: int = 0, feature_names=None) -> dict:
    """
    Get P(walk), P(hit), P(strikeout), etc. for a given context for use in the simulator.
    count_id = balls*4 + strikes (e.g. 0-0 -> 0, 3-2 -> 14). platoon_same: 1 = same hand, 0 = opposite.
    feature_names: list of column names in training order (required for XGBoost; stored in meta when loading).
    """
    row = {"count_id": count_id, "platoon_same": platoon_same}
    fnames = feature_names or getattr(clf, "feature_names_in_", None) or getattr(clf, "feature_names", None)
    if fnames is None:
        fnames = ["count_id", "platoon_same"]
    if "inning" in fnames:
        row["inning"] = inning
    if "outs_when_up" in fnames:
        row["outs_when_up"] = outs
    X = pd.DataFrame([row])
    X = X[[c for c in fnames if c in X.columns]]
    probs = clf.predict_proba(X)[0]
    return dict(zip(le.classes_, probs))


def league_rates_from_data(pas: pd.DataFrame, platoon_filter: str = None) -> dict:
    """
    Simple fallback: empirical outcome rates from data (no ML).
    Use when you just need overall walk%, hit%, K%, etc. for the sim.
    
    Args:
        pas: DataFrame with plate appearance data
        platoon_filter: If "same" or "opposite", filter to that platoon matchup.
                       If None, use all data.
    """
    from pa_data import map_events_to_outcomes
    if "outcome" not in pas.columns:
        pas = map_events_to_outcomes(pas)
    
    # Filter by platoon matchup if specified
    if platoon_filter is not None:
        if "platoon_matchup" not in pas.columns:
            from pa_data import add_platoon_info
            pas = add_platoon_info(pas)
        pas = pas[pas["platoon_matchup"] == platoon_filter].copy()
    
    n = len(pas)
    rates = {}
    for outcome in OUTCOME_ORDER:
        rates[outcome] = (pas["outcome"] == outcome).sum() / n if n else 0.0
    return rates


def main():
    """Fetch recent Statcast PAs, train model, save model and export rates."""
    # Use a recent short window to keep run fast (expand for production)
    start_dt = "2024-01-01"
    end_dt = "2025-11-30"

    pybaseball.cache.enable()
    print("Loading Statcast PA data...")
    pas = load_pa_dataset(start_dt, end_dt)
    if pas.empty:
        print("No data returned. Try different dates or check pybaseball/network.")
        return

    print(f"Loaded {len(pas)} plate appearances.")
    
    # Check platoon distribution
    if "platoon_matchup" in pas.columns:
        platoon_counts = pas["platoon_matchup"].value_counts()
        print(f"\nPlatoon matchup distribution:")
        for matchup, count in platoon_counts.items():
            pct = count / len(pas) * 100
            print(f"  {matchup}: {count:,} ({pct:.1f}%)")

    # Overall empirical rates (no ML) – always useful for the sim
    rates = league_rates_from_data(pas)
    out_path = Path(__file__).parent / "pa_outcome_rates.json"
    with open(out_path, "w") as f:
        json.dump(rates, f, indent=2)
    print(f"\nWrote overall league outcome rates -> {out_path}")

    # Separate rates by platoon matchup
    if "platoon_matchup" in pas.columns:
        print("\nGenerating platoon-specific rates...")
        for matchup in ["same", "opposite"]:
            matchup_rates = league_rates_from_data(pas, platoon_filter=matchup)
            matchup_path = Path(__file__).parent / f"pa_outcome_rates_{matchup}.json"
            with open(matchup_path, "w") as f:
                json.dump(matchup_rates, f, indent=2)
            print(f"  Wrote {matchup}-hand rates -> {matchup_path}")
            print(f"    Sample: Walk={matchup_rates['Walk']:.4f}, K={matchup_rates['Strikeout']:.4f}, HR={matchup_rates['HR']:.4f}")

    # Train ML model for context-dependent probs (uses all data, includes platoon as feature)
    print("\nTraining outcome classifier...")
    clf, le, meta = train_model(pas)
    print(f"Test accuracy: {meta['accuracy']:.4f}")

    model_path = Path(__file__).parent / "pa_outcome_model.pkl"
    with open(model_path, "wb") as f:
        pickle.dump({"clf": clf, "le": le, "meta": meta}, f)
    print(f"Saved model -> {model_path}")

    # Optional: Train separate models for each platoon matchup
    if "platoon_matchup" in pas.columns:
        print("\nTraining platoon-specific models...")
        for matchup in ["same", "opposite"]:
            matchup_pas = pas[pas["platoon_matchup"] == matchup].copy()
            if len(matchup_pas) < 1000:  # Need minimum data
                print(f"  Skipping {matchup}-hand model (only {len(matchup_pas)} PAs)")
                continue
            
            print(f"  Training {matchup}-hand model ({len(matchup_pas):,} PAs)...")
            matchup_clf, matchup_le, matchup_meta = train_model(matchup_pas)
            matchup_model_path = Path(__file__).parent / f"pa_outcome_model_{matchup}.pkl"
            with open(matchup_model_path, "wb") as f:
                pickle.dump({"clf": matchup_clf, "le": matchup_le, "meta": matchup_meta}, f)
            print(f"    Saved {matchup}-hand model -> {matchup_model_path} (accuracy: {matchup_meta['accuracy']:.4f})")

    # Example: probs for 0-0 count, opposite hand
    probs = outcome_probs_for_sim(clf, le, count_id=0, platoon_same=0, feature_names=meta.get("feature_names"))
    print("\nExample probs (0-0, opposite hand):", {k: round(v, 4) for k, v in probs.items()})


if __name__ == "__main__":
    main()
