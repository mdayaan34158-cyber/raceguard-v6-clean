"""Fetch the explicit official 0.007-inch / four-load manifest, not arbitrary URLs."""
from pathlib import Path
import concurrent.futures, hashlib,json,requests
from scipy.io import loadmat
ROOT=Path(__file__).resolve().parents[1]
(ROOT/'data/raw').mkdir(parents=True,exist_ok=True)
records=[]
for label,ids in {'Normal':[97,98,99,100],'Inner Race Fault':[109,110,111,112],'Rolling Element Fault':[122,123,124,125],'Outer Race Fault':[135,136,137,138]}.items():
 for load,i in enumerate(ids):records.append(dict(id=i,label=label,load_hp=load,fs=48000,url=f'https://engineering.case.edu/sites/default/files/{i}.mat',split='test' if load==3 else 'validation' if load==2 else 'train'))
def get(r):
 p=ROOT/'data/raw'/f'{r["id"]}.mat'
 if not p.exists():
  resp=requests.get(r['url'],timeout=90);resp.raise_for_status();p.write_bytes(resp.content)
 d=loadmat(p);key=next(k for k in d if k.endswith('DE_time'));x=d[key].ravel()
 r.update(channel=key,n_samples=len(x),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),rpm=float(next((d[k].ravel()[0] for k in d if 'RPM' in k),[1797,1772,1750,1730][r['load_hp']])),rpm_source='mat' if any('RPM' in k for k in d) else 'official table approximate')
 print(r['id'],len(x),flush=True);return r
if __name__=='__main__':
 out=list(concurrent.futures.ThreadPoolExecutor(max_workers=4).map(get,records))
 (ROOT/'data/manifest.json').write_text(json.dumps(out,indent=2))
