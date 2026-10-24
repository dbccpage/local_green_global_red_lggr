from pathlib import Path
import hashlib, json, re, zipfile

ROOT=Path(r'C:\Users\a343o\source\repos\the_symbol_game')
OUT=Path(__file__).parent
changes={}

def edit(relative, transform):
    p=ROOT/relative
    old=p.read_bytes()
    text=old.decode('utf-8')
    new=transform(text).encode('utf-8')
    if new!=old:
        changes[relative]=(old,new)

edit('omega_engine_atlas/coda_atlas/F004_papers/README.md',
     lambda s: ''.join(line for line in s.splitlines(keepends=True) if not line.startswith('| `012` |')))
edit('omega_engine_atlas/coda_atlas/F004_papers/plans/render_omega_architecture.py',
     lambda s: ''.join(line for line in s.splitlines(keepends=True) if '"012_rsi":' not in line))
edit('omega_engine_woland/context.md',lambda s:s.replace(', `012_rsi`',''))
owner='omega_engine_operads/documentation/host_instructions.md'
edit(owner,lambda s:s.replace(', `012_rsi/`',''))
guide=changes[owner][1]
for name in ['GEMINI.md','.agents/AGENTS.md','.claude/AGENTS.md','.codex/AGENTS.md','.grok/AGENTS.md']:
    old=(ROOT/name).read_bytes()
    assert old==(ROOT/owner).read_bytes(),name+' already differs from owner'
    changes[name]=(old,guide)

catalog='omega_engine_product_planning_office/architecture_review/04_paper_source_catalog.json'
def remove_catalog_row(s):
    # Only the current navigation array; dated observations stay historical.
    s,n=re.subn(r'    \{\r?\n      "directory": "012_rsi",\r?\n      "repository_path": "[^"]+",\r?\n      "scope": "[^"]+"\r?\n    \},\r?\n','',s)
    assert n==1,n
    json.loads(s)
    return s
edit(catalog,remove_catalog_row)

inventory='omega_engine_product_planning_office/plans/review_remediation/grade_a_lean_inventory.json'
def retire(s):
    s=s.replace('"active": 81','"active": 80').replace('"retired": 1,','"retired": 2,')
    prefix='{"root":"omega_engine_atlas/coda_atlas/F004_papers/012_rsi/000_relational_reasoning_and_rsi_impossibility/lean4","scope":"active",'
    assert s.count(prefix)==1
    s=s.replace(prefix,prefix.replace('"scope":"active",','"scope":"retired","scope_at_capture":"active","retirement":{"date":"2026-10-24","reason":"Paper estate moved out of this repository at the author\'s request; historical root is not an active build target."},'))
    s=s.replace('by_scope includes the explicitly recorded 2026-10-22 precursor retirement.','by_scope includes the 2026-10-22 precursor retirement and 2026-10-24 RSI relocation.')
    json.loads(s)
    return s
edit(inventory,retire)

arch=ROOT/'omega_engine_product_planning_office/architecture_review'
pattern=r'\[([^\]]+)\]\([^\r\n)]*(?:012_rsi|036_bell_positive_extensions_and_projection_residuals)[^\r\n)]*\)'
for p in sorted(arch.glob('*.md')):
    edit(p.relative_to(ROOT).as_posix(),lambda s:re.sub(pattern,r'\1 (historical source; package relocated)',s))
html='omega_engine_product_planning_office/architecture_review/03_architecture_dash_v1.html'
edit(html,lambda s:re.sub(r'<a href="[^"]*(?:012_rsi|036_bell_positive_extensions_and_projection_residuals)[^"]*">([^<]*)</a>',r'\1 (historical source; package relocated)',s).replace('kept scoped to 012_rsi deposit payload.','now outside this repository in its relocated paper package.'))
yaml='omega_engine_product_planning_office/architecture_review/02_architecture_map_v01.yaml'
def retire_map(s):
    s=s.replace('status: STANDALONE_COMPANION_SCOPED','status: RELOCATED_PAPER_COMPANION')
    s=s.replace('kept scoped to 012_rsi deposit payload.','relocated outside this repository with its paper package on 2026-10-24.')
    s=s.replace('  source_path: omega_engine_atlas/coda_atlas/F004_papers/012_rsi/', '  historical_source_path: omega_engine_atlas/coda_atlas/F004_papers/012_rsi/')
    return s
edit(yaml,retire_map)

snapshot=OUT/'relocation_source_links_before.zip'
assert not snapshot.exists()
with zipfile.ZipFile(snapshot,'w',compression=zipfile.ZIP_DEFLATED) as z:
    for name,(old,new) in changes.items():z.writestr(name,old)
for name,(old,new) in changes.items():
    assert (ROOT/name).read_bytes()==old
    (ROOT/name).write_bytes(new)
receipt={'source_root':str(ROOT),'edits':{name:{'before':hashlib.sha256(old).hexdigest(),'after':hashlib.sha256(new).hexdigest()} for name,(old,new) in changes.items()},'snapshot_sha256':hashlib.sha256(snapshot.read_bytes()).hexdigest(),'historical_review_receipts_preserved':True}
(OUT/'relocation_source_links.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({'updated_files':list(changes),'historical_receipts':'preserved; active links removed'},indent=2))
