

contract TestA is A {

	constructor() payable {
        B b = new B();

        BuchiChecker bc = new BuchiChecker();
        b.initialize(address(bc));

        buchi_checker_address = address(bc);
        b_addr = address(b);
	}


  function echidna_buchi_checker() public view returns(bool){
       BuchiChecker bc = BuchiChecker(buchi_checker_address);
       return !bc.invalid();
  }
}
