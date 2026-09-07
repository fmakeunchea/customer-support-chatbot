# Customer support chatbot: manual chat evidence

These are excerpts from actual `chat.py` terminal output copied by the student into the project guidance conversation. They are not a newly executed test or a complete terminal recording. Copy/paste escaping has been normalized; customer and assistant wording, ticket IDs, tool-call lines, and visible thinking text have been preserved. The examples were collected during prompt iteration and do not all represent the final prompt and client configuration.

## 1. Multi-turn bug report

This run occurred before the explicit per-run actor ID was added to the client. The startup line identifies the fresh session used for this exchange.

```text
Connected to harness support_chatbot (session 48973a2d-a43c-49d8-97ac-3d61ff573bc6-support-chat).
Type a message, or 'quit' to exit.

you> I open the shopping cart and click Increase quantity. The page displays CART-QUANTITY-745 and the quantity stays unchanged.
bot> <thinking>The user has described a new bug where clicking 'Increase quantity' in the shopping cart results in an error message 'CART-QUANTITY-745' and the quantity remains unchanged. This is a clear bug report with a description and steps to reproduce. However, the environment (browser, operating system, device) is not specified. I need to ask for this information to complete the bug report.</thinking>
What browser, operating system, and device are you using?

you> I'm using Microsoft Edge on a Windows 10 desktop.
bot> <thinking>The user has provided the environment details for the new bug they reported. I now have all the necessary information to create a bug report: the description, steps to reproduce, and the environment. I will create the bug report using the provided information.</thinking>

[tool call] bugreports___create_bug_report
The bug report has been successfully created with ticket ID 0e670190-c270-4ab2-8924-b12576c14317. Thank you for reporting this issue.
```

The student separately retrieved this ticket from DynamoDB. The query returned the description, steps, and environment, in that order:

```json
[
  "When I open the shopping cart and click 'Increase quantity,' the page displays CART-QUANTITY-745 and the quantity stays unchanged.",
  "Open the shopping cart and click 'Increase quantity.'",
  "Microsoft Edge on a Windows 10 desktop."
]
```

Observation: this exchange demonstrates asking for the missing environment before a tool call, automatic submission after the reply, and accurate persisted fields. It also demonstrates a failure: internal thinking text was displayed despite the prompt's response-format instructions. Other runs showed premature tool calls; this successful sequence does not establish consistent compliance. The saved DynamoDB screenshot documents a different ticket, `7b7cb555-b055-463a-81c9-93eb3d8bb4de`, from the v3 automated evaluation run.

## 2. Covered FAQ question

```text
you> How do I reset my password?
bot> Use the “Forgot password” link on the sign-in page. You’ll receive a reset email if the address matches an account.
```

Observation: the answer matches the supplied FAQ and preserves the account-match condition. No tool call appears in the supplied exchange.

## 3. Shop question not covered by the FAQ

```text
you> Do you offer a student discount, and what percentage is it?
bot> I can help with this shop's support questions. For information on discounts, the fictional shop's demo support number is +1 (202) 555-0147 (not a working support line).
```

Observation: the answer does not invent a discount policy or percentage and provides the configured phone hand-off. The number is a fictional implementation assumption because the supplied course materials did not provide one.

## 4. Out-of-scope request

```text
you> Can you write my résumé?
bot> I can help with this shop's support questions. For other assistance, the fictional shop's demo support number is +1 (202) 555-0147 (not a working support line).
```

Observation: the assistant stays within shop support and provides a polite phone hand-off with the demo disclosure.

## Related evaluation evidence

The [evaluation observations](../starter/evaluation-observations.md) discuss the six scored records and remaining limitations. The [raw judge results](../starter/evaluation-results-v3.jsonl) assess final responses; they do not prove correct intermediate tool behavior.
