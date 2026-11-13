"""Expanded regressions for the requested code/interface cross-check."""
import json
import numpy as np,pandas as pd,pytest
from streamlit.testing.v1 import AppTest
from src.services import ROOT,vibration,life,sound,downloads,fingerprint

def button(at,label):return next(x for x in at.button if x.label==label)
def app():return AppTest.from_file(str(ROOT/'streamlit_app.py'),default_timeout=30).run()
def historical(at):return next(x for x in at.checkbox if x.label=='Show selected historical result')

def test_history_current_same_result_no_duplicate_plot_ids():
 at=app();button(at,'Run vibration analysis').click().run();historical(at).set_value(True).run();assert not at.exception
 assert len(at.get('plotly_chart'))==4

def test_nonfinite_unused_metadata_still_exports_valid_json():
 df=pd.read_csv(ROOT/'data/sample_data/normal.csv');df['sensor_note']=[np.inf,-np.inf]+[np.nan]*(len(df)-2)
 d=vibration({'source':'upload','fs':48000,'column':'acceleration','mode':'signal'},df.to_csv(index=False).encode())
 data=json.loads(downloads(d,'vibration')['vibration.json']);assert data['preview'][0]['sensor_note']=='Infinity';assert data['preview'][1]['sensor_note']=='-Infinity';assert data['preview'][2]['sensor_note'] is None

def test_selected_infinite_signal_is_rejected_not_sanitized():
 df=pd.read_csv(ROOT/'data/sample_data/normal.csv');df.loc[0,'acceleration']=np.inf
 with pytest.raises(ValueError):vibration({'source':'upload','fs':48000,'column':'acceleration','mode':'signal'},df.to_csv(index=False).encode())

@pytest.mark.parametrize('mode',['trend','log'])
def test_empty_upload_not_silently_replaced_with_paste(mode):
 if mode=='trend':
  cfg={'rul_mode':'trend','history_text':(ROOT/'data/sample_data/degradation_demo.csv').read_text()};fn=life
 else:cfg={'sound_mode':'log','sound_log':'level_db,duration_sec\n-20,1'};fn=sound
 assert fn(cfg) is not None
 with pytest.raises(ValueError):fn(cfg,b'')

def test_fingerprint_empty_upload_and_no_upload_distinct():
 assert fingerprint({'mode':'trend'},None)!=fingerprint({'mode':'trend'},b'')

def test_none_reference_note_does_not_bypass_documentation():
 with pytest.raises(ValueError):sound({'sound_mode':'demo','offset':100,'reference_note':None})

def test_app_clear_current_preserves_explicit_history():
 at=app();button(at,'Run vibration analysis').click().run();button(at,'Clear current vibration result').click().run()
 assert not at.exception;assert 'v_result' not in at.session_state;assert len(at.session_state['v_history'])==1
 historical(at).set_value(True).run();assert not at.exception;assert len(at.get('plotly_chart'))==2

def test_history_bounded_and_sessions_isolated():
 at=app()
 for _ in range(6):button(at,'Run vibration analysis').click().run()
 assert len(at.session_state['v_history'])==5;historical(at).set_value(True).run();assert not at.exception
 other=app();assert 'v_history' not in other.session_state;assert 'v_result' not in other.session_state

def test_pasted_example_helper_and_custom_geometry():
 at=app();at.selectbox(key='v_source').select('manual').run();button(at,'Load measured Normal example into editor').click().run()
 assert len(at.text_area(key='v_manual').value)>4096
 at.text_input(key='v_rpm').set_value('1800').run();at.checkbox(key='v_geometry').set_value(True).run();button(at,'Run vibration analysis').click().run()
 assert not at.exception;assert at.session_state['v_result']['data']['markers'];assert at.session_state['v_result']['data']['classification_status']=='not_run_by_design'

@pytest.mark.parametrize('unit',['days','cycles'])
def test_rul_units_and_download_consistency(unit):
 at=app();at.sidebar.radio[0].set_value('RUL').run();at.selectbox(key='r_unit').select(unit).run();button(at,'Calculate RUL / allowance').click().run()
 assert not at.exception;d=at.session_state['r_result']['data'];assert d['remaining']==800;assert d['unit']==unit;assert json.loads(downloads(d,'rul')['rul.json'])['unit']==unit

def test_correcting_error_restores_neutral_guidance_before_run():
 at=app();at.selectbox(key='v_source').select('builder').run();at.number_input(key='v_builder_carrier').set_value(9000).run();button(at,'Run vibration analysis').click().run();assert at.error
 at.number_input(key='v_builder_carrier').set_value(2800).run();assert not at.error;assert at.info;assert 'v_result_error' not in at.session_state
 button(at,'Run vibration analysis').click().run();assert not at.exception;assert 'v_result' in at.session_state

def test_export_failure_never_publishes_partial_current_result(monkeypatch):
 import src.services as services
 def broken(*args):return {'nonfinite':float('nan')}
 monkeypatch.setattr(services,'vibration',broken)
 at=app();button(at,'Run vibration analysis').click().run();assert at.error;assert not at.exception;assert 'v_result' not in at.session_state;assert 'v_history' not in at.session_state

def test_sound_offset_and_silence_csv_keep_raw_conventions():
 from scipy.io import wavfile
 import io
 buf=io.BytesIO();wavfile.write(buf,16000,np.zeros(16000,dtype=np.int16))
 d=sound({'sound_mode':'wav'},buf.getvalue());assert d['average_db'] is None;assert 'Silence' in d['alert'];json.loads(downloads(d,'sound')['sound.json'])
 cfg={'sound_mode':'demo','offset':100,'reference_note':'Unverified test only','low':0,'high':140,'warning':85,'critical':100};d=sound(cfg)
 assert d['average_db']<0;assert 'not certified SPL' in d['display_convention'];frame=pd.read_csv(__import__('io').BytesIO(downloads(d,'sound')['sound_intervals.csv']));assert np.allclose(frame.displayed_level_db-frame.raw_level_db,100)
