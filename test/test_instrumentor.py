import pytest
import json
from rvsc import instrumentor

TEST_JSON = '''[  { "triggers": ["Z.x"], "condition": "prev(y) == x" } ]'''


def test_md_reader(snapshot):
    snapshot.assert_match(instrumentor.to_flat_update(json.loads(TEST_JSON)))