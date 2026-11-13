from pathlib import Path
import json,sys
import numpy as np,pandas as pd,pytest
from streamlit.testing.v1 import AppTest
from src.services import *
ROOT=Path(__file__).resolve().parents[1]

@pytest.mark.parametrize('name,expected',list(SCENARIOS.items()))
def test_benchmark_classes(name,expected):
 d=vibration({'source':'sample','sample':name});assert d['predicted_class']==expected;assert d['classification_status']=='performed';assert d['calculations']['windows'];json.dumps(d,allow_nan=False)

def test_synthetic_builder_and_exports():
 for source in ['synthetic','builder']:
  d=vibration({'source':source});assert d['predicted_class']=='Signal analysis complete';assert d['classification_status']=='not_run_by_design';assert d['remaining_life'] is None
  files=downloads(d,'vibration');assert json.loads(files['vibration.json'])['features'];assert b'peak_to_peak' in files['features.csv']
  if source=='builder':assert len(pd.read_csv(__import__('io').BytesIO(files['waveform.csv'])))==8192

def test_upload_manual_geometry_and_validation():
 raw=(ROOT/'data/sample_data/normal.csv').read_bytes();d=vibration({'source':'upload','column':'acceleration','fs':48000,'mode':'classification','compatible':True},raw);assert d['predicted_class']=='Normal'
 with pytest.raises(ValueError):vibration({'source':'upload','column':'wrong','fs':48000},raw)
 x=pd.read_csv(__import__('io').BytesIO(raw)).acceleration.tolist()
 d=vibration({'source':'manual','manual_samples':' '.join(map(str,x)),'fs':48000,'mode':'signal','rpm':'1800','custom_geometry':True,'geometry_z':9,'geometry_d':7.94,'geometry_D':39.04,'geometry_theta':0});assert d['markers'];assert d['calculations']['geometry']
 with pytest.raises(ValueError):vibration({'source':'manual','fs':48000,'manual_samples':'NaN,1'})
 with pytest.raises(ValueError):vibration({'source':'builder','builder_carrier':8000})

def test_metadata_missing_not_exported_as_nan():
 raw=(ROOT/'data/sample_data/normal.csv').read_bytes();df=pd.read_csv(__import__('io').BytesIO(raw));df['extra']=np.nan
 d=vibration({'source':'upload','column':'acceleration','fs':48000,'mode':'signal'},df.to_csv(index=False).encode());assert d['preview'][0]['extra'] is None;json.loads(downloads(d,'vibration')['vibration.json'])

def test_life_modes_downloads_and_bad_history():
 d=life({'rul_mode':'budget','nominal':1000,'age':200,'life_min':900,'life_max':1200});assert d['remaining']==800;assert d['remaining_min']==700;assert downloads(d,'rul')['rul_history.csv'].startswith(b'age,remaining')
 d=life({'rul_mode':'demo','baseline':.2,'limit':1});assert d['remaining']>0;assert d['remaining_min']<=d['remaining']<=d['remaining_max'];assert 'SYNTHETIC' in d['source']
 d=life({'rul_mode':'trend','baseline':.2,'limit':1},(ROOT/'data/sample_data/degradation_demo.csv').read_bytes());assert 'User-supplied' in d['source']
 with pytest.raises(ValueError):life({'rul_mode':'trend','history_text':'age,indicator\n1,x'})

def test_sound_all_sources_offsets_and_no_live_claim():
 wav=(ROOT/'data/sample_data/digital_audio_demo.wav').read_bytes()
 for mode in ['wav','recording']:
  d=sound({'sound_mode':mode},wav);assert d['average_db']==pytest.approx(-23.01,abs=.01);assert 'not continuous' in ' '.join(d['limitations']);assert downloads(d,'sound')['sound_intervals.csv']
 d=sound({'sound_mode':'log','sound_log':'level_db,duration_sec\n60,1\n70,3','convention':'User-declared dB SPL (unverified)','low':0,'high':140,'warning':85,'critical':100});assert d['average_db']==pytest.approx(68.893017,abs=.0001)
 d=sound({'sound_mode':'demo','offset':100,'reference_note':'Test only'});assert 'not certified SPL' in d['display_convention'];assert d['average_db']<0
 with pytest.raises(ValueError):sound({'sound_mode':'demo','offset':100})
 with pytest.raises(ValueError):sound({'sound_mode':'wav','channel':.5},wav)
 with pytest.raises(ValueError):sound({'sound_mode':'demo','low':10,'high':0})

def button(at,label):return next(x for x in at.button if x.label==label)
def app():return AppTest.from_file(str(ROOT/'streamlit_app.py'),default_timeout=30).run()

def test_app_vibration_success_change_hide_and_error_clear():
 at=app();assert not at.exception;button(at,'Run vibration analysis').click().run();assert not at.exception;assert any(x.value=='Normal' for x in at.subheader)
 at.selectbox(key='v_source').select('synthetic').run();assert any('Inputs changed' in x.value for x in at.info);button(at,'Run vibration analysis').click().run();assert any('Signal analysis complete' in x.value for x in at.subheader)
 at.selectbox(key='v_source').select('builder').run();at.number_input(key='v_builder_carrier').set_value(9000).run();button(at,'Run vibration analysis').click().run();assert not at.exception;assert at.error;assert 'v_result' not in at.session_state

def test_app_rul_and_stale_clear():
 at=app();at.sidebar.radio[0].set_value('RUL').run();button(at,'Calculate RUL / allowance').click().run();assert not at.exception;assert any('800.0000 hours' in x.value for x in at.subheader)
 at.number_input(key='r_nominal').set_value(0.).run();assert any('Inputs changed' in x.value for x in at.info);button(at,'Calculate RUL / allowance').click().run();assert at.error;assert not at.exception;assert 'r_result' not in at.session_state
 at.selectbox(key='r_mode').select('demo').run();button(at,'Calculate RUL / allowance').click().run();assert not at.exception;assert at.session_state['r_result']['data']['remaining']>0

def test_app_sound_guide_and_no_gradio_loaded():
 at=app();at.sidebar.radio[0].set_value('Sound').run();button(at,'Analyse sound').click().run();assert not at.exception;assert at.session_state['s_result']['data']['source'].startswith('SIMULATED')
 at.number_input(key='s_digitallow').set_value(10.).run();button(at,'Analyse sound').click().run();assert not at.exception;assert at.error;assert 's_result' not in at.session_state
 at.sidebar.radio[0].set_value('Evidence & guide').run();assert not at.exception
 assert 'gradio' not in sys.modules and 'flask' not in sys.modules

def test_no_microphone_input_does_not_substitute_simulation():
 with pytest.raises(ValueError):sound({'sound_mode':'recording'})
 at=app();at.sidebar.radio[0].set_value('Sound').run();at.selectbox(key='s_mode').select('recording').run();button(at,'Analyse sound').click().run();assert not at.exception;assert at.error;assert 's_result' not in at.session_state
