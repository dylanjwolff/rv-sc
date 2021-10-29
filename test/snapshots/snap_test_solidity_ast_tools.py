# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['test_typer 1'] = {
    'BasicToken': {
        'balances': 'mapping (address=>uint256)',
        'msg.sender': 'address'
    },
    'Deployer': {
        'msg.sender': 'address',
        't': 'ZilliqaToken'
    },
    'ERC20': {
        'msg.sender': 'address'
    },
    'ERC20Basic': {
        'msg.sender': 'address',
        'totalSupply': 'uint256'
    },
    'Ownable': {
        'msg.sender': 'address',
        'owner': 'address'
    },
    'Pausable': {
        'admin': 'address',
        'msg.sender': 'address',
        'pausedOwnerAdmin': 'bool',
        'pausedPublic': 'bool'
    },
    'PausableToken': {
        'msg.sender': 'address'
    },
    'SafeMath': {
        'msg.sender': 'address'
    },
    'StandardToken': {
        'allowed': 'mapping (address=>mapping (address=>uint256))',
        'msg.sender': 'address'
    },
    'ZilliqaToken': {
        'decimals': 'uint8',
        'msg.sender': 'address',
        'name': 'string',
        'symbol': 'string'
    }
}
