# CycleClear submission packet

## Draft Portal fields

**Project name:** CycleClear

**Type:** Standalone GenLayer Native Intelligent Contract

**One-line description:** Validator-judged offer-to-need edges feed a deterministic maximum-participation cycle-packing rule, so one call can lock several disjoint exchanges.

**Mechanism:** Participants post immutable offers and needs. GenLayer validators independently classify each directed edge. Only `MATCH` edges enter a bounded graph. `clear_batch` enumerates approved cycles of two to five listings, selects the disjoint set covering the most participants, and locks the whole selection atomically. Listing IDs break ties. The AI never chooses a cycle or executes a transfer.

**Why GenLayer:** Semantic fit between varied goods and services cannot be captured reliably by exact string equality. GenLayer's leader and validator execution allows the semantic edge decision to be checked by independent nodes, while the allocation rule stays deterministic.

**Distinctiveness:** The owner's earlier SkillLoop reserves one eligible three-person service cycle. CycleClear computes a globally optimal, disjoint batch and demonstrates a graph where a greedy three-person reservation would strand three participants. Reviewer assessment of project distinctiveness remains independent of this technical comparison.

**Limitations:** This is a coordination and reservation record. It does not escrow GEN, verify delivery, settle disputes, or guarantee an offchain exchange. The board is bounded to 16 lifetime listings and eight open listings.

## Required proof before Portal submission

1. Public source repository and immutable commit, with SHA-256 of the exact deployed contract bytes.
2. StudioNet contract address and Explorer URL; deployment transaction finalized with successful leader execution.
3. Six separate posting addresses and finalized successful posting transactions.
4. Eight edge judgments, each finalized successfully and read back as `MATCH`.
5. A finalized successful `clear_batch` transaction, then read-backs showing batch `[1,2]`, cycles `[0,3,4]` and `[1,2,5]`, and all six listings locked once.
6. Guard evidence for an unauthorized cancellation, repeated judgment, and premature clear. Record the finalized execution result and unchanged state; a transaction that errors is expected for each guard.
7. A release manifest linking the source commit, contract, and transaction proofs. Do not call pending or accepted transactions finalized.

## Readiness gates

| Gate | Pass condition | Current status |
| --- | --- | --- |
| Technical | Source validates against pinned SDK and local tests pass | Local PASS; live status pending |
| Distinctiveness | Batch optimization is a real mechanism change from SkillLoop | Technical comparison PASS; reviewer judgment pending |
| Evidence | Public source and finalized live traces plus read-backs | Pending |

The owner submits to the Portal after reviewing the complete proof. Repository visibility and Portal submission require the owner's explicit approval.
