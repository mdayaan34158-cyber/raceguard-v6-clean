"""Package complete native Streamlit source, including preserved prior-source archive."""
from pathlib import Path
import hashlib,zipfile,json,argparse
ROOT=Path(__file__).resolve().parents[1]
SKIP={'.venv','__pycache__','.pytest_cache','.git','.cache','node_modules','dist','build'}
def files(output=None):return sorted(p for p in ROOT.rglob('*') if p.is_file() and (output is None or p.resolve()!=output.resolve()) and not SKIP.intersection(p.relative_to(ROOT).parts) and p.suffix not in ('.pyc','.pyo') and p.name!='SHA256SUMS.txt' and p.relative_to(ROOT).as_posix()!='.streamlit/secrets.toml')
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,default=ROOT.parent/'RaceGuard_Streamlit_RaceGuard_UI_v6.zip');args=parser.parse_args()
 if args.output.suffix.lower()!='.zip':parser.error('Output filename must end with .zip')
 args.output.parent.mkdir(parents=True,exist_ok=True)
 entries=files(args.output);(ROOT/'SHA256SUMS.txt').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(ROOT).as_posix()+'\n' for p in entries))
 with zipfile.ZipFile(args.output,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
  for p in entries+[ROOT/'SHA256SUMS.txt']:z.write(p,Path(ROOT.name)/p.relative_to(ROOT))
 with zipfile.ZipFile(args.output) as z:assert z.testzip() is None;count=len(z.namelist())
 print(json.dumps({'archive':str(args.output),'files':count,'bytes':args.output.stat().st_size,'sha256':hashlib.sha256(args.output.read_bytes()).hexdigest()},indent=2))
