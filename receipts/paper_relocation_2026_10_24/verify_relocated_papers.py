from pathlib import Path
import hashlib,json,os,shutil,subprocess,sys

D=Path(r'C:\Users\a343o\source\repos\lggr')
V=Path(__file__).parent
receipt=D/'receipts/paper_relocation_2026_10_24'
assert json.loads((receipt/'move_verification.json').read_text())['result']=='passed'
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
baseline=json.loads((receipt/'before_move.json').read_text())
for name,digest in baseline['preexisting_destination_edits'].items():
    assert sha(D/name)==digest,'Unrelated destination edit changed: '+name
for name in ['audit_paper_move.py','prepare_paper_relocation.py','relocation_source_links.json','relocation_source_links_before.zip']:
    shutil.copyfile(V/name,receipt/name)
readme=D/'papers/README.md'
old=readme.read_bytes()
(receipt/'papers_README_before.md').write_bytes(old)
addition='''

## RSI and Bell paper packages

The author relocated these packages here on 24 October 2026:

- [Recursive improvement, memory and embedded knowledge](012_rsi/README.md): the two agent-focused RSI monographs and *Institutions That Can Know*, with their sources, formal proofs, censuses and standalone archives.
- [Bell: positive extensions and projection residuals](036_bell_positive_extensions_and_projection_residuals/README.md), v0.13.0: complete finite quantum examples with unbounded CF/N_min, constructed Clifford realizations, and explicitly chosen Archimedean continuum shadows.

The packages retain their sealed release bytes. Dated reports can therefore contain historical source-repository paths. Use each package's own verifier from its current directory. Bell's cold extraction replay compiled 656 named theorems in 55 modules with no custom axioms and passed 60 Python tests. On Windows, extract to a short directory so Lean can open every dependency path; the long-path failure and successful short-path replay are both retained in its `dist/` folder.

[Bell release history](bell_research_history/) preserves the earlier audit records. [Relocation evidence](../receipts/paper_relocation_2026_10_24/move_verification.json) binds every inventoried non-cache file before and after the move. The former Woland RSI harness is retained as historical source support in that evidence directory; it is no longer a source-repository integration.
'''
assert '## RSI and Bell paper packages' not in old.decode('utf-8')
readme.write_bytes(old+addition.encode('utf-8'))
(receipt/'README.md').write_text('''# Paper relocation, 24 October 2026

The author requested the RSI and Bell paper estates be moved from the_symbol_game to lggr/papers. `before_move.json` records all non-cache bytes, including release ZIPs; `move_verification.json` verifies exact equality after the native same-volume moves and absence of the source paths. Cache directories moved too but were excluded from the content inventory.

The source navigation and active build references were removed. Dated, revision-bound review receipts remain historical evidence rather than live links. `relocation_source_links_before.zip` preserves the replaced navigation bytes, and `relocation_source_links.json` records their before/after hashes. The retired Woland RSI harness retains its original source for history; use the relocated papers' own verifiers for current validation.

The chat's worktree was archived with a recoverable Git snapshot after verifying its clean and pushed state. Its unique Bell v0.7.1 ZIP was preserved with the current Bell archives. The two merged chat branches were removed locally; the Bell remote branch was deleted with an exact-SHA lease and the retirement remote branch was already absent. Other worktrees and the user's current branch were left intact.

The migration is local filesystem work. It does not commit or publish either repository. Existing edits to lggr/__init__.py and lggr/streaming.py were verified unchanged. The destination verification logs distinguish package binding/certificate checks from the separate complete Bell cold-extraction replay. RSI Lean builds were not repeated for a byte-preserving directory relocation.
''',encoding='utf-8')
checks=[
    ('bell_package',D/'papers/036_bell_positive_extensions_and_projection_residuals',['tools/package.py']),
    ('rsi_000',D/'papers/012_rsi/000_relational_reasoning_and_rsi_impossibility',['verify_deposit.py']),
    ('rsi_001',D/'papers/012_rsi/001_contextual_prediction_and_self_certification',['verify_deposit.py']),
    ('rsi_002',D/'papers/012_rsi/002_institutions_that_can_know',['verify_deposit.py','--archive'])]
env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTEST_DISABLE_PLUGIN_AUTOLOAD='1')
results=[]
for name,cwd,args in checks:
    log=receipt/(name+'.log')
    print('Checking',name,flush=True)
    with log.open('w',encoding='utf-8',newline='\n') as out:
        result=subprocess.run([sys.executable,'-u','-B','-X','utf8',*args],cwd=cwd,env=env,stdout=out,stderr=subprocess.STDOUT,timeout=900)
    results.append({'check':name,'command':['python','-u','-B','-X','utf8',*args],'cwd':str(cwd),'exit_code':result.returncode,'log_sha256':sha(log)})
    print(name,'exit',result.returncode,flush=True)
    if result.returncode:print(log.read_text(encoding='utf-8')[-8000:],flush=True)
(receipt/'destination_verification.json').write_text(json.dumps({'checks':results,'all_passed':all(r['exit_code']==0 for r in results),'preexisting_destination_edits_unchanged':True,'index_sha256':sha(readme)},indent=2)+'\n')
assert all(r['exit_code']==0 for r in results),'Destination verification failed; see logs'
print('PASS all four relocated paper packages',flush=True)
