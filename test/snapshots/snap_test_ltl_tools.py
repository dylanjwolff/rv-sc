# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import GenericRepr, Snapshot


snapshots = Snapshot()

snapshots['test_impl 1'] = {
    'v0': 2,
    'v1': 0,
    'v2': 1
}

snapshots['test_smoke_ast_pretty 1'] = '''
if (state == 0) {
\tif (!vars[0]) {
\t\tstate = 0;
\t} else {
\t\trevert("Invalid Buchi State");
\t}
\t} else if (vars[0]) {
\t\tstate = 1;
\t} else {
\t\trevert("Invalid Buchi State");
\t}
}
if (state == 1) {
\tif (!vars[0] && !vars[1]) {
\t\tstate = 0;
\t} else {
\t\trevert("Invalid Buchi State");
\t}
\t} else if (vars[0] && !vars[1]) {
\t\tstate = 1;
\t} else {
\t\trevert("Invalid Buchi State");
\t}
}'''

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
