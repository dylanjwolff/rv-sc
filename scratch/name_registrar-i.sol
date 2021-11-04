/*
 * @source: https://github.com/sigp/solidity-security-blog#storage-example
 * @vulnerable_at_lines: 21
 */
// A Locked Name Registrar
contract NameRegistrar {

address buchi_checker_address;
    bool public unlocked = false;  // registrar locked, no name updates

    struct NameRecord { // map hashes to addresses
        bytes32 name;
        address mappedAddress;
    }

    mapping(address => NameRecord) public registeredNameRecord; // records who registered names
    mapping(bytes32 => address) public resolve; // resolves hashes to addresses

    function register(bytes32 _name, address _mappedAddress) public {
        // set up the new NameRecord
        // <yes> <report> OTHER - uninitialized storage
BuchiChecker bc = BuchiChecker(buchi_checker_address);
            address prev_bc_address = buchi_checker_address;
        NameRecord newRecord;
        newRecord.name = _name;
        newRecord.mappedAddress = _mappedAddress;

        resolve[_name] = _mappedAddress;
        registeredNameRecord[msg.sender] = newRecord;
bc.update(0, (registeredNameRecord[msg.sender].name == _name));

        require(unlocked); // only allow registrations if contract is unlocked
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
	if (vars[0]) {
		state = 0;
	} else {
		invalid = true;

	}
} 
        }
}
    

contract TestNameRegistrar is NameRegistrar {

	constructor() payable {
		BuchiChecker bc = new BuchiChecker();
		buchi_checker_address =	 address(bc);
	}


  function echidna_buchi_checker() public view returns(bool){
       BuchiChecker bc = BuchiChecker(buchi_checker_address);
       return !bc.invalid();
  }
}
