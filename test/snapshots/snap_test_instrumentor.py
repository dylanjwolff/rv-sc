# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['test_md_reader_currs 1'] = {
    'Z': {
        'x': [
            (
                0,
                'prev___y == x'
            )
        ]
    }
}

snapshots['test_md_reader_prevs 1'] = {
    'Z': {
        'x': set([
            'y'
        ])
    }
}
