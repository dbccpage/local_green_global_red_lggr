from pathlib import Path
import hashlib,json,zipfile
r=Path.cwd()
old=r.parent/'research/2026_10_23_contextual_review/historical_release/contextual_prediction_v1_8_2_2026-10-23.zip'
out=Path(r'C:\Users\a343o\.codex\visualizations\2026\10\21\01a15f49-0b77-7152-8513-136fd3bd1071\contextual_review_20261023')
proofs={}
with zipfile.ZipFile(old) as z:
 for p in sorted((r/'lean4').glob('*.lean')):
  if p.stem in {'Census','FullCensus','lakefile'}:continue
  rel=p.relative_to(r).as_posix();original=z.read(r.name+'/'+rel)
  proofs[rel]={'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'identical_to_v1_8_2':original==p.read_bytes()}
assert all(v['identical_to_v1_8_2'] for v in proofs.values()),proofs
(out/'unchanged_proofs.json').write_text(json.dumps(proofs,indent=2)+'\n')
print('All',len(proofs),'Lean proof/driver module sources byte-identical to previous v1.8.2 archive')
