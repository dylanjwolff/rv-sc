from rvsc import solidity_ast_tools
from solidity_parser import parser
from rvsc import solc_vm
import tempfile
import pytest
from pathlib import Path


def test_typer(snapshot):
    fname = "verx-benchmarks/Zilliqa/main.sol"
    ast = parser.parse_file(fname, loc=True)

    t = solidity_ast_tools.StateVarTyper()
    parser.visit(ast, t)

    snapshot.assert_match(t.mapping)


# @TODO make sure relative pathing is done Pythonically
@pytest.mark.skip(
    reason="Too many edge cases to resolve with whole Solidity language")
@pytest.mark.parametrize(
    "fname",
    list(Path("verx-benchmarks").glob("*/*.sol"))[0:3],
)
def test_pprint_no_information_loss(fname):
    print(f"TESTING {fname}")
    ast = parser.parse_file(fname, loc=True)

    with open(fname, "r") as f:
        lines = f.readlines()
        p = solidity_ast_tools.SourcePrettyPrinter(lines)
        p.visit(ast)

        first_s = p.out_s

        print(first_s)

        ast = parser.parse(first_s, loc=True)
        p = solidity_ast_tools.SourcePrettyPrinter(first_s.splitlines())
        p.visit(ast)
        second_s = p.out_s

        assert second_s == first_s


# @TODO make sure relative pathing is done Pythonically
@pytest.mark.skip(
    reason="Too many edge cases to resolve with whole Solidity language")
@pytest.mark.parametrize(
    "fname",
    list(Path("verx-benchmarks").glob("*/*.sol"))[0:3],
)
def test_pprint_compiles(fname):
    ast = parser.parse_file(fname, loc=True)

    with open(fname, "r") as f, tempfile.NamedTemporaryFile(mode="w") as ftemp:
        lines = f.readlines()
        p = solidity_ast_tools.SourcePrettyPrinter(lines)
        p.visit(ast)

        ftemp.write(p.out_s)
        ftemp.flush()

        print(f"COMP V {p.compiler_version}")
        solc = solc_vm.Solc(p.compiler_version, major=True)
        result = solc.exec(ftemp.name)

        assert result.returncode == 0, f"Failed to compile {fname}:\n {result.stderr.decode('utf-8')}"