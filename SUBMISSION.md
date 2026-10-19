# CycleClear submission packet

## Draft Portal fields

**Project name:** CycleClear

**Type:** Standalone GenLayer Native Intelligent Contract

**One-line description:** Validator-judged offer-to-need edges feed a deterministic maximum-participation cycle-packing rule, so one call can lock several disjoint exchanges.

**Mechanism:** Participants post immutable offers and needs. GenLayer validators independently classify each directed edge. Only `MATCH` edges enter a bounded graph. `clear_batch` enumerates approved cycles of two to five listings, selects the disjoint set covering the most participants, and locks the whole selection atomically. Listing IDs break ties. The AI never chooses a cycle or executes a transfer.

**Why GenLayer:** Semantic fit between varied goods and services cannot be captured reliably by exact string equality. GenLayer's leader and validator execution allows the semantic edge decision to be checked by independent nodes, while the allocation rule stays deterministic.

**Distinctiveness:** The owner's earlier SkillLoop reserves one eligible three-person service cycle. CycleClear computes a globally optimal, disjoint batch and demonstrates a graph where a greedy three-person reservation would strand three participants. Reviewer assessment of project distinctiveness remains independent of this technical comparison.

**Limitations:** This is a coordination and reservation record. It does not escrow GEN, verify delivery, settle disputes, or guarantee an offchain exchange. The board is bounded to 16 lifetime listings and eight open listings.

## Evidence links

1. Source: [public CycleClear repository](https://github.com/smokexbadlines-dot/cycleclear-genlayer), deployment source commit `96ceebf40de030c73482fd8aaaff8465a89494cc`. Contract SHA-256: `60fbef0c415dfc4ac0896fb83ca84d41ba9d532d77db3db6ae58dcd98996afa6`; the deployed bytes match.
2. StudioNet (chain 61999): [contract address](https://explorer-studio.genlayer.com/address/0x38cf54f97D5621cAfD374C08776d59A1f7F4E176), `0x38cf54f97D5621cAfD374C08776d59A1f7F4E176`.
3. Finalized successful [deployment](https://explorer-studio.genlayer.com/tx/0xb815980727298021557f46a14c91c82afd37229beebe5aa3363b1f2d37edf2f4) and [batch clear](https://explorer-studio.genlayer.com/tx/0x63d9aa332a55a5b3dea538033747f51812a2e78976587744c4f58a07589c8c8a). Both have leader `return` and majority agreement.
4. Six posts, eight `MATCH` judgments, and three guard rollbacks are recorded with finalized transaction IDs in [proof_manifest.json](proof_manifest.json). The guard cases are premature clear, unauthorized cancel, and judged-edge replay.
5. Final state: batch `[1,2]`; cycles `[0,3,4]` and `[1,2,5]`; each of six listings `LOCKED` in exactly one cycle. [verify_studionet.py](verify_studionet.py) rechecks finalized statuses, leader results, byte-identical source, edges, and state via RPC.

## Readiness gates

| Gate | Pass condition | Current status |
| --- | --- | --- |
| Technical | Source validates against pinned SDK, local checks pass, live demo clears | PASS |
| Distinctiveness | Batch optimization is a real mechanism change from SkillLoop | Technical PASS; reviewer judgment pending |
| Evidence | Finalized live traces, byte-identical source, read-backs, public repository | PASS |

The owner reviews this packet and submits the public source and evidence links to the Portal. Portal submission is reserved for the owner.
