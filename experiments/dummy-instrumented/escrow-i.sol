pragma solidity ^0.4.25;

contract Escrow {
address buchi_checker_address;
    enum State { AWAITING_PAYMENT, AWAITING_DELIVERY, COMPLETE }
    
    State public currState;
    
    address public buyer;
    address public seller;
    
    modifier onlyBuyer() {
        require(msg.sender == buyer, "Only buyer can call this method");
        _;
        require(msg.sender == buyer, "Only buyer can call this method");
    }
    
    constructor(address _buyer, address _seller) public {
        buyer = _buyer;
        seller = _seller;
    }
    
    function deposit() onlyBuyer external payable {
BuchiChecker bc = BuchiChecker(buchi_checker_address);
            address prev_bc_address = buchi_checker_address;
bc.update(1, (msg.sender == buyer));
        require(currState == State.AWAITING_PAYMENT, "Already paid");
        currState = State.AWAITING_DELIVERY;
bc.apply_updates_and_check();
    }
    
    function confirmDelivery() onlyBuyer external {
BuchiChecker bc = BuchiChecker(buchi_checker_address);
            address prev_bc_address = buchi_checker_address;
bc.update(1, (msg.sender == buyer));
        require(currState == State.AWAITING_DELIVERY, "Cannot confirm delivery");
        seller.transfer(address(this).balance);
        currState = State.COMPLETE;
bc.apply_updates_and_check();
    }

    function cancel() external {
BuchiChecker bc = BuchiChecker(buchi_checker_address);
            address prev_bc_address = buchi_checker_address;
bc.update(1, (msg.sender == buyer));
bc.update(0, true); // FUNCTION == "cancel" 
        buyer.transfer(address(this).balance);
	currState = State.AWAITING_PAYMENT;
bc.apply_updates_and_check();
bc.update(0, false); // FUNCTION == "cancel" 
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
	if (!vars[0] || vars[1]) {
		state = 0;
	} else {
		invalid = true;

	}
	return;
} 
        }
}
    

contract TestEscrow is Escrow {

	constructor() Escrow(msg.sender, msg.sender) payable {
		BuchiChecker bc = new BuchiChecker();
		buchi_checker_address =	 address(bc);
		
	}


  function echidna_buchi_checker() public view returns(bool){
       BuchiChecker bc = BuchiChecker(buchi_checker_address);
       return true;
  }
}
