from os import name
import spot
import sys
import pprint
import argparse
import json
import os
import sys

file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)

from rvsc import instrumentor

parser = argparse.ArgumentParser(description="Instrument a contract")

parser.add_argument('-s',
                    '--spec',
                    required=True,
                    type=str,
                    nargs=1,
                    help='.SPOT spec file')
parser.add_argument('-m',
                    '--metadata',
                    required=True,
                    type=str,
                    nargs=1,
                    help='.JSON metadata file for spec')
parser.add_argument('-i',
                    '--infile',
                    required=True,
                    type=str,
                    nargs=1,
                    help='input contract .SOL file')
parser.add_argument('-o',
                    '--outfile',
                    type=str,
                    nargs=1,
                    help='output file',
                    default=["out.sol"])

args = parser.parse_args()
print(args)

with open(args.infile[0]) as f, \
     open(args.metadata[0]) as fm, \
     open(args.spec[0]) as fs, \
     open(args.outfile[0], "w") as fo:

    md = json.load(fm)
    spec = fs.read()
    contract = f.read()

    s = instrumentor.instrument(md, spec, contract)
    fo.write(s)
