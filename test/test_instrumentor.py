import pytest
import json
from rvsc import instrumentor
from rvsc.ltl_tools import var_mapping

TEST_JSON = '''[  { "name": "v0", "triggers": ["Z.x"], "condition": "prev(y) == x", "types": { "Z.y": "uint32" } } ]'''


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
