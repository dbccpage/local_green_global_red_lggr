from pathlib import Path
import argparse,hashlib,json,os,re,zipfile
ROOT=Path(__file__).resolve().parents[1]
EXCLUDE={'.git','.lake','__pycache__','.pytest_cache','dist','build'}
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def payload():
 out=[]
 for p in ROOT.rglob('*'):
  rel=p.relative_to(ROOT)
  if any(x in EXCLUDE for x in rel.parts) or p.name in {'MANIFEST.sha256','SHA256SUMS'}:continue
  if p.is_symlink():raise ValueError('symlink in package')
  if p.is_file():out.append(rel.as_posix())
 return sorted(out)
def atomic(p,data):
 q=p.with_name(p.name+'.writing');q.write_bytes(data);os.replace(q,p)
def archive_path():return ROOT/'dist'/'bell_positive_extensions_v0.13.0.zip'

def verify_claim_map(mapping=None):
 mapping = mapping if mapping is not None else json.loads((ROOT/'docs/claim_code_map.yaml').read_text())
 manuscript=(ROOT/(ROOT.name+'.md')).read_text(encoding='utf-8')
 expected=re.findall(r'^\*\*((?:Theorem|Proposition|Lemma|Corollary) \d+[a-z]?) \(',manuscript,re.M)
 actual=[c['id'] for c in mapping['claims']]
 if sorted(actual)!=sorted(expected):raise ValueError('claim map inventory mismatch')
 census=json.loads((ROOT/'axiom_census.json').read_text())['declarations']
 for claim in mapping['claims']:
  if not claim['coverage']:raise ValueError('claim map missing coverage')
  for name in claim['declarations']:
   if name not in census:raise ValueError('claim map unknown theorem '+name)
  for name in claim['checks']:
   path=(ROOT/name).resolve()
   if not path.is_relative_to(ROOT.resolve()) or not path.is_file():raise ValueError('claim map missing check '+name)
def build():
 names=payload();manifest=''.join(sha(ROOT/n)+'  '+n+'\n' for n in names)
 atomic(ROOT/'MANIFEST.sha256',manifest.encode())
 sums=manifest+sha(ROOT/'MANIFEST.sha256')+'  MANIFEST.sha256\n';atomic(ROOT/'SHA256SUMS',sums.encode())
 arc=archive_path();arc.parent.mkdir(exist_ok=True);tmp=arc.with_suffix('.writing')
 with zipfile.ZipFile(tmp,'w',compression=zipfile.ZIP_STORED) as z:
  for n in sorted(names+['MANIFEST.sha256','SHA256SUMS']):
   i=zipfile.ZipInfo(ROOT.name+'/'+n,(2026,10,24,0,0,0));i.create_system=3;i.external_attr=0o100644<<16;z.writestr(i,(ROOT/n).read_bytes())
 os.replace(tmp,arc);atomic(arc.with_suffix('.zip.sha256'),(sha(arc)+'  '+arc.name+'\n').encode())
 print('Built',arc.name,sha(arc))
def verify(archive=True):
 verify_claim_map()
 names=payload();expected=''.join(sha(ROOT/n)+'  '+n+'\n' for n in names)
 if (ROOT/'MANIFEST.sha256').read_bytes()!=expected.encode():raise ValueError('payload inventory or digest mismatch')
 sums=expected+sha(ROOT/'MANIFEST.sha256')+'  MANIFEST.sha256\n'
 if (ROOT/'SHA256SUMS').read_bytes()!=sums.encode():raise ValueError('outer manifest mismatch')
 receipt=json.loads((ROOT/'docs/pdf_build_receipt.json').read_text())
 for name,digest in receipt['bindings'].items():
  if sha(ROOT/name)!=digest:raise ValueError('stale PDF source binding '+name)
 source=json.loads((ROOT/'docs/source_custody.json').read_text())
 if sha(ROOT/source['preserved_copy'])!=source['input_sha256']:raise ValueError('original source changed')
 for item in source.get('review_inputs',[]):
  if sha(ROOT/item['preserved_copy'])!=item['sha256']:raise ValueError('review input changed')
 if archive and archive_path().is_file():
  arc=archive_path()
  if arc.with_suffix('.zip.sha256').read_text()!=sha(arc)+'  '+arc.name+'\n':raise ValueError('archive sidecar mismatch')
  with zipfile.ZipFile(arc) as z:
   all_names=sorted(names+['MANIFEST.sha256','SHA256SUMS'])
   if sorted(z.namelist())!=[ROOT.name+'/'+n for n in all_names]:raise ValueError('archive membership differs')
   for n in all_names:
    if z.read(ROOT.name+'/'+n)!=(ROOT/n).read_bytes():raise ValueError('archive differs '+n)
 print('PASS Bell payload and source custody',len(names),'files')
 return {n:sha(ROOT/n) for n in names}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--build',action='store_true');a=p.parse_args()
 if a.build:build()
 verify()
