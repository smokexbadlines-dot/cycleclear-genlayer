"""Independently verify CycleClear's finalized StudioNet proof.

Requires genlayer-py==0.16.3. Uses an unsaved random address only for reads;
no wallet key, funded account, or write transaction is required.
"""

import base64
import hashlib
import json
from pathlib import Path

from genlayer_py import create_account
from genlayer_py.client import GenLayerClient
from genlayer_py.chains import studionet
from genlayer_py.types import TransactionHashVariant, TransactionStatus


HERE = Path(__file__).resolve().parent
proof = json.loads((HERE / "proof_manifest.json").read_text(encoding="utf-8"))
source = (HERE / "cycleclear.py").read_bytes()
assert hashlib.sha256(source).hexdigest() == proof["source_sha256"]
assert len(proof["transactions"]) == 19

client = GenLayerClient(studionet, create_account())
for record in proof["transactions"]:
    tx = client.get_transaction(record["tx_id"])
    assert tx["status_name"] == TransactionStatus.FINALIZED, record["tx_id"]
    assert str(tx["result_name"]) == "MAJORITY_AGREE", record["tx_id"]
    leader = tx["consensus_data"]["leader_receipt"][0]
    assert leader["result"]["status"] == record["leader_status"], record["tx_id"]

deploy = client.get_transaction(proof["transactions"][0]["tx_id"])
assert deploy["data"]["contract_address"].lower() == proof["contract"].lower()
assert base64.b64decode(deploy["data"]["contract_code"]) == source


def read(method, *args):
    return client.read_contract(
        proof["contract"], method, args=list(args),
        transaction_hash_variant=TransactionHashVariant.LATEST_FINAL,
    )


assert read("listing_count") == 6
assert read("batch_count") == 1
assert read("cycle_count") == 2
assert json.loads(read("get_batch", 1)) == [1, 2]
assert [json.loads(read("get_cycle", i)) for i in (1, 2)] == [[0, 3, 4], [1, 2, 5]]
for provider, receiver in proof["approved_edges"]:
    assert read("get_edge", provider, receiver) == "MATCH"
for i, address in enumerate(proof["participants"]):
    listing = json.loads(read("get_listing", i))
    assert listing["owner"].lower() == address.lower()
    assert listing["state"] == 1
    assert listing["cycle_id"] == [1, 2, 2, 1, 1, 2][i]

print("PASS: 19 finalized transactions, byte-identical source, 8 MATCH edges, 2 cycles, 6 locked listings")
print("Contract:", proof["contract"])
