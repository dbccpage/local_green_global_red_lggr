from pathlib import Path
import subprocess,json,hashlib,zipfile,importlib.util,copy
D=Path.cwd();n=Path(r'C:\Users\a343o\.codex\visualizations\2026\10\21\01a15f49-0b77-7152-8513-136fd3bd1071\bell_integral_quantum')
with zipfile.ZipFile(D/'dist/bell_positive_extensions_v0.7.0.zip') as z:
 preserved=[]
 for name in z.namelist():
  rel=name.removeprefix(D.name+'/')
  if rel.startswith('lean4/') or rel.startswith('code/') or rel.startswith('jupyter_notebooks/') or rel in ['axiom_census.json','tools/replay_lean.py','verify_deposit.py','requirements.txt']:
   assert z.read(name)==(D/rel).read_bytes(),rel;preserved.append(rel)
 print('PASS unchanged proof/census/code/replay payload:',len(preserved),'files')
spec=importlib.util.spec_from_file_location('bell_package',D/'tools/package.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
mod.verify_claim_map();m=json.loads((D/'docs/claim_code_map.yaml').read_text())
e=next(c for c in m['claims'] if c['id']=='Theorem 8');assert e['coverage']=='Lean qualitative factorization and exact finite scalar minimax.'
for kind in ['omitted','duplicate','unknown','missing_check','escape_check']:
 bad=copy.deepcopy(m)
 if kind=='omitted':bad['claims'].pop()
 if kind=='duplicate':bad['claims'].append(copy.deepcopy(bad['claims'][0]))
 if kind=='unknown':bad['claims'][0]['declarations']=['Bell.Nonexistent']
 if kind=='missing_check':bad['claims'][0]['checks']=['missing.py']
 if kind=='escape_check':bad['claims'][0]['checks']=['../outside.py']
 try:mod.verify_claim_map(bad)
 except ValueError:pass
 else:raise AssertionError(kind)
print('PASS exact requested coverage, all 12 claims, and five rejected invalid-map mutations')
for page in [1,5,6,10,18,20,21]:
 target=n/f'v071_page_{page}'
 subprocess.run(['pdftoppm','-f',str(page),'-l',str(page),'-scale-to','1400','-singlefile','-png',str(D/(D.name+'.pdf')),str(target)],check=True)
 old=n/f'v07_sealed_page_{page}.png'
 print('PDF page',page,'unchanged' if old.read_bytes()==target.with_suffix('.png').read_bytes() else 'changed')
info=subprocess.check_output(['pdfinfo',str(D/(D.name+'.pdf'))],text=True)
print(info)
