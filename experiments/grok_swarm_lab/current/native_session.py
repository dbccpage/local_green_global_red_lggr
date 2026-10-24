"""One actual native-proposal session; offline replay needs no model service.

The parent Codex session dispatches at most three native role turns and writes
their raw JSON responses. This local host waits for the two branch responses
after supplying real observed metadata. It never calls a paid provider API.
"""
import json
from pathlib import Path
import time
from lggr_swarm_lab.fixtures import generate_cases
from lggr_swarm_lab.common import save
from lggr_swarm_lab.host import Host, replay
from lggr_swarm_lab.benchmark import build_development

def main():
    root=Path(__file__).resolve().parent
    output=root/'evidence/native'
    planner=json.loads((output/'planner-response.json').read_text(encoding='utf-8'))
    case=next(c for c in generate_cases('dev') if c['family']=='equal_reports' and c['variant']==1)
    planner_input=json.loads((output/'planner-input.json').read_text(encoding='utf-8'))
    host=Host(case,'C',build_development(root),{'plan':planner['plan'],'planner_response':planner,'planner_input':planner_input,
        'dispatch_policy':{'native_role_turn_limit':3,'roles':['planner','orders','refunds'],
                           'token_usage':None,'provider_cost':None,'model_settings':'inherited Codex settings; exact usage not exposed'}})
    def before_workers(active):
        for branch in ('orders','refunds'):
            save(output/f'{branch}-input.json',{'branch':branch,'source':active._branch_source(branch),
                'planner':active.plan,'observed_semantics':active.observations.get('semantics'),'task':case['public']['task']})
        print('READY: native worker input artifacts written',flush=True)
        deadline=time.monotonic()+600
        while time.monotonic()<deadline:
            if all((output/f'{b}-response.json').exists() for b in ('orders','refunds')):
                return {b:json.loads((output/f'{b}-response.json').read_text(encoding='utf-8')) for b in ('orders','refunds')}
            time.sleep(0.5)
        raise RuntimeError('Native role responses did not arrive within the bounded session')
    run=host.run(before_workers=before_workers)
    run['native_runtime_accounting']={'actual_role_turns':3,'native_turn_cap':3,'native_provider_tokens':None,
        'native_provider_cost':None,'local_tool_attempts':run['metrics']['attempts'],
        'separation':'three recorded native model dispatches are separate from local tool-attempt units; no token inference; replay or reexecution of recorded proposals issues no new native call'}
    save(output/'run.json',run)
    save(output/'replay.json',replay(run))
    print(json.dumps({'action':run['action'],'task_correct':run['judgment']['task_correct'],
                      'admissible':run['judgment']['admissible'],'attempts':run['metrics']['attempts']}),flush=True)

if __name__=='__main__':
    main()
