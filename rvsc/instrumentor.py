"""
Instrumentor Module
    
This module provides various classes and functions that instrument a Solidity AST 
with various runtime checks
"""
from solidity_parser import parser
from collections import defaultdict
from . import ltl_tools
import spot
from . import solidity_ast_tools
import re


class Unimplemented(Exception):
    pass


class SplitRets:
    """Return statement splitter

    This is a "visitor" class which splits return statements into two statements.
    """
    def __init__(self, source_lines, contracts):
        self.source_lines = [[l] for l in source_lines]
        self.f_rets = []
        self.contracts = contracts
        self.contract = None

    def visitContractDefinition(self, n: parser.Node):
        self.contract = n.name

    def visitFunctionDefinition(self, n: parser.Node):
        """Records function return types

        Args:
            n (parser.Node): A function definition AST Node

        Raises:
            Unimplemented: raised for multiple return types which are not yet supported
        """
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
        """Splits the return statement
        
        Replaces the return statement in self.source_lines with a temporary variable
        taking the value of the returned expression and a separate return statement
        of that temporary variable.

        Args:
            n (parser.Node): a return statement node

        Raises:
            Unimplemented: due to issues with the third pary solidity parser, multi-line
            return statements are unsupported
        """
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
        """Gets the instrumented code with split return statements

        Returns:
            str: instrumented code
        """
        s = ""
        for line in self.source_lines:
            for sub_line in line:
                if sub_line == None:
                    continue
                s += sub_line
        return s


class FixRets:
    """Visitor that fixes a bug in the AST generated by the third-party Solidity parser
    """
    def __init__(self, source_lines):
        self.source_lines = source_lines

    def visitBlock(self, n: parser.Node):
        """Finds and repairs return statements not recognized by the parser


        Args:
            n (parser.Node): a block of Solidity code
        """

        for i, stmt in enumerate(n.statements):
            if stmt == None:
                continue
            if "return" in self.source_lines[stmt.loc["start"]["line"] - 1]:
                n.statements[i] = parser.Node(ctx=CtxStub(stmt.loc))
                n.statements[i].type = "ReturnStatement"
                n.statements[i].expression = stmt


class CtxStub:
    """A stub of the Solidity parser Ctx to allow us to create nodes
    """
    def __init__(self, loc):
        self.start = CtxSubStub(loc["start"])
        self.stop = CtxSubStub(loc["end"])


class CtxSubStub:
    """A stub of the Solidity parser Ctx start and stop to allow us to create nodes
    """
    def __init__(self, sub_loc):
        self.line = sub_loc["line"]
        self.column = sub_loc["column"]


def get_prevname(var: str):
    """Replaces problematic characters to produce a Solidity variable name
    """
    var = var.replace(".", "_")
    var = var.replace("]", "_")
    var = var.replace("[", "_")
    var = var.replace(")", "_")
    var = var.replace("(", "_")
    return f"prev___{var}"


