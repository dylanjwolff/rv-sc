import pytest
import json
from rvsc import instrumentor
from rvsc.ltl_tools import var_mapping

TEST_JSON = '''[  { "name": "v0", "triggers": ["Z.x"], "condition": "prev(y) == x", "types": { "Z.y": "uint32" } } ]'''
TEST_JSON_F = '''[  { "name": "v0", "triggers": ["Z.FUNCTION == \\"foo\\""], "condition": "y == x", "types": { "Z.y": "uint32" } }, 
                    { "name": "v1", "triggers": ["Z.FUNCTION_END"], "condition": "a == b" } ]'''


def test_md_reader_currs(snapshot):
    var_mapping = {"v0": 0}
    snapshot.assert_match(
        instrumentor.to_flat_update(json.loads(TEST_JSON), var_mapping)[0])


def test_md_reader_prevs(snapshot):
    var_mapping = {"v0": 0}
    snapshot.assert_match(
        instrumentor.to_flat_update(json.loads(TEST_JSON), var_mapping)[1])


def test_md_reader_types(snapshot):
    var_mapping = {"v0": 0}
    snapshot.assert_match(
        instrumentor.to_flat_update(json.loads(TEST_JSON), var_mapping)[2])


def test_F_reader(snapshot):
    var_mapping = {"v0": 0, "v1": 1}
    print(TEST_JSON_F)
    r = instrumentor.to_flat_update(json.loads(TEST_JSON_F), var_mapping)
    snapshot.assert_match(r[0])
