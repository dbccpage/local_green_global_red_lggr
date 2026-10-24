from pathlib import Path
import os,json,hashlib,zipfile,shutil
source=Path(r'C:\Users\a343o\source\repos\the_symbol_game\omega_engine_atlas\coda_atlas\F004_papers\012_rsi\001_contextual_prediction_and_self_certification')
w=Path(r'C:\Users\a343o\.codex\visualizations\2026\10\21\01a15f49-0b77-7152-8513-136fd3bd1071\contextual_review_20261023')
parent=w.parent/'cp183'
parent.mkdir(exist_ok=False)
archive=source/(source.name+'_2026-10-23.zip')
with zipfile.ZipFile(archive) as z:
 for i in z.infolist():
  p=Path(i.filename)
  assert p.parts[0]==source.name and '..' not in p.parts and not p.is_absolute()
 z.extractall(parent)
cold=parent/source.name
assert not (cold/'lean4/.lake').exists()
try:os.link(archive,cold/archive.name)
except OSError:shutil.copyfile(archive,cold/archive.name)
entries={}
for line in (cold/'SHA256SUMS').read_text().splitlines():
 if not line or line.startswith('#'):continue
 digest,relative=line.split('  ',1)
 entries[relative]=digest
entries['SHA256SUMS']=hashlib.sha256((cold/'SHA256SUMS').read_bytes()).hexdigest()
(w/'cold_original_seal.json').write_text(json.dumps(entries,indent=2)+'\n')
record={'archive':str(archive),'extraction':str(cold),'no_initial_lake_cache':True,'sealed_files':len(entries),'sha256':hashlib.file_digest(archive.open('rb'),'sha256').hexdigest()}
(w/'cold_extraction.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record,indent=2))
