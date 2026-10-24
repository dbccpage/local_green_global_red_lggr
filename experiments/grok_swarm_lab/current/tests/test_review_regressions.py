"""Review counterexamples beyond the original frozen fixture mixture."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from lggr_swarm_lab.benchmark import collect_fixed_trace, replay_file, _fixed_fingerprint
from lggr_swarm_lab.common import save
from lggr_swarm_lab.evidence import EvidenceBook, EvidenceError, branch_event
from lggr_swarm_lab.fixtures import generate_cases
from lggr_swarm_lab.host import run_case, replay, replay_fingerprint
from lggr_swarm_lab.oracle import judge, reference_rows
from test_oracle import clean_trace


class AuxiliaryReviewTests(unittest.TestCase):
    def case(self, verdict=True, **scope):
        case = deepcopy(generate_cases('development')[0])
        case['public']['contract']['required_auxiliary_queries'] = [{'query_id':'aux','scope':'endpoint','baseline':0}]
        case['scenario']['negative_evidence'] = [{'query_id':'aux','global_verdict':verdict, **scope}]
        return case

    def test_scoped_negative_blocks_both_controllers_and_judge(self):
        for mode in ('B','C'):
            run = run_case(self.case(False), mode)
            self.assertEqual(run['action'], 'block')
            self.assertFalse(run['judgment']['admissible'])
            self.assertTrue(replay(run)['replayed'])
            self.assertTrue(any(f['code']=='AUXILIARY_NEGATIVE' for d in run['decisions'] for f in d['decision']['findings']))

    def test_required_known_matching_evidence_for_final_admission(self):
        for mode in ('B','C'):
            for variant in ('missing','unknown','wrong_scope','wrong_baseline','nonterminal','known'):
                with self.subTest(mode=mode, variant=variant):
                    case=self.case()
                    if variant=='missing': case['scenario']['negative_evidence']=[]
                    elif variant=='unknown': case['scenario']['negative_evidence'][0]['global_verdict']=None
                    elif variant=='wrong_scope': case['scenario']['negative_evidence'][0]['scope']='every_prefix'
                    elif variant=='wrong_baseline': case['scenario']['negative_evidence'][0]['baseline']=False
                    elif variant=='nonterminal': case['scenario']['negative_evidence'][0]['terminal']=False
                    run=run_case(case,mode)
                    if variant=='known':
                        self.assertEqual(run['action'],'commit')
                        self.assertTrue(run['judgment']['admissible'])
                    else:
                        self.assertNotEqual(run['action'],'commit')
                        self.assertFalse(run['judgment']['admissible'])
                    self.assertTrue(replay(run)['replayed'])

    def test_independent_oracle_checks_required_evidence_even_when_host_commits(self):
        for declaration in ('aux', {'query_id':'aux','scope':'endpoint','baseline':0}):
            for verdict in (True,False,None,'absent'):
                with self.subTest(declaration=declaration,verdict=verdict):
                    case=self.case(verdict)
                    case['public']['contract']['required_auxiliary_queries']=[declaration]
                    trace=clean_trace(case)
                    if verdict=='absent': case['scenario']['negative_evidence']=[]
                    else: trace['negative_evidence']=[{'query_id':'aux','scope':'endpoint','baseline':0,
                        'terminal':True,'verdict':verdict,'source':'sqlite.branch_contract'}]
                    result=judge(case,reference_rows(case),trace)
                    self.assertEqual(result['admissible'],verdict is True)
                    if verdict in (None,'absent'): self.assertEqual(result['admissibility_status'],'unknown')

    def test_matching_positive_does_not_erase_negative(self):
        case=self.case(False)
        case['scenario']['negative_evidence'].append({'query_id':'aux','global_verdict':True})
        for mode in ('B','C'):
            run=run_case(case,mode)
            self.assertEqual(run['action'],'block')
            self.assertFalse(run['judgment']['admissible'])

    def test_same_id_multiple_scopes_are_not_overwritten(self):
        requirements=[{'query_id':'aux','scope':scope,'baseline':0} for scope in ('endpoint','every_prefix')]
        samples=[{'query_id':'aux','scope':scope,'baseline':0,'terminal':True,'verdict':True,'source':'test'} for scope in ('endpoint','every_prefix')]
        merged=EvidenceBook({'required_auxiliary_queries':requirements}).merge([branch_event('one',{'global_samples':samples})])
        self.assertFalse(merged['unsupported'])

    def test_replay_rejects_labels_and_counters_even_if_resealed(self):
        run=run_case(self.case(False),'C')
        for field in ('defect_kind','attempts','probe_attempts','repair_attempts','canary_effects','evidence_bytes'):
            for reseal in (False,True):
                with self.subTest(field=field,reseal=reseal):
                    changed=deepcopy(run)
                    if field=='defect_kind': changed[field]='FORGED'
                    else: changed['metrics'][field]+=100
                    if reseal: changed['replay_fingerprint']=replay_fingerprint(changed)
                    with self.assertRaises(EvidenceError): replay(changed)

    def test_fixed_trace_recomputes_summary_flags(self):
        run=run_case(generate_cases('development')[0],'B')
        with tempfile.TemporaryDirectory() as directory:
            folder=Path(directory)
            save(folder/'run.json',run)
            original=collect_fixed_trace(run,run['development'])
            original.update(source_run_file='run.json',source_run_sha256=hashlib.sha256((folder/'run.json').read_bytes()).hexdigest())
            save(folder/'fixed.json',original)
            self.assertTrue(replay_file(folder/'fixed.json')['replayed'])
            for field in ('decisions_equal','findings_equal','complete'):
                for reseal in (False,True):
                    changed=deepcopy(original)
                    changed[field]=not changed[field]
                    if reseal: changed['comparison_fingerprint']=_fixed_fingerprint(changed)
                    save(folder/'fixed.json',changed)
                    with self.assertRaises(EvidenceError): replay_file(folder/'fixed.json')
