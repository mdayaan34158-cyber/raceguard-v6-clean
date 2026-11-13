import io,json
from pathlib import Path
import numpy as np,pytest
from scipy.io import wavfile
from scipy.stats import linregress
from src.rul import life_budget,trend_rul
from src.sound import analyse_audio,analyse_wav,level_summary,simulated_audio

def test_budget_exact_scenario():
 d=life_budget({'nominal':1000,'age':200,'life_min':900,'life_max':1200,'warning':100,'critical':20})
 assert d['remaining']==800;assert d['remaining_min']==700;assert d['remaining_max']==1000;assert d['consumed_fraction']==.2
 assert 'NOT a statistical' in d['range_label'];assert d['maximum_expected_life']==1200

def test_budget_overdue():
 d=life_budget({'nominal':100,'age':150});assert d['remaining']==0;assert d['overdue']==50;assert d['consumed_fraction']==1

@pytest.mark.parametrize('data',[{'nominal':0,'age':10},{'nominal':100,'age':-1},{'nominal':100,'age':1,'life_min':90},{'nominal':100,'age':1,'life_min':120,'life_max':150},{'nominal':100,'age':1,'critical':11,'warning':10},{'nominal':'nan','age':1},{'nominal':100,'age':1,'unit':'weeks'}])
def test_invalid_budget(data):
 with pytest.raises(ValueError):life_budget(data)

def test_linear_crossing_exact():
 x=np.arange(0,60,10);y=.2+.01*x;d=trend_rul({'limit':1,'baseline':.2},x,y)
 assert d['expected_total']==pytest.approx(80);assert d['remaining']==pytest.approx(30);assert d['fit']['slope']==pytest.approx(linregress(x,y).slope);assert d['remaining_min']==pytest.approx(30);assert d['remaining_max']==pytest.approx(30)

def test_noisy_ci_brackets_estimate():
 x=np.arange(20)*10;y=.2+.002*x+np.random.default_rng(42).normal(0,.015,20)
 d=trend_rul({'limit':1,'baseline':.2},x,y)
 assert d['remaining_min']<d['remaining']<d['remaining_max'];assert d['fit']['last_two_holdout_rmse']>0
 assert all(r['remaining'] is None or np.isfinite(r['remaining']) for r in d['history'])

def test_negative_and_flat_have_no_rul():
 for y in [np.linspace(.6,.2,10),np.full(10,.2)]:
  d=trend_rul({'limit':1},np.arange(10),y);assert d['remaining'] is None;assert d['remaining_max'] is None

def test_threshold_reached():
 d=trend_rul({'limit':1},np.arange(10),np.linspace(.2,1.1,10));assert d['remaining']==0;assert 'already reached' in d['status']

@pytest.mark.parametrize('x,y',[(list(range(5)),list(range(5))),([0,1,1,3,4,5],[.1]*6),([0,1,2,3,4,5],[.1,.2,np.nan,.3,.4,.5]),([-1,0,1,2,3,4],[.1]*6)])
def test_bad_history(x,y):
 with pytest.raises(ValueError):trend_rul({'limit':1},x,y)

def test_sine_dbfs_exact():
 x=.1*np.sin(2*np.pi*1000*np.arange(16000)/16000);d=analyse_audio(x,16000)
 assert d['average_db']==pytest.approx(-23.0102999566);assert d['sample_peak_db']==pytest.approx(-20);assert len(d['history']['level_db'])==4;assert d['clipped_samples']==0

def test_sound_silence_null_not_zero():
 d=analyse_audio(np.zeros(1600),16000);assert d['average_db'] is None;assert d['minimum_db'] is None;assert d['current_db'] is None
 json.dumps(d,allow_nan=False)

def test_sound_energy_weighting():
 d=level_summary([0,-20],[1,3]);assert d['average_db']==pytest.approx(10*np.log10((1+.03)/4));assert d['average_db']!=pytest.approx(-15)

def test_sound_pcm_and_channels():
 buf=io.BytesIO();a=np.stack([np.zeros(16000),.1*np.sin(2*np.pi*1000*np.arange(16000)/16000)],axis=1);wavfile.write(buf,16000,(a*32767).astype(np.int16))
 assert analyse_wav(buf.getvalue(),0)['average_db'] is None;assert analyse_wav(buf.getvalue(),1)['average_db']==pytest.approx(-23.01,abs=.01)
 with pytest.raises(ValueError):analyse_wav(buf.getvalue(),2)

def test_wav_uint8():
 buf=io.BytesIO();wavfile.write(buf,8000,np.full(800,np.uint8(128)));assert analyse_wav(buf.getvalue())['average_db'] is None

@pytest.mark.parametrize('levels,dt', [([np.inf],[1]),([1],[-1]),([1,2],[1]),([301],[1]),([0],[86401])])
def test_sound_bad_logs(levels,dt):
 with pytest.raises(ValueError):level_summary(levels,dt)

def test_nonfinite_audio_and_bad_wav():
 with pytest.raises(ValueError):analyse_audio(np.full(1600,np.nan),16000)
 with pytest.raises(ValueError):analyse_wav(b'not a wav')

def test_float_overrange_preserved():
 d=analyse_audio(np.full(16000,1.1),16000);assert d['average_db']>0;assert d['clipped_samples']==16000

def test_sound_simulation_label():
 d=simulated_audio(-24);assert d['source'].startswith('SIMULATED');assert d['average_db']<=-24;assert d['duration_sec']==8

def test_weak_slope_range_is_withheld():
 x=np.arange(6.);y=np.array([.1,.4,.15,.5,.3,.65])
 d=trend_rul({'limit':1,'min_r2':0},x,y)
 assert d['remaining'] is not None
 if d['fit']['slope_ci95'][0]<=0:assert d['remaining_max'] is None

def test_large_age_shift_keeps_centered_crossing_interval():
 x=np.arange(20)*10.;y=.2+.002*x+np.random.default_rng(32).normal(0,.01,20)
 d=trend_rul({'limit':1},x,y);shifted=trend_rul({'limit':1},x+1e10,y)
 for field in ['remaining','remaining_min','remaining_max']:assert shifted[field]==pytest.approx(d[field],abs=.00001)
 assert shifted['fit']['rmse']==pytest.approx(d['fit']['rmse'])

def test_tiny_slope_does_not_crash_or_emit_infinite_ci():
 d=trend_rul({'limit':1e-301,'min_r2':0},np.arange(6),np.arange(6)*1e-302)
 assert d['remaining'] is not None;assert d['remaining_max'] is None;json.dumps(d,allow_nan=False)
