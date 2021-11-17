from os import path
import subprocess as sp
import os.path
import re
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.style as style
import time
from os import listdir


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


TEST_NAME_RE = re.compile(r"contract\s+(Test\S+)")


def get_test_name_from_file(path):
    f = open(path)
    s = f.read()
    o = re.search(TEST_NAME_RE, s)
    test_name = o.group(1)
    return test_name


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

# plt.show()

sns.catplot(
    x="function",  # x variable name
    y="gas",  # y variable name
    hue="file",  # group variable name
    data=dfg,  # dataframe to plot
    kind="bar")

# plt.show()

base_path = "experiments/dummy-instrumented/"
files = os.listdir(base_path)
files = [base_path + f for f in files if os.path.isfile(base_path + f)]

contracts_files = [(get_test_name_from_file(f), f) for f in files]

path_dummy_t = "experiments/dummy_times_casino.pkl"
if os.path.isfile(path_dummy_t):
    times = pd.read_pickle(path_dummy_t)
else:
    (_, times) = gather_data(contracts_files, 30, num_tests=1000)
    times.to_pickle(path_dummy_t)

tput = 1000 / times
print(tput.index.levels[0])

desc = tput.groupby("file").describe()
for c in desc.columns:
    if not ("mean" in c[1] or "std" in c[1]):
        desc = desc.drop(c, axis=1)
tput = desc.stack()
print(tput.round(2).to_latex())
