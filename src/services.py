"""Framework-independent validated services. No Gradio, Flask, HTTP adapter or UI imports."""
import json,html,hashlib
from pathlib import Path
import numpy as np
import pandas as pd
from .processing import read_csv,validate_signal
from .inference import analyse
from .inputs import parse_manual,build_signal,geometry_from_form
from .demo_reference import generate_synthetic_demo_recording
from .rul import life_budget,trend_rul
from .sound import analyse_wav,simulated_audio,level_summary
ROOT=Path(__file__).resolve().parents[1]
MANIFEST=json.loads((ROOT/'data/manifest.json').read_text())
RPMS={r['label']:r['rpm'] for r in MANIFEST if r['split']=='test'}
SCENARIOS={label.lower().replace(' ','_'):label for label in ['Normal','Inner Race Fault','Outer Race Fault','Rolling Element Fault']}

def fingerprint(config,content=None):
    h=hashlib.sha256(json.dumps(config,sort_keys=True,allow_nan=True,default=str).encode());h.update(b'NO_UPLOAD' if content is None else b'UPLOAD:'+content);return h.hexdigest()

def preview_records(df):
    """Valid JSON preview; selected signal stays strictly validated, never imputed.
    Nonfinite *unused metadata* is labelled text, not an invalid JSON number.
    """
    frame=df.head(8).astype(object).where(df.head(8).notna(),None)
    def encode(value):
        if isinstance(value,(float,np.floating)) and not np.isfinite(value):
            return None if np.isnan(value) else 'Infinity' if value>0 else '-Infinity'
        return value
    return [{k:encode(v) for k,v in row.items()} for row in frame.to_dict('records')]

def vibration(config,content=None):
    c=dict(config);source=c.get('source','sample');name=c.get('sample','normal')
    if name not in SCENARIOS:raise ValueError('Select a supported scenario.')
    builder=None
    if source=='sample':
        df=read_csv((ROOT/'data/sample_data'/f'{name}.csv').read_bytes());x=df.acceleration;fs=48000.;mode=c.get('mode','classification');compatible=True;rpm=float(RPMS[SCENARIOS[name]]);label='CWRU held-out example — '+SCENARIOS[name];column='acceleration'
    elif source=='synthetic':
        df=generate_synthetic_demo_recording(SCENARIOS[name],n_samples=8192,fs=12000);x=df.DE_vibration;fs=12000.;mode='signal';compatible=False;rpm=None;label='SYNTHETIC illustration — '+SCENARIOS[name];column='DE_vibration'
    elif source=='builder':
        x,fs,rpm,builder=build_signal(c);mode='signal';compatible=False;label='SYNTHETIC parameter-built waveform — no diagnosis';column='synthetic_acceleration';df=pd.DataFrame({column:x})
    elif source in ('manual','upload'):
        try:fs=float(c.get('fs','nan'));r=str(c.get('rpm','')).strip();rpm=float(r) if r else None
        except (ValueError,TypeError) as e:raise ValueError('Sample rate and supplied RPM must be numeric.') from e
        mode=c.get('mode','signal');compatible=c.get('compatible') in (True,'true');column=c.get('column','acceleration')
        if source=='manual':
            x=parse_manual(c.get('manual_samples',''),fs)
            if len(x)>262144:raise ValueError('Manual input is limited to 262144 samples; use CSV for longer data.')
            df=pd.DataFrame({'acceleration':x});column='acceleration';label='Pasted measured waveform (provenance not verified)'
        else:
            df=read_csv(content)
            if column not in df.columns:raise ValueError('Select an existing signal column explicitly.')
            if column.lower() in ('time','time_sec','rpm','motor_rpm','condition_label','source_type'):raise ValueError('Choose vibration signal, not a metadata column.')
            x=df[column];label='Uploaded measured CSV (provenance not verified)'
            if 'time_sec' in df:
                t=validate_signal(df.time_sec,fs);delta=np.diff(t)
                if np.any(delta<=0) or not np.allclose(delta,1/fs,rtol=.03,atol=1e-9):raise ValueError('time_sec is nonuniform or disagrees with the declared sampling rate.')
    else:raise ValueError('Unsupported vibration source.')
    c['custom_geometry']='true' if c.get('custom_geometry') in (True,'true') else 'false'
    geometry=geometry_from_form(c,rpm)
    d=analyse(x,fs,mode,label,rpm,compatible,geometry,builder);d.update(signal_column=column,preview=preview_records(df))
    if source in ('manual','builder'):d['raw_input_samples']=np.asarray(x,dtype=float).tolist()
    return d

