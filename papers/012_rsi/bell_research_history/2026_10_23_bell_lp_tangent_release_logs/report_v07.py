from pathlib import Path
import datetime,hashlib,json,shutil,subprocess,zipfile
n=Path(__file__).parent
d=Path(r'C:\Users\a343o\source\repos\the_symbol_game\omega_engine_atlas\coda_atlas\F004_papers\002_projection_obstruction\036_bell_positive_extensions_and_projection_residuals')
research=d.parent/'research';stem='2026_10_23_bell_lp_tangent_release'

def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def main():
 labels=['v07_root_lean','v07_audit','v07_pdf_final','v07_package','v07_extract','v07_clean_verify','v07_final_package_check']
 checks={x:json.loads((n/(x+'.json')).read_text()) for x in labels}
 assert all(x['exit_code']==0 for x in checks.values())
 c=json.loads((d/'axiom_census.json').read_text())
 assert c['count']==256 and c['custom_axioms']==[]
 with zipfile.ZipFile(d/'dist/bell_positive_extensions_v0.6.0.zip') as z:
  old=json.loads(z.read(d.name+'/axiom_census.json'))
  for name in z.namelist():
   rel=name.removeprefix(d.name+'/')
   if rel.startswith('lean4/Bell/') and rel.endswith('.lean'):
    assert z.read(name)==(d/rel).read_bytes(),rel
 assert len(old['declarations'])==181
 assert all(c['declarations'][name]==axioms for name,axioms in old['declarations'].items())
 new=sorted(set(c['declarations'])-set(old['declarations']));assert len(new)==75
 v=json.loads((d/'lean4/vendor/manifest.json').read_text())
 candidate=json.loads((n/'vendor_v0.7.0/manifest.json').read_text())
 assert v['files']==candidate['files'] and v['modules']==candidate['modules']
 pdf=json.loads((d/'docs/pdf_build_receipt.json').read_text())
 a=d/'dist/bell_positive_extensions_v0.7.0.zip'
 log=(n/'v07_clean_verify.txt').read_text(encoding='utf-8')
 for marker in ['26 passed','39/39 checks passed.','PASS independent exact checks: 8 repair and 7 negative-mass certificates','PASS fresh Bell census: 256 theorems; no custom axioms','PASS fresh Bell Lean census, exact tests, numerical examples, review certificates, and direct notebook-cell replay']:
  assert marker in log,marker
 assert a.with_suffix('.zip.sha256').read_text()==sha(a)+'  '+a.name+'\n'
 with zipfile.ZipFile(a) as z:
  assert len(z.namelist())==67
 new_modules=['ConvexDistance','LinearProgramming','Polyhedral','PolyhedralProjection','Repair','RepairGeometry','SignedDuality','TangentCone']
 receipt={
  'date_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'version':'0.7.0',
  'repository_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=d,text=True).strip(),
  'working_tree_scope':'Bell package remains in the existing checkout; no commit or publication performed',
  'package':{'path':str(a),'bytes':a.stat().st_size,'sha256':sha(a),'payload_files':65,'manifest_control_files':2,'payload_manifest_sha256':sha(d/'MANIFEST.sha256')},
  'lean':{'theorems':256,'modules':20,'new_modules':new_modules,'new_theorems':new,'previous_modules_preserved_byte_for_byte':12,'previous_axiom_entries_preserved':181,'axioms':sorted({x for xs in c['declarations'].values() for x in xs}),'custom_axioms':[],'census_sha256':sha(d/'axiom_census.json'),'dependency_modules':v['module_count'],'dependency_files':len(v['files']),'dependency_archive_sha256':sha(d/'lean4/vendor/dependencies.tar.gz'),'dependency_closure':'Independently recomputed from all twenty Bell module imports; module list and every file digest equal the retained pinned v0.4 bundle'},
  'checks':checks,'clean_extraction':str(n/'clean_release_v0.7.0'/d.name),
  'dependency_cache_provenance':'Freshly unpacked from the v0.7 standalone dependency archive; no seeded cache; all files revalidated',
  'python':{'exact_tests':26,'supplied_review_checks':39,'separately_checked_certificates':{'repair':8,'negative_mass':7},'LP_solves_numerical':14,'two_qubit_times':5,'Mermin_assignments':64,'notebook':'direct Python-cell replay passed','model_independence':'review_certificates checks returned answers using shared model helpers; bell_certificates independently enumerates the deterministic model'},
  'claim_map':{'numbered_claims':12,'invalid_mapping_mutations_rejected':5},
  'pdf':pdf,'source_custody':json.loads((d/'docs/source_custody.json').read_text()),
  'scope':'Attained weighted Bell repair and normalized signed-negative-mass LP duality; witness and explicit slack-variable optima. Finite elimination proves the actual Bell simplex image polyhedral. Its active cone equals the intrinsic closed radial cone, with exact short-ray repair and a quadratic trajectory remainder estimate. Primal and dual optimizers and finite presentations are constructed. Signed duality assumes an inhabited normalized signed fiber; zero-repair characterization assumes positive context weights; the trajectory remainder is a premise. The positive time window is existential, not an executable duration bound. No Python simplex implementation correctness or general dynamical remainder derivation is asserted.',
  'cleanup':'Removed only the prior verified v0.6 clean-extraction scratch directory for disk space, after checking its retained archive and successful replay. Historical archives, source bundles and receipts remain.'}
 logs=research/(stem+'_logs');logs.mkdir(exist_ok=False)
 for label in labels:
  for suffix in ['.txt','.json']:shutil.copyfile(n/(label+suffix),logs/(label+suffix))
 for name in ['axiom_report.txt','build_report.txt']:shutil.copyfile(d/'lean4'/name,logs/name)
 for name in ['audit_v07.py','extract_v07.py','run_live.py','report_v07.py']:shutil.copyfile(n/name,logs/name)
 receipt['logs']={p.name:sha(p) for p in sorted(logs.iterdir())}
 p=research/(stem+'.json');assert not p.exists();p.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8',newline='\n')
 text=f'''# Bell LP and tangent-cone release, 23 October 2026

Version **0.7.0** adds **75 named Lean theorems** in eight modules, giving an exhaustive census of **256** in twenty modules. The finite LP results construct attained primal and dual optima for weighted Bell repair, prove its support-witness and slack-variable formulations, and construct optimal normalized signed extensions with their negative-mass and vertex-spread duals. Signed duality explicitly requires an inhabited normalized signed fiber.

Finite real-variable elimination and linear-image closure construct an inequality presentation of the actual Bell simplex image. The active-constraint tangent cone is proved equal to the intrinsic closed radial cone. For a local starting behavior, repair along a sufficiently short ray equals time times distance of its velocity to that cone. A trajectory remainder bounded by C t^2 gives the same C t^2 error in repair. The positive time window is an existence theorem; the trajectory remainder is a premise. Positive weights are required for zero repair to characterize the unweighted local behavior. Nonnegative weights are handled through the weighted image.

Fresh source compilation and the complete verifier from a clean ZIP extraction passed under Lean 4.35.0. The exhaustive census uses only `propext`, `Quot.sound`, and `Classical.choice`; it has no custom axioms or admitted proofs. All twelve previous modules and all 181 previous axiom entries are unchanged. Recomputing the dependency closure confirmed the existing pinned bundle already includes every required module: {v['module_count']} modules and {len(v['files'])} individually hashed files. Clean replay unpacked those dependencies itself and matched the complete final census.

The clean package passed **26 tests**, the supplied **39/39 checks**, separate checks of **8 repair and 7 negative-mass certificates**, 14 numerical LP solves, finite matrix/observer/Mermin checks, and direct notebook-cell replay. All **65 payload files** retained their hashes throughout verification. All **12 numbered claims** are mapped to their actual evidence, and five malformed-map mutations were rejected. The source-bound **21-page PDF** has zero overfull boxes; pages 1, 5, 6, 10, 18, 20 and 21 were visually reviewed.

The supplied review is preserved byte-for-byte and assessed in the package. Its encoding, linear-map, signed-table, reference, and evidence-independence corrections are incorporated. The fixed-witness limitation at a saturating product start is included as a written argument, explicitly outside the Lean census. The Python simplex implementation is not certified by the mathematical LP duality proofs.

Archive: `../{d.name}/dist/{a.name}`  
Bytes: `{a.stat().st_size}`  
SHA-256: `{sha(a)}`

The companion JSON and raw logs bind commands, durations, theorem names, source and archive digests, clean extraction, and PDF inspection. Historical archives and receipts are retained. Infinite-dimensional trace-class conversions, full isotropic repair-cost sharpness, Mermin/cohomology results, and general trajectory remainder derivations remain outside the census. No Git commit or publication was performed.
'''
 (research/(stem+'.md')).write_text(text,encoding='utf-8',newline='\n')
 print('Recorded release:',research/(stem+'.md'));print('Archive sha256:',sha(a))
if __name__=='__main__':main()
