from rvsc import solidity_ast_tools
from solidity_parser import parser
import subprocess as sp

import tempfile


def test_pprint_no_information_loss():
    # @TODO make sure relative pathing is done Pythonically
    fname = 'verx-benchmarks/Zilliqa/main.sol'
    ast = parser.parse_file(fname, loc=True)

    with open(fname, "r") as f:
        lines = f.readlines()
        p = solidity_ast_tools.SourcePrettyPrinter(lines)
        p.visit(ast)

        first_s = p.out_s

        ast = parser.parse(first_s, loc=True)
        p = solidity_ast_tools.SourcePrettyPrinter(first_s.splitlines())
        p.visit(ast)
        second_s = p.out_s

        print(len(first_s), len(second_s))
        assert first_s == second_s


def test_pprint_compiles():
    # @TODO make sure relative pathing is done Pythonically
    fname = 'verx-benchmarks/Zilliqa/main.sol'
    ast = parser.parse_file(fname, loc=True)

    with open(fname, "r") as f, tempfile.NamedTemporaryFile(mode="w") as ftemp:
        lines = f.readlines()
        p = solidity_ast_tools.SourcePrettyPrinter(lines)
        p.visit(ast)

        ftemp.write(p.out_s)
        ftemp.flush()

        result = sp.run(["~/.npm-global/bin/solcjs", ftemp.name],
                        capture_output=True)
        assert result.returncode == 0, f"Failed to compile {fname}:\n {result.stderr.decode('utf-8')}"
