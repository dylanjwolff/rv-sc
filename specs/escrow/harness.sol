

contract TestEscrow is Escrow {

	constructor() Escrow(msg.sender, msg.sender) payable {
		BuchiChecker bc = new BuchiChecker();
		buchi_checker_address =	 address(bc);
		
	}


  function echidna_buchi_checker() public view returns(bool){
       BuchiChecker bc = BuchiChecker(buchi_checker_address);
       return !bc.invalid();
  }
}
