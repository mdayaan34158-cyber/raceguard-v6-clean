"""FULL MAIN INTERFACE — deploy with: python -m streamlit run app.py.
Numerical services remain in src/ for independent testing and maintenance.
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from src.services import vibration,life,sound,downloads,fingerprint,ROOT,SCENARIOS
from src.processing import read_csv
from src.inference import load_model
from src.presentation import BRAND,NOTICE,FOOTER,hero,kpis,bearing
st.set_page_config(page_title='RaceGuard | Analysis studio',page_icon='⚙️',layout='wide')
st.html('<style>'+(ROOT/'assets/raceguard.css').read_text()+'</style>')

@st.cache_resource
def model_ready(revision):
    # A changed/replaced artifact must invalidate readiness, not reuse an old badge.
    return load_model()['name']

def line(series,xlabel,ylabel,bounds=None,*,key):
    fig=go.Figure()
    for label,x,y,dashed in series:fig.add_trace(go.Scatter(x=x,y=y,name=label,mode='lines+markers' if len(x)<100 else 'lines',connectgaps=False,line={'dash':'dash' if dashed else 'solid'}))
    fig.update_layout(template='plotly_dark',paper_bgcolor='#101d29',plot_bgcolor='#101d29',colorway=['#53dfca','#79aefd','#f6b764'],font=dict(color='#adc2cf',size=11),height=290,margin=dict(l=20,r=20,t=35,b=35),xaxis_title=xlabel,yaxis_title=ylabel,legend=dict(orientation='h',y=1.15),hovermode='x unified')
    if bounds:fig.update_yaxes(range=list(bounds),autorange=False)
    st.plotly_chart(fig,width='stretch',config={'displaylogo':False},key=key)

def export_buttons(d,kind,prefix):
    st.caption('Export before closing. JSON retains provenance, units, formulas and limitations.')
    files=downloads(d,kind)
    for name,data in files.items():st.download_button('Download '+name,data,file_name=name,mime='application/json' if name.endswith('.json') else 'text/csv' if name.endswith('.csv') else 'text/html',key=prefix+name,on_click='ignore')

def execute(key,fn,config,content,pressed):
    sig=fingerprint(config,content)
    if pressed:
        st.session_state.pop(key,None);st.session_state.pop(key+'_error',None)
        try:
            with st.spinner('Processing validated inputs…'):
                d=fn(config,content)
                # Publish only after the full download bundle is also serializable.
                downloads(d,{'v_result':'vibration','r_result':'rul','s_result':'sound'}[key])
            st.session_state[key]={'signature':sig,'data':d}
            if key=='v_result':st.session_state['v_history']=(st.session_state.get('v_history',[])+[d])[-5:]
        except Exception as e:
            # Clear failed current results, including exports. No substituted synthetic output.
            st.session_state[key+'_error']={'signature':sig,'message':str(e)}
    error=st.session_state.get(key+'_error')
    if error and error['signature']!=sig:
        st.session_state.pop(key+'_error',None);error=None
    if error and error['signature']==sig:st.error('Input/computation error: '+error['message'])
    result=st.session_state.get(key)
    if result and result['signature']!=sig:st.info('Inputs changed. Run again to refresh; previous output is not shown as current.');return None
    return result['data'] if result else None

def vibration_view(d,prefix='v'):
    st.html(bearing(d,prefix));st.subheader(d['predicted_class']);st.caption(d['source'])
    a,b,c=st.columns(3);a.metric('Review',d['review_state']);b.metric('Completed windows',d['n_windows']);c.metric('Window agreement', 'Not assessed' if d['window_agreement'] is None else f"{d['window_agreement']:.1%}")
    st.write(d['action']);st.caption('Analysis: '+d['analysis_status']+' · classification: '+d['classification_status']+' · agreement is not failure probability.')
    p=d['plots'];line([('Waveform',p['time'],p['signal'],False)],'Seconds',d['units'],key=prefix+'_wave');line([('FFT amplitude',p['frequency'],p['amplitude'],False)],'Frequency Hz','Amplitude',key=prefix+'_fft')
    st.dataframe(pd.DataFrame(d['features']),width='stretch',hide_index=True)
    with st.expander('Worked formulas and substitutions (all windows)'):st.json(d['calculations'])
    if d['markers']:st.write('Explanatory bearing-frequency markers (Hz)');st.json(d['markers'])
    with st.expander('Provenance, complete JSON and limitations'):
        for s in d['limitations']:st.write('• '+s)
        st.json(d)
    export_buttons(d,'vibration',prefix)

def vibration_page():
    # Show KPI evidence only when it matches the current committed inputs.
    left,right=st.columns([1,1.65],gap='large')
    with left,st.container(border=True):
        st.subheader('Signal acquisition');st.caption('01 · SOURCE & PARAMETERS')
        labels={'sample':'CWRU benchmark example','upload':'Measured CSV upload','manual':'Paste measured samples','synthetic':'Synthetic illustration','builder':'Numeric synthetic builder'}
        source=st.selectbox('Input source',list(labels),format_func=labels.get,key='v_source');cfg={'source':source};content=None
        if source in ('sample','synthetic'):cfg['sample']=st.selectbox('Scenario',list(SCENARIOS),format_func=SCENARIOS.get,key='v_sample')
        if source in ('upload','manual'):
            cfg['fs']=st.number_input('True sample rate (Hz)',value=48000.,key='v_fs');cfg['rpm']=st.text_input('Known RPM (blank if unknown)',key='v_rpm')
            cfg['mode']=st.selectbox('Analysis mode',['signal','classification'],key='v_mode');cfg['compatible']=st.checkbox('I declare compatible drive-end acceleration in g',key='v_compatible')
            if source=='upload':
                upload=st.file_uploader('Vibration CSV',type=['csv'],key='v_file');content=upload.getvalue() if upload else None
                if content:
                    try:
                        df=read_csv(content);st.caption(f'{len(df)} rows · choose the signal explicitly; no rows dropped.');st.dataframe(df.head(8),hide_index=True)
                        cfg['column']=st.selectbox('Signal column',list(df.columns),key='v_column')
                    except Exception as e:st.error('CSV preview: '+str(e))
            else:
                if st.button('Load measured Normal example into editor'):
                    st.session_state['v_manual']=' '.join(map(str,pd.read_csv(ROOT/'data/sample_data/normal.csv').acceleration.tolist()))
                cfg['manual_samples']=st.text_area('Measured samples (numbers only)',height=150,key='v_manual')
        if source=='builder':
            st.caption('Actual generated waveform; classification always off. Values are illustrative.')
            for key,label,value in [('builder_fs','Builder sample rate Hz',12000.),('builder_n','Sample count',8192),('builder_rpm','Builder RPM',1800.),('builder_amplitude','Sine amplitude',.08),('builder_noise','Noise sigma',.04),('builder_impact_amp','Impact amplitude',.6),('builder_rate','Impact rate Hz',107.),('builder_carrier','Carrier Hz',2800.),('builder_decay','Decay ms',1.),('builder_seed','Random seed',42)]:cfg[key]=st.number_input(label,value=value,key='v_'+key)
        if source in ('sample','upload','manual','builder'):
            with st.expander('Optional actual bearing geometry'):
                cfg['custom_geometry']=st.checkbox('Use supplied geometry for markers only',key='v_geometry')
                if cfg['custom_geometry']:
                    for key,label,value in [('geometry_z','Rolling element count',9),('geometry_d','Ball diameter',7.94),('geometry_D','Pitch diameter (same unit)',39.04),('geometry_theta','Contact angle degrees',0.)]:cfg[key]=st.number_input(label,value=value,key='v_'+key)
        pressed=st.button('Run vibration analysis',type='primary',width='stretch')
        if st.button('Clear current vibration result'):st.session_state.pop('v_result',None);st.session_state.pop('v_result_error',None)
    with right:
        d=execute('v_result',vibration,cfg,content,pressed)
        st.html(kpis(d))
        if d:vibration_view(d)
        else:st.html(bearing(None,'empty'))
        if not d and not st.session_state.get('v_result_error'):st.info('Choose actual input or a labelled example, then Run. Synthetic signals are not classified as real faults.')
    history=st.session_state.get('v_history',[])
    if history:
        with st.expander('Session vibration history — last 5 successful runs'):
            selected=st.selectbox('Stored run',range(len(history)),format_func=lambda i:f"{i+1}: {history[i]['source']} / {history[i]['predicted_class']}")
            if st.checkbox('Show selected historical result'):
                st.warning('Historical result: source/settings below belong to that saved run, not the current input controls.');vibration_view(history[selected],prefix='history')

def rul_page():
    st.subheader('Life planning & degradation trend');st.caption('No RUL is learned from the fault classifier. Use justified service-life assumptions or a real chronological higher-is-worse indicator history.')
    left,right=st.columns([1,2],gap='large')
    with left,st.container(border=True):
        mode=st.selectbox('Life-planning method',['budget','trend','demo'],key='r_mode');cfg={'rul_mode':mode,'unit':st.selectbox('Operating-age unit',['hours','days','cycles'],key='r_unit')};content=None
        if mode=='budget':
            cfg['age']=st.number_input('Accumulated operating age',value=200.,key='r_age');cfg['nominal']=st.number_input('Nominal total service life',value=1000.,key='r_nominal')
            cfg['life_min']=st.text_input('Optional minimum total life',key='r_min');cfg['life_max']=st.text_input('Optional maximum total life (paired)',key='r_max')
        else:
            cfg['baseline']=st.number_input('Healthy reference indicator',value=.2,key='r_baseline');cfg['limit']=st.number_input('Maintenance/failure indicator limit',value=1.,key='r_limit');cfg['min_r2']=st.number_input('Minimum R² screening gate (not confidence)',value=.5,key='r_gate')
            if mode=='trend':
                upload=st.file_uploader('Degradation CSV: age,indicator',type=['csv'],key='r_file');content=upload.getvalue() if upload else None;cfg['history_text']=st.text_area('Or paste age,indicator CSV',key='r_text')
        cfg['warning']=st.number_input('Warning at remaining life ≤',value=100.,key='r_warn');cfg['critical']=st.number_input('Critical at remaining life ≤',value=20.,key='r_critical')
        st.caption('Project examples, not safety/shutdown thresholds. Replace default assumptions.')
        pressed=st.button('Calculate RUL / allowance',type='primary',width='stretch');st.download_button('Download synthetic history example',(ROOT/'data/sample_data/degradation_demo.csv').read_bytes(),'degradation_demo.csv',on_click='ignore')
    with right:
        d=execute('r_result',life,cfg,content,pressed)
        if not d:
            if not st.session_state.get('r_result_error'):st.info('Enter justified assumptions/history, then calculate to see the result.')
            return
        unit=d['unit'];fmt=lambda x:'Unavailable' if x is None else f'{x:,.4f} {unit}'
        st.subheader('Remaining: '+fmt(d['remaining']));st.caption(d['source']);st.write(d['status']);st.progress(d['consumed_fraction'],text=d['health_label'])
        st.table(pd.DataFrame({'Parameter':['Current operating age','Nominal/projected threshold age','Supplied maximum total life','Remaining lower bound/scenario','Remaining upper bound/scenario'],'Value':[fmt(d[k]) for k in ['current_age','expected_total','maximum_expected_life','remaining_min','remaining_max']]}))
        st.write(d['range_label']);st.warning(d['reliability']);t=d['trend']
        if mode=='budget':line([('Declared allowance',t['age'],t['remaining'],False)],'Operating '+unit,'Remaining '+unit,key='r_budget')
        else:
            line([('Observed',t['age'],t['indicator'],False),('Fit / projection',t['line_age'],t['line_indicator'],True),('Entered limit',t['line_age'],[t['limit']]*len(t['line_age']),True)],'Operating '+unit,'Entered indicator units',key='r_indicator')
            hist=d['history'];line([('Prefix-fit remaining',[p['age'] for p in hist],[p['remaining'] for p in hist],False)],'Operating '+unit,'Remaining '+unit,key='r_prefix_history');st.dataframe(pd.DataFrame(hist),hide_index=True)
        with st.expander('Fit diagnostics, formulas and limitations'):st.json(d)
        export_buttons(d,'rul','r')

def sound_page():
    st.subheader('Sound source & recorded measurement');st.info('Microphone recording is analysed after Stop; this is NOT continuously streaming live telemetry. Audio is uploaded to this server. dBFS is not calibrated SPL/dBA.')
    left,right=st.columns([1,2],gap='large')
    with left,st.container(border=True):
        mode=st.selectbox('Sound source',['demo','wav','recording','log'],format_func={'demo':'Simulated digital audio','wav':'WAV upload','recording':'Microphone recording','log':'External level log'}.get,key='s_mode');cfg={'sound_mode':mode};content=None
        if mode=='demo':cfg['target_dbfs']=st.number_input('Simulated upper RMS dBFS',value=-24.,key='s_target')
        elif mode=='wav':
            upload=st.file_uploader('Uncompressed WAV',type=['wav'],key='s_wav');content=upload.getvalue() if upload else None
        elif mode=='recording':
            recording=st.audio_input('Record microphone — Stop before analysis',sample_rate=16000,key='s_record',help='HTTPS/localhost and microphone permission required. Sent to server; no fake fallback. Maximum analysed recording: 300 seconds.')
            content=recording.getvalue() if recording else None
        else:
            cfg['convention']=st.selectbox('External level convention',['dBFS','User-declared dB SPL (unverified)'],key='s_convention');upload=st.file_uploader('Level log CSV',type=['csv'],key='s_logfile');content=upload.getvalue() if upload else None;cfg['sound_log']=st.text_area('Or paste level_db,duration_sec CSV',key='s_log')
        if mode in ('wav','recording'):cfg['channel']=st.number_input('Zero-based audio channel',value=0,step=1,key='s_channel')
        spl=mode=='log' and cfg.get('convention')!='dBFS';scale='spl' if spl else 'digital'
        for key,label,default in [('low','Display minimum dB',0. if spl else -90.),('high','Display maximum dB',140. if spl else 0.),('warning','Project warning dB',85. if spl else -20.),('critical','Project high-alert dB',100. if spl else -6.)]:cfg[key]=st.number_input(label,value=default,key='s_'+scale+key)
        if mode!='log':
            with st.expander('Optional reference offset — not SPL calibration'):
                cfg['offset']=st.number_input('Reference offset dB (0 = none)',value=0.,key='s_offset');cfg['reference_note']=st.text_input('Reference and measurement conditions (required if offset)',key='s_note')
        st.caption('All thresholds are project examples, NOT safe exposure limits. Meter uses displayed dB, not linear pressure/power.')
        pressed=st.button('Analyse sound',type='primary',width='stretch');st.download_button('Download synthetic sine WAV',(ROOT/'data/sample_data/digital_audio_demo.wav').read_bytes(),'digital_audio_demo.wav',on_click='ignore')
    with right:
        d=execute('s_result',sound,cfg,content,pressed)
        if not d:
            if not st.session_state.get('s_result_error'):st.info('Choose a source; finish recording/uploading before selecting Analyse sound.')
            return
        settings=d['display_settings'];offset=settings['offset'];fmt=lambda x:'Silence / −∞' if x is None else f'{x+offset:.3f}'
        current=None if d['current_db'] is None else d['current_db']+offset
        st.subheader(fmt(d['current_db'])+' '+d['display_convention']);st.caption(d['source']);st.write(d['alert'])
        frac=0. if current is None else float(np.clip((current-settings['low'])/(settings['high']-settings['low']),0,1));st.progress(frac,text=f"Display scale {settings['low']:g} to {settings['high']:g} dB · position {frac:.1%} (clipped; numeric value not clipped)")
        a,b,c=st.columns(3);a.metric('Minimum interval',fmt(d['minimum_db']));b.metric('Maximum interval',fmt(d['maximum_db']));c.metric('Energy average',fmt(d['average_db']))
        st.caption(f"Raw sample peak: {d['sample_peak_db']} dBFS (not true peak) · clipped samples: {d['clipped_samples']} · duration: {d['duration_sec']:.3f} sec")
        h=d['history'];line([('Interval levels',h['time_sec'],[None if x is None else x+offset for x in h['level_db']],False)],'Elapsed seconds',d['display_convention'],(settings['low'],settings['high']),key='s_intervals')
        st.dataframe(pd.DataFrame({'elapsed_sec':h['time_sec'],'duration_sec':h['duration_sec'],'raw_level_db':h['level_db']}),hide_index=True)
        st.warning(d['reliability'])
        with st.expander('Sound formulas, conventions and limitations'):st.json(d)
        export_buttons(d,'sound','s')

def guide_page():
    st.subheader('Measured benchmark & operating guide');st.write('Stored model/weights and narrow same-rig CWRU evaluation are unchanged. Benchmark accuracy is not industrial validation or actual asset-life accuracy.')
    st.json(json.loads((ROOT/'models/evaluation.json').read_text()));st.download_button('Download current two-page user guide',(ROOT/'docs/USER_MANUAL.pdf').read_bytes(),'RaceGuard_Streamlit_User_Guide.pdf',mime='application/pdf',on_click='ignore')
    st.markdown('**Run:** `python -m streamlit run app.py`. Deploy via Streamlit Community Cloud with `streamlit_app.py` as entry point. No Gradio, Flask wrapper or iframe is used. Microphone records completed clips, not a continuous live stream.')
    st.warning('Recordings are transmitted to the server. Do not record sensitive audio on a public app. Browser/device gain and preprocessing are not acoustic calibration. No certified SPL/dBA, exposure compliance, machine safety or survival probability claim.')
    st.markdown((ROOT/'DATA_RIGHTS.md').read_text())

st.sidebar.html(BRAND)
st.sidebar.caption('WORKSPACE')
page=st.sidebar.radio('Workspace',['Vibration','RUL','Sound','Evidence & guide'],key='workspace',label_visibility='collapsed')
model_name=None
try:
    metadata=(ROOT/'models/model.joblib').stat()
    model_name=model_ready((metadata.st_mtime_ns,metadata.st_size))
except Exception as e:st.sidebar.error('Model unavailable: '+str(e))
st.sidebar.html('<div class="rg-note"><strong>● OFFLINE BENCHMARK</strong><br>Evidence before certainty.<br>Built for learning, not safety-critical decisions.<br><br>CWRU · Drive-end vibration<br>Streamlit · RaceGuard edition</div>')
st.html(hero(page,model_name))
st.html(NOTICE)
{'Vibration':vibration_page,'RUL':rul_page,'Sound':sound_page,'Evidence & guide':guide_page}[page]()
st.html(FOOTER)
