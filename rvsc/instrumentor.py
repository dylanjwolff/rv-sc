from solidity_parser import parser
from enum import Enum
from collections import defaultdict
import json
import ltl_tools
import spot
import solidity_ast_tools


class Unimplemented(Exception):
    pass


class SplitRets:
    def __init__(self, source_lines, contracts):
        self.source_lines = [[l] for l in source_lines]
        self.f_rets = []
        self.contracts = contracts
        self.contract = None

    def visitContractDefinition(self, n: parser.Node):
        self.contract = n.name

    def visitFunctionDefinition(self, n: parser.Node):
        if self.contract not in self.contracts:
            return
        if n.returnParameters:
            self.f_rets = [
                p.typeName.name for p in n.returnParameters.parameters
            ]
            if len(self.f_rets) > 1:
                raise Unimplemented("multiple ret types not supported!")
        else:
            self.f_rets = []

    def visitReturnStatement(self, n: parser.Node):
        if self.contract not in self.contracts:
            return

        if not n.loc["end"]["line"] == n.loc["start"]["line"]:
            raise Unimplemented("multi-line ret!")

        source_line_index = n.loc["start"]["line"] - 1

        pp = solidity_ast_tools.SourcePrettyPrinter([])
        pp.visit(n.expression)
        ret_exp = pp.out_s

        temp_var_decls = []
        temp_vars = []
        for i, ret_t in enumerate(self.f_rets):
            tv = f"temp_ret_instrum_{i}"
            temp_var_decls += [f"{ret_t} {tv} = {ret_exp};\n"]
            temp_vars += [tv]
        ret_stmt = f'return {", ".join(temp_vars)};\n'
        self.source_lines[source_line_index] = temp_var_decls + [ret_stmt]

    def instrumented(self):
        s = ""
        for line in self.source_lines:
            for sub_line in line:
                if sub_line == None:
                    continue
                s += sub_line
        return s


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
    def __init__(
        self,
        source_lines,
        updaters={
            "ZilliqaToken": {
                "balances": [(0, "balances==TURKEY")],
                "owner": [(1, "owner==CHICKEN")],
                "FUNCTION": [(2, 'FUNCTION == "transfer"')]
            }
        }):
        self.updaters = updaters
        self.source_lines = [[l] for l in source_lines]
        self.source_lines[-1].extend(pprint_checker())
        self.contract_name = None

    def visitContractDefinition(self, n: parser.Node):
        self.contract_name = n.name
        if not self.contract_name in self.updaters.keys():
            return
        if len(n.subNodes) == 0:
            raise ValueError("body-less contract")
        first = n.subNodes[0].loc["start"]["line"] - 1
        self.source_lines[first] = ["address buchi_checker_address;\n"
                                    ] + self.source_lines[first]
        last = n.subNodes[-1].loc["end"]["line"] - 1
        self.source_lines[last].extend(INITIALIZE_CLIENT)

    def visitFunctionDefinition(self, n: parser.Node):
        if not self.contract_name in self.updaters.keys():
            return
        if n.isConstructor:
            return
        sc = FindStateChanges(self.updaters[self.contract_name].keys())
        parser.visit(n, sc)

        fn_name = get_fn_name(n)
        if len(n.body) > 0:
            self.source_lines[first_line(n) - 1].extend(HEADER)
            for update in self.updaters[self.contract_name]["FUNCTION"]:
                self.source_lines[first_line(n) - 1].extend(
                    pprint_update(update, fn_name))

        for line, val in sc.observed.items():
            for update in self.updaters[self.contract_name][val]:
                self.source_lines[line].extend(pprint_update(update))

        if len(n.body) > 0:
            for line, is_ret in fn_exits(n):
                if is_ret:
                    self.source_lines[line] = [FOOTER
                                               ] + self.source_lines[line]
                else:
                    self.source_lines[line].append(FOOTER)

    def instrumented(self):
        s = ""
        for line in self.source_lines:
            for sub_line in line:
                if sub_line == None:
                    continue
                s += sub_line
        return s


INITIALIZE_CLIENT = """function initialize(address a) {
        if (address(buchi_checker_address) == address(0)) {
            buchi_checker_address = a;
        }
}
    """
FOOTER = f"bc.apply_updates();\nbc.check();\n"
HEADER = f"BuchiChecker bc = BuchiChecker(buchi_checker_address);\n"