class SourceInstrumentor:
    """Runtime property-checking instrumentator "visitor" pattern class
    """
    def __init__(self, source_lines, updaters, prevs, state_var_types):
        self.updaters = updaters
        self.source_lines = [[l] for l in source_lines]
        self.source_lines[-1].extend(pprint_checker())
        self.contract_name = None
        self.prevs = prevs
        self.state_var_types = state_var_types

    def visitContractDefinition(self, n: parser.Node):
        """Records the contract name and adds initialization for contract-level
        instrumentation variables in self.source_lines

        Args:
            n (parser.Node): a contract AST node

        Raises:
            UnimplementedError: empty contracts are not supported
        """
        self.contract_name = n.name
        if not self.contract_name in self.updaters.keys():
            return
        if len(n.subNodes) == 0:
            raise Unimplemented("body-less contract")
        first = n.subNodes[0].loc["start"]["line"] - 1
        self.source_lines[first] = ["address buchi_checker_address;\n"
                                    ] + self.source_lines[first]

        contract_types = self.state_var_types[self.contract_name]
        for _, prevs in self.prevs[self.contract_name].items():
            prev_decls = []
            for var in prevs:
                if get_prevname(var) in contract_types:
                    prev_type = contract_types[get_prevname(var)]
                else:
                    prev_type = contract_types[var]

                prev_decls.extend(f"{prev_type} {get_prevname(var)};\n")
            self.source_lines[first].extend(prev_decls)

        last = n.subNodes[-1].loc["end"]["line"] - 1
        self.source_lines[last].extend(INITIALIZE_CLIENT)

    def visitFunctionDefinition(self, n: parser.Node):
        """Instruments the function in self.source_lines
        
        Args:
            n (parser.Node): a function definition AST node
        """
        updated = []

        if not self.contract_name in self.updaters.keys():
            return
        if n.isConstructor:
            return
        sc = FindStateChanges(self.updaters[self.contract_name].keys())
        parser.visit(n, sc)

        fn_name = get_fn_name(n)
        if len(n.body) > 0:
            self.source_lines[first_line(n) - 1].extend(HEADER)

            first_instrumentations = []
            for update in self.updaters[self.contract_name]["msg.sender"]:
                updated.append("msg.sender")
                first_instrumentations.extend(pprint_update(update))

            fn_updates = []
            fn_updated = None
            for update in self.updaters[self.contract_name]["FUNCTION"]:
                if update[1] == fn_name:
                    updated.append("FUNCTION")
                    fn_updated = update
                    fn_updates.extend(pprint_update(update, fn_name))

            if len(fn_updates) > 0:
                fn_updates = ["if (bc.get_call_depth() <= 1) {\n"] + fn_updates
                fn_updates.append("}\n")
            first_instrumentations.extend(fn_updates)

        for arg in n.parameters.parameters:
            for update in self.updaters[self.contract_name][arg.name]:
                updated.append(arg.name)
                self.source_lines[first_line(n) - 1].extend(
                    pprint_update(update))

        for line, val in sc.observed.items():
            for update in self.updaters[self.contract_name][val]:
                updated.append(val)
                self.source_lines[line].extend(pprint_update(update))

        end_updaters = self.updaters[self.contract_name]["FUNCTION_END"]
        end_updates = [pprint_update(ud) for ud in end_updaters]
        if len(end_updates) > 0:
            updated.append("FUNCTION_END")

        end_updates.append(FOOTER)

        if len(fn_updates) > 0:
            end_updates.append("if (bc.get_call_depth() <= 1) {\n")
            end_updates.extend(pprint_update(
                fn_updated, fn_name, exit_fn=True))  # exit fn after check
            end_updates.append("}\n")

        end_updates.append("bc.exit();\n")

        if len(n.body) > 0:
            for line, is_ret in fn_exits(n):
                if is_ret:
                    self.source_lines[
                        line] = end_updates + self.source_lines[line]
                else:
                    self.source_lines[line].extend(end_updates)

        for trigger in set(updated):
            if trigger in self.prevs[self.contract_name].keys():
                prev_inits = [
                    f"{get_prevname(var)} = {var};\n"
                    for var in self.prevs[self.contract_name][trigger]
                ]
                self.source_lines[first_line(n) - 1].extend(prev_inits)
        self.source_lines[first_line(n) - 1].extend(first_instrumentations)

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
HEADER = f"""BuchiChecker bc = BuchiChecker(buchi_checker_address);
            address prev_bc_address = buchi_checker_address;
            bc.enter();\n""" # @TODO make optional


def pprint_checker():
    """Pretty-prints the monitoring contract
    """

    return """
\n\ncontract BuchiChecker {
        uint256 state = {INITIAL_STATE};
        uint32[] updates_k;
        bool[] updates_v;
        mapping(uint32 => bool) vars;
        bool public invalid = false;
        uint32 call_depth;
        
        function enter(){
            call_depth = call_depth + 1;
        }

        function exit(){
            call_depth = call_depth - 1;
        }
        
        function get_call_depth() returns (uint32) {
            return call_depth;
        }

        function update(uint32 k, bool v) {
                updates_k.push(k);
                updates_v.push(v);
        }

        function apply_updates() {
                if (call_depth > 1) { return; }
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
                if (call_depth > 1) { return; }
               {CHECK_SWITCH_CASE} 
        }
}
    """


def get_fn_name(fn: parser.Node):
    """Gets the name of a function definition AST node

    Args:
        fn (parser.Node): [description]

    Returns:
        [type]: [description]
    """
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
    """Finds the line numbers for each exit point in the function

    Args:
        fn (parser.Node): a function definition AST node

    Returns:
        [int]: a list of line numbers of the exit points
    """
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
    """Gives the first line of a function

    Args:
        fn (parser.Node): a function definition AST node

    Returns:
        int: a line number
    """
    assert len(fn.body) > 0, "1st line only impltd for functions with bodies"
    return fn.body.statements[0].loc["start"]["line"] - 1


class FindStateChanges:
    """Visitor to find instrumentation points in AST
    """
    def __init__(self,
                 observables=[
                     "owner", "balances", "FUNCTION_START", "FUNCTION_NAME"
                 ]):
        self.observed = defaultdict(lambda: [], {})
        self.observables = observables

    def visitVariableDeclarationStatement(self, n: parser.Node):
        """Notes initialized variable declarations of triggering variables

        Args:
            n (parser.Node): variable declaration AST node

        Raises:
            Unimplemented: Multiple-variable instrumentation not supported
        """

        if n.initialValue:
            if len(n.variables) > 1:
                raise Unimplemented("multi-initialized var decl stmt")
            if n.variables[0].name in self.observables:
                self.observed[n.loc["end"]["line"] - 1] = n.variables[0].name

    def visitBinaryOperation(self, n: parser.Node):
        """Notes assigning operations of triggering variables

        Args:
            n (parser.Node): a binary operation AST node
        """

        if n.operator in ["=", "+=", "-="]:
            base_name = self.extractAccessBase(n.left)
            if base_name in self.observables:
                self.observed[n.loc["end"]["line"] - 1] = base_name

    def extractAccessBase(self, n: parser.Node):
        """Recursively extracts the base variable for array and struct accesses

        Args:
            n (parser.Node): a LHS AST node

        Raises:
            Unimplemented: for unknown LHS operators

        Returns:
            str: the name of the base variable
        """
        if n.type == "Identifier":
            return n.name
        elif n.type == "IndexAccess":
            return self.extractAccessBase(n.base)
        elif n.type == "MemberAccess":
            return self.extractAccessBase(n.expression)
        else:
            raise Unimplemented("Unknown Assignment LHS")


