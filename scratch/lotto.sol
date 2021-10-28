 pragma solidity ^0.4.26;
 
 contract Lotto {
     bool public payedOut = false;
     address public winner;
     uint public winAmount;

     // ... extra functionality here

     function sendToWinner() public {
         require(!payedOut);
         // <yes> <report> UNCHECKED_LL_CALLS
         winner.send(winAmount);
         payedOut = true;
     }

     function withdrawLeftOver(uint256 i) public {
         require(payedOut);
         // <yes> <report> UNCHECKED_LL_CALLS
	if (i < 100) {
         msg.sender.send(this.balance);
	}
     }
 }

contract TestLotto is Lotto {

  function echidna_balance_under_1000() public view returns(bool){
       return !payedOut;
  }
}