def life(config,content=None):
    mode=config.get('rul_mode','budget')
    if mode=='budget':return life_budget(config)
    if mode=='demo':df=read_csv((ROOT/'data/sample_data/degradation_demo.csv').read_bytes());label='SYNTHETIC degradation demo — not real failure validation'
    elif mode=='trend':df=read_csv(content if content is not None else config.get('history_text','').encode());label='User-supplied operating-age history (provenance unverified)'
    else:raise ValueError('Unsupported life-planning mode.')
    if not {'age','indicator'}<=set(df.columns):raise ValueError('Trend CSV needs age,indicator headers, at least 6 ordered operating ages.')
    return trend_rul(config,pd.to_numeric(df.age,errors='raise'),pd.to_numeric(df.indicator,errors='raise'),label)

def sound(config,content=None):
    mode=config.get('sound_mode','demo')
    if mode=='demo':d=simulated_audio(config.get('target_dbfs',-24))
    elif mode in ('wav','recording'):
        try:channel=int(config.get('channel',0))
        except (ValueError,TypeError) as e:raise ValueError('Channel must be a zero-based integer.') from e
        if float(config.get('channel',0))!=channel:raise ValueError('Channel must be an integer.')
        d=analyse_wav(content,channel)
        if mode=='recording':d['source']='Browser microphone recording uploaded through Streamlit — not continuous live telemetry'
    elif mode=='log':
        df=read_csv(content if content is not None else config.get('sound_log','').encode())
        if not {'level_db','duration_sec'}<=set(df.columns):raise ValueError('Log needs level_db,duration_sec headers.')
        d=level_summary(pd.to_numeric(df.level_db,errors='raise'),pd.to_numeric(df.duration_sec,errors='raise'),config.get('convention','dBFS'),source='User-supplied sound level log (unverified)')
    else:raise ValueError('Unsupported sound source.')
    low,high,warn,critical,offset=[float(config.get(k,v)) for k,v in [('low',-90),('high',0),('warning',-20),('critical',-6),('offset',0)]]
    if not np.isfinite([low,high,warn,critical,offset]).all() or not -300<=low<high<=300 or not low<=warn<=critical<=high or abs(offset)>200:raise ValueError('Require finite −300 ≤ low < high ≤ 300 dB, low ≤ warning ≤ high alert ≤ high, and offset within ±200 dB.')
    note=str(config.get('reference_note') or '').strip()
    if offset and not note:raise ValueError('Document reference/conditions before applying an offset; still unverified.')
    if offset and mode=='log':raise ValueError('Offsets apply to digital recordings/simulation only, not external logs.')
    d['display_settings']=dict(low=low,high=high,warning=warn,critical=critical,offset=offset,reference_note=note)
    d['display_convention']='User-reference-adjusted dB (unverified; not certified SPL)' if offset else d['convention']
    level=None if d['current_db'] is None else d['current_db']+offset
    d['alert']='Silence — no finite dB' if level is None else 'High project alert' if level>=critical else 'Project warning' if level>=warn else 'Below configured thresholds'
    if level is not None and not low<=level<=high:d['alert']+='; outside display range (number preserved)'
    d['limitations']+=['Streamlit analyses completed recordings, not continuously streamed microphone telemetry.','Microphone recordings are sent to the server. Browser/device processing and encoding may alter gain; physical acoustic calibration is not established.']
    return d

def downloads(d,kind):
    files={kind+'.json':json.dumps(d,indent=2,allow_nan=False).encode()}
    if kind=='vibration':
        files['features.csv']=pd.DataFrame(d['features']).to_csv(index=False).encode()
        if 'raw_input_samples' in d:
            x=d['raw_input_samples'];files['waveform.csv']=pd.DataFrame({'time_sec':np.arange(len(x))/d['fs'],'acceleration':x}).to_csv(index=False).encode()
        files['analysis_report.html']=('<!doctype html><meta charset="utf-8"><title>RaceGuard analysis</title><style>body{font:14px Arial;margin:32px}pre{white-space:pre-wrap}</style><h1>RaceGuard / educational signal analysis</h1><pre>'+html.escape(json.dumps(d,indent=2,allow_nan=False))+'</pre>').encode()
    elif kind=='rul':
        hist=list(zip(d['trend']['age'],d['trend']['remaining'])) if d['mode']=='budget' else d['history']
        frame=pd.DataFrame(hist,columns=['age','remaining']) if d['mode']=='budget' else pd.DataFrame(hist)
        files['rul_history.csv']=frame.to_csv(index=False).encode()
    else:
        h=d['history'];offset=d['display_settings']['offset'];files['sound_intervals.csv']=pd.DataFrame({'elapsed_sec':h['time_sec'],'duration_sec':h['duration_sec'],'raw_level_db':h['level_db'],'displayed_level_db':[None if x is None else x+offset for x in h['level_db']]}).to_csv(index=False).encode()
    return files
