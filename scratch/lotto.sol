 pragma solidity ^0.4.26;
 
 contract Lotto {
     bool public payedOut = false;
     address public winner;
     uint public winAmount = 10;

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
