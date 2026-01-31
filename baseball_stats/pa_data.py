"""
Load plate-appearance-level data from Statcast for ML modeling.
Each row = one completed PA with outcome (events) and context (count, batter, pitcher, etc.).
Event -> outcome mapping is derived from Statcast data via rule-based logic (no hardcoded event list).
"""
import pandas as pd
from pybaseball import statcast

OUTCOME_ORDER = ["Walk", "HBP", "Single", "Double", "Triple", "HR", "Strikeout", "Out"]


def _event_to_outcome(event: str) -> str:
    """
    Map a single Statcast event string to simulator outcome. Uses pattern rules so we
    don't depend on a hardcoded list of events; new Statcast event types still get classified.
    """
    if pd.isna(event):
        return "Out"
    e = event.lower().strip()
    if e == "walk":
        return "Walk"
    if e == "hit_by_pitch":
        return "HBP"
    if e == "single":
        return "Single"
    if "double_play" in e or e == "double_play":
        return "Out"
    if e == "double":
        return "Double"
    if "triple_play" in e or e == "triple_play":
        return "Out"
    if e == "triple":
        return "Triple"
    if e == "home_run":
        return "HR"
    if "strikeout" in e:
        return "Strikeout"
    # Everything else (field_out, force_out, sac_fly, sac_bunt, field_error, etc.) -> Out
    return "Out"


def fetch_statcast_pas(start_dt: str, end_dt: str) -> pd.DataFrame:
    """
    Fetch Statcast data and keep one row per plate appearance (rows where events is set).
    start_dt / end_dt: 'YYYY-MM-DD'
    """
    import pybaseball
    pybaseball.cache.enable()
    raw = statcast(start_dt=start_dt, end_dt=end_dt)
    if raw is None or raw.empty:
        return pd.DataFrame()
    # Only the final pitch of each PA has 'events' set
    pas = raw[raw["events"].notna()].copy()
    return pas


def map_events_to_outcomes(pas: pd.DataFrame) -> pd.DataFrame:
    """Add outcome category from Statcast 'events' using rule-based mapping (no hardcoded event list)."""
    pas = pas.copy()
    pas["outcome"] = pas["events"].map(_event_to_outcome)
    return pas


def load_pa_dataset(start_dt: str, end_dt: str) -> pd.DataFrame:
    """
    Load PA-level dataset with outcome and basic context for modeling.
    Returns DataFrame with columns including: outcome, balls, strikes, p_throws (L/R), stand (L/R), etc.
    """
    pas = fetch_statcast_pas(start_dt, end_dt)
    if pas.empty:
        return pas
    pas = map_events_to_outcomes(pas)
    # Coerce numeric where needed
    for col in ["balls", "strikes"]:
        if col in pas.columns:
            pas[col] = pd.to_numeric(pas[col], errors="coerce").fillna(0).astype(int)
    return pas
