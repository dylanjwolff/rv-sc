from os import name
import spot
import sys
import pprint
from ltl_tools import ltl_to_ba_ast, pretty_print_ba_ast

from solidity_parser import parser


class V:
    def visitBinaryOperation(self, n: parser.Node):
        if n.operator == '=':
            pass
            # pprint.pprint(n.left)


ast = parser.parse_file(sys.argv[1])
# pprint.pprint(ast)
parser.visit(ast, V())
