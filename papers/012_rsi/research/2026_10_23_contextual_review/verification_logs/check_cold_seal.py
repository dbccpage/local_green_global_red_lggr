from pathlib import Path
import hashlib,json
w=Path(r'C:\Users\a343o\.codex\visualizations\2026\10\21\01a15f49-0b77-7152-8513-136fd3bd1071\contextual_review_20261023')
cold=Path(json.loads((w/'cold_extraction.json').read_text())['extraction'])
expected=json.loads((w/'cold_original_seal.json').read_text())
changed=[p for p,h in expected.items() if not (cold/p).is_file() or hashlib.file_digest((cold/p).open('rb'),'sha256').hexdigest()!=h]
result={'sealed_files':len(expected),'changed':changed,'full_census_sha256':hashlib.sha256((cold/'lean4/FullCensus.lean').read_bytes()).hexdigest()}
(w/'cold_final_seal.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result));assert not changed
