from pathlib import Path, PurePosixPath
import datetime, hashlib, json, os, shutil, subprocess, sys, time, zipfile

work = Path(__file__).parent
root = Path(r'C:\Users\a343o\source\repos\the_symbol_game\omega_engine_atlas\coda_atlas\F004_papers\012_rsi\000_relational_reasoning_and_rsi_impossibility')
archive, = root.glob('*.zip')
digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
target = work/'clean_v1.2.3'
target.mkdir(exist_ok=False)
with zipfile.ZipFile(archive) as z:
    seen = set()
    for info in z.infolist():
        path = PurePosixPath(info.filename)
        if path.is_absolute() or '..' in path.parts or path.parts[0] != root.name:
            raise ValueError('Unsafe member')
        if info.filename.casefold() in seen:
            raise ValueError('Duplicate member')
        seen.add(info.filename.casefold())
        dest = target.joinpath(*path.parts)
        if not dest.resolve().is_relative_to(target.resolve()):
            raise ValueError('Escaping member')
        dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_bytes(z.read(info))
clean = target/root.name
shutil.copy2(archive, clean/archive.name)
env = dict(os.environ, PYTHONUTF8='1', PYTHONDONTWRITEBYTECODE='1',
           PYTEST_DISABLE_PLUGIN_AUTOLOAD='1',ELAN_HOME=r'C:\Users\a343o\source\repos\.elan')
env['PATH'] = r'C:\Users\a343o\source\repos\.elan\toolchains\leanprover--lean4---v4.35.0\bin;C:\Users\a343o\AppData\Local\Pandoc;C:\Users\a343o\AppData\Local\Programs\MiKTeX\miktex\bin\x64;'+env['PATH']
env.pop('PYTHONPATH',None); env.pop('CARGO_TARGET_DIR',None)
checks = [
    ('clean_tests', ['-m','pytest','code/tests','-q','--basetemp',str(work/'clean_pytest')]),
    ('clean_named', ['tools/replay_lean_axiom_census.py','--replay']),
    ('clean_full', ['tools/replay_full_axiom_census.py','--check']),
    ('clean_deposit', ['verify_deposit.py','--lean']),
    ('clean_zip', ['tools/rebuild_release.py','--check']),
    ('clean_wheel', ['tools/verify_installed_wheel.py','--output',str(work/'clean_wheel_result.json')]),
]
rows=[]
for label,args in checks:
    start=time.time()
    command=[sys.executable,'-X','utf8',*args]
    print('Running '+label,flush=True)
    p=subprocess.run(command,cwd=clean,env=env,capture_output=True,text=True,encoding='utf-8',timeout=600)
    log=work/(label+'.txt');log.write_text(p.stdout+p.stderr,encoding='utf-8',newline='\n')
    result={'label':label,'command':command,'cwd':str(clean),'exit_code':p.returncode,
            'seconds':time.time()-start,'log':log.name,'log_sha256':digest(log)}
    (work/(label+'.json')).write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    rows.append(result)
    print(json.dumps(result),flush=True)
    print((p.stdout+p.stderr)[-1200:],flush=True)
    if p.returncode: break
report={'status':'PASS' if len(rows)==len(checks) and all(r['exit_code']==0 for r in rows) else 'FAIL',
        'archive':archive.name,'archive_sha256':digest(archive),'checks':rows,
        'timestamp_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'lean_cache_present_before_checks':False,'sibling_source_required':False,
        'prerequisites':'Python 3.12, declared Python dependencies, rustc, Lean 4.35.0, rendering inspection tools'}
(work/'clean_replay_result.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
sys.exit(0 if report['status']=='PASS' else 1)
