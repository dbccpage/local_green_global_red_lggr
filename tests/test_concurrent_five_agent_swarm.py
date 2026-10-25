"""Concurrent scheduling, budget preflight, strong baseline, and tamper tests."""
from copy import deepcopy
from decimal import Decimal
import itertools
import json
from pathlib import Path
import tempfile
import threading
import time
import unittest

from experiments.live_five_agent_swarm.client import Events, MODELS, RunStopped, event_digest
from experiments.live_five_agent_swarm.domain import fixture
from experiments.live_five_agent_swarm.oracle import feasible
from experiments.concurrent_five_agent_swarm.client import BatchClient
from experiments.concurrent_five_agent_swarm.runner import campaign, replay, source_hashes, capacity_diagnostics
from tests.test_live_five_agent_swarm import StubClient


def fake_transport(payload):
    events = Events()
    StubClient(events).complete(payload["model"], payload["messages"])
    raw = events.records[-1]["data"]["response"]
    messages = payload['messages']
    if messages[-1]['role'] == 'tool':
        board = json.loads(messages[-1]['content'])
        if 'jobs' in board:
            worker = messages[0]['content'].split('dispatch agent ')[1].split(',')[0]
            job = next(j for j in board['jobs'] if j['id'] == worker)
            taken = {p['slot'] for w,p in {**board['proposals'], **board['completed']}.items()
                     if w != worker and (w < worker or w in board['completed'])}
            slots = sorted(set(job['allowed_slots']) & set(board['active_slots']) - taken)
            if slots:
                args = {'slot': slots[0], 'epoch': board['epoch'],
                        'total_cents': sum(x['unit_cents']*x['quantity'] for x in job['items'])}
                raw['choices'][0]['message']['tool_calls'][0]['function'] = {'name': 'propose', 'arguments': json.dumps(args)}
    return {"response": raw, "started_ns": 1, "finished_ns": 2}


class ConcurrentSwarmTests(unittest.TestCase):
    def test_real_thread_overlap_and_atomic_wave_budget(self):
        barrier = threading.Barrier(5)
        seen = []
        def transport(payload):
            start = time.monotonic_ns()
            seen.append(threading.get_ident())
            barrier.wait(timeout=5)
            time.sleep(.01)
            return {"response": {"model": payload["model"], "usage": {"cost": .0001},
                    "choices": [{"message": {"role": "assistant", "content": "ok"}}]},
                    "started_ns": start, "finished_ns": time.monotonic_ns()}
        calls = [(m, [{"role": "user", "content": "test"}]) for m in MODELS]
        client = BatchClient(Events(), '.001', transport=transport)
        with self.assertRaises(RunStopped): client.batch(calls)
        self.assertEqual(seen, [])
        self.assertEqual(client.calls, 0)
        client = BatchClient(Events(), '1', transport=transport)
        self.assertEqual(len(client.batch(calls)), 5)
        self.assertEqual(len(set(seen)), 5)
        self.assertEqual(client.max_inflight, 5)
        self.assertEqual(client.spent, Decimal('.0005'))

    def test_failed_wave_settles_other_inflight_calls_and_holds_unknown_cost(self):
        def transport(payload):
            if payload['model'] == MODELS[1]:
                return {'error': 'TimeoutError', 'started_ns': 1, 'finished_ns': 3}
            return {'response': {'model': payload['model'], 'usage': {'cost': '.0001'},
                    'choices': [{'message': {'role': 'assistant'}}]}, 'started_ns': 1, 'finished_ns': 2}
        events = Events()
        client = BatchClient(events, '1', transport=transport)
        with self.assertRaises(RunStopped):
            client.batch([(m, []) for m in MODELS[:2]])
        self.assertEqual(client.calls, 2)
        reserve = Decimal(events.records[1]['data']['reserved_usd'])
        self.assertEqual(client.spent, reserve+Decimal('.0001'))
        self.assertEqual([e['kind'] for e in events.records], ['api_request', 'api_request', 'api_response', 'api_error', 'wave_result'])

    def test_conventional_hall_checker_matches_independent_search(self):
        state = fixture(5200)
        for active in itertools.chain.from_iterable(itertools.combinations(state['slots'], n) for n in range(9)):
            state['active_slots'] = list(active)
            self.assertEqual(capacity_diagnostics(state)['feasible'], feasible(state))

    def test_complete_campaign_replay_rejects_rehashed_prompt_receipt_and_summary_edits(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td)/'events.jsonl'
            events = Events(path)
            config = {'phase': 'development', 'seeds': [5100], 'models': MODELS, 'budget_usd': '1'}
            events.emit('start', {'source_hashes': source_hashes(), 'source_commit': 'test-double', 'config': config})
            client = BatchClient(events, '1', transport=fake_transport)
            result = campaign(client, events, config)
            self.assertEqual(result['invalid_execution_count'], 0)
            self.assertEqual(result['max_inflight_requests'], 5)
            self.assertFalse(result['cases'][0]['baseline_failed'])
            self.assertEqual(replay(path), result)
            def tamper(kind, change):
                records = deepcopy(events.records)
                change(next(r['data'] for r in records if r['kind'] == kind))
                for i, r in enumerate(records):
                    r['previous'] = records[i-1]['sha256'] if i else None
                    r['sha256'] = event_digest({k:v for k,v in r.items() if k != 'sha256'})
                path.write_text('\n'.join(json.dumps(r) for r in records), encoding='utf-8')
                with self.assertRaises(ValueError): replay(path)
            tamper('api_request', lambda d: d['request']['messages'][0].update(content='nonsense'))
            tamper('gate', lambda d: d.update(global_pass=not d['global_pass']))
            tamper('summary', lambda d: d.update(api_attempts=0))
            tamper('api_response', lambda d: d.update(charged_usd='0'))
            path.write_text('\n'.join(json.dumps(r) for r in events.records), encoding='utf-8')
            (Path(td)/'summary.json').write_text(json.dumps({**result, 'invalid_execution_count': 1}), encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'saved summary'): replay(path)


if __name__ == '__main__': unittest.main()
