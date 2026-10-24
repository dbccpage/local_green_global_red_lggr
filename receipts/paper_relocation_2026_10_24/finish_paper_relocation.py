from pathlib import Path
import ast,hashlib,json,shutil

D=Path(r'C:\Users\a343o\source\repos\lggr')
V=Path(__file__).parent
receipt=D/'receipts/paper_relocation_2026_10_24'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
data=json.loads((receipt/'destination_verification.json').read_text())
assert data['all_passed']
for item in data['checks']:
    assert sha(receipt/(item['check']+'.log'))==item['log_sha256']
tree=ast.parse((V/'verify_relocated_papers.py').read_text())
addition=next(ast.literal_eval(node.value) for node in tree.body if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='addition' for t in node.targets))
index=D/'papers/rsi_and_bell_packages.md'
assert not index.exists()
index.write_text(addition.lstrip().replace('## RSI and Bell paper packages','# RSI and Bell paper packages',1),encoding='utf-8')
data['index_path']=str(index)
data['index_sha256']=sha(index)
data['shared_README_change_observed_during_verification']=True
data['shared_README_final_sha256']=sha(D/'papers/README.md')
baseline=json.loads((receipt/'before_move.json').read_text())
assert all(sha(D/n)==h for n,h in baseline['preexisting_destination_edits'].items())
(receipt/'destination_verification.json').write_text(json.dumps(data,indent=2)+'\n')
for name in ['verify_relocated_papers.py','finish_paper_relocation.py','paper_move_plan.json']:
    shutil.copyfile(V/name,receipt/name)
with (receipt/'README.md').open('a',encoding='utf-8') as f:
    f.write('\nThe shared papers/README.md changed during the verification run. Its final contents were left in place; papers/rsi_and_bell_packages.md supplies the migration navigation without overwriting the shared index.\n')
cleanup={
    'worktree':'C:\\Users\\a343o\\.codex\\worktrees\\remove-seven-foc-folders\\the_symbol_game',
    'worktree_archived_with_recoverable_snapshot':True,
    'local_branches_deleted':['codex/remove-seven-foc-folders','codex/add-bell-projection-paper'],
    'remote_branch_deleted_with_lease':{'branch':'codex/add-bell-projection-paper','expected_sha':'33f8b1aaa598c872b498b2b44f6eaf04a9f178a8'},
    'retirement_remote_branch_already_absent':True,
    'merged_pull_requests':[1331,1332],
    'visualization_root':str(V),
    'visualization_cleanup_complete':False,
    'other_worktrees_and_current_branch_preserved':True,
    'verification':{'host_guidance_parity_test':'1 passed','release_hash_check':'passed','source_runtime_dependency_scan':'only retired harness referenced migrated paper paths','git_diff_check':'passed'},
}
(receipt/'cleanup.json').write_text(json.dumps(cleanup,indent=2)+'\n')
print('PASS destination navigation and receipts finalized')
