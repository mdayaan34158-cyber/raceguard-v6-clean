"""Manual waveform entry and explicit, reproducible simulation inputs."""
import re
import numpy as np
from .processing import validate_signal

def parse_manual(text, fs):
    if not text.strip():raise ValueError('Paste acceleration samples, or load an example into the editor.')
    if re.search(r'[,;]\s*[,;]',text):raise ValueError('Empty value between separators. Missing samples must not be silently removed.')
    tokens=re.split(r'[\s,;]+',text.strip())
    if any(not t for t in tokens):raise ValueError('Remove leading/trailing separators or empty samples.')
    try:x=np.array([float(t) for t in tokens],dtype=float)
    except ValueError as e:raise ValueError('Manual samples must be plain numbers separated by commas, semicolons, spaces or newlines. Do not paste a CSV header.') from e
    return validate_signal(x,fs)

def number(form,key,default,low,high,integer=False):
    try:v=float(form.get(key,default))
    except (ValueError,TypeError) as e:raise ValueError(f'{key} must be numeric.') from e
    if not np.isfinite(v) or v<low or v>high or (integer and not v.is_integer()):
        raise ValueError(f'{key} must be {"an integer " if integer else ""}between {low} and {high}.')
    return int(v) if integer else v

def build_signal(form):
    fs=number(form,'builder_fs',12000,1000,192000)
    n=number(form,'builder_n',8192,4096,262144,True)
    rpm=number(form,'builder_rpm',1800,1,60000)
    amplitude=number(form,'builder_amplitude',.08,0,100)
    noise=number(form,'builder_noise',.04,0,100)
    impact_amp=number(form,'builder_impact_amp',.6,0,100)
    rate=number(form,'builder_rate',107,0,1000)
    carrier=number(form,'builder_carrier',2800,1,96000)
    decay_ms=number(form,'builder_decay',1,0.05,50)
    seed=number(form,'builder_seed',42,0,4294967295,True)
    if rpm/60>=fs/2:raise ValueError('Synthetic rotational frequency exceeds Nyquist. Increase fs or decrease RPM.')
    if carrier>=fs/2:raise ValueError('Synthetic carrier must be strictly below fs/2 (Nyquist).')
    if rate>=fs/2:raise ValueError('Synthetic impact rate must be below Nyquist.')
    t=np.arange(n)/fs;rng=np.random.default_rng(seed)
    base=amplitude*np.sin(2*np.pi*(rpm/60)*t)
    x=base+noise*rng.normal(size=n)
    tau=decay_ms/1000
    if rate>0 and impact_amp>0:
        length=max(2,int(np.ceil(8*tau*fs)));u=np.arange(min(length,n))/fs
        pulse=impact_amp*np.exp(-u/tau)*np.sin(2*np.pi*carrier*u)
        for start in (np.arange(0,n/fs,1/rate)*fs).astype(int):
            count=min(len(pulse),n-start)
            if count>0:x[start:start+count]+=pulse[:count]
    validate_signal(x,fs)
    params=dict(fs=fs,n=n,rpm=rpm,amplitude=amplitude,noise_sigma=noise,impact_amplitude=impact_amp,impact_rate_hz=rate,carrier_hz=carrier,decay_ms=decay_ms,seed=seed)
    return x,fs,rpm,params

def geometry_from_form(form,rpm):
    if form.get('custom_geometry')!='true':return None
    if rpm is None:raise ValueError('Custom bearing-frequency calculation requires a known RPM.')
    z=number(form,'geometry_z','',2,100,True)
    d=number(form,'geometry_d','',0.000001,10000)
    D=number(form,'geometry_D','',0.000001,10000)
    theta=number(form,'geometry_theta','',0,89)
    if d>=D:raise ValueError('Ball diameter d must be smaller than pitch diameter D, in the same units.')
    return dict(z=z,d=d,D=D,theta_deg=theta,rpm=float(rpm))
