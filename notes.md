2 Observations...
1. Return statements need to be split... if they contain something that changes the state could miss it otherwise
2. Error handling... if a function errors out and dies, do we throw away the updates? What about a nested function call? Do we need to associate functions with txids or something similar?


It looks like uninterpreted functions are passed as fresh variables to e.g. SPOT

We need instrumentation to
    a) Find instances where variables / uninterp. fn values / special cases (BALANCE, FUNCTION) can change... i.e. assignments, begin fn, etc.
    b) after that line, inject something that updates the global state
    c) changes the specs to a formula with only fresh vars, and keeps the mapping of vars to actual functions


    
