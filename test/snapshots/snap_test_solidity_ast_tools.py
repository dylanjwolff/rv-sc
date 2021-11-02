# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['test_typer 1'] = {
    'BasicToken': {
        'balances': 'mapping (address=>uint256)',
        'msg.sender': 'address',
        'this.balance': 'uint256'
    },
    'Deployer': {
        'msg.sender': 'address',
        't': 'ZilliqaToken',
        'this.balance': 'uint256'
    },
    'ERC20': {
        'msg.sender': 'address',
        'this.balance': 'uint256'
    },
    'ERC20Basic': {
        'msg.sender': 'address',
        'this.balance': 'uint256',
        'totalSupply': 'uint256'
    },
    'Ownable': {
        'msg.sender': 'address',
        'owner': 'address',
        'this.balance': 'uint256'
    },
    'Pausable': {
        'admin': 'address',
        'msg.sender': 'address',
        'pausedOwnerAdmin': 'bool',
        'pausedPublic': 'bool',
        'this.balance': 'uint256'
    },
    'PausableToken': {
        'msg.sender': 'address',
        'this.balance': 'uint256'
    },
    'SafeMath': {
        'msg.sender': 'address',
        'this.balance': 'uint256'
    },
    'StandardToken': {
        'allowed': 'mapping (address=>mapping (address=>uint256))',
        'msg.sender': 'address',
        'this.balance': 'uint256'
    },
    'ZilliqaToken': {
        'decimals': 'uint8',
        'msg.sender': 'address',
        'name': 'string',
        'symbol': 'string',
        'this.balance': 'uint256'
    }
}
