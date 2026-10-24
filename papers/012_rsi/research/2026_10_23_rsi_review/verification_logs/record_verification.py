from pathlib import Path
import datetime, hashlib, importlib.util, json, shutil, subprocess, sys, zipfile

work = Path(__file__).parent
root = Path(r'C:\Users\a343o\source\repos\the_symbol_game\omega_engine_atlas\coda_atlas\F004_papers\012_rsi\000_relational_reasoning_and_rsi_impossibility')
repo = Path(r'C:\Users\a343o\source\repos\the_symbol_game')
dossier = root.parent/'research/2026_10_23_rsi_review'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
replay=json.loads((work/'clean_replay_result.json').read_text())
if replay['status'] != 'PASS': raise RuntimeError('Clean replay did not pass')
archive,=root.glob('*.zip')
if sha(archive)!=replay['archive_sha256']: raise RuntimeError('Release changed after clean verification')
logs=dossier/'verification_logs';logs.mkdir(exist_ok=True)
for pattern in ('*.txt','*.json','*.py'):
    for p in work.glob(pattern): shutil.copy2(p,logs/p.name)
history=dossier/'historical_release';history.mkdir(exist_ok=True)
old,=work.glob('v1.2.2_*.zip')
shutil.copy2(old,history/old.name)
spec=importlib.util.spec_from_file_location('named_census',root/'tools/replay_lean_axiom_census.py')
census=importlib.util.module_from_spec(spec);spec.loader.exec_module(census)
unchanged={}
with zipfile.ZipFile(old) as z:
    for name in ('RelationalRsiNoGo.lean','RsiImpossible.lean'):
        prior=z.read(f'{root.name}/lean4/{name}').decode('utf-8')
        present=(root/'lean4'/name).read_text(encoding='utf-8')
        unchanged[name]=census.strip_comments(prior).split()==census.strip_comments(present).split()
if not all(unchanged.values()): raise RuntimeError('Legacy theorem code changed')
wheel=json.loads((work/'clean_wheel_result.json').read_text())
if any(sha(root/'code'/name)!=digest for name,digest in wheel['wheel_payload_sha256'].items()):
    raise RuntimeError('Installed wheel differs from the final source')
render=json.loads((root/'docs/render_receipt.json').read_text())
source_inputs={p.relative_to(dossier).as_posix():sha(p) for p in (dossier/'supplied_packet').rglob('*') if p.is_file()}
source_inputs['pasted_review.txt']=sha(dossier/'pasted_review.txt')
report={
 'edition':'1.2.3','timestamp_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'review_target_commit':'e15a9d4ac6298524ce370cae679314aa0fef7585',
 'review_pin_scope':'Supplied reviewer provenance; current working-tree payloads independently hashed.',
 'git_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip(),
 'checkout_scope':'Existing dirty checkout; no commit, push or publication performed.',
 'archive':{'path':str(archive),'sha256':sha(archive),'bytes':archive.stat().st_size},
 'previous_archive':{'path':str(history/old.name),'sha256':sha(old)},
 'source_tests':{'passed':221,'note':'Collected executions include the legacy aggregator reexports.'},
 'review_regressions':17,'named_theorems':118,'full_package_declarations':609,'local_lean_modules':8,
 'new_lean_theorems':{'PrefixBounds':5,'ReviewCountermodels':4},
 'axiom_policy':['propext','Quot.sound','Classical.choice'],'custom_axioms':0,
 'legacy_theorem_code_unchanged':unchanged,
 'source_inputs_sha256':source_inputs,'clean_extraction':replay,'installed_wheel':wheel,
 'python_version':sys.version,'rustc_version':subprocess.check_output(['rustc','--version'],text=True).strip(),
 'lean_toolchain':(root/'lean4/lean-toolchain').read_text().strip(),
 'render':{'pages':7,'visually_inspected_pages':[1,4,6],
           'pdf_sha256':sha(root/'relational_reasoning_and_rsi_impossibility_monograph.pdf'),
           'missing_glyphs':render['missing_glyphs'],'overfull_hboxes':render['overfull_hboxes'],
           'compiler_outputs':render['compiler_outputs'],'toc_generated':False},
 'verification_log_sha256':{p.name:sha(p) for p in logs.iterdir() if p.is_file()},
 'limitations':['Native EIS checker covers metadata only, not obstruction replay or authenticated identity.',
                'No universal Python/Rust-to-Lean refinement or completeness of floating-point LP search.',
                'No fresh live-provider, gateway-host or broad quantum Rust runs; prior results remain historical.',
                'Paper 001 remains at 1.8.2 and was not modified or rebuilt by this review repair.',
                'Fresh extraction uses declared installed Python, scientific libraries, rustc, Lean and render-inspection prerequisites.']}
