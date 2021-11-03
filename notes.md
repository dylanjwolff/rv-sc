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

nested calls might not work... foo( ... ) { bar() } 
	need a call stack in instrumented contract, only check if callstack is empty

concurrent calls also problem
	no, this is fine because the whole execution is transactional

frame as test-time instrumentation
   
triggers on e.g. winner.send()


6/10
| Vulnerability | Description | Level |
| --- | --- | -- |
| [Reentrancy](https://github.com/smartbugs/smartbugs/blob/master/dataset/reentrancy) | Reentrant function calls make a contract to behave in an unexpected way | Solidity | reentrancy\_dao.sol |
| [Access Control](https://github.com/smartbugs/smartbugs/blob/master/dataset/access_control) | Failure to use function modifiers or use of tx.origin | Solidity | multiowned\_vulnerable.sol |
| [Arithmetic](https://github.com/smartbugs/smartbugs/blob/master/dataset/arithmetic) | Integer over/underflows | Solidity | timelock.sol |
| [Unchecked Low Level Calls](https://github.com/smartbugs/smartbugs/blob/master/dataset/unchecked_low_level_calls) | call(), callcode(), delegatecall() or send() fails and it is not checked | Solidity | lotto.sol |
| [Denial Of Service](https://github.com/smartbugs/smartbugs/blob/master/dataset/denial_of_service) | The contract is overwhelmed with time-consuming computations | Solidity | escrow.sol |
| [Bad Randomness](https://github.com/smartbugs/smartbugs/blob/master/dataset/bad_randomness) | Malicious miner biases the outcome | Blockchain |
| [Front Running](https://github.com/smartbugs/smartbugs/blob/master/dataset/front_running) | Two dependent transactions that invoke the same contract are included in one block | Blockchain |
| [Time Manipulation](https://github.com/smartbugs/smartbugs/blob/master/dataset/time_manipulation) | The timestamp of the block is manipulated by the miner | Blockchain | n/a |
| [Short Addresses](https://github.com/smartbugs/smartbugs/blob/master/dataset/short_addresses) | EVM itself accepts incorrectly padded arguments | EVM |
| [Unknown Unknowns](https://github.com/smartbugs/smartbugs/blob/master/dataset/other) | Vulnerabilities not identified in DASP 10 | N.A |
