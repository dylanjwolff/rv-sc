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

from lark import Transformer


class Edge:
    def __init__(self, a, b, c):
        self.cond = a
        self.dest = b
        self.accsig = c

    def __str__(self):
        return f"Edge({self.cond}, {self.dest}, {self.accsig})"

    def __repr__(self):
        return "Edge()"


import lark


class MyTransformer(Transformer):
    def state(self, name_edge):
        n = name_edge[0]
        e = name_edge[1:]
        return n, e

    def body(self, b):
        return list(b)

    def edge(self, e: lark.Tree):
        cond = e[0].children if e[0].data == "label" else None
        dest = e[1] if e[0].data == "label" else e[0]
        accsig = e[-1] if e[-1].data == "accsig" else None

        return Edge(cond, dest, accsig)


tformed = MyTransformer().transform(ptree)


def pretty_exp(e: lark.Tree):
    s = ""
    if e.data == "bool":
        (b, ) = e.children
        s += "TRUE" if b == "t" else "FALSE"
        return s
    elif e.data == "var":
        (n, ) = e.children
        s += f"v{n}"
        return s
    elif e.data == "not":
        s += f'!{pretty_exp(e.children[0])}'
        return s
    elif e.data == "paren":
        mid = pretty_exp(e.children[0])
        s += f"{s} ({mid})"
        return s
    elif e.data == "and":
        left = pretty_exp(e.children[0])
        right = pretty_exp(e.children[1])
        s += f"{left} and {right}"
        return s
    elif e.data == "or":
        left = pretty_exp(e.children[0])
        right = pretty_exp(e.children[1])
        s += f"{left} or {right}"
        return s
    else:
        raise ValueError("switch case exhausted")


pretty_s = ""
for state in tformed:
    pretty_s += f"\nif state == {state[0].children[0]}:"
    for edge in state[1]:
        if edge.cond != None:
            pretty_s += f'\n\tif {pretty_exp(edge.cond[0])}:'
        pretty_s += f"\n\t\tstate = {edge.dest.children[0]}"

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