from solcx import compile_source
from web3 import Web3
from web3.middleware import geth_poa_middleware
from . import solidity_ast_tools
from solidity_parser import parser
from . import solc_vm


def web3_geth_setup():

    w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    w3.eth.default_account = w3.eth.accounts[0]
    return w3


def compile_contracts(w3, fname):
    contracts = open(fname).read()
    solc_vm.Solc(solidity_ast_tools.get_compiler_version(contracts)).install()
    compiled_sol = compile_source(contracts)

    contracts = {}
    for contract_id, contract_interface in compiled_sol.items():
        bytecode = contract_interface['bin']
        abi = contract_interface['abi']
        contracts[contract_id.split(":")[1]] = w3.eth.contract(
            abi=abi, bytecode=bytecode)
    return contracts


def constructZilliqaToken(w3, contracts, instrumented=False):
    contract = contracts["ZilliqaToken"]
    tx_hash = contract.constructor(w3.eth.accounts[0], 100).transact()
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    constructedZ = w3.eth.contract(address=tx_receipt.contractAddress,
                                   abi=contract.abi)

    if instrumented:
        bc_tx_receipt = constructBuchiChecker(w3, contracts["BuchiChecker"])
        init_hash = constructedZ.functions.initialize(
            bc_tx_receipt.contractAddress).transact()
        init_receipt = w3.eth.wait_for_transaction_receipt(init_hash)
    return (constructedZ, )


def constructBuchiChecker(w3, contract):
    tx_hash = contract.constructor().transact()
    return w3.eth.wait_for_transaction_receipt(tx_hash)
