from pathlib import Path
import hashlib,json,os,sys

R=Path(r'C:\Users\a343o\source\repos\the_symbol_game')
D=Path(r'C:\Users\a343o\source\repos\lggr')
V=Path(__file__).parent
P=R/'omega_engine_atlas/coda_atlas/F004_papers'
bell='036_bell_positive_extensions_and_projection_residuals'
receipt=D/'receipts/paper_relocation_2026_10_24'
skip={'.lake','.git','__pycache__','.pytest_cache','target','.ipynb_checkpoints'}

def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def inventory(root):
    files=[root] if root.is_file() else []
    if root.is_dir():
        for base,dirs,names in os.walk(root):
            dirs[:]=sorted(n for n in dirs if n not in skip)
            files.extend(Path(base)/n for n in sorted(names) if not n.endswith('.pyc'))
    result={}
    for i,p in enumerate(files,1):
        name=p.relative_to(root).as_posix() if root.is_dir() else p.name
        assert not p.is_symlink(),str(p)
        result[name]={'bytes':p.stat().st_size,'sha256':sha(p)}
        if i%1000==0:print(root.name,i,'files hashed',flush=True)
    return result

if sys.argv[1]=='capture':
    clean=json.loads((P/'002_projection_obstruction'/bell/'dist/clean_extraction_v0.13.0.json').read_text())
    assert clean['result']=='passed' and clean['lean_theorems']==656
    assert not receipt.exists(),'Receipt directory already exists'
    mappings=[(P/'012_rsi',D/'papers/012_rsi'),(P/'002_projection_obstruction'/bell,D/'papers'/bell)]
    history=P/'002_projection_obstruction/research'
    mappings.extend((p,D/'papers/bell_research_history'/p.name) for p in sorted(history.iterdir()) if p.name.startswith('2026_10_23_bell_'))
    mappings.extend([
        (R/'omega_engine_atlas/coda_atlas/prompts/quantum_relational_rsi',D/'papers/012_rsi/research/source_repo_support/quantum_relational_rsi'),
        (R/'omega_engine_woland/tests/rsi',receipt/'retired_source_support/woland_rsi')])
    for source,dest in mappings:
        assert source.resolve().is_relative_to(R) and source.exists(),source
        assert dest.resolve().is_relative_to(D) and not dest.exists(),dest
    data={'date':'2026-10-24','source_repository':str(R),'destination_repository':str(D),
          'bell_archive_verified':clean,
          'preexisting_destination_edits':{n:sha(D/n) for n in ['lggr/__init__.py','lggr/streaming.py']},
          'cache_directories_excluded_from_hash_inventory':sorted(skip),
          'operation':'same-volume directory moves; all files move, including caches',
          'moves':[]}
    for source,dest in mappings:
        print('Hashing',source,flush=True)
        data['moves'].append({'source':str(source),'destination':str(dest),'files':inventory(source)})
    receipt.mkdir(parents=True)
    (receipt/'before_move.json').write_text(json.dumps(data,indent=2)+'\n')
    (V/'paper_move_plan.json').write_text(json.dumps([{'source':str(s),'destination':str(d)} for s,d in mappings],indent=2)+'\n')
    print('PASS capture',sum(len(m['files']) for m in data['moves']),'files',flush=True)
elif sys.argv[1]=='verify':
    data=json.loads((receipt/'before_move.json').read_text())
    for m in data['moves']:
        assert not Path(m['source']).exists(),'Source remains: '+m['source']
        destination=Path(m['destination'])
        got=inventory(destination)
        # A separately moved support tree can be nested in an earlier directory move.
        # Verify it in its own row rather than counting it as a change to the parent.
        nested=[Path(other['destination']).relative_to(destination).as_posix()+'/'
                for other in data['moves'] if other is not m
                and Path(other['destination']).is_relative_to(destination)]
        got={name:entry for name,entry in got.items()
             if not any(name.startswith(prefix) for prefix in nested)}
        assert got==m['files'],'Moved contents differ: '+m['destination']
        print('PASS unchanged',m['destination'],len(got),'files',flush=True)
    result={'result':'passed','source_paths_absent':True,'all_inventoried_file_bytes_unchanged':True,
            'inventoried_files':sum(len(m['files']) for m in data['moves']),
            'before_move_sha256':sha(receipt/'before_move.json'),'moves':len(data['moves'])}
    (receipt/'move_verification.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
else:raise SystemExit('capture or verify required')
