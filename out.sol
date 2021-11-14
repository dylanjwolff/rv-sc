/*
 * @source: https://github.com/sigp/solidity-security-blog
 * @author: -
 * @vulnerable_at_lines: 22
 */

//added pragma version
 pragma solidity ^0.4.0;
 
 contract TimeLock {

address buchi_checker_address;
     mapping(address => uint) public balances;
uint prev___lockTime_msg_sender_;
     mapping(address => uint) public lockTime;

     function deposit() public payable {
BuchiChecker bc = BuchiChecker(buchi_checker_address);
            address prev_bc_address = buchi_checker_address;
            bc.enter();
prev___lockTime_msg_sender_ = lockTime[msg.sender];
         balances[msg.sender] += msg.value;
         lockTime[msg.sender] = now + 1 weeks;
bc.update(1, (lockTime[msg.sender] >= prev___lockTime_msg_sender_));
bc.apply_updates();
bc.check();
bc.exit();
     }

     function increaseLockTime(uint _secondsToIncrease) public {
         // <yes> <report> ARITHMETIC
BuchiChecker bc = BuchiChecker(buchi_checker_address);
            address prev_bc_address = buchi_checker_address;
            bc.enter();
prev___lockTime_msg_sender_ = lockTime[msg.sender];
if (bc.get_call_depth() <= 1) {
bc.update(0, true); // FUNCTION == "increaseLockTime" 
}
         lockTime[msg.sender] += _secondsToIncrease;
bc.update(1, (lockTime[msg.sender] >= prev___lockTime_msg_sender_));
bc.apply_updates();
bc.check();
if (bc.get_call_depth() <= 1) {
bc.update(0, false); // FUNCTION == "increaseLockTime" 
}
bc.exit();
     }

     function withdraw() public {
BuchiChecker bc = BuchiChecker(buchi_checker_address);
            address prev_bc_address = buchi_checker_address;
            bc.enter();
         require(balances[msg.sender] > 0);
         require(now > lockTime[msg.sender]);
         uint transferValue = balances[msg.sender];
         balances[msg.sender] = 0;
         msg.sender.transfer(transferValue);
bc.apply_updates();
bc.check();
bc.exit();
     }
function initialize(address a) {
        if (address(buchi_checker_address) == address(0)) {
            buchi_checker_address = a;
        }
}
     }




contract BuchiChecker {
        uint256 state = 0;
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
               
if (state == 0) {
	if (!vars[0] || vars[1]) {
		state = 0;
	} else {
		invalid = true;

	}
	return;
} 
        }
}
    

contract TestTimeLock is TimeLock {

	constructor() payable {
		BuchiChecker bc = new BuchiChecker();
		buchi_checker_address =	 address(bc);
	}


  function echidna_buchi_checker() public view returns(bool){
       BuchiChecker bc = BuchiChecker(buchi_checker_address);
       return !bc.invalid();
  }
}
