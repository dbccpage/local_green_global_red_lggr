from pathlib import Path
import os,sys,json,time,datetime,subprocess
n=Path(__file__).parent
label=sys.argv[1];args=[sys.executable,'-X','utf8',*sys.argv[2:]]
env=dict(os.environ,PYTHONUTF8='1',PYTHONDONTWRITEBYTECODE='1',PYTEST_DISABLE_PLUGIN_AUTOLOAD='1',ELAN_HOME=r'C:\Users\a343o\source\repos\.elan')
env['PATH']=r'C:\Users\a343o\source\repos\.elan\toolchains\leanprover--lean4---v4.35.0\bin;C:\Users\a343o\AppData\Local\Pandoc;C:\Users\a343o\AppData\Local\Programs\MiKTeX\miktex\bin\x64;'+env['PATH']
start=time.time();print('Running',label,flush=True)
with (n/(label+'.txt')).open('w',encoding='utf-8',newline='\n') as log:
 p=subprocess.Popen(args,cwd=Path.cwd(),env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,encoding='utf-8',bufsize=1)
 for line in p.stdout:
  log.write(line);log.flush();print(line,end='',flush=True)
 rc=p.wait()
receipt={'label':label,'command':args,'cwd':str(Path.cwd()),'timestamp_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'seconds':time.time()-start,'exit_code':rc,'log':label+'.txt'}
(n/(label+'.json')).write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps(receipt),flush=True);sys.exit(rc)
