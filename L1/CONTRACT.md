# Sanad task contracts (Level 1)

Sanad is a university help desk. Students write short messages in English (`en`),
Modern Standard Arabic (`msa`), Egyptian Arabic (`egy`), Arabizi (`arabizi`, Arabic
in Latin letters and digits), or a mix. Three services work on these messages. Each
contract follows the shape of book Example 1.4: input, output, reference labels,
evaluation, fallback, with the language varieties and the most harmful error
stated for each. Routing is kept separate from advice.

---

## 1. Router

1. **Input.** One student message, its date, and any earlier turns the service
   actually receives. In the Sanad data only the message text is available (no date,
   no earlier turns), so version 0 reads the text alone. The original text is kept
   unchanged; normalisation happens in a shared step, not in the stored message.
   Language varieties: `en`, `msa`, `egy`, `arabizi`, or a mix.
2. **Routing output.** One label from `access`, `assessment`, `registration`,
   `fees`, `other`. If a message contains two separate requests, or the router will
   not choose, it returns no label (`None`) and the desk asks which request to
   handle first.
3. **Urgency output.** A separate yes/no flag, not part of the label: urgent when
   the student is blocked from an assessment due within 24 hours or is locked out
   of the portal with a deadline running. If the deadline is unknown, the service
   asks for it and does not guess. The Level 1 data has no urgency labels, so this
   flag is specified here but not yet measured.
4. **Reference labels.** Two annotators label each test message using written
   rules, before seeing any model output. A help-desk reviewer settles
   disagreements. (The Sanad tickets are constructed teaching tickets whose single
   `intent` label was fixed by the course team when each ticket was written.)
5. **Evaluation.** On held-out messages (the dev split now, the test split only at
   Level 6), report routing accuracy with its rough 95% margin, per-intent
   precision and recall, and macro-F1, separately for each language variety. Report
   counts as well as rates, because each variety has only 5 dev tickets. Urgent-flag
   recall will be added once urgency labels exist; the proposed target is at least
   0.90, with every missed urgent case reviewed. A measure that weights costly
   routing errors more than cheap ones waits for Chapter 4.
6. **Fallback.** When the message is unclear, has two requests, or no approved
   procedure applies, hand it to help-desk staff. Routing never changes a
   registration or an account by itself.

**Most harmful error.** An urgent or money-related ticket routed to `other`: a
`fees` ticket (instalments, a late payment, a refund) or an `assessment` ticket
(an appeal or a deadline) sent to `other`, and an `access` ticket (cannot log in)
sent to `other`. `other` is the general queue, so nobody who owns the deadline
sees the ticket and the student waits while it runs. A missed urgent flag is the
same failure in another form.

**Which routing errors cost most, in words.**

1. *Urgent or money intent sent to `other`.* The ticket has no owner, and the harm
   grows each day it goes unseen. This costs most.
2. *One specific intent sent to another specific intent* (for example `fees` to
   `registration`). A person on the wrong team still reads it and can forward it,
   so the cost is a delay.
3. *`other` sent to a specific intent.* A staff member reads a ticket that needs no
   action. This costs a little wasted time and is the cheapest wrong answer.
4. *No label (`None`).* The ticket goes straight to a human. It costs staff time
   but never leaves a student unseen.

Plain accuracy counts all of these as equal mistakes, which is why accuracy alone
is not enough here.

**Baseline.** Version 0 always answers the most frequent training intent. It is a
floor that every later router must beat on the same dev split.

---

## 2. Search (answer lookup, kept separate from routing)

1. **Input.** One student question, in the same varieties as a ticket. Only the
   text is received. The original text is kept.
2. **Output.** A ranked list of at most `k = 3` approved FAQ passage ids, best
   first, containing only passages judged relevant. An empty list is allowed. The
   service returns approved passages; it does not write new advice.
3. **Reference labels.** Each test question lists the passage ids that answer it
   (the `faq` field), written by the course team and checked by a second reader
   using the same written rule: a passage is correct if following it would solve the
   student's problem. A question may have more than one correct passage.
4. **Evaluation.** On held-out questions, report MRR and precision at 3, by
   language variety, plus the count of questions that returned an empty list.
   Report counts as well as rates (5 dev tickets per variety).
5. **Language varieties.** `en`, `msa`, `egy`, `arabizi`. The passages are written
   in English and Arabic script, so a variety that uses neither script nor spelling
   (Arabizi) is the hardest case.
6. **Fallback.** When the result list is empty, or no approved procedure applies,
   say that no answer was found and hand the question to help-desk staff.

**Most harmful error.** The correct passage is missing from the top 3 while other
passages are shown: the student reads a confident but wrong rule (a wrong deadline,
a wrong fee policy, a wrong reset procedure) and acts on it. Close behind is the
right passage ranked below wrong ones. An empty result is a safe failure; a wrong
passage shown with confidence is not.

---

## 3. Keyboard (next-word suggestion)

Built at Level 3. At this level only the contract is written.

1. **Input.** The tokens the student has typed so far in a message (the history),
   in any of the four varieties or a mix.
2. **Output.** Up to `k = 3` suggested next tokens, best first. The model can also
   give the probability of any candidate next token, which is used for perplexity.
3. **Reference labels.** No one labels it by hand. The reference is the token the
   student actually wrote next. Every token of every held-out ticket is one case.
4. **Evaluation.** Report acc1 (first suggestion correct), acc@3 (correct token
   among the first three), perplexity, and the fraction of target tokens outside the
   training vocabulary, separately for each variety. Perplexity is comparable only
   between keyboards that use the same tokenizer.
5. **Language varieties.** `en`, `msa`, `egy`, `arabizi`. Spelling in Arabizi and
   dialect varies a lot, so many targets may be out of vocabulary.
6. **Fallback.** Show no suggestion. A blank suggestion bar is always safe, and the
   keyboard never suggests a course code, amount or date it is not confident about.

**Most harmful error.** A suggestion that changes the meaning of a message and is
accepted without notice: a wrong course code, amount or date in a ticket about money
or a deadline. An unhelpful suggestion costs one wasted glance; an accepted wrong
one can send the ticket to the wrong place or state the wrong amount.
