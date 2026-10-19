# CycleClear

CycleClear is a standalone GenLayer Native Intelligent Contract for **maximum-participation batch barter clearing**. A participant posts one immutable offer and one need. Validators independently judge a directed offer→request edge as `MATCH`, `NO_MATCH`, or `UNCLEAR`. Deterministic code then chooses a set of vertex-disjoint exchange cycles that includes the largest possible number of participants and locks the whole batch in one transaction. Listing IDs break ties lexicographically.

The AI judges only semantic fit. It never chooses a cycle, a participant, a number, or a transfer. A `MATCH` edge can change the feasible graph; a batch can clear several complete cycles even when no pair can trade alone. Unjudged and ambiguous edges never qualify.

## Why this is a separate mechanism

The owner's earlier [SkillLoop](https://github.com/smokexbadlines-dot/skillloop-genlayer) already stores judged directed edges and reserves the first three-person cycle. CycleClear adds a different clearing invariant: **among all currently approved cycles of two to five listings, no alternative disjoint cycle packing can lock more participants**. A greedy first-cycle lock can strand otherwise matchable people. CycleClear solves that graph-wide conflict before changing any listing state. The bounded eight-listing board permits exhaustive deterministic optimization.

| Mechanism | SkillLoop | CycleClear |
| --- | --- | --- |
| Validator judgment | Directed service fit | Directed offer→request fit |
| Clearing rule | First eligible three-person cycle | Maximum-participation disjoint cycle packing |
| State effect | One cycle reserved | Multiple non-overlapping cycles locked atomically |
| New invariant | A valid three-party cycle is reserved | No larger packing exists among approved edges at clearing time |

This is a substantive algorithm and state transition change, though review-cohort distinctiveness remains a steward's judgment.

## Contract behavior

- Each address has at most one live open listing. Listing text is 10–240 characters per field and cannot change after posting. Posting consents to an automatic lock if a complete approved batch exists.
- A listing expires seven days after posting. Its owner may cancel it while open. Expired or cancelled listings cannot enter a new judgment or clearing batch.
- Any address may call `judge_edge(provider_id, receiver_id)` once per directed pair. The LLM sees only frozen onchain text and must return one allowlisted verdict. A validator independently reruns the same prompt and requires exact verdict equality. Malformed output becomes `UNCLEAR`.
- Any address may call `clear_batch()`. Code enumerates simple approved cycles of length two to five, optimizes disjoint packing by participant count, and uses lexicographic cycle order for ties. One transaction marks all selected listings `LOCKED`, assigns cycle IDs, and records a batch ID. A listing cannot appear twice in a batch.
- Capacity is 16 lifetime listings, eight concurrently open listings, and at most five listings per cycle. These bounds constrain graph search cost. A new deployment is required after 16 posts.

`LOCKED` is a public coordination record. There is no GEN escrow, token transfer, delivery attestation, or onchain enforcement of the offchain goods and services.

## Six-person mechanism demo

Use six distinct addresses. The wording deliberately includes paraphrases and bounded requirements that make validator interpretation meaningful.

| ID | Offer | Need |
| --- | --- | --- |
| 0 | Create an editable SVG flyer for a local event | WCAG accessibility checklist for my one-page website |
| 1 | Record English voiceover up to 30 seconds | Editable SVG event flyer |
| 2 | Review a one-page website against WCAG and provide a checklist | English narration no longer than half a minute |
| 3 | Translate up to 200 English words into Spanish | Editable SVG flyer for a local event |
| 4 | Provide a WCAG accessibility checklist for a one-page website | Spanish translation of at most 200 English words |
| 5 | Design an editable SVG event flyer | Accessibility review with WCAG checklist for a one-page site |

Judge these eight directed edges: `0→1`, `1→2`, `2→0`, `0→3`, `3→4`, `4→0`, `2→5`, `5→1`. Check each `get_edge` read-back. With all eight `MATCH`, the first lexicographic cycle is `[0,1,2]`, which would lock only three people if cleared greedily. The maximum packing is `[0,3,4]` plus `[1,2,5]`, locking all six in one `clear_batch()` call. The two chosen cycles are disjoint. None of the eight approved edges forms a reciprocal pair.

For a guard demonstration, try `clear_batch()` before a closing edge exists, call `cancel(0)` from a different address, and retry an already judged edge. Each should fail without changing state. After a successful batch, `get_batch(1)` should return `[1,2]`, `get_cycle(1)` should return `[0,3,4]`, `get_cycle(2)` should return `[1,2,5]`, and every listing should have state `1` with the corresponding cycle ID. Only **FINALIZED + successful leader execution**, followed by state read-backs, counts as live proof. If a live verdict is `NO_MATCH` or `UNCLEAR`, investigate the exact judgment; do not present a mock verdict as live success.

## Local verification

With Python 3.12 and `genvm-linter` installed:

```sh
python -m unittest -v test_cycleclear_mock.py
genvm-lint check cycleclear.py
```

The mock tests cover three-party closure, six-party batch optimization, atomic disjoint locks, owner authorization, expiry, edge replay, forged leader verdicts, and malformed judgments. A separate GenLayer `gltest` direct-mode check exercised real SDK storage and validator callbacks. The pinned SDK passed semantic validation. These local checks do not establish live consensus or finality.

## Submission evidence

Before submission, supply a public source commit and byte-identical deployed source, an Explorer address, finalized successful transactions for the demo and guard failures, read-backs, and a release manifest. No Portal submission should claim these until they exist. See [SUBMISSION.md](SUBMISSION.md) for the evidence checklist and draft Portal fields.

## Official references

- [Contract syntax and pinned runner](https://docs.genlayer.com/developers/intelligent-contracts/first-contract)
- [Storage types](https://docs.genlayer.com/developers/intelligent-contracts/features/storage)
- [Non-deterministic blocks](https://docs.genlayer.com/developers/intelligent-contracts/features/non-determinism)
- [Transaction finality](https://docs.genlayer.com/understand-genlayer-protocol/core-concepts/optimistic-democracy/finality)
