from pathlib import Path
import hashlib,subprocess,sys
D=Path.cwd();a=D/'dist/bell_positive_extensions_v0.7.1.zip'
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
before=sha(a)
subprocess.run([sys.executable,'tools/package.py','--build'],check=True)
assert sha(a)==before
print('PASS byte-identical archive rebuild:',before)
