pragma solidity 0.4.26;

contract Auction {
    uint32 high_bid = 0;
    address high_bidder;
    uint last_bid_time =  0;
    address escrow;

    constructor (address _escrow) {
        escrow = _escrow;
    }
    
    function bid(uint32 amt) {
        require(amt > high_bid);
        high_bid = amt;
        high_bidder = msg.sender;
        Escrow e = Escrow(escrow);
        e.cancel();
        e.set_buyer(high_bidder);
        e.transfer(msg.value);
    }
    
    function close() {
        require(now -  last_bid_time > 60 minutes);
        require(msg.sender == high_bidder);
        high_bid = 0;
    }
}

contract Escrow {
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
        require(currState == State.AWAITING_PAYMENT);
        buyer = _buyer;
    }
    
    function() onlyBuyer external payable {
        require(currState == State.AWAITING_PAYMENT, "Already paid");
        currState = State.AWAITING_DELIVERY;
    }
    
    function confirmDelivery() onlyBuyer external {
        require(currState == State.AWAITING_DELIVERY, "Cannot confirm delivery");
        seller.transfer(address(this).balance);
        currState = State.COMPLETE;
    }

    function cancel() external {
        buyer.transfer(address(this).balance);
	    currState = State.AWAITING_PAYMENT;
    }
}
