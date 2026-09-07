"""Offline checks for tool-call evidence, independent of AWS credentials."""
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import Mock, patch

spec = importlib.util.spec_from_file_location(
    'evaluation', Path(__file__).resolve().parents[1] / 'generate-eval-dataset.py')
evaluation = importlib.util.module_from_spec(spec)
spec.loader.exec_module(evaluation)


class TraceTests(unittest.TestCase):
    def run_stream(self, events, trace):
        with patch.object(evaluation, '_event_stream', return_value=iter(events)):
            return evaluation.invoke_harness_once(Mock(), 'harness', 'gateway', 'bug', trace)

    def test_rejected_call_counts_even_when_final_answer_asks_for_details(self):
        events = [
            {'contentBlockStart': {'contentBlockIndex': 0, 'start': {
                'toolUse': {'name': 'bugreports___create_bug_report', 'toolUseId': 'one'}}}},
            {'contentBlockDelta': {'delta': {'toolUse': {'input': '{"description":'}}}},
            {'contentBlockDelta': {'delta': {'toolUse': {'input': '"bug"}'}}}},
            {'messageStop': {'stopReason': 'tool_use'}},
            {'contentBlockStart': {'start': {'toolResult': {'toolUseId': 'one', 'status': 'success'}}}},
            {'contentBlockDelta': {'delta': {'toolResult': [{'text': '{"error":"missing environment"}'}]}}},
            {'messageStop': {'stopReason': 'tool_result'}},
            {'contentBlockDelta': {'delta': {'text': 'What environment are you using?'}}},
            {'messageStop': {'stopReason': 'end_turn'}},
        ]
        trace = {}
        result = self.run_stream(events, trace)
        self.assertEqual(result['final_output_text'], 'What environment are you using?')
        self.assertEqual(trace['events'], events)
        check = evaluation.check_tool_count(trace, 0)
        self.assertEqual(check['observed'], 1)
        self.assertEqual(check['status'], 'fail')

    def test_no_call_passes_and_fabricated_confirmation_fails_required_call(self):
        trace = {}
        self.run_stream([{'contentBlockDelta': {'delta': {'text': 'Ticket created.'}}}], trace)
        self.assertEqual(evaluation.check_tool_count(trace, 0)['status'], 'pass')
        self.assertEqual(evaluation.check_tool_count(trace, 1)['status'], 'fail')

    def test_partial_trace_is_inconclusive_on_stream_failure(self):
        event = {'messageStart': {'role': 'assistant'}}
        def broken():
            yield event
            raise RuntimeError('stream interrupted')
        trace = {}
        with self.assertRaises(RuntimeError):
            self.run_stream(broken(), trace)
        self.assertEqual(trace['events'], [event])
        self.assertEqual(evaluation.check_tool_count(trace, 0)['status'], 'inconclusive')


if __name__ == '__main__':
    unittest.main()
