from pathlib import Path
import hashlib,json,shutil,datetime
r=Path.cwd()
w=Path(r'C:\Users\a343o\.codex\visualizations\2026\10\21\01a15f49-0b77-7152-8513-136fd3bd1071\contextual_review_20261023')
dest=r/'docs/review_2026_10_23_checks'
for name in ['source_execution_replay.txt','source_execution_replay.json']:
 shutil.copyfile(w/name,dest/name)
labels=['source_tests_verified','source_named_verified','source_full_census','source_execution_replay','repaired_review','pdf_build']
runs={label:json.loads((w/(label+'.json')).read_text()) for label in labels}
assert all(record['exit_code']==0 for record in runs.values())
paths=['code/contextuality_lp.py','code/tests/test_review_boundaries.py','tools/rebuild_release.py','tools/replay_full_axiom_census.py','tools/replay_lean_axiom_census.py','verify_deposit.py','lean4/source_hashes.json','lean4/FullCensus.lean','lean4/axiom_report.txt','lean4/full_axiom_report.txt','docs/lp_certificates.json','docs/simplex_execution_cases.json','docs/render_receipt.json']
record={'schema':'contextual-prediction.source-verification.v1','edition':'1.8.3','date':'2026-10-23','working_tree_base_commit':'bf6b87751e254c7aeac5ebf1b26f51bdcabaaa67','review_target_commit':'e15a9d4ac6298524ce370cae679314aa0fef7585','scope':'Current source package on Windows; extracted archive verification is recorded separately outside the archive. No new Rust or live provider trial.','tests':{'passed':218,'failed':0,'new_regressions':48},'lean':{'named_theorems':161,'named_without_axioms':49,'full_declarations':941,'modules':17,'actual_build_and_replay':True,'unchanged_proof_module_bytes':17,'approved_axioms':['propext','Quot.sound','Classical.choice']},'execution_comparisons':95,'contextuality_fixtures':5,'independent_lp_cases':1000,'lp_outcomes':{'optimal':435,'infeasible':269,'unbounded':296},'lp_mismatches':0,'source_sha256':{p:hashlib.sha256((r/p).read_bytes()).hexdigest() for p in paths},'runs':runs,'pdf':{'pages':17,'visually_inspected':[1,15],'formula_occurrences':50,'missing_glyphs':0,'overfull_hboxes':0},'evidence_ceiling':'Finite regression checks and actual scoped Lean executions; no universal Python refinement or crash-atomic multi-file promotion theorem.'}
(r/'docs/source_verification_v1_8_3.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8',newline='\n')
print('Recorded source verification and logs')
