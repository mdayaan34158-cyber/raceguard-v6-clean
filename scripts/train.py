"""Fixed protocol: select on 2 HP, evaluate once on untouched 3 HP. No tuning on test."""
from pathlib import Path
import sys,json,platform
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import numpy as np,pandas as pd,joblib,sklearn
from scipy.io import loadmat
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.dummy import DummyClassifier
from sklearn.metrics import accuracy_score,f1_score,classification_report,confusion_matrix
from src.processing import features,FS,WINDOW

def prepare(manifest,split):
    tables=[];labels=[];ids=[]
    for r in manifest:
        if r['split']!=split:continue
        x=loadmat(ROOT/'data/raw'/f'{r["id"]}.mat')[r['channel']].ravel()[:FS*4]
        table,tail=features(x);tables.append(table);labels.extend([r['label']]*len(table));ids.extend([r['id']]*len(table))
        r['used_samples']=len(x);r['n_windows']=len(table);r['unused_tail']=tail
    return pd.concat(tables,ignore_index=True),np.array(labels),ids

def main():
    manifest=json.loads((ROOT/'data/manifest.json').read_text())
    train,ytr,_=prepare(manifest,'train');val,yv,_=prepare(manifest,'validation')
    candidates={'Dummy':DummyClassifier(strategy='most_frequent'),'Logistic Regression':make_pipeline(StandardScaler(),LogisticRegression(max_iter=2000,C=1,random_state=42)), 'SVM':make_pipeline(StandardScaler(),SVC(C=2,kernel='rbf',probability=False)), 'Random Forest':RandomForestClassifier(n_estimators=120,max_depth=12,class_weight='balanced',random_state=42,n_jobs=2)}
    scores={}
    for name,model in candidates.items():
        model.fit(train,ytr);pred=model.predict(val)
        scores[name]={'accuracy':accuracy_score(yv,pred),'macro_f1':f1_score(yv,pred,average='macro')}
    selected=max((k for k in candidates if k!='Dummy'),key=lambda k:scores[k]['macro_f1'])
    # Refit selected configuration only on development (0–2 HP), no test contact.
    model=candidates[selected];model.fit(pd.concat([train,val],ignore_index=True),np.concatenate([ytr,yv]))
    test,yt,ids=prepare(manifest,'test');pred=model.predict(test)
    evaluation={'protocol':'Train 0/1 HP, select on 2 HP, refit 0/1/2 HP, final test 3 HP. Fixed 4 seconds per recording, 4096-sample nonoverlap windows, DE 48 kHz.','selected_model':selected,'validation':scores,'test_accuracy':accuracy_score(yt,pred),'test_macro_f1':f1_score(yt,pred,average='macro'),'classification_report':classification_report(yt,pred,output_dict=True,zero_division=0),'classes':list(model.classes_),'confusion_matrix':confusion_matrix(yt,pred,labels=model.classes_).tolist(),'counts':{'train':len(train),'validation':len(val),'test':len(test)},'limitations':['Same rig and possibly same physical fault bearings across loads. Not unseen-bearing validation.','One fixed split, one fault diameter (0.007 inch), one outer-race position. No calibrated uncertainty or industrial severity.','Normal baseline files interpreted as 48 kHz based on published review; MAT variables lack explicit fs metadata.'],'versions':{'python':platform.python_version(),'sklearn':sklearn.__version__,'numpy':np.__version__}}
    artifact={'model':model,'fs':FS,'window':WINDOW,'feature_names':list(train.columns),'name':selected,'version':1,'preprocessing':'independent-window-demean; no bandpass; nonoverlap','classes':list(model.classes_)}
    joblib.dump(artifact,ROOT/'models/model.joblib')
    (ROOT/'models/evaluation.json').write_text(json.dumps(evaluation,indent=2))
    (ROOT/'data/manifest.json').write_text(json.dumps(manifest,indent=2))
    pd.DataFrame({'recording_id':ids,'actual':yt,'predicted':pred}).to_csv(ROOT/'models/test_predictions.csv',index=False)
    # Short held-out examples: genuine benchmark data, not synthetic or independent evaluation.
    for r in manifest:
        if r['split']=='test':
            x=loadmat(ROOT/'data/raw'/f'{r["id"]}.mat')[r['channel']].ravel()[:WINDOW*8]
            slug=r['label'].lower().replace(' ','_')
            pd.DataFrame({'acceleration':x}).to_csv(ROOT/'data/sample_data'/f'{slug}.csv',index=False)
    print(json.dumps(evaluation,indent=2))
if __name__=='__main__':main()
