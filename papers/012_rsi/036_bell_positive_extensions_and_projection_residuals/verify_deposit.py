"""Verify package bytes, exact certificates, finite reproductions, and notebook cells."""
from pathlib import Path
import json,os,subprocess,sys
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'tools'))
from package import verify
from replay_lean import replay
before=verify()
replay()
env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTEST_DISABLE_PLUGIN_AUTOLOAD='1')
test_files=sorted(str(p.relative_to(ROOT)) for p in (ROOT/'code/tests').glob('test_*.py'))
for start in range(0,len(test_files),3):
 subprocess.run([sys.executable,'-m','pytest','-q',*test_files[start:start+3]],cwd=ROOT,env=env,check=True,timeout=300)
for args in [['code/reproduce_examples.py'],['docs/source_inputs/verify_obstruction.py'],['code/review_certificates.py'],['code/contextual_fraction.py'],['tools/generate_comparison_fixture.py'],['code/quantum_evolution.py'],['code/chained_quantum.py'],['code/chain_comparisons.py'],['tools/verify_five_fixture.py'],['code/smoothed_gram.py'],['code/smoothed_quantum.py']]:
 subprocess.run([sys.executable,*args],cwd=ROOT,env=env,check=True,timeout=300)
notebook=json.loads((ROOT/'jupyter_notebooks/001_exact_bell_certificates.ipynb').read_text())
os.chdir(ROOT);scope={}
for cell in notebook['cells']:
 if cell['cell_type']=='code':exec(compile(''.join(cell['source']),'Bell notebook','exec'),scope)
if before!=verify():raise ValueError('payload mutated during verification')
print('PASS fresh Bell Lean census, exact tests, numerical examples, review certificates, and direct notebook-cell replay')
