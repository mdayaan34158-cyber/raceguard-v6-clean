"""
Signal Preprocessing & Windowing Module
Machine Learning-Based Bearing Fault Classification in Induction Motors
"""
from typing import Dict, List, Tuple
import numpy as np
import pandas as pd
from scipy import signal
VALID_LABELS = [
    "Normal",
    "Inner Race Fault",
    "Outer Race Fault",
    "Rolling Element Fault",
]
def validate_vibration_dataframe(df: pd.DataFrame) -> Tuple[bool, str, List[str]]:
    """
    Validate an uploaded DataFrame to ensure it contains numeric vibration columns
    and sufficient samples for signal processing.
    """
    if df is None or df.empty:
        return False, "The uploaded CSV file is empty.", []
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if not numeric_cols:
        return (
            False,
            "No numeric columns found in the uploaded CSV. Please upload a CSV containing numeric vibration \
    measurements.",
            [],
        )
    if len(df) < 64:
        return (
            False,
            f"Dataset contains only {len(df)} rows. At least 64 time-series samples are required for \
    windowing.",
            numeric_cols,
        )
    return True, "Valid vibration dataset loaded.", numeric_cols
def clean_signal(raw_series: pd.Series) -> np.ndarray:
    """
    Clean a numeric vibration signal column by interpolating missing values (NaNs),
    and returning a clean 1D NumPy float array.
    """
    s = pd.to_numeric(raw_series, errors="coerce")
    if s.isna().all():
        raise ValueError("Selected signal column contains only non-numeric or missing values.")
    if s.isna().any():
        s = s.interpolate(method="linear").bfill().ffill()
    return s.to_numpy(dtype=np.float64)
def preprocess_signal(
    raw_signal: np.ndarray,
    remove_dc: bool = True,
    apply_bandpass: bool = False,
    fs: float = 12000.0,
    lowcut: float = 20.0,
    highcut: float = 5000.0,
) -> np.ndarray:
    """
    Apply mean removal (DC offset suppression) and optional Butterworth bandpass filtering.
    """
    x = np.asarray(raw_signal, dtype=np.float64).copy()
    if remove_dc:
        x = x - np.mean(x)
    if apply_bandpass and len(x) > 32:
        nyq = 0.5 * fs
        low = max(0.001, min(lowcut / nyq, 0.98))
        high = max(low + 0.01, min(highcut / nyq, 0.99))
        b, a = signal.butter(4, [low, high], btype="band")
        x = signal.filtfilt(b, a, x)
    return x
def segment_signal_windows(
    signal_array: np.ndarray,
    window_size: int = 512,
    overlap_pct: float = 50.0,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Segment a 1D vibration signal into overlapping windows.
    """
    x = np.asarray(signal_array, dtype=np.float64)
    if window_size <= 0:
        raise ValueError("Window size must be a positive integer.")
    if len(x) < window_size:
        raise ValueError(
            f"Signal length ({len(x)}) is shorter than the selected window size ({window_size})."
        )
    overlap_pct = float(np.clip(overlap_pct, 0.0, 90.0))
    step = max(1, int(round(window_size * (1.0 - overlap_pct / 100.0))))
    starts = np.arange(0, len(x) - window_size + 1, step, dtype=int)
    windows = np.stack([x[s : s + window_size] for s in starts], axis=0)
    return windows, starts
def generate_synthetic_demo_recording(
    condition: str = "Normal",
    n_samples: int = 4096,
    fs: float = 12000.0,
    seed: int = 42,
) -> pd.DataFrame:
    """
    Generate clearly labelled synthetic vibration waveforms for Demo Mode exploration.
    NOTE: Synthetic waveforms are purely illustrative and do not represent physical motor validation.
    """
    rng = np.random.default_rng(seed)
    t = np.arange(n_samples) / fs
    f_rot = 29.95
    base = 0.08 * np.sin(2 * np.pi * f_rot * t) + 0.03 * np.sin(2 * np.pi * 2 * f_rot * t)
    if condition == "Normal":
        sig = base + rng.normal(0, 0.045, n_samples)
    elif condition == "Inner Race Fault":
        bpfi = 162.18
        impulses = np.zeros(n_samples)
        period = max(1, int(fs / bpfi))
        for idx in range(0, n_samples, period):
            L = min(80, n_samples - idx)
            decay = np.exp(-np.arange(L) / 12.0)
            carrier = np.sin(2 * np.pi * 3200 * (np.arange(L) / fs))
            mod = 1.0 + 0.45 * np.cos(2 * np.pi * f_rot * (idx / fs))
            impulses[idx : idx + L] += 0.65 * mod * decay * carrier
        sig = base + impulses + rng.normal(0, 0.07, n_samples)
    elif condition == "Outer Race Fault":
        bpfo = 107.36
        impulses = np.zeros(n_samples)
        period = max(1, int(fs / bpfo))
        for idx in range(0, n_samples, period):
            L = min(90, n_samples - idx)
            decay = np.exp(-np.arange(L) / 10.0)
            carrier = np.sin(2 * np.pi * 2800 * (np.arange(L) / fs))
            impulses[idx : idx + L] += 0.85 * decay * carrier
        sig = base + impulses + rng.normal(0, 0.06, n_samples)
    else:
        bsf = 141.17
        ftf = 11.93
        impulses = np.zeros(n_samples)
        period = max(1, int(fs / bsf))
        for idx in range(0, n_samples, period):
            L = min(75, n_samples - idx)
            decay = np.exp(-np.arange(L) / 14.0)
            carrier = np.sin(2 * np.pi * 3500 * (np.arange(L) / fs))
            mod = 0.7 + 0.5 * np.sin(2 * np.pi * ftf * (idx / fs))
            impulses[idx : idx + L] += 0.52 * mod * decay * carrier
        sig = base + impulses + rng.normal(0, 0.08, n_samples)
    return pd.DataFrame(
        {
            "time_sec": np.round(t, 6),
            "DE_vibration": np.round(sig, 6),
            "motor_rpm": np.full(n_samples, 1797),
            "condition_label": np.full(n_samples, condition),
            "source_type": np.full(n_samples, "SYNTHETIC_DEMO"),
        }
    )
