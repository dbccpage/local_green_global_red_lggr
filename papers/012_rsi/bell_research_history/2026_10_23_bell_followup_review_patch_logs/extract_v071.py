from pathlib import Path
import zipfile,hashlib
n=Path(__file__).parent
d=Path(r'C:\Users\a343o\source\repos\the_symbol_game\omega_engine_atlas\coda_atlas\F004_papers\002_projection_obstruction\036_bell_positive_extensions_and_projection_residuals')
a=d/'dist/bell_positive_extensions_v0.7.1.zip'
with a.open('rb') as f:digest=hashlib.file_digest(f,'sha256').hexdigest()
assert a.with_suffix('.zip.sha256').read_text()==digest+'  '+a.name+'\n'
w=n/'clean_release_v0.7.1';w.mkdir(exist_ok=False)
with zipfile.ZipFile(a) as z:
 for name in z.namelist():
  target=(w/name).resolve()
  assert target.is_relative_to(w.resolve()) and name.startswith(d.name+'/'),name
 z.extractall(w)
print('PASS clean extraction:',w/d.name)
print('Verified input archive sha256:',digest)
