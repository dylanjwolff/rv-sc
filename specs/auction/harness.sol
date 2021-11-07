

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
