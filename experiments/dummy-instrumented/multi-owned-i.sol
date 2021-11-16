/*
 * @source: https://github.com/SmartContractSecurity/SWC-registry/blob/master/test_cases/solidity/unprotected_critical_functions/multiowned_vulnerable/multiowned_vulnerable.sol
 * @author: -
 * @vulnerable_at_lines: 38
 */

pragma solidity ^0.4.23;

/**
 * @title MultiOwnable
 */
contract MultiOwnable {
address buchi_checker_address;
  address public root;
address prev___owners_msg_sender_;
  mapping (address => address) public owners; // owner => parent of owner

  /**
  * @dev The Ownable constructor sets the original `owner` of the contract to the sender
  * account.
  */
  constructor() public {
    root = msg.sender;
    owners[root] = root;
  }

  /**
  * @dev Throws if called by any account other than the owner.
  */
  modifier onlyOwner() {
    require(owners[msg.sender] != 0);
    _;
  }

  /**
  * @dev Adding new owners
  * Note that the "onlyOwner" modifier is missing here.
  */
  // <yes> <report> ACCESS_CONTROL
  function newOwner(address _owner) external returns (bool) {
BuchiChecker bc = BuchiChecker(buchi_checker_address);
            address prev_bc_address = buchi_checker_address;
prev___owners_msg_sender_ = owners[msg.sender];
bc.update(2, (prev___owners_msg_sender_ == 0));
bc.update(0, true); // FUNCTION == "newOwner" 
    require(_owner != 0);
    owners[_owner] = msg.sender;
bc.update(1, (owners[_owner] == 0));
bool temp_ret_instrum_0 = true;
bc.apply_updates_and_check();
bc.update(0, false); // FUNCTION == "newOwner" 
return temp_ret_instrum_0;
  }

  /**
    * @dev Deleting owners
    */
  function deleteOwner(address _owner) onlyOwner external returns (bool) {
BuchiChecker bc = BuchiChecker(buchi_checker_address);
            address prev_bc_address = buchi_checker_address;
prev___owners_msg_sender_ = owners[msg.sender];
bc.update(2, (prev___owners_msg_sender_ == 0));
    require(owners[_owner] == msg.sender || (owners[_owner] != 0 && msg.sender == root));
    owners[_owner] = 0;
bc.update(1, (owners[_owner] == 0));
bool temp_ret_instrum_0 = true;
bc.apply_updates_and_check();
return temp_ret_instrum_0;
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
	if (!vars[0] || vars[1] || !vars[2]) {
		state = 0;
	} else {
		invalid = true;

	}
	return;
} 
        }
}
    

contract TestMultiOwnable is MultiOwnable {

	constructor() payable {
		BuchiChecker bc = new BuchiChecker();
		buchi_checker_address =	 address(bc);
	}


  function echidna_test_buchi() returns (bool) {
    BuchiChecker bc = BuchiChecker(buchi_checker_address);
    return true;
  }

}

