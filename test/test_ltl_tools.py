import spot
from rvsc import ltl_tools


def test_smoke_ba_ast(snapshot):
    g: str = spot.translate('!F(red & X(yellow))', 'monitor', 'det').to_str()
    ast = ltl_tools.ltl_to_ba_ast(g)

    snapshot.assert_match(ast)


def test_smoke_ast_pretty(snapshot):
    g: str = spot.translate('!F(red & X(yellow))', 'monitor', 'det').to_str()
    ast = ltl_tools.ltl_to_ba_ast(g)
    s = ltl_tools.pretty_print_ba_ast(ast)

    snapshot.assert_match(s)


def test_impl(snapshot):
    g: str = spot.translate('G( ( !v0 & v1 ) => v2 )', 'monitor',
                            'det').to_str()
    s = ltl_tools.var_mapping(g)
    snapshot.assert_match(s)


def test_var_mapping(snapshot):
    g: str = spot.translate('!F(red & X(yellow))', 'monitor', 'det').to_str()
    vm = ltl_tools.var_mapping(g)

    snapshot.assert_match(vm)


def test_start_state(snapshot):
    g: str = spot.translate('!F(red & X(yellow))', 'monitor', 'det').to_str()
    s = ltl_tools.start_state(g)

    snapshot.assert_match(s)
