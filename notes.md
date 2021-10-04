It looks like uninterpreted functions are passed as fresh variables to e.g. SPOT

We need instrumentation to
    a) Find instances where variables / uninterp. fn values / special cases (BALANCE, FUNCTION) can change... i.e. assignments, begin fn, etc.
    b) after that line, inject something that updates the global state
    c) changes the specs to a formula with only fresh vars, and keeps the mapping of vars to actual functions
    