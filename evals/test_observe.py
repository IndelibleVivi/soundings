"""Per-decision ordering, content roles, coverage and trace-integrity counterexamples."""
import json
from pathlib import Path
import tempfile
import unittest
import observe


class ObservationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.trace = self.root/'trace.jsonl'
        self.annotations = self.root/'annotations.json'
        self.host = self.root/'host.jsonl'
        self.events = [
            {'type':'item.completed','item':{'type':'command_execution','exit_code':0,
             'command':'cat reference.md','aggregated_output':'Only local text is supported.\n'}},
            {'type':'item.completed','item':{'type':'agent_message','text':'Choose the local route.'}},
            {'type':'item.completed','item':{'type':'file_change','status':'completed','changes':[{'path':'app.py'}]}}
        ]
        self.write_trace()

    def write_trace(self):
        self.trace.write_text(''.join(json.dumps(e)+'\n' for e in self.events))

    def delivery(self, **changes):
        return dict({'kind':'content.delivered','stream':'trace','line':1,
            'pointer':'/item/aggregated_output','excerpt':'Only local text','representation':'extracted',
            'role':'source_body','origin':'fixed_corpus','completeness':'excerpt','source_id':'api-v2',
            'note':'Visible qualifier.','relations':[{'decision_id':'route','relevance':'refutes','note':'Excludes remote fallback.'}]}, **changes)

    def commitment(self, **changes):
        return dict({'kind':'commitment','stream':'trace','line':2,'pointer':'/item/text',
                     'excerpt':'Choose the local','decision_id':'route','note':'Explicit design choice.'}, **changes)

    def annotate(self, entries=None, complete=False, host=None):
        value={'schema':observe.SCHEMA,'trace_sha256':observe.digest(self.trace),
            'decisions':[{'decision_id':'route','question':'Which route fits local operation?'}],
            'events':entries if entries is not None else [self.delivery(),self.commitment()],
            'coverage':[{'decision_id':'route','trace_ranges':[[1,3]],
                'delivery_annotations':'complete' if complete else 'partial',
                'host_context':'complete' if complete else 'unknown'}]}
        if host is not None:
            self.host.write_text(''.join(json.dumps(e)+'\n' for e in host))
            value['host_context_sha256']=observe.digest(self.host)
        self.annotations.write_text(json.dumps(value))

    def read(self, host=False):
        return observe.timeline(self.trace,self.annotations,self.host if host else None)

    def status(self, result):
        return result['decisions'][0]['relevant_source_body_before_commitment']

    def test_relevant_source_precedes_specific_commitment(self):
        self.annotate();result=self.read()
        self.assertEqual(self.status(result),'yes')
        self.assertEqual(result['decisions'][0]['external_source_body_before_commitment'],'yes')
        self.assertEqual(result['host_selection'],'unknown')
        self.assertEqual(result['content_application'],'requires-semantic-review')
        self.assertNotIn('delivery_before_commitment',result)

    def test_skill_and_search_summary_do_not_become_source_body(self):
        for role in ['skill_guidance','search_summary','task_input','interpretation']:
            self.annotate([self.delivery(role=role),self.commitment()],complete=True)
            self.assertEqual(self.status(self.read()),'no')

    def test_unclassified_content_remains_unknown(self):
        self.annotate([self.delivery(role='unknown'),self.commitment()],complete=True)
        self.assertEqual(self.status(self.read()),'unknown')

    def test_missing_annotation_is_unknown_until_explicit_full_coverage(self):
        self.annotate([self.commitment()]);self.assertEqual(self.status(self.read()),'unknown')
        self.annotate([self.commitment()],complete=True);self.assertEqual(self.status(self.read()),'no')
        data=json.loads(self.annotations.read_text());data['coverage'][0]['trace_ranges']=[[2,3]]
        self.annotations.write_text(json.dumps(data));self.assertEqual(self.status(self.read()),'unknown')
        data['coverage'][0].update(trace_ranges=[[1,3]],host_context='partial')
        self.annotations.write_text(json.dumps(data));self.assertEqual(self.status(self.read()),'unknown')

    def test_same_call_internal_order_is_unknown(self):
        self.events[0]['item']['aggregated_output']+='Chosen route: local.';self.write_trace()
        self.annotate([self.delivery(),self.commitment(line=1,pointer='/item/aggregated_output',excerpt='Chosen route')],complete=True)
        self.assertEqual(self.status(self.read()),'unknown')

    def test_unrelated_unknown_and_multiple_decisions(self):
        for relevance,expected in [('irrelevant','no'),('unknown','unknown')]:
            self.annotate([self.delivery(relations=[{'decision_id':'route','relevance':relevance,'note':'Applicability assessment.'}]),self.commitment()],complete=True)
            self.assertEqual(self.status(self.read()),expected)
        data=json.loads(self.annotations.read_text());data['decisions'].append({'decision_id':'layout','question':'How to organize writing?'})
        self.annotations.write_text(json.dumps(data))
        self.assertEqual(self.read()['decisions'][1]['relevant_source_body_before_commitment'],'unknown')

    def test_recorded_host_source_and_catalog(self):
        self.annotate([self.delivery(stream='host_context',pointer='/text',origin='supplied'),self.commitment()],
                      host=[{'text':'Only local text','before_trace_line':1}])
        result=self.read(host=True)
        self.assertEqual(self.status(result),'yes')
        self.assertEqual(result['events'][0]['basis'],'recorded-host-context')
        self.assertEqual(result['decisions'][0]['external_source_body_before_commitment'],'unknown')
        entry={'kind':'capability.catalog','stream':'host_context','line':1,'pointer':'/text','excerpt':'lookup','note':'Recorded host disclosure.'}
        self.annotate([entry],host=[{'text':'lookup available','before_trace_line':1}])
        self.assertEqual(self.read(host=True)['events'][0]['kind'],'capability.catalog')

    def test_unpositioned_host_source_does_not_imply_order(self):
        self.annotate([self.delivery(stream='host_context',pointer='/text'),self.commitment()],complete=True,host=[{'text':'Only local text'}])
        self.assertEqual(self.status(self.read(host=True)),'unknown')

    def test_command_path_and_self_report_are_not_delivery(self):
        for entry in [self.delivery(pointer='/item/command',excerpt='reference.md'),self.delivery(line=2,pointer='/item/text',excerpt='Choose')]:
            self.annotate([entry])
            with self.assertRaisesRegex(ValueError,'successful tool output'):self.read()

    def test_failed_command_and_mcp_metadata_are_not_delivery(self):
        self.events[0]['item']['exit_code']=1;self.write_trace();self.annotate()
        with self.assertRaises(ValueError):self.read()
        self.events[0]={'type':'item.completed','item':{'type':'mcp_tool_call','status':'completed','result':{'content':[],'_meta':{'path':'reference.md'}}}}
        self.write_trace();self.annotate([self.delivery(pointer='/item/result/_meta/path',excerpt='reference.md')])
        with self.assertRaises(ValueError):self.read()

    def test_real_mcp_text_and_error_result(self):
        self.events[0]={'type':'item.completed','item':{'type':'mcp_tool_call','status':'completed',
            'result':{'content':[{'type':'text','text':'Only local text'}]}}}
        self.write_trace();entry=self.delivery(pointer='/item/result/content/0/text')
        self.annotate([entry,self.commitment()]);self.assertEqual(self.status(self.read()),'yes')
        self.events[0]['item']['result']['isError']=True;self.write_trace();self.annotate([entry])
        with self.assertRaises(ValueError):self.read()

    def test_trace_and_host_drift(self):
        self.annotate();self.trace.write_text(self.trace.read_text()+'{}\n')
        with self.assertRaisesRegex(ValueError,'binding mismatch'):self.read()
        self.annotate([],host=[{'text':'catalog'}]);self.host.write_text('{"text":"changed"}\n')
        with self.assertRaisesRegex(ValueError,'context binding mismatch'):self.read(host=True)

    def test_false_excerpt_duplicate_invalid_decision_line_and_role(self):
        for entries in [[self.delivery(excerpt='fabricated')],[self.delivery(),self.delivery()],
                        [self.commitment(decision_id='undeclared')],[self.delivery(line=99)],
                        [self.delivery(role='unrecognized')]]:
            self.annotate(entries)
            with self.assertRaises(ValueError):self.read()

    def test_v1_annotations_must_migrate(self):
        self.annotate();data=json.loads(self.annotations.read_text());data['schema']='soundings.observations.v1'
        self.annotations.write_text(json.dumps(data))
        with self.assertRaisesRegex(ValueError,'migrate'):self.read()

    def test_file_change_is_not_commitment(self):
        entry={'kind':'artifact.changed','stream':'trace','line':3,'pointer':'/item/changes/0/path','excerpt':'app.py','note':'Reported change.'}
        self.annotate([self.delivery(),entry]);self.assertEqual(self.status(self.read()),'unknown')
        self.events[2]['item']['status']='failed';self.write_trace();self.annotate([entry])
        with self.assertRaises(ValueError):self.read()

    def test_review_template_is_pending(self):
        path=self.root/'receipt.json';path.write_text(json.dumps({'schema_version':2,'verification_summary':{
            'human_review':{'required':True,'requirements':['Preserve the qualifier.']}}}))
        result=observe.review_template(path)
        self.assertEqual(result['status'],'pending')
        self.assertEqual(result['requirement_outcomes'],{'Preserve the qualifier.':'inconclusive'})


if __name__=='__main__':unittest.main()
