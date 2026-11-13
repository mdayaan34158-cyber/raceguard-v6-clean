"""Numerical calculation ledger generated from the exact signal and model features."""
import numpy as np
from .processing import WINDOW

def fmt(v):
    return f'{float(v):.12g}'

def card(name,formula,substitution,value,note=''):
    return dict(name=name,formula=formula,substitution=substitution,value=float(value) if isinstance(value,(int,float,np.floating,np.integer)) else value,note=note)

def signal_ledger(x,fs,feature_values=None):
    x=np.asarray(x,dtype=float);n=len(x);mu=float(np.mean(x));center=x-mu
    sx=float(x.sum());sq=float(np.sum(x*x));ss=float(np.sum(center**2));sa=float(np.abs(x).sum());sr=float(np.sqrt(np.abs(x)).sum())
    peak=float(np.max(np.abs(x)));lo=float(x.min());hi=float(x.max());rms=float(np.sqrt(sq/n));sd=float(np.sqrt(ss/(n-1)))
    m2=ss/n;m3=float(np.mean(center**3));m4=float(np.mean(center**4));g1=m3/m2**1.5;b2=m4/m2**2
    skew=np.sqrt(n*(n-1))/(n-2)*g1;kurt=((n-1)/((n-2)*(n-3)))*((n+1)*(b2-3)+6)+3
    eps=1e-12;mag=np.abs(np.fft.rfft(center));freq=np.fft.rfftfreq(n,1/fs);s_mag=float(mag.sum());s_fmag=float(np.dot(freq,mag));centroid=s_fmag/(s_mag+eps)
    values=dict(mean=mu,std_dev=sd,rms=rms,peak=peak,peak_to_peak=hi-lo,crest_factor=peak/(rms+eps),kurtosis=kurt,skewness=skew,shape_factor=rms/(sa/n+eps),impulse_factor=peak/(sa/n+eps),clearance_factor=peak/((sr/n)**2+eps),spectral_centroid_hz=centroid)
    if feature_values is not None:values.update(feature_values)
    f=fmt
    rows=[
      card('Mean','μ = Σxᵢ / N',f'{f(sx)} / {n}',values['mean']),
      card('Population variance','σ² = Σ(xᵢ−μ)² / N',f'{f(ss)} / {n}',m2,'Shown for clarity; the model uses SAMPLE standard deviation.'),
      card('Sample variance','s² = Σ(xᵢ−μ)² / (N−1)',f'{f(ss)} / ({n}−1)',ss/(n-1)),
      card('Sample standard deviation','s = √[Σ(xᵢ−μ)² / (N−1)]',f'√[{f(ss)} / {n-1}]',values['std_dev']),
      card('RMS','RMS = √(Σxᵢ² / N)',f'√({f(sq)} / {n})',values['rms']),
      card('Absolute peak','peak = max|xᵢ|',f'max|xᵢ| over {n} samples = {f(peak)}',values['peak']),
      card('Peak-to-peak','p2p = max(x) − min(x)',f'{f(hi)} − ({f(lo)})',values['peak_to_peak']),
      card('Crest factor','CF = peak / (RMS + ε)',f'{f(peak)} / ({f(rms)} + 1e−12)',values['crest_factor']),
      card('Skewness (bias corrected)','G₁ = √[N(N−1)]/(N−2) × m₃/m₂^(3/2)',f'√[{n}×{n-1}]/{n-2} × {f(m3)}/{f(m2)}^(3/2)',values['skewness'],'mᵣ = Σ(xᵢ−μ)^r / N; SciPy bias=False.'),
      card('Ordinary kurtosis (bias corrected)','K = (N−1)/[(N−2)(N−3)] × [(N+1)(m₄/m₂²−3)+6] + 3',f'{n-1}/({n-2}×{n-3}) × [({n+1})×({f(m4)}/{f(m2)}²−3)+6] + 3',values['kurtosis'],'Ordinary/Pearson kurtosis, not excess; Gaussian theoretical value is 3, not an alarm limit.'),
      card('Shape factor','SF = RMS / (Σ|xᵢ|/N + ε)',f'{f(rms)} / ({f(sa)}/{n} + 1e−12)',values['shape_factor']),
      card('Impulse factor','IF = peak / (Σ|xᵢ|/N + ε)',f'{f(peak)} / ({f(sa)}/{n} + 1e−12)',values['impulse_factor']),
      card('Clearance factor','CLF = peak / [(Σ√|xᵢ|/N)² + ε]',f'{f(peak)} / [({f(sr)}/{n})² + 1e−12]',values['clearance_factor']),
      card('Spectral centroid','C = Σ fₖ|Xₖ| / (Σ|Xₖ| + ε)',f'{f(s_fmag)} / ({f(s_mag)} + 1e−12)',values['spectral_centroid_hz'],'Un-tapered rFFT of centered samples, matching the trained feature. This is amplitude weighting, not PSD.'),
      card('Sample spacing','Δt = 1 / fs',f'1 / {f(fs)}',1/fs,'seconds'),
      card('Window/record duration','T = N / fs',f'{n} / {f(fs)}',n/fs,'Duration represented by N samples; final timestamp is (N−1)/fs.'),
      card('FFT bin spacing','Δf = fs / N',f'{f(fs)} / {n}',fs/n,'Hz; does not guarantee resolving two nearby tones.'),
      card('Nyquist frequency','f_N = fs / 2',f'{f(fs)} / 2',fs/2,'Hz')]
    taper=np.hanning(n);spectrum=np.fft.rfft(center*taper);k=int(np.argmax(np.abs(spectrum)[1:])+1);scale=1 if k==0 or (n%2==0 and k==n//2) else 2
    rows.extend([
      card('DFT / FFT definition','Xₖ = Σₙ₌₀ᴺ⁻¹ (xₙ−μ) exp(−j2πkn/N)',f'Hann-display FFT at bin k={k}: Re={fmt(spectrum[k].real)}, Im={fmt(spectrum[k].imag)}',float(np.abs(spectrum[k])),'For display replace (xₙ−μ) with (xₙ−μ)×hₙ, hₙ=0.5[1−cos(2πn/(N−1))]. Value shown is the magnitude of that complex FFT bin.'),
      card('Display peak-bin frequency','fₖ = k fs / N',f'{k}×{fmt(fs)}/{n}',k*fs/n,'Largest non-DC Hann-display bin, not a fault-frequency confirmation.'),
      card('Display peak-bin amplitude','Aₖ = sₖ |FFT[(x−μ)h]ₖ| / Σh; sₖ=2 except DC/even-N Nyquist',f'{scale}×{fmt(abs(spectrum[k]))}/{fmt(taper.sum())}',scale*abs(spectrum[k])/taper.sum(),'Chart is first model window only. For other selected windows, this is an additional window-specific calculation.')])
    return dict(n=n,sum_x=sx,sum_x_squared=sq,sum_centered_squared=ss,sum_absolute=sa,sum_sqrt_absolute=sr,m2=m2,m3=m3,m4=m4,first_samples=x[:8].tolist(),last_samples=x[-8:].tolist(),rows=rows)

def characteristic_ledger(rpm,compatible,geometry=None):
    if rpm is None:return [],{}
    f=rpm/60;rows=[card('Shaft frequency','fᵣ = RPM / 60',f'{fmt(rpm)} / 60',f,'Hz')]
    if geometry:
        z=geometry['z'];d=geometry['d'];D=geometry['D'];theta=geometry['theta_deg'];q=(d/D)*np.cos(np.deg2rad(theta))
        vals={'BPFO':(z/2)*f*(1-q),'BPFI':(z/2)*f*(1+q),'BSF':(D/(2*d))*f*(1-q*q),'FTF':.5*f*(1-q)}
        rows.extend([
          card('Geometry ratio','q = (d/D)cosθ',f'({fmt(d)}/{fmt(D)})cos({fmt(theta)}°)',q),
          card('BPFO','BPFO = (Z/2) fᵣ (1−q)',f'({z}/2)×{fmt(f)}×(1−{fmt(q)})',vals['BPFO']),
          card('BPFI','BPFI = (Z/2) fᵣ (1+q)',f'({z}/2)×{fmt(f)}×(1+{fmt(q)})',vals['BPFI']),
          card('BSF','BSF = [D/(2d)] fᵣ (1−q²)',f'[{fmt(D)}/(2×{fmt(d)})]×{fmt(f)}×(1−{fmt(q)}²)',vals['BSF'],'Ball spin, not twice-spin contact rate.'),
          card('FTF','FTF = ½ fᵣ (1−q)',f'0.5×{fmt(f)}×(1−{fmt(q)})',vals['FTF'])])
        return rows,vals
    if compatible:
        factors={'BPFO':3.5848,'BPFI':5.4152,'FTF':.39828,'2×BSF (CWRU rolling element)':4.7135}
        for name,k in factors.items():rows.append(card(name,'f = published CWRU multiplier × fᵣ',f'{k} × {fmt(f)}',k*f,'Specific CWRU drive-end reference, not a generic bearing.'))
        return rows,{k:v*f for k,v in factors.items()}
    return rows,{}

def build_ledger(x,fs,table,result,rpm,compatible,geometry=None,builder=None):
    x=np.asarray(x,dtype=float);windows=[]
    for i,row in enumerate(table.to_dict('records')):
        raw=x[i*WINDOW:(i+1)*WINDOW];offset=float(raw.mean());w=raw-offset
        ledger=signal_ledger(w,fs,row);ledger.update(index=i,start_sample=i*WINDOW,end_sample=(i+1)*WINDOW-1,removed_mean=offset,preprocessing=f'wᵢ = rawᵢ − {fmt(offset)}; N={WINDOW}; no filtering or resampling')
        windows.append(ledger)
    # Raw panel only computes whole-input basic stats; do not invent undefined whole-record moments.
    raw_n=len(x);mu=float(x.mean());ss=float(np.sum((x-mu)**2));sq=float(np.sum(x*x));peak=float(np.max(np.abs(x)))
    raw=[card('Raw mean','μ = Σxᵢ/N',f'{fmt(x.sum())}/{raw_n}',mu),card('Raw RMS','RMS = √(Σxᵢ²/N)',f'√({fmt(sq)}/{raw_n})',result['stats']['rms']),card('Raw sample standard deviation','s = √[Σ(xᵢ−μ)²/(N−1)]',f'√({fmt(ss)}/{raw_n-1})',result['stats']['std_dev']),card('Raw peak','max|xᵢ|',f'max|xᵢ| = {fmt(peak)}',peak),card('Raw peak-to-peak','max−min',f'{fmt(x.max())}−({fmt(x.min())})',result['stats']['peak_to_peak']),card('Raw crest factor','peak/(RMS+ε)',f'{fmt(peak)}/({fmt(result["stats"]["rms"])}+1e−12)',result['stats']['crest_factor'])]
    # Basic stats panel also reports bias-corrected ordinary kurtosis.
    m2=ss/raw_n;m4=float(np.mean((x-mu)**4));raw.append(card('Raw ordinary kurtosis','K = (N−1)/[(N−2)(N−3)] × [(N+1)(m₄/m₂²−3)+6]+3',f'{raw_n-1}/({raw_n-2}×{raw_n-3}) × [{raw_n+1}×({fmt(m4)}/{fmt(m2)}²−3)+6]+3',result['stats']['kurtosis']))
    bearing,markers=characteristic_ledger(rpm,compatible,geometry)
    n=len(table);used=n*WINDOW
    coverage=[card('Completed windows','W = floor(N_input / L)',f'floor({len(x)}/{WINDOW})',n),card('Trailing samples excluded from model','tail = N_input − W×L',f'{len(x)}−{n}×{WINDOW}',len(x)-used)]
    inference=[]
    if result['mode']=='classification':
        winning=result['predicted_class'];count=result['votes'][winning]
        inference=[card('Window votes','count(c) = Σⱼ 1[predictionⱼ=c]',f'{winning}: {count} of {n} windows',count),card('Window agreement','A = max count(c) / W',f'{count}/{n}',count/n,'NOT probability, calibration, severity or safety.'),card('Final class','argmax_c count(c)',str(result['votes']),winning,'Deterministic alphabetical tie breaking; low agreement → Monitor.'),card('Provisional review state','if A<0.70: Monitor; else Normal if class=Normal; else Warning',f'A={fmt(count/n)}, class={winning}',result['review_state'],'0.70 is an unvalidated project policy, not an engineering standard.')]
    return dict(version=2,raw_rows=raw,coverage=coverage,windows=windows,bearing=bearing,inference=inference,geometry=geometry,builder=builder,notes=['These sums are computed over every sample in the specified scope, not an illustrative substitute dataset.','Displayed substitutions use 12 significant digits; computation uses float64. Small display-rounding differences are expected.','Raw panel statistics and demeaned model-window statistics use different scopes. Select the model window explicitly.','FFT chart uses a Hann taper. Spectral-centroid features use the preserved un-tapered FFT convention.']) ,markers
