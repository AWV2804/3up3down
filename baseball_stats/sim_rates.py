"""
Use in your baseball simulator: load league rates or the ML model to get PA outcome probabilities.
"""
import json
import pickle
from pathlib import Path

_path = Path(__file__).parent


def load_league_rates() -> dict:
    """Load empirical outcome rates (Walk, Single, HR, Strikeout, Out, etc.) from JSON."""
    rates_path = _path / "pa_outcome_rates.json"
    if not rates_path.exists():
        raise FileNotFoundError(
            f"Run pa_model.py first to generate {rates_path}"
        )
    with open(rates_path) as f:
        return json.load(f)


def load_outcome_model():
    """Load trained classifier, label encoder, and meta (includes feature_names). Returns (clf, le, meta)."""
    model_path = _path / "pa_outcome_model.pkl"
    if not model_path.exists():
        raise FileNotFoundError(
            f"Run pa_model.py first to train and save {model_path}"
        )
    with open(model_path, "rb") as f:
        data = pickle.load(f)
    meta = data.get("meta", {})
    return data["clf"], data["le"], meta


def get_outcome_probs(count_balls: int, count_strikes: int, same_hand: bool, use_ml: bool = True) -> dict:
    """
    Get outcome probabilities for one plate appearance.
    same_hand: True if batter and pitcher use same hand (e.g. L vs L).
    use_ml: if True and model exists, use ML; else use league rates.
    Returns dict: outcome name -> probability (e.g. "Walk", "Single", "Strikeout", "Out", ...).
    """
    if use_ml:
        try:
            from pa_model import outcome_probs_for_sim
            clf, le, meta = load_outcome_model()
            count_id = count_balls * 4 + count_strikes
            platoon_same = 1 if same_hand else 0
            return outcome_probs_for_sim(clf, le, count_id=count_id, platoon_same=platoon_same, feature_names=meta.get("feature_names"))
        except FileNotFoundError:
            pass
    return load_league_rates()