def to_flat_update(md_json, var_mapping):
    """Restructures the input specification to be used by the instrumentor

    Args:
        md_json (dict): the JSON metadata for our specification
        var_mapping (dict): the mappping from LTL variables to SPOT variable numbers

    Returns:
        (dict, dict, dict): a thruple of mappings of the conditions, prev functions, 
            and type information
    """
    mp = defaultdict(lambda: defaultdict(lambda: set([]), {}), {})
    mc = defaultdict(lambda: defaultdict(lambda: [], {}), {})
    mt = defaultdict(lambda: {}, {})
    for var in md_json:
        for k in var["triggers"]:
            condition = var["condition"]
            contract, trigger = k.split(".", maxsplit=1)

            prevs = re.findall(r'prev\([^)]+\)', condition)
            prevs = [p[5:-1].strip() for p in prevs]
            mp[contract][trigger].update(prevs)

            if "FUNCTION" in condition:
                # @TODO add some checks here
                condition = condition.split("==")[1].strip()

            for p in prevs:
                condition = re.sub(r'prev\([^)]+\)',
                                   get_prevname(p),
                                   condition,
                                   count=1)

            if "types" in var:
                for k, type in var["types"].items():
                    contract, val = k.split(".", maxsplit=1)
                    mt[contract][get_prevname(val)] = type
            mc[contract][trigger] += [(var_mapping[var["name"]], condition)]
    return (mc, mp, mt)


def pprint_update(u, fn_name=None, exit_fn=False):
    """Pretty-prints the update statement for a variable

    Args:
        u (int, str): a tuple of the updated variable id and its condition
        fn_name (str, optional): the name of the function if the condition involves a function name
        exit_fn (bool, optional): whether or not this checks on exit. Defaults to False.

    Returns:
        [type]: [description]
    """
    s = f"bc.update({u[0]}, ({u[1]}));\n"
    # s = s.replace("SUM", "bc.sum")
    if "SUM" in s:
        s = f"bc.update({u[0]}, (true));\n"

    if fn_name:
        if fn_name == u[1] and not exit_fn:
            s = f"bc.update({u[0]}, true); // FUNCTION == {u[1]} \n"
        else:
            s = f"bc.update({u[0]}, false); // FUNCTION == {u[1]} \n"

    return s


def instrument(md, spec, contract, for_fuzzer=False):
    """Primary function weaving together various components of the instrumentation
    process

    Args:
        md (dict): the input specification JSON metadata
        spec (str): the LTL formula in SPOT format
        contract (str): the Solidity code for the smart contracts to be instrumented
        for_fuzzer (bool, optional): Flag for whether or not the instrumentation is 
        for fuzzing (True) or for runtime assurance. Defaults to False.

    Returns:
        str: instrumented contracts
    """

    ast = parser.parse(contract, loc=True)
    spot_form = spot \
        .translate(spec, 'monitor').to_str()

    ltl_ast = ltl_tools.ltl_to_ba_ast(spot_form)
    var_mapping = ltl_tools.var_mapping(spot_form)

    if for_fuzzer:
        ltl_switch_case = ltl_tools.pretty_print_ba_ast(
            ltl_ast, failure_case="invalid = true;\n")
    else:
        ltl_switch_case = ltl_tools.pretty_print_ba_ast(ltl_ast)

    md, prevs, annot_prev_types = to_flat_update(md, var_mapping)

    lines = contract.splitlines(keepends=True)
    typer = solidity_ast_tools.StateVarTyper()
    parser.visit(ast, typer)

    r = FixRets(lines)
    parser.visit(ast, r)
    sr = SplitRets(lines, md.keys())
    parser.visit(ast, sr)
    split_ret_src = sr.instrumented()

    split_ret_lines = split_ret_src.splitlines(keepends=True)
    ast = parser.parse(split_ret_src, loc=True)
    r = FixRets(split_ret_lines)
    parser.visit(ast, r)

    for k, v in typer.mapping.items():
        annot_prev_types[k] = annot_prev_types[k] | v

    p = SourceInstrumentor(split_ret_lines,
                           md,
                           prevs=prevs,
                           state_var_types=annot_prev_types)
    parser.visit(ast, p)
    s = p.instrumented()

    s = s.replace("{CHECK_SWITCH_CASE}", ltl_switch_case)
    s = s.replace("{INITIAL_STATE}", str(ltl_tools.start_state(spot_form)))
    return s