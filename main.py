import sys
import pprint

from solidity_parser import parser


class V:
    def visitPragmaDirective(self, n: parser.Node):
        print("Example Visitor: " + str(n))


ast = parser.parse_file(sys.argv[1])
# pprint.pprint(ast)
parser.visit(ast, V())