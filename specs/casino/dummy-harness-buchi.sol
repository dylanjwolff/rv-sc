

contract TestCasino is Casino {

	constructor() payable {
		BuchiChecker bc = new BuchiChecker();
		buchi_checker_address =	 address(bc);
	}


  function echidna_dummy() public view returns(bool){
       return true;
  }
}
