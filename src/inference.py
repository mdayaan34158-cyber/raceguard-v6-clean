"""Inference, transparent window votes, and provisional review states (not engineering risk)."""
from pathlib import Path
from collections import Counter
import numpy as np
import joblib
from .processing import features,validate_signal,stats,plots,FS,WINDOW
ROOT=Path(__file__).resolve().parents[1]

def load_model():
    # Only trusted, application-owned artifact. Never deserialize uploaded artifacts.
    a=joblib.load(ROOT/'models/model.joblib')
    if a.get('version')!=1 or a.get('fs')!=FS or a.get('window')!=WINDOW:
        raise ValueError('Unsupported model artifact configuration.')
    return a

def review_state(label,agreement):
    if agreement<0.7:
        return 'Monitor','Windows disagree. Repeat acquisition and request engineering review.'
    if label=='Normal':
        return 'Normal','No known benchmark fault pattern dominates. Continue routine checks; this does not certify safety.'
    return 'Warning','A known benchmark fault pattern dominates. Arrange qualified inspection; do not infer severity or remaining life.'

def analyse(x,fs,mode='classification',source='CSV upload',rpm=None,compatible=False,geometry=None,builder=None):
    x=validate_signal(x,fs)
    if mode not in ('classification','signal'):
        raise ValueError('Unsupported diagnostic mode.')
    result=dict(source=source,mode=mode,n_samples=len(x),fs=fs,stats=stats(x),plots=plots(x,fs),severity=None,remaining_life=None,uncertainty=None,fault_location=None,model_probability=None,units='user supplied / arbitrary' if not compatible else 'g (declared by user or CWRU source)',limitations=['Offline educational decision support; not a machinery safety system.','No severity, calibrated fault probability or automatic shutdown decision. Vibration snapshots alone do not establish RUL; use the separate declared-input Life planning tab.'])
    table,tail=features(x,fs)
    result.update(features=table.to_dict('records'),feature_names=list(table.columns),n_windows=len(table),unused_tail=tail)
    if mode=='classification':
        if fs!=FS:
            raise ValueError('This model requires 48000 Hz. No silent resampling. Use signal-only mode for other rates.')
        if not compatible:
            raise ValueError('Confirm CWRU-compatible drive-end acceleration in g, or use signal-only mode.')
        artifact=load_model();pred=artifact['model'].predict(table[artifact['feature_names']]);counts=Counter(pred)
        winner=sorted(counts,key=lambda k:(-counts[k],k))[0];agreement=float(counts[winner]/len(pred))
        state,action=review_state(winner,agreement)
        result.update(predicted_class=winner,review_state=state,action=action,window_agreement=agreement,votes={k:int(counts[k]) for k in artifact['classes']},window_predictions=pred.tolist(),model_name=artifact['name'],fault_location=winner if state=='Warning' else None)
        result['limitations'].append('Four-class closed-set model: unknown faults and out-of-domain signals may be misclassified confidently. Window agreement is NOT probability or calibrated confidence.')
    else:
        result.update(predicted_class='Signal analysis complete',review_state='Not assessed',action='Waveform, FFT, statistics and per-window calculations completed successfully. Fault classification is intentionally not run in this signal-only/synthetic mode.',window_agreement=None,votes={},model_name='Not used',window_predictions=[])
    result['markers']={}
    if rpm is not None:
        if not np.isfinite(rpm) or rpm<=0:raise ValueError('RPM must be finite and positive when supplied.')
        # Specific verified CWRU drive-end reference, not an arbitrary bearing.
        if compatible:
            f=rpm/60
            result['markers']={'BPFO':3.5848*f,'BPFI':5.4152*f,'FTF':0.39828*f,'2×BSF (CWRU rolling element)':4.7135*f}
    result['model_decision'] = []
    if mode=='classification':
        forest=artifact['model']
        scores=forest.predict_proba(table[artifact['feature_names']])
        leaf_sums=np.sum([tree.predict_proba(table[artifact['feature_names']].to_numpy()) for tree in forest.estimators_],axis=0)
        result['model_decision']=[dict(leaf_sums={c:float(v) for c,v in zip(artifact['classes'],leaf_sums[i])},window=i,scores={c:float(v) for c,v in zip(artifact['classes'],row)},n_trees=len(forest.estimators_),predicted=str(pred[i])) for i,row in enumerate(scores)]
    from .formulas import build_ledger
    result['calculations'],calculated_markers=build_ledger(x,fs,table,result,rpm,compatible,geometry,builder)
    result['markers']=calculated_markers
    if geometry:
        result['limitations'].append('Custom geometry changes explanatory frequency markers only; it does not retrain or adapt the CWRU classifier.')
    result['analysis_status']='complete'
    result['classification_status']='performed' if mode=='classification' else 'not_run_by_design'
    return result
