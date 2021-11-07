pragma solidity 0.4.26;

contract Auction {
address buchi_checker_address;
    uint32 high_bid = 0;
    address high_bidder;
    uint last_bid_time =  0;
    address escrow;

    constructor (address _escrow) {
        escrow = _escrow;
    }
    
    function bid(uint32 amt) {
BuchiChecker bc = BuchiChecker(buchi_checker_address);
            address prev_bc_address = buchi_checker_address;
            bc.enter();
if (bc.get_call_depth() <= 1) {
bc.update(0, false); // FUNCTION == "close" 
}
        require(amt > high_bid);
        high_bid = amt;
        high_bidder = msg.sender;
        Escrow e = Escrow(escrow);
        e.cancel();
        e.set_buyer(high_bidder);
        e.transfer(msg.value);
bc.apply_updates();
bc.check();
bc.exit();
    }
    
    function close() {
BuchiChecker bc = BuchiChecker(buchi_checker_address);
            address prev_bc_address = buchi_checker_address;
            bc.enter();
if (bc.get_call_depth() <= 1) {
bc.update(0, true); // FUNCTION == "close" 
}
        require(now -  last_bid_time > 60 minutes);
        require(msg.sender == high_bidder);
        high_bid = 0;
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
    
    function set_buyer(address _buyer) {
BuchiChecker bc = BuchiChecker(buchi_checker_address);
            address prev_bc_address = buchi_checker_address;
            bc.enter();
if (bc.get_call_depth() <= 1) {
bc.update(1, false); // FUNCTION == "confirmDelivery" 
}
        require(currState == State.AWAITING_PAYMENT);
        buyer = _buyer;
bc.apply_updates();
bc.check();
bc.exit();
    }
    
    function() onlyBuyer external payable {
BuchiChecker bc = BuchiChecker(buchi_checker_address);
            address prev_bc_address = buchi_checker_address;
            bc.enter();
if (bc.get_call_depth() <= 1) {
bc.update(1, false); // FUNCTION == "confirmDelivery" 
}
        require(currState == State.AWAITING_PAYMENT, "Already paid");
        currState = State.AWAITING_DELIVERY;
bc.apply_updates();
bc.check();
bc.exit();
    }
    
    function confirmDelivery() onlyBuyer external {
BuchiChecker bc = BuchiChecker(buchi_checker_address);
            address prev_bc_address = buchi_checker_address;
            bc.enter();
if (bc.get_call_depth() <= 1) {
bc.update(1, true); // FUNCTION == "confirmDelivery" 
}
        require(currState == State.AWAITING_DELIVERY, "Cannot confirm delivery");
        seller.transfer(address(this).balance);
        currState = State.COMPLETE;
bc.apply_updates();
bc.check();
bc.exit();
    }

    function cancel() external {
BuchiChecker bc = BuchiChecker(buchi_checker_address);
            address prev_bc_address = buchi_checker_address;
            bc.enter();
if (bc.get_call_depth() <= 1) {
bc.update(1, false); // FUNCTION == "confirmDelivery" 
}
        buyer.transfer(address(this).balance);
	    currState = State.AWAITING_PAYMENT;
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
    



contract TestAuction is Auction {

	constructor() payable {
        Escrow e = new Escrow(msg.sender, msg.sender);

        BuchiChecker bc = new BuchiChecker();

        e.initialize(address(bc));

        Auction a = new Auction(address(e));

        buchi_checker_address = address(bc);
        escrow = address(e);
	}


  function echidna_buchi_checker() public view returns(bool){
       BuchiChecker bc = BuchiChecker(buchi_checker_address);
       return !bc.invalid();
  }
}
