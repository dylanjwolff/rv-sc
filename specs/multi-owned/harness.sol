

contract TestMultiOwnable is MultiOwnable {

  function echidna_test_buchi() returns (bool) {
    BuchiChecker bc = BuchiChecker(buchi_checker_address);
    return !bc.invalid();
  }

}

