from rvsc import instrumentor
from rvsc import ltl_tools
import json
import tempfile
from rvsc import node_setup
import os
import pytest
import polling2
import requests

ENDPOINT = "http://localhost:8545"


@pytest.fixture
def geth_ethnode():
    os.system("pkill geth")
    os.system("geth --dev --http &")

    try:
        result = polling2.poll(lambda: is_up(ENDPOINT),
                               timeout=10,
                               step=1,
                               max_tries=100)
        yield ()
    finally:
        os.system("pkill geth")


def is_up(http_endpoint):
    try:
        return requests.get(ENDPOINT).status_code == 200
    except requests.exceptions.RequestException:
        return False


def test_smoke_e2e_Zilliqa(geth_ethnode):
    contract_name = "Zilliqa"
    spec_name = "spec_02"

    metadata_file = f"specs/{contract_name}/spec/{spec_name}.json"
    spec_file = f"specs/{contract_name}/spec/{spec_name}.spot"

    ofname = "verx-benchmarks/Zilliqa/main.sol"

    with open(ofname, "r") as f, \
         open(metadata_file) as fm, \
         open(spec_file) as fs, \
         tempfile.NamedTemporaryFile(mode="w", delete=False) as ftemp:

        md = json.load(fm)
        spec = fs.read()
        contract = f.read()

        s = instrumentor.instrument(md, spec, contract, for_fuzzer=True)
        ftemp.write(s)
        ifname = ftemp.name

    w3 = node_setup.web3_geth_setup()

    original_contracts = node_setup.compile_contracts(w3, ofname)
    instrum_contracts = node_setup.compile_contracts(w3, ifname)

    (constructedZ, ) = node_setup.constructZilliqaToken(w3, original_contracts)

    tx_hash = constructedZ.functions.burn(50).transact()
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    (constructedZ, ) = node_setup.constructZilliqaToken(
        w3, instrum_contracts, True)

    tx_hash = constructedZ.functions.burn(50).transact()
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    os.system(f"rm {ifname}")
