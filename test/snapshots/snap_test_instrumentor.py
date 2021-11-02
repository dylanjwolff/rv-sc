# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['test_md_reader 1'] = (
    {
        'Z': {
            'x': [
                (
                    0,
                    'prev(y) == x'
                )
            ]
        }
    },
    {
        'Z': set([
            'y'
        ])
    }
)
