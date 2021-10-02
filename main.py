import sys
import pprint

from solidity_parser import parser

SourceUnit = parser.parse_file(sys.argv[1])
pprint.pprint(SourceUnit)
