from solcx import install_solc
from solcx import compile_source
from web3 import Web3
import pprint

# Note: based off of the web3 quickstart documentation
install_solc(version='0.4.26')

pp = pprint.PrettyPrinter()
fname = "verx-benchmarks/Zilliqa/main.sol"
contracts: str = open(fname).read()
contract: str = contracts.split("contract")[1]
print(contract)

compiled_sol = compile_source(contract)
contract_id, contract_interface = compiled_sol.popitem()

bytecode = contract_interface['bin']
abi = contract_interface['abi']
# @TODO change to use environment variable
w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))
w3.eth.default_account = w3.eth.accounts[0]
zil = w3.eth.contract(abi=abi, bytecode=bytecode)
z = zil.constructor(w3.eth.accounts[0], 0).transact()
z.pause(False, False)
pp.pprint(z)