(dossier/'verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
md=f'''# RSI independent-review remediation and release

Version **1.2.3**, verified 2026-10-23. All fourteen supplied findings have a
[current response](../../000_relational_reasoning_and_rsi_impossibility/docs/review_response_2026_10_23.md).
Eight supplied negative controls reproduced their described behavior before
repair. The earlier claim that the shipped cochain solver had been repaired was
not supported by that fresh baseline. The actual deposited implementation now
reconstructs and independently checks exact rational certificates.

| Verification layer | Result |
|---|---|
| Source pytest suite | 221 passed; 17 new review regressions |
| Fresh extracted pytest suite | 221 passed, including fresh Lean compilation |
| Named Lean census, source and extracted | 118 theorems; 90 axiom-free; only standard foundations |
| Full Lean census, source and extracted | 609 declarations across eight local modules |
| New formal results | Five finite-prefix/charge theorems and four reviewer scope controls |
| Installed wheel from extraction | PASS: 15 module/resource imports, exact annulus optimum 9, native metadata parity and full CLI |
| Native policy boundary | Eight adversarial/control identity records agree across Python/Rust |
| Active repair | Independent certificate replay and positive integer price; negative-price refusal also tested under Python -O |
| Canonical PDF rebuild | Seven pages, zero missing glyphs/overfull boxes; pages 1, 4 and 6 visually inspected |
| Manifests and deterministic ZIP | Two-way membership/hash checks and canonical byte equality pass |

The pytest total counts collected executions, including legacy aggregate
reexports. Original theorem code in `RelationalRsiNoGo.lean` and
`RsiImpossible.lean` is unchanged apart from comments; comparison with the
preserved previous archive confirms this. No new custom axioms or unfinished
proofs were introduced. The cold extraction started without a Lean build cache.

[Standalone package](../../000_relational_reasoning_and_rsi_impossibility/{archive.name})
contains the manuscript/PDF, proofs/censuses, tests, native source/resources and
isolated wheel verifier. SHA-256:
`{sha(archive)}` ({archive.stat().st_size:,} bytes).

[Machine-readable receipt](verification.json) binds the archive, PDF, original
review inputs, previous archive, source/wheel payloads and individual command
logs. [Supplied packet](supplied_packet/REVIEW_README.txt) and
[baseline replay](baseline_review.txt) are preserved unchanged. Failed initial
Lean and local-setuptools attempts remain in the verification logs alongside the
successful retries. The complete reviewer provenance is a supplied claim; the
fresh working-tree and release hashes here are independently computed.

The standalone prerequisites are Python 3.12 for this replay, NumPy/SciPy,
pytest, rustc, Lean 4.35.0 and the declared rendering inspection tools. The
isolated wheel test installed NumPy {wheel['smoke']['versions']['numpy']} and
SciPy {wheel['smoke']['versions']['scipy']} into a fresh venv with no system site
packages or checkout PYTHONPATH. Wheel payload bytes match the final source.

Native EIS results now explicitly say **metadata only**. They do not certify an
obstruction predicate, authenticate a host or establish statistical independence.
The asynchronous shift remains an explicitly controlled synthetic defect model.
The current run adds no live-provider or broad native-host experiment and no
universal implementation-refinement proof. Paper 001 remains unchanged at
version 1.8.2. No commit, push, DOI or public deposit was made.
'''
(dossier/'verification.md').write_text(md,encoding='utf-8')
print(json.dumps({'status':'PASS','archive_sha256':sha(archive),'receipt':str(dossier/'verification.md')}))
