# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import GenericRepr, Snapshot


snapshots = Snapshot()

snapshots['test_smoke_ast_pretty 1'] = '''
if state == 0:
\tif !v0:
\t\tstate = 0
\tif v0:
\t\tstate = 1
if state == 1:
\tif !v0 and !v1:
\t\tstate = 0
\tif v0 and !v1:
\t\tstate = 1'''

snapshots['test_smoke_ba_ast 1'] = [
    (
        GenericRepr("Tree('statename', [Token('SIGNED_INT', '0')])"),
        [
            GenericRepr('Edge()'),
            GenericRepr('Edge()')
        ]
    ),
    (
        GenericRepr("Tree('statename', [Token('SIGNED_INT', '1')])"),
        [
            GenericRepr('Edge()'),
            GenericRepr('Edge()')
        ]
    )
]
