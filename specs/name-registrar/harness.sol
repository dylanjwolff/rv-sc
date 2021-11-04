

contract TestNameRegistrar is NameRegistrar {

	constructor() payable {
		BuchiChecker bc = new BuchiChecker();
		buchi_checker_address =	 address(bc);
	}


  function echidna_buchi_checker() public view returns(bool){
       BuchiChecker bc = BuchiChecker(buchi_checker_address);
       return !bc.invalid();
  }
}
