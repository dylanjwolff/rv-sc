from os import path
import subprocess as sp
import os.path
import re
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


def single_trial(contract_name,
                 contract_file,
                 num_tests=200,
                 df=pd.DataFrame()):
    o = sp.run(
        f"echidna-test --contract {contract_name} {contract_file} --test-limit {num_tests} --config <(echo \"estimateGas: true\") --format text",
        shell=True,
        executable="/bin/bash",
        capture_output=True)

    lines_with_max = [
        line.decode("utf-8") for line in o.stdout.splitlines()
        if "maximum" in str(line)
    ]

    max_parse = re.compile(r"(\S+) used a maximum of (\d+) gas")

    mapping = {}
    for line in lines_with_max:
        o = re.search(max_parse, line)
        fn_name = o.group(1)
        gas = int(o.group(2))
        if fn_name != "initialize":
            mapping[fn_name] = gas
    df = df.append(mapping, ignore_index=True)
    return df


def multi_trial(contract_name,
                contract_file,
                num_trials,
                num_tests=200,
                df=pd.DataFrame()):
    for i in range(0, num_trials):
        df = single_trial(contract_name, contract_file, num_tests, df)
    return df


def gather_data(contracts_files, trials, num_tests=2000):
    data = []
    filenames = []
    for contract_name, contract_file in contracts_files:
        data.append(
            multi_trial(contract_name, contract_file, trials, num_tests))
        filenames.append(contract_file)

    df = pd.concat(data, keys=filenames, names=["file", "trial"], join="inner")
    df.columns.name = "function"

    return df


contract_name = "TestCasino"
base_contract_file = "experiments/casino/casino-baseline.sol"
larva_contract_file = "experiments/casino/casino-larva.sol"
buchi_contract_file = "experiments/casino/casino-buchi.sol"

contracts_files = zip(
    [contract_name] * 3,
    [base_contract_file, larva_contract_file, buchi_contract_file])

path = "experiments/gas_casino.pkl"
if os.path.isfile(path):
    df = pd.read_pickle(path)
else:
    df = gather_data(contracts_files, 2)
    df.to_pickle(path)
df = df.drop("timeoutBet", axis=1)
df = df.stack()
df.name = "gas"
df = df.reset_index()

sns.catplot(
    x="function",  # x variable name 
    y="gas",  # y variable name
    hue="file",  # group variable name
    data=df,  # dataframe to plot
    kind="bar")

plt.show()