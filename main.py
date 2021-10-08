from os import name
import spot
import sys
import pprint
from parsec import *

from solidity_parser import parser


class V:
    def visitBinaryOperation(self, n: parser.Node):
        if n.operator == '=':
            pass
            # pprint.pprint(n.left)


ast = parser.parse_file(sys.argv[1])
# pprint.pprint(ast)
parser.visit(ast, V())

print(spot.version())
g: spot.twa_graph = spot.translate('!F(red & X(yellow))', 'monitor', 'det')
g_str = g.to_str()

from lark import Lark

leparser = Lark(r"""
    labelexpr:    bool 
                | SIGNED_INT -> var
                | "!" labelexpr  -> not
                | "(" labelexpr ")" -> paren
                | labelexpr "&" labelexpr -> and
                | labelexpr "|" labelexpr -> or

    bool: "t" | "f"
    
    body: state*
    state: statename edge*
    
    statename: "State:" label? SIGNED_INT ESCAPED_STRING? accsig?

    accsig: "{" SIGNED_INT* "}"
    edge: label? stateconj accsig?
    label: "[" labelexpr "]"
    stateconj: SIGNED_INT | stateconj "&" SIGNED_INT 

    %import common.ESCAPED_STRING
    %import common.SIGNED_INT
    %import common.WS
    %ignore WS
    """,
                start='body')
body_str = g_str.split("--BODY--")[-1].split("--END--")[0]
print(body_str)
ptree = leparser.parse(body_str)
print(ptree.pretty())

from lark import Transformer


class Edge:
    def __init__(a, b, c):
        self.cond = a
        self.dest = b
        self.accsig = c


import lark


class MyTransformer(Transformer):
    def state(self, name_edge):
        n = name_edge[0]
        e = name_edge[1:]
        return n, e

    def body(self, b):
        return list(b)

    def edge(self, e: lark.Tree):
        if e[0].data == "label":
            print("LAV")
        return e


tformed = MyTransformer().transform(ptree)
print(tformed)


def pretty_exp(e: lark.Tree):
    print(e)


pretty_s = ""
for state in tformed:
    pretty_s += "\nif " + str(state[0]) + ":"
    for edge in state[1]:
        pretty_exp(edge)

print(pretty_s)

# label-expr ::= BOOLEAN | INT | ANAME | "!" label-expr
#              | "(" label-expr ")"
#              | label-expr "&" label-expr
#              | label-expr "|" label-expr

# body             ::= (state-name edge*)*
# state-name       ::= "State:" label? INT STRING? acc-sig?
# acc-sig          ::= "{" INT* "}"
# edge             ::= label? state-conj acc-sig?
# label            ::= "[" label-expr "]"