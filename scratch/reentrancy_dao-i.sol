/*
 * @source: https://github.com/ConsenSys/evm-analyzer-benchmark-suite
 * @author: Suhabe Bugrara
 * @vulnerable_at_lines: 18
 */

pragma solidity ^0.4.19;

contract ReentrancyDAO {
address buchi_checker_address;
    mapping (address => uint) credit;
uint prev___balance;
uint prev___credit_msg_sender_;
    uint balance;

    function withdrawAll() public {
BuchiChecker bc = BuchiChecker(buchi_checker_address);
prev___balance = balance;
prev___credit_msg_sender_ = credit[msg.sender];
bc.update(0, true); // FUNCTION == "withdrawAll" 
        uint oCredit = credit[msg.sender];
        if (oCredit > 0) {
            balance -= oCredit;
            // <yes> <report> REENTRANCY
            bool callResult = msg.sender.call.value(oCredit)();
            require (callResult);
            credit[msg.sender] = 0;
        }
bc.update(1, (balance == prev___balance - prev___credit_msg_sender_));
bc.apply_updates();
bc.check();
    }

    function deposit() public payable {
BuchiChecker bc = BuchiChecker(buchi_checker_address);
prev___balance = balance;
prev___credit_msg_sender_ = credit[msg.sender];
bc.update(0, false); // FUNCTION == "withdrawAll" 
        credit[msg.sender] += msg.value;
        balance += msg.value;
bc.update(1, (balance == prev___balance - prev___credit_msg_sender_));
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
    

contract TestReentrancyDAO is ReentrancyDAO {

	constructor() payable {
		BuchiChecker bc = new BuchiChecker();
		buchi_checker_address =	 address(bc);
		balance = 100;
	}


  function echidna_buchi_checker() public view returns(bool){
       BuchiChecker bc = BuchiChecker(buchi_checker_address);
       return !bc.invalid();
  }
}
