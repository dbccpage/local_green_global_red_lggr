from pathlib import Path
import copy, hashlib, importlib.util, json, re, zipfile
D=Path(r'C:\Users\a343o\source\repos\the_symbol_game\omega_engine_atlas\coda_atlas\F004_papers\002_projection_obstruction\036_bell_positive_extensions_and_projection_residuals')
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
c=json.loads((D/'axiom_census.json').read_text())
assert c['count']==181 and c['custom_axioms']==[]
with zipfile.ZipFile(D/'dist/bell_positive_extensions_v0.5.0.zip') as z:
 old=json.loads(z.read(D.name+'/axiom_census.json'))
 preserved=[]
 for name in z.namelist():
  relative=name.removeprefix(D.name+'/')
  if relative.startswith('lean4/Bell/') and relative.endswith('.lean'):
   assert z.read(name)==(D/relative).read_bytes(),relative
   preserved.append(relative)
 assert len(preserved)==11
 assert z.read(D.name+'/lean4/vendor/manifest.json')==(D/'lean4/vendor/manifest.json').read_bytes()
 assert all(c['declarations'][name]==axioms for name,axioms in old['declarations'].items())
new=sorted(set(c['declarations'])-set(old['declarations']))
assert len(new)==34 and all(n.startswith('Bell.Separable.') for n in new)
assert sha(D/'lean4/vendor/dependencies.tar.gz')=='4ba752aeb082b6997cf88ea316d7d6603c6b876b6973b01a38b8e363625cc6b3'
for p in (D/'lean4/Bell').glob('*.lean'):
 assert not re.search(r'\b(sorry|admit|native_decide)\b',p.read_text(encoding='utf-8')),p
spec=importlib.util.spec_from_file_location('bell_package',D/'tools/package.py')
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
mod.verify_claim_map()
mapping=json.loads((D/'docs/claim_code_map.yaml').read_text())
for kind in ['omitted','duplicate','unknown_theorem','missing_check','escape_check']:
 bad=copy.deepcopy(mapping)
 if kind=='omitted':bad['claims'].pop()
 if kind=='duplicate':bad['claims'].append(copy.deepcopy(bad['claims'][0]))
 if kind=='unknown_theorem':bad['claims'][0]['declarations']=['Bell.Nonexistent']
 if kind=='missing_check':bad['claims'][0]['checks']=['missing.py']
 if kind=='escape_check':bad['claims'][0]['checks']=['../outside.py']
 try:mod.verify_claim_map(bad)
 except ValueError:pass
 else:raise AssertionError('Invalid map accepted: '+kind)
print('PASS: 11 previous Lean modules and 147 axiom entries unchanged; 34 new theorems')
print('PASS: identical pinned offline dependency archive and manifest')
print('PASS: all 12 numbered claims mapped; five invalid mapping mutations rejected')
