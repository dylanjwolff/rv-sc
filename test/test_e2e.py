from rvsc import instrumentor
from rvsc import ltl_tools
import json
import tempfile
from rvsc import experiments


def test_smoke_e2e_Zilliqa():
    contract_name = "Zilliqa"
    spec_name = "spec_02"

    metadata_file = f"specs/{contract_name}/spec/{spec_name}.json"
    spec_file = f"specs/{contract_name}/spec/{spec_name}.spot"

    ofname = "verx-benchmarks/Zilliqa/main.sol"

    with open(ofname, "r") as f, \
         open(metadata_file) as fm, \
         open(spec_file) as fs, \
         tempfile.NamedTemporaryFile(mode="w") as ftemp:

        md = json.load(fm)
        spec = fs.read()
        contract = f.read()

        s = instrumentor.instrument(md, spec, contract)
        ftemp.write(s)
        ifname = ftemp.name

    w3 = experiments.web3_setup()

    original_contracts = experiments.compile_contracts(w3, ofname)
    instrum_contracts = experiments.compile_contracts(w3, ifname)

    (constructedZ, ) = experiments.constructZilliqaToken(
        w3, original_contracts)

    tx_hash = constructedZ.functions.burn(50).transact()
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    (constructedZ, ) = experiments.constructZilliqaToken(
        w3, instrum_contracts, True)

    tx_hash = constructedZ.functions.burn(50).transact()
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
