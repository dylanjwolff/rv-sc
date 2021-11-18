# Runtime Verification of Smart Contracts
[![main Actions Status](https://github.com/dylanjwolff/rv-sc/workflows/main/badge.svg)](https://github.com/dylanjwolff/rv-sc/actions)

A tool for multi-contract runtime/testtime verification

## Building
This project has a large number of dependencies from disparate sources.
The easiest way to build and use the project is with Docker.
First **initialize the submodule for VerX benchmarks**:

 `git submodule update --init --recursive`

Then you can use e.g.:
```
docker build . -t rvsc:latest
docker run -it rvsc:latest /bin/bash
```

The build process takes several minutes (up to 20), mostly from building Spot from source.

If you don't want to build the image from scratch, it should be available on Docker Hub:
```
docker pull wolffdy/rvsc
```

Otherwise, you can follow along the steps in the Dockerfile locally to install yourself. 

### Dependency Notes

Not necessary for the Docker Container, but maybe helpful for a local build.

#### Spot

This tool uses Spot to generate automata from LTL formulas.
I've observed the website and repository for Spot to be down with quite some frequency in early October '21.
As such, I've included a tarball with v2.9.8 of Spot in this repository directly to avoid sporadic CI issues.
I was only able to get this working by building and installing it manually (see Dockerfile for steps).

#### Geth

Installed via the Ubuntu package manager

#### Solc

Installed with Solcx automatically by our tool on invocation (can be done manually with e.g. `python3 rvsc/solc_vm.py 0.4.26`).
Echidna expects `solc` to be on path, so you'll need to symbolically link to `~/solcx/----` as well for that.

I observed a bug on one of my machines that prevented Echidna from fuzzing contracts that compiled with warnings.
If this occurs, you can use something like the wrapper script in the base directory as your Solc installation.

#### Echidna

I used the latest Linux static binary release 1.7.2, available on Github (see Dockerfile)

#### VerX Benchmarks

Initially the plan had been to do hybrid verification on these benchmarks with VerX, but since that tool is no longer available we pivoted to using the SmartBugs repository instead.
Still, one of the tests depends on a contract from this repository, so make sure you initialize that submodule with `git submodule update --init --recursive`

#### Python / Pip

This has been tested using Python 3.9.7. 
All Python related dependencies can be installed from the `requirements.txt` file except for libspot.
I was only able to get libspot working manually (see Dockerfile).

## Usage

### Instrumentation
The tool itself is a Python library in the rvsc directory, but can be used to instrument contracts with:
```python3 main.py```
from the base directory of this repository.
This CLI has a `--help` option with documentation.
There are several sample contracts in the `sample-contracts` directory and specifications for those contracts in `specs`.

For example you could do:
```
python3 main.py -s specs/lotto/prev.spot -m specs/lotto/prev.json -f -i sample-contracts/lotto.sol
```
To instrument the `lotto.sol` sample contract.

### Fuzzing

The Docker container also comes with a fuzzer, Echidna, that can be used to find violations of specifications in contracts.
Echidna requires that the contact under test be extended with a special test-harness contract to find bugs.
We've provided several harnesses for each of our examples alongside the specifications for the contract within the `specs` directory.
You can append the test harness to the instrumented contract output by our tool with e.g.:
```cat specs/lotto/harness.sol >> out.sol```
Here `out.sol` is the name of your instrumented contract.

Alternatively, the instrumented contracts in `example-instrumented` should already have these harnesses and can fuzzed directly with no modifications.
To fuzz a contract run e.g.:
```echidna-test --contract TestLotto example-instrumented/lotto-i.sol```
Here TestLotto is the name of the test harness contract, which can be found by looking in the Solidity file of the harnessed and instrumented contract.

### Experiments

The code for running the experiments discussed in our presentation and report is in the `experiments` directory.
The data from these experiments lives there as well.
You can theoretically run the experiments in the Docker container with 
```python3 experiments/runner.py```
, but the plots won't work because it's running in a Docker container, and the data for the throughput experiment will be output in LaTeX table format, which is not very readable.
The data for the MTTF experiment was gathered by hand due to Echidna having a mandatory, costly test-case reduction step that would otherwise greatly inflate the timings.
This data is in a CSV file in the experiments directory.
By default the experiment runner will pick up the data from the `.pkl` files rather than regenerating the data, so to run them fully again just delete those files (this may take several minutes).