def pprint_checker():
    return """
\n\ncontract BuchiChecker {
        uint256 state;
        uint32[] updates_k;
        bool[] updates_v;
        mapping(uint32 => bool) vars;

        constructor() {
                state = 0;
        }

        function update(uint32 k, bool v) {
                updates_k.push(k);
                updates_v.push(v);
        }

        function apply_updates() {
                while (updates_v.length > 0) {
                        uint32 k = updates_k[updates_k.length-1];
                        updates_k.length--;

                        bool v = updates_v[updates_v.length-1];
                        updates_v.length--;

                        vars[k] = v;
                }
        }

        function sum(uint32[] n) returns (uint32) {
            return 0;
        }

        function check() {
               {CHECK_SWITCH_CASE} 
        }
}
    """


def get_fn_name(fn: parser.Node):
    if len(fn.body) == 0:
        return
    if fn.isConstructor:
        fname = '"CONSTRUCTOR"'
    elif fn.name:
        fname = f'"{fn.name}"'
    else:
        fname = '"FALLBACK"'
    return fname


def fn_exits(fn: parser.Node):
    assert len(fn.body) > 0, "Exits only implemented for functions with bodies"
    if fn.body.statements[-1].type == "ReturnStatement":
        isRet = True
    else:
        isRet = False
    exits = [(fn.body.statements[-1].loc["end"]["line"] - 1, isRet)]
    for stmt in fn.body.statements[0:-1]:
        if stmt.type == "ReturnStatement":
            exits.append((stmt.loc["end"]["line"] - 1, True))
    return exits


def first_line(fn: parser.Node):
    assert len(fn.body) > 0, "1st line only impltd for functions with bodies"
    return fn.body.statements[0].loc["start"]["line"] - 1


class FindStateChanges:
    def __init__(self,
                 observables=[
                     "owner", "balances", "FUNCTION_START", "FUNCTION_NAME"
                 ]):
        self.observed = defaultdict(lambda: [], {})
        self.observables = observables

    def visitBinaryOperation(self, n: parser.Node):
        if n.operator == '=':
            if n.left.type == "Identifier":
                if n.left.name in self.observables:
                    self.observed[n.loc["end"]["line"] - 1] = n.left.name
                pass
            elif n.left.type == "IndexAccess":
                x = n.left
                while x.type == "IndexAccess":
                    x = x.base

                if x.name in self.observables:
                    self.observed[x.loc["end"]["line"] - 1] = x.name
            else:
                raise Unimplemented("Unknown Assignment LHS")


def to_flat_update(md_json):
    mc = defaultdict(lambda: defaultdict(lambda: [], {}), {})
    for i, var in enumerate(md_json):
        for k in var["triggers"]:
            contract, trigger = k.split(".")
            mc[contract][trigger] += [(i, var["condition"])]
    return mc


def pprint_update(u, fn_name=None):
    s = f"bc.update({u[0]}, ({u[1]}));\n"
    # s = s.replace("SUM", "bc.sum")
    if "SUM" in s:
        s = f"bc.update({u[0]}, (true));\n"

    if fn_name:
        s = s.replace("FUNCTION", fn_name)

    return s


contract_name = "Zilliqa"
spec_name = "spec_02"

metadata_file = f"specs/{contract_name}/spec/{spec_name}.json"
spec_file = f"specs/{contract_name}/spec/{spec_name}.spot"

fname = "verx-benchmarks/Zilliqa/main.sol"
ast = parser.parse_file(fname, loc=True)

with open(fname, "r") as f, \
     open(metadata_file) as fm, \
     open(spec_file) as fs:
    md = json.load(fm)
    spot_form = spot \
        .translate(fs.read(), 'monitor', 'det').to_str()
    ltl_ast = ltl_tools.ltl_to_ba_ast(spot_form)
    ltl_switch_case = ltl_tools.pretty_print_ba_ast(ltl_ast)

    md = to_flat_update(md)
    print(md)

    lines = f.readlines()
    # m = FindStateChanges()
    r = FixRets(lines)
    sr = SplitRets(lines, md.keys())
    parser.visit(ast, r)
    parser.visit(ast, sr)
    split_src = sr.instrumented()
    lines = split_src.splitlines(keepends=True)

    ast = parser.parse(split_src, loc=True)
    r = FixRets(lines)
    p = SourceInstrumentor(lines, md)
    parser.visit(ast, r)
    parser.visit(ast, p)
    # parser.visit(ast, m)
    # print(m.observed)
    s = p.instrumented()
    s = s.replace("{CHECK_SWITCH_CASE}", ltl_switch_case)

    with open("out.sol", "w") as fout:
        fout.write(s)
        # print(s)
        pass
