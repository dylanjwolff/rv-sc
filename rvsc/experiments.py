from solcx import install_solc
from solcx import compile_source
from web3 import Web3
import pprint
from web3.middleware import geth_poa_middleware

# Note: based off of the web3 quickstart documentation
install_solc(version='0.4.26')
# @TODO change to use environment variable
w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))

# @TODO use environment variable to indicate GETH?
w3.middleware_onion.inject(geth_poa_middleware, layer=0)
w3.eth.default_account = w3.eth.accounts[0]

ofname = "verx-benchmarks/Zilliqa/main.sol"
ifname = "test-resources/main.sol"

pp = pprint.PrettyPrinter()


def compile_contracts(fname):
    contracts: str = open(fname).read()
    compiled_sol = compile_source(contracts)

    contracts = {}
    for contract_id, contract_interface in compiled_sol.items():
        bytecode = contract_interface['bin']
        abi = contract_interface['abi']
        contracts[contract_id.split(":")[1]] = w3.eth.contract(
            abi=abi, bytecode=bytecode)
    return contracts


original_contracts = compile_contracts(ofname)
instrum_contracts = compile_contracts(ifname)

contract = original_contracts["ZilliqaToken"]
oldgas = 0
tx_hash = contract.constructor(w3.eth.accounts[1], 100).transact()
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
oldgas += tx_receipt["gasUsed"]

constructedZ = w3.eth.contract(address=tx_receipt.contractAddress,
                               abi=contract.abi)
tx_hash = constructedZ.functions.transfer(w3.eth.accounts[1], 50).transact()
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
oldgas += tx_receipt["gasUsed"]
print(f"Original used {oldgas}")

gas = 0
tx_hash = instrum_contracts["BuchiChecker"].constructor().transact()
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
print(tx_receipt)

contract = instrum_contracts["ZilliqaToken"]
gas = 0
tx_hash = contract.constructor(w3.eth.accounts[1], 100,
                               tx_receipt.contractAddress).transact()
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
gas += tx_receipt["gasUsed"]

constructedZ = w3.eth.contract(address=tx_receipt.contractAddress,
                               abi=contract.abi)
tx_hash = constructedZ.functions.transfer(w3.eth.accounts[1], 50).transact()
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
gas += tx_receipt["gasUsed"]
print(f"{gas-oldgas} more gas used")
