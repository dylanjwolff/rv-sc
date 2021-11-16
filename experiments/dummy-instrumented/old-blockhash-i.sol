/*
 * @source: https://github.com/SmartContractSecurity/SWC-registry/blob/master/test_cases/weak_randomness/old_blockhash.sol
 * @author: -
 * @vulnerable_at_lines: 35
 */

pragma solidity ^0.4.24;

//Based on the the Capture the Ether challange at https://capturetheether.com/challenges/lotteries/predict-the-block-hash/
//Note that while it seems to have a 1/2^256 chance you guess the right hash, actually blockhash returns zero for blocks numbers that are more than 256 blocks ago so you can guess zero and wait.
contract PredictTheBlockHashChallenge {

address buchi_checker_address;
    struct guess{
      uint block;
      bytes32 guess;
    }

    mapping(address => guess) guesses;

    constructor() public payable {
        // require(msg.value == 1 ether); removing for fuzzing DJW
    }

    function lockInGuess(bytes32 hash) public payable {
BuchiChecker bc = BuchiChecker(buchi_checker_address);
            address prev_bc_address = buchi_checker_address;
        require(guesses[msg.sender].block == 0);
        require(msg.value == 1 ether);

        guesses[msg.sender].guess = hash;
        guesses[msg.sender].block  = block.number + 1;
bc.apply_updates_and_check();
    }

    function settle() public {
BuchiChecker bc = BuchiChecker(buchi_checker_address);
            address prev_bc_address = buchi_checker_address;
        require(block.number > guesses[msg.sender].block);
        // <yes> <report> BAD_RANDOMNESS
        bytes32 answer = blockhash(guesses[msg.sender].block);
bc.update(0, (answer == 0));

        guesses[msg.sender].block = 0;
        if (guesses[msg.sender].guess == answer) {
            msg.sender.transfer(2 ether);
        }
bc.apply_updates_and_check();
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
        
        
        function update(uint32 k, bool v) {
                updates_k.push(k);
                updates_v.push(v);
        }

        function apply_updates_and_check() {
            for (uint i=0; i < updates_v.length; i++) {
                uint32 k = updates_k[i];
                bool v = updates_v[i];
                vars[k] = v;
            }
            updates_k.length = 0;
            updates_v.length = 0;

            
if (state == 0) {
	if (!vars[0]) {
		state = 0;
	} else {
		invalid = true;

	}
	return;
} 
        }
}
    

contract TestPBHC is PredictTheBlockHashChallenge {

	constructor() payable {
		BuchiChecker bc = new BuchiChecker();
		buchi_checker_address =	 address(bc);
	}


  function echidna_buchi_check() public view returns(bool){
       BuchiChecker bc = BuchiChecker(buchi_checker_address);
       return true;
  }
}
