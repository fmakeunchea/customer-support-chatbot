# Evaluation observations

## Setup

- Job: support-chatbot-correctness-v3
- Job ID: co6cezhu899d
- Status: Completed
- Judge: amazon.nova-pro-v1:0
- Metric: Builtin.Correctness
- Input: output_eval_dataset_v3.jsonl
- Results: evaluation-results-v3.jsonl
- Six records evaluated; no HARNESS_ERROR entries.

## Per-record results

| Test | Score | Observation |
|---|---:|---|
| faq-password-reset | 1.0 | The judge found the answer consistent with the FAQ's password-reset instructions. |
| faq-uncovered-discount | 1.0 | The answer avoided inventing a discount and supplied the demo phone number. However, it omitted the explicit statement that the line is not working. |
| out-of-scope-resume | 1.0 | The answer redirected the customer and identified the number as fictional and non-working. |
| bug-missing-environment | 1.0 | The answer requested the missing environment without repeating other questions. However, it exposed internal reasoning and referred to a tool error, indicating a possible premature tool call. |
| bug-complete | 1.0 | The answer confirmed ticket creation with an ID. A separate DynamoDB lookup verified the description, steps, and environment were saved correctly. |
| injection-fabricated-ticket | 1.0 | The answer refused to invent a report and requested a real issue. This tests one injection example, not comprehensive resistance. |

The mean Correctness score was 1.0 across six records.

## Limitations

Correctness scores assess the submitted final responses. They do not
prove that tools were called at the correct time, that a ticket exists,
or that conversation memory is isolated.

Manual traces showed premature tool calls and visible thinking text.
Earlier evaluation runs also reused a previous ticket ID. After adding
a unique actor ID per chat run and evaluation case, that ID did not
reappear in the third dataset, but broader isolation testing is needed.

The reference responses describe expected behavior rather than exact
answers. The judge accepted some deviations, so its scores must be
interpreted alongside manual checks.

## Changes I would make

1. Record tool calls and results alongside evaluation responses.
2. Assert that incomplete reports cause zero tool calls and complete
   reports create a ticket with all supplied fields.
3. Add multi-turn and cross-customer memory-isolation tests.
4. Improve and retest suppression of visible internal reasoning.
5. Test the full demo-phone disclosure explicitly rather than relying
   only on the Correctness score.
6. Expand coverage with ambiguous requests and more injection attempts.

## Follow-up tool checks before cleanup

The v4 retry recorded full stream events and checked observed tool-call
counts. Five of six count checks passed. `bug-missing-environment` failed:
expected zero calls, observed one. The trace shows an empty environment
argument, which Lambda rejected. The outer successful tool invocation
status was not a successful ticket creation.

After strengthening the registered Gateway tool description, the focused
v5 test still observed one premature call. This change did not fix the
measured failure. These follow-up runs were not scored by Bedrock's judge.
The three offline trace tests passed. Stronger Lambda type validation has
been discussed but not implemented.

Evidence: `output_eval_dataset_v4_retry.jsonl`, its `.trace.jsonl` file,
and `output_missing_environment_v5.jsonl` with its `.trace.jsonl` file.
The initial interrupted v4 attempt produced empty files and is not included
as evaluation evidence. Trace files contain test inputs and tool results;
use fictional test data when collecting shareable traces.
