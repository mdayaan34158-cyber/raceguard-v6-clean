"""Digital audio and external-level log summaries; no automatic microphone SPL calibration."""
import io
import warnings
import numpy as np
from scipy.io import wavfile
from .rul import finite


def db(amplitude):
    return float(20*np.log10(amplitude)) if amplitude>0 else None


def level_summary(levels,durations,convention='dBFS',source='Uploaded levels'):
    values=np.asarray(levels,dtype=float);dt=np.asarray(durations,dtype=float)
    if values.ndim!=1 or dt.ndim!=1 or len(values)!=len(dt) or not 1<=len(values)<=10000:raise ValueError('Sound log requires 1–10000 level/duration pairs.')
    if not np.isfinite(values).all() or not np.isfinite(dt).all() or np.any(dt<=0) or np.any(np.abs(values)>300):raise ValueError('Levels must be finite within ±300 dB and durations finite/positive. No rows are discarded.')
    if float(dt.sum())>86400:raise ValueError('Sound log exceeds the supported 24-hour aggregation span.')
    if convention not in ('dBFS','User-declared dB SPL (unverified)'):raise ValueError('Declare dBFS or externally measured dB SPL; weighting/calibration are not inferred.')
    peak=float(values.max());mean_db=float(peak+10*np.log10(np.dot(dt,10**((values-peak)/10))/dt.sum()))
    return dict(source=source,convention=convention,duration_sec=float(dt.sum()),current_db=float(values[-1]),minimum_db=float(values.min()),maximum_db=peak,average_db=mean_db,sample_peak_db=None,clipped_samples=None,history={'time_sec':np.cumsum(dt).tolist(),'level_db':values.tolist(),'duration_sec':dt.tolist()},formulas=[f'Energy average = 10 log10[Σ Δtᵢ×10^(Lᵢ/10) / ΣΔtᵢ] = {mean_db:.9g} {convention}','Minimum/maximum are interval levels, NOT instantaneous waveform peaks.'],reliability='Externally supplied level logs; calibration, sensor accuracy and weighting are user-declared, not independently verified.',limitations=['Do not mix dBA, dBC, unweighted SPL or dBFS in a single log.','Average is energy/duration weighted, not arithmetic mean of decibels.','No true-peak, standard time weighting, frequency weighting or occupational exposure compliance calculation.'])


def analyse_audio(x,fs,source='Uploaded WAV',channel=0):
    data=np.asarray(x,dtype=float)
    if data.ndim!=1 or not 16<=len(data)<=10_000_000:raise ValueError('Audio needs 16–10000000 samples in the selected channel.')
    fs=finite(fs,'Audio sampling frequency',1000,192000)
    if not np.isfinite(data).all() or np.any(np.abs(data)>10):raise ValueError('Audio contains invalid/nonfinite or unsupported sample amplitudes.')
    if len(data)/fs>300:raise ValueError('WAV/audio analysis is limited to 300 seconds.')
    length=max(1,int(round(fs*.25)));levels=[];times=[];durations=[];energies=[]
    for start in range(0,len(data),length):
        a=data[start:start+length];power=float(np.mean(a*a));levels.append(db(np.sqrt(power)));times.append((start+len(a))/fs);durations.append(len(a)/fs);energies.append(power)
    total_rms=float(np.sqrt(np.mean(data*data)));peak=float(np.max(np.abs(data)));silent=any(v is None for v in levels)
    return dict(source=source,convention='dBFS',sample_rate=fs,selected_channel=channel,duration_sec=len(data)/fs,current_db=levels[-1],minimum_db=None if silent else min(levels),maximum_db=max((v for v in levels if v is not None),default=None),average_db=db(total_rms),sample_peak_db=db(peak),clipped_samples=int(np.sum(np.abs(data)>=.999)),silent_intervals=int(sum(v is None for v in levels)),history={'time_sec':times,'level_db':levels,'duration_sec':durations},formulas=[f'RMS = sqrt(Σx²/N) = {total_rms:.12g}; L_RMS = 20 log10(RMS / 1) = {db(total_rms)} dBFS',f'Sample peak = max|x| = {peak:.12g}; L_peak = 20 log10(peak / 1) = {db(peak)} dBFS','0 dBFS is RMS=1 under this digital convention; a peak-amplitude-1 sine has RMS level about −3.0103 dBFS. Silence has no finite logarithm; null means digital silence, NOT 0 dB.'],reliability='Digital amplitude measurement only. Absolute SPL, frequency response and physical accuracy are not established.',limitations=['Not dBA/dBC and not calibrated sound pressure. WAV gain, microphone processing, distance and source affect levels.','Peak is sample peak, NOT intersample true peak or certified acoustic peak.','Intervals are 0.25 seconds (last may be shorter); no IEC Fast/Slow or A/C weighting is claimed.','Near-full-scale samples flag possible clipping; actual analog clipping may occur below that point.'])


def analyse_wav(content,channel=0):
    if not content or len(content)>20*1024*1024:raise ValueError('WAV must be nonempty and at most 20 MB.')
    try:
        with warnings.catch_warnings():
            warnings.simplefilter('error',wavfile.WavFileWarning)
            fs,a=wavfile.read(io.BytesIO(content))
    except Exception as exc:raise ValueError('Use a well-formed uncompressed PCM or floating-point WAV. MP3/AAC are not supported.') from exc
    if a.dtype==np.uint8:x=(a.astype(float)-128)/128
    elif np.issubdtype(a.dtype,np.signedinteger):x=a.astype(float)/(2**(a.dtype.itemsize*8-1))
    elif np.issubdtype(a.dtype,np.floating):x=a.astype(float)
    else:raise ValueError('Unsupported WAV encoding.')
    n_channels=1 if x.ndim==1 else x.shape[1] if x.ndim==2 else 0
    if not 1<=n_channels<=8 or channel<0 or channel>=n_channels:raise ValueError('Selected WAV channel does not exist (zero-based), or channel count exceeds 8.')
    result=analyse_audio(x if x.ndim==1 else x[:,channel],fs,channel=channel);result['available_channels']=n_channels
    return result


def simulated_audio(target_dbfs=-24):
    level=finite(target_dbfs,'Simulated sine RMS level',-90,-4)
    fs=16000;t=np.arange(fs*8)/fs
    # Envelope changes are deliberately explicit, not fake live microphone readings.
    envelope=.7+.3*np.sin(2*np.pi*.3*t)
    x=np.sqrt(2)*10**(level/20)*envelope*np.sin(2*np.pi*1000*t)
    result=analyse_audio(x,fs,source='SIMULATED digital sine with changing envelope — not a microphone')
    result['simulation']={'nominal_upper_rms_dbfs':level,'sine_hz':1000,'envelope':'0.7 + 0.3 sin(2π×0.3 t)','duration_sec':8}
    return result
