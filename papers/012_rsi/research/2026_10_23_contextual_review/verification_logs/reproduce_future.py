from pathlib import Path
import importlib.util,datetime,json,hashlib
root=Path.cwd()
spec=importlib.util.spec_from_file_location('rebuild',root/'tools/rebuild_release.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
archive=module.archive_path(root)
hashfile=lambda p: hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
paths=[archive,root/'MANIFEST.sha256',root/'SHA256SUMS']
before={p.name:hashfile(p) for p in paths}
class LaterDate(datetime.date):
 @classmethod
 def today(cls):return cls(2031,4,9)
module.datetime.date=LaterDate
module.refresh(root)
errors=module.validate(root)
after={p.name:hashfile(p) for p in paths}
assert not errors,errors
assert before==after,(before,after)
record={'simulated_today':'2031-04-09','publication_date':'2026-10-23','unchanged_envelope':True,'sha256':after,'validation_errors':errors}
w=Path(r'C:\Users\a343o\.codex\visualizations\2026\10\21\01a15f49-0b77-7152-8513-136fd3bd1071\contextual_review_20261023')
(w/'cold_reproduction.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record,indent=2))
