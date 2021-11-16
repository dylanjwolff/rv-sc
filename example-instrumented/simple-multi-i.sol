contract A {
address buchi_checker_address;
    uint32 number;
    address b_addr;

    function set_both(uint32 num) {
BuchiChecker bc = BuchiChecker(buchi_checker_address);
            address prev_bc_address = buchi_checker_address;
bc.update(0, true); // FUNCTION == "set_both" 
        B b = B(b_addr);
        number = num;
        b.set(num);
bc.apply_updates_and_check();
bc.update(0, false); // FUNCTION == "set_both" 
    }
function initialize(address a) {
        if (address(buchi_checker_address) == address(0)) {
            buchi_checker_address = a;
        }
}
    }

contract B {
address buchi_checker_address;
    uint32 number;

    function set(uint32 num) {
BuchiChecker bc = BuchiChecker(buchi_checker_address);
            address prev_bc_address = buchi_checker_address;
bc.update(1, true); // FUNCTION == "set" 
        number = num;
bc.apply_updates_and_check();
bc.update(1, false); // FUNCTION == "set" 
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
	} else if (vars[0]) {
		state = 1;
	} else {
		invalid = true;

	}
	return;
}
if (state == 1) {
	if (!vars[0] && vars[1]) {
		state = 0;
	} else if (vars[0] && vars[1]) {
		state = 1;
	} else {
		invalid = true;

	}
	return;
} 
        }
}
    

contract TestA is A {

	constructor() payable {
        B b = new B();

        BuchiChecker bc = new BuchiChecker();
        b.initialize(address(bc));

        buchi_checker_address = address(bc);
        b_addr = address(b);
	}


  function echidna_buchi_checker() public view returns(bool){
       BuchiChecker bc = BuchiChecker(buchi_checker_address);
       return !bc.invalid();
  }
}
