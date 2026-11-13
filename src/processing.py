"""Strict, shared signal contract for training and HTTP inference."""
import io
import numpy as np
import pandas as pd
from .feature_extraction import FEATURE_NAMES, extract_features_from_windows, compute_basic_signal_stats
FS=48000
WINDOW=4096
MAX_SAMPLES=1_000_000

def read_csv(content):
    if not content or len(content)>20*1024*1024:
        raise ValueError('CSV must be nonempty and at most 20 MB.')
    try:
        df=pd.read_csv(io.BytesIO(content), on_bad_lines='error')
    except Exception as exc:
        raise ValueError('Cannot parse CSV. Use a UTF-8 comma-separated file with a header.') from exc
    if df.empty or len(df)>MAX_SAMPLES:
        raise ValueError('CSV must contain 1–1,000,000 rows.')
    return df

def validate_signal(values, fs, minimum=WINDOW):
    if not np.isfinite(fs) or fs<=0:
        raise ValueError('Sampling frequency must be finite and positive.')
    try:
        x=pd.to_numeric(pd.Series(values),errors='raise').to_numpy(dtype=float)
    except (ValueError,TypeError) as exc:
        raise ValueError('Signal must contain only numbers; corrupted cells are not interpolated.') from exc
    if len(x)<minimum or len(x)>MAX_SAMPLES:
        raise ValueError(f'Signal needs {minimum}–{MAX_SAMPLES} samples.')
    if not np.isfinite(x).all():
        raise ValueError('Signal contains missing or infinite values. No records were silently discarded.')
    if np.max(np.abs(x))>1e6 or np.std(x)<1e-12:
        raise ValueError('Signal is constant, near-constant, or outside supported numerical range.')
    return x

def features(x,fs=FS):
    x=validate_signal(x,fs)
    # Each window is demeaned independently, identically in train and inference.
    n=len(x)//WINDOW
    windows=x[:n*WINDOW].reshape(n,WINDOW).copy()
    windows-=windows.mean(axis=1,keepdims=True)
    table=extract_features_from_windows(windows,fs)
    if not np.isfinite(table.to_numpy()).all():
        raise ValueError('Undefined signal features; check sensor input.')
    return table, len(x)-n*WINDOW

def plots(x,fs):
    # First 4096 actual samples; spectrum is not a fabricated full-record spectrum.
    segment=x[:WINDOW]-np.mean(x[:WINDOW])
    taper=np.hanning(len(segment))
    mag=np.abs(np.fft.rfft(segment*taper))/taper.sum()
    mag[1:-1]*=2
    stride=max(1,len(segment)//1800)
    return dict(time=(np.arange(len(segment))[::stride]/fs).tolist(),signal=segment[::stride].tolist(),frequency=np.fft.rfftfreq(len(segment),1/fs).tolist(),amplitude=mag.tolist(),resolution_hz=fs/len(segment))

def stats(x):
    return compute_basic_signal_stats(x)
