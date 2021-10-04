import sys
import pprint

from solidity_parser import parser


class V:
    def visitBinaryOperation(self, n: parser.Node):
        if n.operator == '=':
            print("Example Visitor: " + str(n))


ast = parser.parse_file(sys.argv[1])
# pprint.pprint(ast)
parser.visit(ast, V())