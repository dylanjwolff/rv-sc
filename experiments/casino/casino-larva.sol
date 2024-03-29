pragma solidity 0.4.26;
contract LARVA_Casino {
  modifier LARVA_Constructor {
    _;
    {
      LARVA_EnableContract();
    }
  }
  modifier LARVA_DEA_2_handle_after_timeoutBet__no_parameters {
    if ((LARVA_STATE_2 == 2)) {
      LARVA_STATE_2 = 1;
    }
    _;
  }
  modifier LARVA_DEA_2_handle_after_resolveBet__no_parameters {
    if ((LARVA_STATE_2 == 2)) {
      LARVA_STATE_2 = 1;
    }
    _;
  }
  modifier LARVA_DEA_2_handle_after_placeBet__no_parameters {
    if ((LARVA_STATE_2 == 1)) {
      LARVA_STATE_2 = 2;
    }
    _;
  }
  modifier LARVA_DEA_2_handle_after_openTable__no_parameters {
    if ((LARVA_STATE_2 == 0)) {
      LARVA_STATE_2 = 1;
    }
    _;
  }
  modifier LARVA_DEA_2_handle_after_closeTable__no_parameters {
    if ((LARVA_STATE_2 == 1)) {
      LARVA_STATE_2 = 0;
    } else {
      if ((LARVA_STATE_2 == 2)) {
        LARVA_STATE_2 = 3;
      }
    }
    _;
  }
  modifier LARVA_DEA_1_handle_after_assignment_pot {
    _;
    if ((LARVA_STATE_1 == 2) && (LARVA_previous_pot > pot)) {
      LARVA_STATE_1 = 3;
    }
  }
  modifier LARVA_DEA_1_handle_after_timeoutBet__no_parameters {
    if ((LARVA_STATE_1 == 2)) {
      LARVA_STATE_1 = 0;
    }
    _;
  }
  modifier LARVA_DEA_1_handle_after_resolveBet__no_parameters {
    if ((LARVA_STATE_1 == 2)) {
      LARVA_STATE_1 = 0;
    }
    _;
  }
  modifier LARVA_DEA_1_handle_after_placeBet__parameters__value (uint _value) {
    if ((LARVA_STATE_1 == 0) && (_value <= pot)) {
      LARVA_STATE_1 = 2;
      total += _value;
    }
    _;
  }
  modifier LARVA_DEA_1_handle_after_closeTable__no_parameters {
    if ((LARVA_STATE_1 == 0) && (pot == 0)) {
      LARVA_STATE_1 = 1;
    }
    _;
  }
  int8 LARVA_STATE_1 = 0;
  int8 LARVA_STATE_2 = 0;
  function LARVA_set_pot_pre (uint _pot) LARVA_DEA_1_handle_after_assignment_pot public returns (uint) {
    LARVA_previous_pot = pot;
    pot = _pot;
    return LARVA_previous_pot;
  }
  function LARVA_set_pot_post (uint _pot) LARVA_DEA_1_handle_after_assignment_pot public returns (uint) {
    LARVA_previous_pot = pot;
    pot = _pot;
    return pot;
  }
  uint private LARVA_previous_pot;
  uint total;
  enum LARVA_STATUS {RUNNING, STOPPED}
  function LARVA_EnableContract () private {
    LARVA_Status = LARVA_STATUS.RUNNING;
  }
  function LARVA_DisableContract () private {
    LARVA_Status = LARVA_STATUS.STOPPED;
  }
  LARVA_STATUS private LARVA_Status = LARVA_STATUS.STOPPED;
  modifier LARVA_ContractIsEnabled {
    require(LARVA_Status == LARVA_STATUS.RUNNING);
    _;
  }
  mapping (uint => mapping (uint => address[])) placedBets;
  mapping (uint => mapping (address => uint)) potShare;
  uint[] numbersGuessed;
  uint private pot;
  uint tableID;
  uint tableOpenTime;
  address owner;
  constructor () LARVA_Constructor public {
    owner = msg.sender;
  }
  function openTable () LARVA_DEA_2_handle_after_openTable__no_parameters LARVA_ContractIsEnabled public {
    require(msg.sender == owner);
    require(tableOpenTime == 0);
    tableOpenTime = now;
    tableID++;
  }
  function closeTable () LARVA_DEA_2_handle_after_closeTable__no_parameters LARVA_DEA_1_handle_after_closeTable__no_parameters LARVA_ContractIsEnabled public {
    require(msg.sender == owner);
    require(pot == 0);
    delete numbersGuessed;
  }
  function timeoutBet () LARVA_DEA_2_handle_after_timeoutBet__no_parameters LARVA_DEA_1_handle_after_timeoutBet__no_parameters LARVA_ContractIsEnabled public {
    require(msg.sender == owner);
    require(now - tableOpenTime > 60 minutes);
    require(pot != 0);
    for (uint i = 0; i < numbersGuessed.length; i++) {
      uint l = placedBets[tableID][numbersGuessed[i]].length;
      for (uint j = 0; j < l; j++) {
        address better = placedBets[tableID][numbersGuessed[i]][l];
        better.transfer(potShare[tableID][better]);
        delete placedBets[tableID][numbersGuessed[i]];
      }
    }
    closeTable();
  }
  function placeBet (uint guessNo) LARVA_DEA_2_handle_after_placeBet__no_parameters LARVA_DEA_1_handle_after_placeBet__parameters__value(guessNo) LARVA_ContractIsEnabled public {
    require(msg.value > 1 ether);
    potShare[tableID][msg.sender] += msg.value;
    placedBets[tableID][guessNo].push(msg.sender);
    numbersGuessed.push(guessNo);
    LARVA_set_pot_post((pot) + (msg.value));
  }
  function resolveBet (uint _secretNumber) LARVA_DEA_2_handle_after_resolveBet__no_parameters LARVA_DEA_1_handle_after_resolveBet__no_parameters LARVA_ContractIsEnabled public {
    require(msg.sender == owner);
    uint l = placedBets[tableID][_secretNumber].length;
    if (l != 0) {
      for (uint i = 0; i < l; i++) {
        placedBets[tableID][_secretNumber][i].transfer(pot / l);
      }
    }
    pot = 0;
    closeTable();
  }

}



contract TestCasino is LARVA_Casino {

  function echidna_dummy_check() public view returns(bool){
       return true;
  }
}
