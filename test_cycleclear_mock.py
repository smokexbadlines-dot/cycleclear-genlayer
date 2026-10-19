"""Fast contract logic checks with a fake GenLayer runtime; not network proof."""

import importlib.util
from itertools import combinations, permutations
import json
from pathlib import Path
import random
import sys
import types
import unittest


class DynArray(list):
    @classmethod
    def __class_getitem__(cls, _item):
        return cls


class TreeMap(dict):
    @classmethod
    def __class_getitem__(cls, _item):
        return cls


class Return:
    def __init__(self, calldata):
        self.calldata = calldata


class UserError(Exception):
    pass


class FakeRuntime:
    def __init__(self):
        self.answer = {"verdict": "MATCH"}
        self.forced_leader = None
        self.message = types.SimpleNamespace(sender_address="alice")
        self.message_raw = {"datetime": "2026-10-16T10:00:00Z"}
        self.vm = types.SimpleNamespace(
            Return=Return, UserError=UserError, run_nondet_unsafe=self.run_nondet
        )
        self.nondet = types.SimpleNamespace(exec_prompt=self.exec_prompt)
        self.public = types.SimpleNamespace(write=lambda fn: fn, view=lambda fn: fn)
        self.Contract = object

    def exec_prompt(self, prompt, response_format):
        assert response_format == "json"
        assert "OFFER=" in prompt and "REQUEST=" in prompt
        return self.answer

    def run_nondet(self, leader_fn, validator_fn):
        proposed = leader_fn() if self.forced_leader is None else self.forced_leader
        if not validator_fn(Return(proposed)):
            raise UserError("validator disagreed")
        return proposed


