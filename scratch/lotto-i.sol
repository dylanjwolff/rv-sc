 pragma solidity ^0.4.26;
 
 contract Lotto {
address buchi_checker_address;
     bool public payedOut = false;
uint256 prev___this_balance;
     address public winner;
     uint public winAmount = 1;

     // ... extra functionality here

     function sendToWinner() public {
BuchiChecker bc = BuchiChecker(buchi_checker_address);
bc.update(0, true); // FUNCTION == "sendToWinner" 
prev___this_balance = this.balance;
         require(!payedOut);
         // <yes> <report> UNCHECKED_LL_CALLS
         winner.transfer(winAmount);
         payedOut = true;
bc.update(1, (this.balance == prev___this_balance - winAmount));
bc.apply_updates();
bc.check();
     }

     function withdrawLeftOver(uint256 i) public {
BuchiChecker bc = BuchiChecker(buchi_checker_address);
bc.update(0, false); // FUNCTION == "sendToWinner" 
         require(payedOut);
         // <yes> <report> UNCHECKED_LL_CALLS
	if (i < 100) {
         msg.sender.send(this.balance);
	}
bc.apply_updates();
bc.check();
     }
function initialize(address a) {
        if (address(buchi_checker_address) == address(0)) {
            buchi_checker_address = a;
        }
}
     }



contract BuchiChecker {
        uint256 state;
        uint32[] updates_k;
        bool[] updates_v;
        mapping(uint32 => bool) vars;
        bool public invalid = false;

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
               
if (state == 0) {
	if (!vars[0] || vars[1]) {
		state = 0;
	} else {
		invalid = true;

	}
} 
        }
}

contract TestLotto is Lotto {

	constructor() payable {
		BuchiChecker bc = new BuchiChecker();
		buchi_checker_address =	 address(bc);
        winner = msg.sender;
	}


  function echidna_balance_under_1000() public view returns(bool){
       BuchiChecker bc = BuchiChecker(buchi_checker_address);
       return !bc.invalid();
  }
}
