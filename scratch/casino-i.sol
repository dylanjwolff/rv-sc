pragma solidity 0.4.26;

contract Casino{

address buchi_checker_address;
    mapping(uint => mapping (uint => address[])) placedBets;
    mapping(uint => mapping(address => uint)) potShare;

    uint[] numbersGuessed;
    
    uint pot;

    uint tableID;
    uint tableOpenTime;
    bool open;
    bool betted;

    address owner;

    constructor() public{
        owner = msg.sender;
    }

    function openTable() public{
BuchiChecker bc = BuchiChecker(buchi_checker_address);
            address prev_bc_address = buchi_checker_address;
bc.update(0, true); // FUNCTION == "openTable" 
bc.update(3, false); // FUNCTION == "closeTable" 
bc.update(4, false); // FUNCTION == "placeBet" 
bc.update(1, false); // FUNCTION == "resolveBet" 
bc.update(2, false); // FUNCTION == "timeoutBet" 
        require(msg.sender == owner);
        require(tableOpenTime == 0);
        require(!open);

        tableOpenTime = now;
        open = true;
        tableID++;
bc.apply_updates();
bc.check();
    }

    function closeTable() public{
BuchiChecker bc = BuchiChecker(buchi_checker_address);
            address prev_bc_address = buchi_checker_address;
bc.update(0, false); // FUNCTION == "openTable" 
bc.update(3, true); // FUNCTION == "closeTable" 
bc.update(4, false); // FUNCTION == "placeBet" 
bc.update(1, false); // FUNCTION == "resolveBet" 
bc.update(2, false); // FUNCTION == "timeoutBet" 
        require(msg.sender == owner);
        require(pot == 0);
        require(open);

        open = false;
        delete numbersGuessed;
bc.apply_updates();
bc.check();
    }

    function timeoutBet() public{
BuchiChecker bc = BuchiChecker(buchi_checker_address);
            address prev_bc_address = buchi_checker_address;
bc.update(0, false); // FUNCTION == "openTable" 
bc.update(3, false); // FUNCTION == "closeTable" 
bc.update(4, false); // FUNCTION == "placeBet" 
bc.update(1, false); // FUNCTION == "resolveBet" 
bc.update(2, true); // FUNCTION == "timeoutBet" 
        require(msg.sender == owner);
        require(now - tableOpenTime > 60 minutes);
        require(open);
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
bc.apply_updates();
bc.check();
    }

    function placeBet(uint guessNo) payable public{
BuchiChecker bc = BuchiChecker(buchi_checker_address);
            address prev_bc_address = buchi_checker_address;
bc.update(0, false); // FUNCTION == "openTable" 
bc.update(3, false); // FUNCTION == "closeTable" 
bc.update(4, true); // FUNCTION == "placeBet" 
bc.update(1, false); // FUNCTION == "resolveBet" 
bc.update(2, false); // FUNCTION == "timeoutBet" 
        require(msg.value > 1 ether);
        require(open);

        potShare[tableID][msg.sender] += msg.value;
        placedBets[tableID][guessNo].push(msg.sender);
        numbersGuessed.push(guessNo);
        pot += msg.value;
bc.apply_updates();
bc.check();
    }

    //we assume owner is trusted
    function resolveBet(uint _secretNumber) public{
BuchiChecker bc = BuchiChecker(buchi_checker_address);
            address prev_bc_address = buchi_checker_address;
bc.update(0, false); // FUNCTION == "openTable" 
bc.update(3, false); // FUNCTION == "closeTable" 
bc.update(4, false); // FUNCTION == "placeBet" 
bc.update(1, true); // FUNCTION == "resolveBet" 
bc.update(2, false); // FUNCTION == "timeoutBet" 
        require(open);
        require(pot > 0);
        require(msg.sender == owner);

        uint l = placedBets[tableID][_secretNumber].length;
        if(l != 0){
            for (uint i = 0; i < l; i++) {
                placedBets[tableID][_secretNumber][i].transfer(pot/l);
            }
        }

        pot = 0;

        closeTable();
bc.apply_updates();
bc.check();
    }
function initialize(address a) {
        if (address(buchi_checker_address) == address(0)) {
            buchi_checker_address = a;
        }
}
    }



contract BuchiChecker {
        uint256 state = 1;
        uint32[] updates_k;
        bool[] updates_v;
        mapping(uint32 => bool) vars;
        bool public invalid = false;

        function update(uint32 k, bool v) {
                updates_k.push(k);
                updates_v.push(v);
        }

        function apply_updates() {
                while (updates_v.length > 0) {
                        uint32 k = updates_k[updates_k.length-1];
                        updates_k.length--;

                        bool v = updates_v[updates_v.length-1];
                        updates_v.length--;

                        vars[k] = v;
                }
        }

        function sum(uint32[] n) returns (uint32) {
            return 0;
        }

        function check() {
               
if (state == 0) {
	if (!vars[0] && !vars[1] && !vars[2] && vars[3] && !vars[4]) {
		state = 3;
	} else {
		invalid = true;

	}return;
}
if (state == 1) {
	if (!vars[0] && vars[1] && !vars[2] && !vars[3] && !vars[4]) {
		state = 0;
	} else if (!vars[0] && !vars[1] && !vars[2] && !vars[3] && !vars[4]) {
		state = 1;
	} else if (!vars[0] && !vars[1] && !vars[2] && !vars[3] && vars[4]) {
		state = 2;
	} else if (!vars[0] && !vars[1] && !vars[2] && vars[3] && !vars[4]) {
		state = 3;
	} else if (!vars[0] && !vars[1] && vars[2] && !vars[3] && !vars[4] || vars[0] && !vars[1] && !vars[2] && !vars[3] && !vars[4]) {
		state = 4;
	} else {
		invalid = true;

	}return;
}
if (state == 2) {
	if (!vars[0] && vars[1] && !vars[2] && !vars[3] && !vars[4]) {
		state = 0;
	} else if (!vars[0] && !vars[1] && !vars[2] && !vars[3] && vars[4]) {
		state = 2;
	} else if (!vars[0] && !vars[1] && vars[2] && !vars[3] && !vars[4]) {
		state = 4;
	} else {
		invalid = true;

	}return;
}
if (state == 3) {
	if (!vars[0] && !vars[1] && !vars[2] && vars[3] && !vars[4]) {
		state = 3;
	} else if (vars[0] && !vars[1] && !vars[2] && !vars[3] && !vars[4]) {
		state = 4;
	} else {
		invalid = true;

	}return;
}
if (state == 4) {
	if (!vars[0] && !vars[1] && !vars[2] && !vars[3] && vars[4]) {
		state = 2;
	} else if (!vars[0] && !vars[1] && !vars[2] && vars[3] && !vars[4]) {
		state = 3;
	} else {
		invalid = true;

	}return;
} 
        }
}
    

contract TestCasino is Casino {

	constructor() payable {
		BuchiChecker bc = new BuchiChecker();
		buchi_checker_address =	 address(bc);
	}


  function echidna_buchi_check() public view returns(bool){
       BuchiChecker bc = BuchiChecker(buchi_checker_address);
       return !bc.invalid();
  }
}
