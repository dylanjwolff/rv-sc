prev(msg.sender) == msg.sender is not supported currently... problem is polymorphic way to handle this... How can we store prev(msg.sender) without knowing its type... probably need to punt

Can / may need to restrict access to update functions to address(es) of contracts, otherwise malicious user could change states directly. Do so using modifiers [here](https://ethereum.stackexchange.com/questions/24222/how-can-i-restrict-a-function-to-make-it-only-callable-by-one-contract/24223)

Two Observations...
1. Return statements need to be split... if they contain something that changes the state could miss it otherwise
2. Error handling... if a function errors out and dies, do we throw away the updates? What about a nested function call? Do we need to associate functions with txids or something similar?
 --- Instrumentation handles this case ^^^^^^^

It looks like uninterpreted functions are passed as fresh variables to e.g. SPOT

We need instrumentation to
    a) Find instances where variables / uninterp. fn values / special cases (BALANCE, FUNCTION) can change... i.e. assignments, begin fn, etc.
    b) after that line, inject something that updates the global state
    c) changes the specs to a formula with only fresh vars, and keeps the mapping of vars to actual functions

Inheritance is another potential issue. How do we instrument parent conctract methods that are invoked with "super"

    