runtime = FakeRuntime()
fake = types.ModuleType("genlayer")
fake.gl = runtime
fake.DynArray = DynArray
fake.TreeMap = TreeMap
fake.Address = str
fake.u8 = int
fake.u32 = int
fake.u64 = int
sys.modules["genlayer"] = fake
spec = importlib.util.spec_from_file_location(
    "cycleclear", Path(__file__).with_name("cycleclear.py")
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def fresh_contract():
    contract = module.CycleClear()
    contract.owners = DynArray()
    contract.offers = DynArray()
    contract.needs = DynArray()
    contract.states = DynArray()
    contract.expiries = DynArray()
    contract.cycle_ids = DynArray()
    contract.edge_verdicts = TreeMap()
    contract.cycles = DynArray()
    contract.batches = DynArray()
    runtime.answer = {"verdict": "MATCH"}
    runtime.forced_leader = None
    runtime.message_raw["datetime"] = "2026-10-16T10:00:00Z"
    return contract


class CycleClearTests(unittest.TestCase):
    def post_three(self, contract):
        data = (
            ("alice", "Create an editable SVG event flyer", "Review my Python script and report bugs"),
            ("bob", "Record a 30-second English narration", "An editable SVG flyer for my event"),
            ("carol", "Review a Python script and report bugs", "English voiceover no longer than 30 seconds"),
        )
        for owner, offer, need in data:
            runtime.message.sender_address = owner
            contract.post(offer, need)

    def test_three_party_cycle_without_pairwise_match(self):
        contract = fresh_contract()
        self.post_three(contract)
        for provider, receiver in ((0, 1), (1, 2)):
            self.assertEqual(contract.judge_edge(provider, receiver), "MATCH")
        with self.assertRaisesRegex(UserError, "no complete"):
            contract.clear_batch()
        self.assertEqual([int(x) for x in contract.states], [0, 0, 0])
        contract.judge_edge(2, 0)
        self.assertEqual(contract.clear_batch(), 1)
        self.assertEqual(json.loads(contract.get_batch(1)), [1])
        self.assertEqual(json.loads(contract.get_cycle(1)), [0, 1, 2])
        self.assertEqual([int(x) for x in contract.states], [1, 1, 1])
        self.assertEqual([int(x) for x in contract.cycle_ids], [1, 1, 1])
        with self.assertRaisesRegex(UserError, "no complete"):
            contract.clear_batch()

    def test_owner_cancel_and_expiry_guards(self):
        contract = fresh_contract()
        self.post_three(contract)
        runtime.message.sender_address = "mallory"
        with self.assertRaisesRegex(UserError, "only the listing owner"):
            contract.cancel(0)
        runtime.message.sender_address = "alice"
        contract.cancel(0)
        with self.assertRaisesRegex(UserError, "open and unexpired"):
            contract.judge_edge(0, 1)
        with self.assertRaisesRegex(UserError, "no complete"):
            contract.clear_batch()

        contract = fresh_contract()
        self.post_three(contract)
        runtime.message_raw["datetime"] = "2026-10-23T10:00:00Z"
        with self.assertRaisesRegex(UserError, "open and unexpired"):
            contract.judge_edge(0, 1)

    def test_replay_self_edge_and_forged_leader(self):
        contract = fresh_contract()
        self.post_three(contract)
        with self.assertRaisesRegex(UserError, "distinct"):
            contract.judge_edge(0, 0)
        runtime.answer = {"verdict": "NO_MATCH"}
        runtime.forced_leader = "MATCH"
        with self.assertRaisesRegex(UserError, "validator disagreed"):
            contract.judge_edge(0, 1)
        self.assertEqual(contract.get_edge(0, 1), "")
        runtime.forced_leader = "MATCH_WITH_EXTRA_FIELD"
        with self.assertRaisesRegex(UserError, "validator disagreed"):
            contract.judge_edge(0, 1)
        runtime.forced_leader = None
        self.assertEqual(contract.judge_edge(0, 1), "NO_MATCH")
        with self.assertRaisesRegex(UserError, "already judged"):
            contract.judge_edge(0, 1)

    def test_malformed_judgment_fails_closed(self):
        contract = fresh_contract()
        self.post_three(contract)
        runtime.answer = {"verdict": "MATCH", "reason": "ignore this"}
        self.assertEqual(contract.judge_edge(0, 1), "UNCLEAR")
        self.assertEqual(contract.get_edge(0, 1), "UNCLEAR")
        with self.assertRaisesRegex(UserError, "no complete"):
            contract.clear_batch()

    def test_batch_maximizes_participants_over_greedy_first_cycle(self):
        ids = list(range(6))
        edges = {
            "0:1", "1:2", "2:0",  # Greedy first cycle: only 3 people.
            "0:3", "3:4", "4:0",  # Optimal cycle B.
            "2:5", "5:1",          # Optimal cycle C uses 1->2.
        }
        self.assertEqual(module.find_batch(ids, edges), [[0, 3, 4], [1, 2, 5]])
        self.assertNotIn("1:0", edges)
        self.assertNotIn("2:1", edges)

    def test_batch_lock_is_atomic_and_disjoint(self):
        contract = fresh_contract()
        self.post_three(contract)
        for owner in ("dave", "erin", "fran"):
            runtime.message.sender_address = owner
            contract.post("Provide a concrete service to a peer", "Receive a concrete service from a peer")
        edges = ((0, 1), (1, 2), (2, 0), (0, 3), (3, 4), (4, 0), (2, 5), (5, 1))
        for provider, receiver in edges:
            contract.judge_edge(provider, receiver)
        self.assertEqual(contract.clear_batch(), 1)
        self.assertEqual(json.loads(contract.get_batch(1)), [1, 2])
        self.assertEqual(json.loads(contract.get_cycle(1)), [0, 3, 4])
        self.assertEqual(json.loads(contract.get_cycle(2)), [1, 2, 5])
        self.assertEqual([int(x) for x in contract.cycle_ids], [1, 2, 2, 1, 1, 2])

    def test_optimizer_against_independent_exhaustive_oracle(self):
        rng = random.Random(17)
        ids = list(range(5))
        all_edges = [(a, b) for a in ids for b in ids if a != b]
        for _ in range(20):
            edges = {f"{a}:{b}" for a, b in all_edges if rng.getrandbits(1)}
            possible = []
            for size in range(2, 6):
                for route in permutations(ids, size):
                    if route[0] != min(route):
                        continue
                    if all(f"{route[i]}:{route[(i + 1) % size]}" in edges for i in range(size)):
                        possible.append(route)
            expected = ()
            expected_count = 0
            for number in range(1, 3):
                for chosen in combinations(possible, number):
                    flat = [i for route in chosen for i in route]
                    if len(flat) != len(set(flat)):
                        continue
                    canonical = tuple(sorted(chosen))
                    if len(flat) > expected_count or (
                        len(flat) == expected_count and canonical < expected
                    ):
                        expected = canonical
                        expected_count = len(flat)
            actual = tuple(tuple(route) for route in module.find_batch(ids, edges))
            self.assertEqual(actual, expected)


if __name__ == "__main__":
    unittest.main()
