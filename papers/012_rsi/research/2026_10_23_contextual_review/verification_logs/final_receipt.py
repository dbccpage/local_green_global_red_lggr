from pathlib import Path
import hashlib,json,shutil,datetime
r=Path(r'C:\Users\a343o\source\repos\the_symbol_game\omega_engine_atlas\coda_atlas\F004_papers\012_rsi\001_contextual_prediction_and_self_certification')
w=Path(r'C:\Users\a343o\.codex\visualizations\2026\10\21\01a15f49-0b77-7152-8513-136fd3bd1071\contextual_review_20261023')
e=r.parent/'research/2026_10_23_contextual_review'
hashfile=lambda p: hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
labels=['source_tests_verified','source_named_verified','source_full_census','source_execution_replay','repaired_review','pdf_build','archive_build','source_deposit','cold_extract','cold_tests','cold_independent_review','cold_deposit_lean','cold_seal','cold_future_reproduction']
runs={label:json.loads((w/(label+'.json')).read_text()) for label in labels}
assert all(x['exit_code']==0 for x in runs.values())
archive=r/(r.name+'_2026-10-23.zip')
extraction=json.loads((w/'cold_extraction.json').read_text())
seal=json.loads((w/'cold_final_seal.json').read_text())
future=json.loads((w/'cold_reproduction.json').read_text())
assert not seal['changed'] and future['unchanged_envelope']
assert hashfile(archive)==extraction['sha256']==future['sha256'][archive.name]
source=json.loads((r/'docs/source_verification_v1_8_3.json').read_text())
independent=json.loads((w/'cold_independent_results.json').read_text())
assert independent['fuzz']['cases']==1000 and not independent['fuzz']['mismatches']
for rel,digest in source['source_sha256'].items():assert hashfile(r/rel)==digest,rel
logs=e/'verification_logs';logs.mkdir(exist_ok=True)
for p in w.iterdir():
 if p.is_file() and p.suffix in {'.json','.txt','.py','.png'}:shutil.copyfile(p,logs/p.name)
old=e/'historical_release/contextual_prediction_v1_8_2_2026-10-23.zip'
record={'schema':'contextual-prediction.release-verification.v1','edition':'1.8.3','date_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'review_target_commit':source['review_target_commit'],'working_tree_base_commit_observed':source['working_tree_base_commit'],'source_verification':source,'archive':{'path':str(archive),'bytes':archive.stat().st_size,'sha256':hashfile(archive)},'previous_archive':{'path':str(old),'bytes':old.stat().st_size,'sha256':hashfile(old)},'extraction':extraction,'extracted_tests':{'passed':218,'failed':0},'extracted_lean':{'fresh_package_build':True,'initial_lake_cache':False,'dependency_scope':'Pinned offline vendored dependencies, including their supplied compiled artifacts. Not a fresh bootstrap of Mathlib from source.','named_theorems':161,'full_declarations':941,'execution_comparisons':95,'approved_axioms':['propext','Quot.sound','Classical.choice']},'cold_independent_review':independent,'seal':seal,'later_date_reproduction':future,'runs':runs,'scope_limits':['Windows Python 3.12 and Lean 4.35.0; no native Linux run','CRLF and LF no-write regressions, with mocked Lean subprocess for orchestration only','Actual Lean compilation and census replay performed separately in source and extracted package','No new native Rust, live-provider or universal Python-refinement claim','No process-termination or concurrent-edit transaction guarantee'],'failed_attempts_preserved':{'source_tests':'Stale uncertainty source-hash binding after checker edit; refreshed explicitly, then passed','source_tests_sealed':'Test injection accidentally also intercepted backup restoration; fixture corrected','source_tests_release':'Test injection also intercepted manifest promotion; fixture narrowed to the staged ZIP'} }
record['review_packet_sha256']={p.relative_to(e/'supplied_packet').as_posix():hashfile(p) for p in sorted((e/'supplied_packet').rglob('*')) if p.is_file()}
(e/'verification.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8',newline='\n')
body=f'''# Contextual Prediction v1.8.3 — review repair and release verification

All three API and reproducibility findings are repaired. The user-supplied review targets v1.6.0 at `{source['review_target_commit']}`; the same defects were present in the local v1.8.2 release. This v1.8.3 repair is bound by exact source and archive hashes, not represented as a new Git commit or publication. Paper 000 remains unchanged.

| Check | Current result |
| --- | --- |
| Source Python suite | 218 passed, including 48 new API/release regressions |
| Freshly extracted Python suite | 218 passed |
| Supplied independent LP replay, source and extracted package | 1,000 exact checks each, zero SciPy disagreements: 435 optimal, 269 infeasible, 296 unbounded |
| Contextuality fixtures | Five exact source-bound certificates reproduced |
| Actual named Lean audit | 161 theorems, 49 without axioms |
| Actual full Lean audit | 941 declarations across 17 modules |
| Actual Lean/Python execution comparison | 95 complete outputs matched |
| Fresh extracted Lean/deposit verifier | Passed, starting with no package `.lake` cache |
| Original sealed bytes after complete verification | All 305 unchanged, including `FullCensus.lean` and the manifest |
| Full archive rebuild under simulated 2031-04-09 clock | Byte-identical archive and both manifests; pinned publication date 2026-10-23 |
| Documents | 17-page PDF; 50 matched formula occurrences; zero missing glyphs and overfull boxes; pages 1 and 15 visually inspected |
| Mathematical source change | All 17 Lean proof/driver module files byte-identical to v1.8.2 |

Only `propext`, `Quot.sound`, and `Classical.choice` occur in the censuses. These proof results are actual Lean executions, separate from the mocked subprocesses used to test census file-write behavior. The cold package build uses the pinned offline dependency bundle and its supplied compiled artifacts; it does not bootstrap Mathlib from source.

The optimal checker now accepts original integer/Fraction inputs and rejects malformed witnesses without raising. The outer defect checker is defensive as well. Full-census check mode is read-only, with regeneration reserved for `--write`; a final manifest check compares against original expectations even if a manifest were rewritten. The release tool pins names/timestamps to publication metadata, requires `--new-release` for version/date changes, validates staging before promotion, and restores the previous envelope on the tested ordinary promotion exception.

The CRLF/LF tests prohibit file-writing calls on both success and failure paths. This was verified on Windows, not Linux. The production-size later-date rebuild complements the small regression fixture. Replacement rollback is not a crash-atomic or concurrent-edit transaction guarantee.

Archive: `{archive.name}`  
Size: {archive.stat().st_size:,} bytes  
SHA-256: `{hashfile(archive)}`

The prior v1.8.2 archive is preserved under `historical_release/`; the review packet is preserved verbatim under `supplied_packet/`. `verification.json` binds their hashes, current source hashes, invocation commands, timings and log paths. `verification_logs/` retains successful and failed development attempts. One source-suite failure was a stale source binding; two intermediate regression failures came from an overly broad failure-injection fixture. The corrected source and cold suites both pass. The supplied independent script's hardcoded old commit identifier is retained as source material, not used as an identity claim for the current files.

The standalone ZIP includes the review packet, replay scripts, current source verification records, proof reports, fixtures, regressions and vendored dependency closure. This external receipt records the final archive identity and cold verification to avoid an archive-self-hash cycle. Earlier Rust/gateway/live-model records remain historical; no new such execution is claimed.
'''
(e/'verification.md').write_text(body,encoding='utf-8',newline='\n')
print(json.dumps({'receipt':str(e/'verification.md'),'archive_sha256':record['archive']['sha256'],'all_checks_passed':True},indent=2))
