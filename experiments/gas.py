from os import path
import subprocess as sp
import os.path
import re
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.style as style
import time


def single_trial(contract_name,
                 contract_file,
                 num_tests=200,
                 dfg=pd.DataFrame(),
                 dft=pd.DataFrame()):
    start = time.time()
    o = sp.run(
        f"echidna-test --contract {contract_name} {contract_file} --test-limit {num_tests} --config <(echo \"estimateGas: true\") --format text",
        shell=True,
        executable="/bin/bash",
        capture_output=True)
    end = time.time()

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
    dfg = dfg.append(mapping, ignore_index=True)
    dft = dft.append({"time (s)": end - start}, ignore_index=True)
    return (dfg, dft)


def multi_trial(contract_name,
                contract_file,
                num_trials,
                num_tests=200,
                dfg=pd.DataFrame(),
                dft=pd.DataFrame()):
    for i in range(0, num_trials):
        (dfg, dft) = single_trial(contract_name, contract_file, num_tests, dfg,
                                  dft)
    return (dfg, dft)


def gather_data(contracts_files, trials, num_tests=200):
    data_g = []
    data_t = []
    filenames = []
    for contract_name, contract_file in contracts_files:
        dfg, dft = multi_trial(contract_name, contract_file, trials, num_tests)
        data_g.append(dfg)
        data_t.append(dft)
        filenames.append(contract_file)

    dfg = pd.concat(data_g,
                    keys=filenames,
                    names=["file", "trial"],
                    join="inner")
    dfg.columns.name = "function"

    dft = pd.concat(data_t,
                    keys=filenames,
                    names=["file", "trial"],
                    join="inner")

    return (dfg, dft)


contract_name = "TestCasino"
base_contract_file = "experiments/casino/casino-baseline.sol"
larva_contract_file = "experiments/casino/casino-larva.sol"
buchi_contract_file = "experiments/casino/casino-buchi.sol"

contracts_files = zip(
    [contract_name] * 3,
    [base_contract_file, larva_contract_file, buchi_contract_file])

path_g = "experiments/gas_casino.pkl"
path_t = "experiments/time_casino.pkl"
if os.path.isfile(path_g) and os.path.isfile(path_t):
    dfg = pd.read_pickle(path_g)
    dft = pd.read_pickle(path_t)
else:
    (dfg, dft) = gather_data(contracts_files, 30)
    dfg.to_pickle(path_g)
    dft.to_pickle(path_t)
dfg = dfg.drop("timeoutBet", axis=1)
dfg = dfg.stack()
dfg.name = "gas"
dfg = dfg.reset_index()

dft = dft.reset_index()

# style.use('seaborn-poster')  #sets the size of the charts
style.use('ggplot')

sns.catplot(
    x="file",  # x variable name
    y="time (s)",  # y variable name
    data=dft,  # dataframe to plot
    kind="bar")

plt.show()

sns.catplot(
    x="function",  # x variable name
    y="gas",  # y variable name
    hue="file",  # group variable name
    data=dfg,  # dataframe to plot
    kind="bar")

plt.show()