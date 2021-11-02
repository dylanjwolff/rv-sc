contract TestMultiOwnable is MultiOwnable {

  function echidna_test_buchi() {
    BuchiChecker bc = BuchiChecker(buchi_checker_address);
    return !bc.invalid();
  }

}

