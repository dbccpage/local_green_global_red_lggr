from pathlib import Path
import datetime,hashlib,json,shutil,subprocess,zipfile
n=Path(__file__).parent
d=Path(r'C:\Users\a343o\source\repos\the_symbol_game\omega_engine_atlas\coda_atlas\F004_papers\002_projection_obstruction\036_bell_positive_extensions_and_projection_residuals')
stem='2026_10_23_bell_followup_review_patch';research=d.parent/'research'
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def main():
 labels=['v071_audit','v071_pdf','v071_package','v071_repro','v071_extract','v071_clean_verify']
 checks={label:json.loads((n/(label+'.json')).read_text()) for label in labels}
 failure=json.loads((n/'v071_clean_verify_disk_failure.json').read_text())
 assert failure['exit_code']==1 and 'No space left on device' in (n/'v071_clean_verify_disk_failure.txt').read_text(encoding='utf-8')
 assert all(c['exit_code']==0 for c in checks.values())
 log=(n/'v071_clean_verify.txt').read_text(encoding='utf-8')
 for marker in ['26 passed','39/39 checks passed.','PASS independent exact checks: 8 repair and 7 negative-mass certificates','PASS fresh Bell census: 256 theorems; no custom axioms','PASS fresh Bell Lean census, exact tests, numerical examples, review certificates, and direct notebook-cell replay']:
  assert marker in log,marker
 c=json.loads((d/'axiom_census.json').read_text());assert c['count']==256 and not c['custom_axioms']
 a=d/'dist/bell_positive_extensions_v0.7.1.zip';digest=sha(a)
 assert a.with_suffix('.zip.sha256').read_text()==digest+'  '+a.name+'\n'
 assert 'PASS byte-identical archive rebuild: '+digest in (n/'v071_repro.txt').read_text()
 with zipfile.ZipFile(d/'dist/bell_positive_extensions_v0.7.0.zip') as z:
  assert z.read(d.name+'/axiom_census.json')==(d/'axiom_census.json').read_bytes()
  for name in z.namelist():
   rel=name.removeprefix(d.name+'/')
   if rel.startswith(('lean4/','code/','jupyter_notebooks/')) or rel in ['tools/replay_lean.py','verify_deposit.py','requirements.txt']:
    assert z.read(name)==(d/rel).read_bytes(),rel
 with zipfile.ZipFile(a) as z:
  assert len(z.namelist())==70
  for name in z.namelist():
   rel=name.removeprefix(d.name+'/');assert z.read(name)==(d/rel).read_bytes(),rel
 m=json.loads((d/'docs/claim_code_map.yaml').read_text());coverage=next(x['coverage'] for x in m['claims'] if x['id']=='Theorem 8')
 assert coverage=='Lean qualitative factorization and exact finite scalar minimax.'
 receipt={'date_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'version':'0.7.1','repository_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=d,text=True).strip(),'scope':'Documentation and packaging patch; no mathematical or computational changes. Reviewer reports concern v0.6 and do not assert an independent review of v0.7 proofs.','correction':{'claim':'Theorem 8','coverage':coverage,'already_present':['Section 9.3 finitely specified matrix qualification','Proposition 9 explicit linear maps']},'package':{'path':str(a),'sha256':digest,'bytes':a.stat().st_size,'payload_files':68,'manifest_control_files':2,'manifest_sha256':sha(d/'MANIFEST.sha256'),'deterministic_second_build':'byte-identical'},'lean':{'theorems':256,'modules':20,'new_theorems':0,'custom_axioms':[],'census_sha256':sha(d/'axiom_census.json'),'all_proofs_and_census_byte_identical_to':'0.7.0','fresh_clean_extraction_build':'passed'},'checks':checks,'initial_clean_attempt':failure,'initial_attempt_resolution':'Disk filled while unpacking dependencies. Preserved the failed log, removed only verified v0.7.0 and failed v0.7.1 scratch extractions plus a duplicate candidate bundle, retained all release archives and receipts, then restarted from a new extraction.','clean_extraction':str(n/'clean_release_v0.7.1'/d.name),'environment':'Python 3.12; Lean 4.35.0; PYTHONPATH and CARGO_TARGET_DIR cleared; fresh bundled dependency extraction; no sibling repository imports','python':{'exact_tests':26,'supplied_checks':39,'repair_certificates':8,'negative_mass_certificates':7,'numerical_LP_solves':14,'notebook':'direct Python-cell replay passed'},'claim_map':{'numbered_claims':12,'rejected_invalid_map_mutations':5},'pdf':json.loads((d/'docs/pdf_build_receipt.json').read_text()),'source_custody':json.loads((d/'docs/source_custody.json').read_text()),'publication':'No commit or publication performed; v0.7.0 archive and receipt retained.'}
 logs=research/(stem+'_logs');logs.mkdir(exist_ok=False)
 for label in labels+['v071_clean_verify_disk_failure']:
  for suffix in ['.txt','.json']:shutil.copyfile(n/(label+suffix),logs/(label+suffix))
 for name in ['audit_v071.py','extract_v071.py','repro_v071.py','run_live_v071.py','report_v071.py']:shutil.copyfile(n/name,logs/name)
 receipt['logs']={p.name:sha(p) for p in sorted(logs.iterdir())}
 p=research/(stem+'.json');assert not p.exists();p.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8',newline='\n')
 text=f'''# Bell follow-up review patch, 23 October 2026

Version **0.7.1** applies the requested Theorem 8 claim-map correction exactly:

> Lean qualitative factorization and exact finite scalar minimax.

The unsupported reference to a general bounded-but-infinite-fiber minimax extension is removed. Qualitative factorization has broader scope; the minimax result requires a finite nonempty history set. The review's matrix-encoding and linear-map edits were already in v0.7.0.

The follow-up review is preserved byte-for-byte, hashed in source custody, and assessed as a review of the v0.6 selection. Its reported 39 exact checks, eight repair certificates and seven negative-mass certificates are distinguished from our local replay. It did not independently rebuild Lean or review the later v0.7 LP/tangent proofs. Historical drafts and erroneous older notes remain labeled research inputs with their corrections recorded.

All **20 Lean modules**, the complete **256-theorem census**, numerical code, certificate checkers, notebook and tests are byte-identical to v0.7.0. The updated archive passed a fresh clean-extraction Lean build and full census comparison, **26 tests**, **39/39 supplied checks**, **8 repair and 7 negative-mass certificate checks**, numerical examples and direct notebook-cell replay. The fresh run verified all 20,672 bundled dependency file hashes and left all 68 payload file hashes unchanged. There are no new theorems or custom axioms.

The rebuilt **21-page PDF** is bound to its Markdown, TeX, compilation log and auxiliary record. It has zero missing glyphs or overfull boxes. Pages 1 and 18 were visually reviewed; sampled pages 5, 6, 10, 20 and 21 are pixel-identical to the previously reviewed v0.7.0 renderings. The manuscript does not generate a table of contents.

The archive's second build was byte-identical. All 12 numbered claims are mapped, and five malformed-map mutations were rejected.

Archive: `../{d.name}/dist/{a.name}`  
Bytes: `{a.stat().st_size}`  
SHA-256: `{digest}`

The initial clean attempt stopped during dependency extraction with a disk-space error. Its failed log is preserved separately. Only obsolete task-owned verification extractions and a duplicate scratch dependency bundle were removed; the successful run restarted from a new extraction. The companion JSON and raw logs bind both attempts, commands, durations, source/archive digests and the clean extraction. The previous release archive and receipt are retained. No Git commit or publication was performed.
'''
 (research/(stem+'.md')).write_text(text,encoding='utf-8',newline='\n')
 print('Recorded patch receipt:',research/(stem+'.md'));print('Archive sha256:',digest)
if __name__=='__main__':main()
