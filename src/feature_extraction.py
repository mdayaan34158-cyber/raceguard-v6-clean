"""
Time-Domain & Spectral Feature Extraction Module
Machine Learning-Based Bearing Fault Classification in Induction Motors
"""
from typing import Dict, List
import numpy as np
import pandas as pd
from scipy import stats
FEATURE_NAMES: List[str] = [
    "mean",
    "std_dev",
    "rms",
    "peak",
    "peak_to_peak",
    "crest_factor",
    "kurtosis",
    "skewness",
    "shape_factor",
    "impulse_factor",
    "clearance_factor",
    "spectral_centroid_hz",
]
def compute_basic_signal_stats(signal_array: np.ndarray) -> Dict[str, float]:
    """
    Compute fundamental signal statistics displayed on the Signal Processing page.
    All values are computed directly from the input signal array.
    """
    x = np.asarray(signal_array, dtype=np.float64)
    if len(x) == 0:
        return {
            "mean": 0.0,
            "rms": 0.0,
            "std_dev": 0.0,
            "peak_to_peak": 0.0,
            "peak": 0.0,
            "kurtosis": 0.0,
            "crest_factor": 0.0,
        }
    mean_val = float(np.mean(x))
    rms_val = float(np.sqrt(np.mean(np.square(x))))
    std_val = float(np.std(x, ddof=1)) if len(x) > 1 else 0.0
    p2p_val = float(np.ptp(x))
    peak_val = float(np.max(np.abs(x)))
    kurt_val = float(stats.kurtosis(x, fisher=False, bias=False)) if len(x) > 3 else 3.0
    crest_val = float(peak_val / (rms_val + 1e-12))
    return {
        "mean": mean_val,
        "rms": rms_val,
        "std_dev": std_val,
        "peak_to_peak": p2p_val,
        "peak": peak_val,
        "kurtosis": kurt_val,
        "crest_factor": crest_val,
    }
def extract_window_features(window: np.ndarray, fs: float = 12000.0) -> Dict[str, float]:
    """
    Extract 12 statistical time-domain and basic spectral features from a single vibration window.
    """
    w = np.asarray(window, dtype=np.float64)
    eps = 1e-12
    mean_val = float(np.mean(w))
    std_val = float(np.std(w, ddof=1)) if len(w) > 1 else 0.0
    rms_val = float(np.sqrt(np.mean(np.square(w))))
    abs_w = np.abs(w)
    mean_abs = float(np.mean(abs_w))
    peak_val = float(np.max(abs_w))
    p2p_val = float(np.ptp(w))
    crest_factor = float(peak_val / (rms_val + eps))
    kurt_val = float(stats.kurtosis(w, fisher=False, bias=False)) if len(w) > 3 else 3.0
    skew_val = float(stats.skew(w, bias=False)) if len(w) > 2 else 0.0
    shape_factor = float(rms_val / (mean_abs + eps))
    impulse_factor = float(peak_val / (mean_abs + eps))
    root_amp = float(np.square(np.mean(np.sqrt(abs_w))))
    clearance_factor = float(peak_val / (root_amp + eps))
    fft_mag = np.abs(np.fft.rfft(w - mean_val))
    freqs = np.fft.rfftfreq(len(w), d=1.0 / fs)
    mag_sum = float(np.sum(fft_mag))
    spectral_centroid = float(np.sum(freqs * fft_mag) / (mag_sum + eps))
    return {
        "mean": mean_val,
        "std_dev": std_val,
        "rms": rms_val,
        "peak": peak_val,
        "peak_to_peak": p2p_val,
        "crest_factor": crest_factor,
        "kurtosis": kurt_val,
        "skewness": skew_val,
        "shape_factor": shape_factor,
        "impulse_factor": impulse_factor,
        "clearance_factor": clearance_factor,
        "spectral_centroid_hz": spectral_centroid,
    }
def extract_features_from_windows(windows: np.ndarray, fs: float = 12000.0) -> pd.DataFrame:
    """
    Extract feature matrix DataFrame from a 2D array of windows (n_windows, window_size).
    """
    rows = [extract_window_features(win, fs=fs) for win in windows]
    return pd.DataFrame(rows, columns=FEATURE_NAMES)
