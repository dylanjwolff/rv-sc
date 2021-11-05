import subprocess as sp
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


contract_name = "TestEscrow"
contract_file = "scratch/escrow-i.sol"
df = multi_trial(contract_name, contract_file, 2)

b_contract_name = "TestEscrow"
b_contract_file = "scratch/escrow-baseline.sol"
b_df = multi_trial(b_contract_name, b_contract_file, 2)

df = pd.concat([df, b_df],
               keys=[contract_file, b_contract_file],
               names=["file", "trial"])
df.columns.name = "function"

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