# Runtime Verification of Smart Contracts
[![main Actions Status](https://github.com/dylanjwolff/rv-sc/workflows/main/badge.svg)](https://github.com/dylanjwolff/rv-sc/actions)

## Building
The easiest way to build the project is with docker.
You can use e.g.:
```
docker build . -t rvsc:latest
docker run -it rvsc:latest /bin/bash
```

Otherwise, you can follow along the steps in the Dockerfile locally to install yourself.

## Parity / OpenEthereum

Use `cargo +1.51.0 build --release --features final` to build... There seems to be a bug uncovered by the most recent stable release of `rustc`.

## Spot

This tool uses Spot to generate automata from LTL formulas.
I've observed the website and repository for Spot to be down with quite some frequency in early October '21.
As such, I've included a tarball with v2.9.8 of Spot in this repository directly to avoid sporadic CI issues.
