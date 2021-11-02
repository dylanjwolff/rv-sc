

contract TestMultiOwnable is MultiOwnable {

	constructor() payable {
		BuchiChecker bc = new BuchiChecker();
		buchi_checker_address =	 address(bc);
	}


  function echidna_test_buchi() returns (bool) {
    BuchiChecker bc = BuchiChecker(buchi_checker_address);
    return !bc.invalid();
  }

}

