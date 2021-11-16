pragma solidity ^0.4.25;

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
    
    function deposit() onlyBuyer external payable {
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


contract TestEscrow is Escrow {
	constructor() Escrow(msg.sender, msg.sender) payable {
	}


  function echidna_dummy() public view returns(bool){
       return true;
  }
}
