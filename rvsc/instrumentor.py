from solidity_parser import parser
from enum import Enum
from collections import defaultdict


class Unimplemented(Exception):
    pass


class FixRets:
    def __init__(self, source_lines):
        self.source_lines = source_lines

    def visitBlock(self, n: parser.Node):
        for i, stmt in enumerate(n.statements):
            if stmt == None:
                continue
            if "return" in self.source_lines[stmt.loc["start"]["line"] - 1]:
                n.statements[i] = parser.Node(ctx=CtxStub(stmt.loc))
                n.statements[i].type = "ReturnStatement"
                n.statements[i].expression = stmt


class CtxStub:
    def __init__(self, loc):
        self.start = CtxSubStub(loc["start"])
        self.stop = CtxSubStub(loc["end"])


class CtxSubStub:
    def __init__(self, sub_loc):
        self.line = sub_loc["line"]
        self.column = sub_loc["column"]


def create_ctx(loc):
    ctx = parser.ParserRuleContext()
    ctx.start.line


class SourceInstrumentor:
    def __init__(self, source_lines):
        self.source_lines = [[l] for l in source_lines]

    def visitFunctionDefinition(self, n: parser.Node):
        sc = FindStateChanges()
        parser.visit(n, sc)

        for line, val in sc.observed.items():
            self.source_lines[line].extend(val)

        if len(n.body) > 0:
            for line in fn_exits(n):
                self.source_lines[line].append("EXIT\n")

    def instrumented(self):
        s = ""
        for line in self.source_lines:
            for sub_line in line:
                if sub_line == None:
                    continue
                s += sub_line
        return s


def fn_exits(fn: parser.Node):
    assert len(fn.body) > 0, "Exits only implemented for functions with bodies"
    exits = [fn.body.statements[-1].loc["end"]["line"] - 1]
    for stmt in fn.body.statements[0:-1]:
        if stmt.type == "ReturnStatement":
            exits.append(stmt.loc["end"]["line"] - 1)
    return exits


def first_line(fn: parser.Node):
    assert len(fn.body) > 0, "1st line only impltd for functions with bodies"
    return fn.body.statements[0].loc["start"]["line"] - 1


class FindStateChanges:
    def __init__(
        self,
        observables={
            "owner": ["Burn(owner, _value)\n"],
            "balances": ["balances[_to]\n"],
            "FUNCTION_START": ["balances[msg.sender]\n"],
            "FUNCTION_NAME": None
        }):
        self.observed = defaultdict(lambda: [], {})
        self.observables = observables

    def visitFunctionDefinition(self, n: parser.Node):
        if len(n.body) == 0:
            return
        if n.isConstructor:
            fname = "CONSTRUCTOR\n"
        elif n.name:
            fname = n.name + "\n"
        else:
            fname = "FALLBACK\n"
        self.observed[first_line(n) - 1].append(f"FNAME={fname}")
        self.observed[first_line(n) - 1].extend(
            self.observables["FUNCTION_START"])

    def visitBinaryOperation(self, n: parser.Node):
        if n.operator == '=':
            if n.left.type == "Identifier":
                if n.left.name in self.observables.keys():
                    self.observed[n.loc["end"]["line"] -
                                  1] = self.observables[n.left.name]
                pass
            elif n.left.type == "IndexAccess":
                x = n.left
                while x.type == "IndexAccess":
                    x = x.base

                if x.name in self.observables.keys():
                    self.observed[x.loc["end"]["line"] -
                                  1] = self.observables[x.name]
            else:
                raise Unimplemented("Unknown Assignment LHS")


fname = "verx-benchmarks/Zilliqa/main.sol"
ast = parser.parse_file(fname, loc=True)

with open(fname, "r") as f:
    lines = f.readlines()
    p = SourceInstrumentor(lines)
    m = FindStateChanges()
    r = FixRets(lines)
    parser.visit(ast, r)
    parser.visit(ast, p)
    # parser.visit(ast, m)
    # print(m.observed)
    print(p.instrumented())
