"""Tools for working with the SPOT library output
"""
from lark import Lark
from lark import Transformer
import lark

## Grammar below copied from https://github.com/adl/hoaf/
# label-expr ::= BOOLEAN | INT | ANAME | "!" label-expr
#              | "(" label-expr ")"
#              | label-expr "&" label-expr
#              | label-expr "|" label-expr

# body             ::= (state-name edge*)*
# state-name       ::= "State:" label? INT STRING? acc-sig?
# acc-sig          ::= "{" INT* "}"
# edge             ::= label? state-conj acc-sig?
# label            ::= "[" label-expr "]"

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
                start="body")


class Edge:
    """An edge in the automaton
    """
    def __init__(self, a, b, c):
        self.cond = a
        self.dest = b
        self.accsig = c

    def __str__(self):
        return f"Edge({self.cond}, {self.dest}, {self.accsig})"

    def __repr__(self):
        return "Edge()"


class MyTransformer(Transformer):
    """A Lark transformer for the AST of SPOT's output
    """
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


class Unreachable(Exception):
    pass


def ltl_to_ba_ast(ltl_str):
    """Parses the SPOT library output

    Args:
        ltl_str (str): output from the SPOT library

    Returns:
        the transformed AST of the automaton
    """
    body_str = ltl_str.split("--BODY--")[-1].split("--END--")[0]

    ptree = leparser.parse(body_str)

    tformed = MyTransformer().transform(ptree)

    return tformed


def var_mapping(ltl_str):
    """Extracts the mapping of variables to variable ID's in the SPOT output

    Args:
        ltl_str (str): output from the SPOT library

    Returns:
        mapping (dict): a mapping of variable names to IDs
    """
    ap = ltl_str.split("AP:")[1].split("\n", 1)[0]
    ap = ap.replace('"', "")
    varnames = ap.split()[1:]
    mapping = {}
    for ind, var in enumerate(varnames):
        mapping[var] = ind
    return mapping


def start_state(ltl_str):
    """Extracts the starting state of the automaton in the SPOT library output

    Args:
        ltl_str (str): the SPOT library output

    Returns:
        start (int): the starting state ID
    """
    start = ltl_str.split("Start:")[1].split("\n", 1)[0]
    start = start.strip()
    return int(start)


def pretty_print_ba_exp(e: lark.Tree):
    """Recursively pretty-prints a Buchi automaton expression in Solidity

    Args:
        e (lark.Tree): the transformed AST of the parser SPOT library output

    Raises:
        Unreachable: if an unknown expression is in the AST

    Returns:
        s (str): the resulting string Solidity expression
    """
    s = ""
    if e.data == "bool":
        (b, ) = e.children
        s += "true" if b == "t" else "false"
        return s
    elif e.data == "var":
        (n, ) = e.children
        s += f"vars[{n}]"
        return s
    elif e.data == "not":
        s += f"!{pretty_print_ba_exp(e.children[0])}"
        return s
    elif e.data == "paren":
        mid = pretty_print_ba_exp(e.children[0])
        s += f"{s} ({mid})"
        return s
    elif e.data == "and":
        left = pretty_print_ba_exp(e.children[0])
        right = pretty_print_ba_exp(e.children[1])
        s += f"{left} && {right}"
        return s
    elif e.data == "or":
        left = pretty_print_ba_exp(e.children[0])
        right = pretty_print_ba_exp(e.children[1])
        s += f"{left} || {right}"
        return s
    else:
        raise Unreachable("Switch case exhausted!")


def pretty_print_ba_ast(
    ba_ast,
    failure_case='revert("Invalid Buchi State");',
):
    """Pretty prints the Buchi automaton as a series of if-else conditions in Solidity

    Args:
        ba_ast (lark.Tree): the transformed parsed SPOT library output
        failure_case (str, optional): What to do if a specification is violated.
            Defaults to 'revert("Invalid Buchi State");'.

    Raises:
        Unreachable: Edges of the automaton should always have conditions

    Returns:
        str: the Solidity code
    """
    pretty_s = ""
    for state in ba_ast:
        pretty_s += f"\nif (state == {state[0].children[0]}) {{"
        for edge in state[1]:
            if edge.cond is None:
                raise Unreachable("No edge condition!")
            if edge == state[1][0]:
                pretty_s += f"\n\tif ({pretty_print_ba_exp(edge.cond[0])}) {{"
            else:
                pretty_s += f"\n\t}} else if ({pretty_print_ba_exp(edge.cond[0])}) {{"
            pretty_s += f"\n\t\tstate = {edge.dest.children[0]};"
        if len(state[1]) > 0:
            pretty_s += f"\n\t}} else {{\n\t\t{failure_case}\n\t}}"
        pretty_s += "\n\treturn;"
        pretty_s += "\n}"

    return pretty_s
