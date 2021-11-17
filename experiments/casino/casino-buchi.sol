pragma solidity 0.4.26;

contract Casino{

address buchi_checker_address;
    mapping(uint => mapping (uint => address[])) placedBets;
uint prev___pot;
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
bc.update(4, true); // FUNCTION == "openTable" 
        require(msg.sender == owner);
        require(tableOpenTime == 0);
        require(!open);

        tableOpenTime = now;
        open = true;
        tableID++;
bc.apply_updates_and_check();
bc.update(4, false); // FUNCTION == "openTable" 
    }

    function closeTable() public{
BuchiChecker bc = BuchiChecker(buchi_checker_address);
            address prev_bc_address = buchi_checker_address;
bc.update(5, true); // FUNCTION == "closeTable" 
        require(msg.sender == owner);
        require(pot == 0);
        require(open);

        open = false;
        delete numbersGuessed;
bc.apply_updates_and_check();
bc.update(5, false); // FUNCTION == "closeTable" 
    }

    function timeoutBet() public{
BuchiChecker bc = BuchiChecker(buchi_checker_address);
            address prev_bc_address = buchi_checker_address;
bc.update(3, true); // FUNCTION == "timeoutBet" 
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
bc.apply_updates_and_check();
bc.update(3, false); // FUNCTION == "timeoutBet" 
    }

    function placeBet(uint guessNo) payable public{
BuchiChecker bc = BuchiChecker(buchi_checker_address);
            address prev_bc_address = buchi_checker_address;
prev___pot = pot;
bc.update(0, true); // FUNCTION == "placeBet" 
        require(msg.value > 1 ether);
        require(open);

        potShare[tableID][msg.sender] += msg.value;
        placedBets[tableID][guessNo].push(msg.sender);
        numbersGuessed.push(guessNo);
        pot += msg.value;
bc.update(1, (prev___pot < pot));
bc.apply_updates_and_check();
bc.update(0, false); // FUNCTION == "placeBet" 
    }

    //we assume owner is trusted
    function resolveBet(uint _secretNumber) public{
BuchiChecker bc = BuchiChecker(buchi_checker_address);
            address prev_bc_address = buchi_checker_address;
prev___pot = pot;
bc.update(2, true); // FUNCTION == "resolveBet" 
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
bc.update(1, (prev___pot < pot));

        closeTable();
bc.apply_updates_and_check();
bc.update(2, false); // FUNCTION == "resolveBet" 
    }
function initialize(address a) {
        if (address(buchi_checker_address) == address(0)) {
            buchi_checker_address = a;
        }
}
    }



contract BuchiChecker {
        uint256 state = 0;
        uint32[] updates_k;
        bool[] updates_v;
        mapping(uint32 => bool) vars;
        bool public invalid = false;
        
        
        function update(uint32 k, bool v) {
                updates_k.push(k);
                updates_v.push(v);
        }

        function apply_updates_and_check() {
            for (uint i=0; i < updates_v.length; i++) {
                uint32 k = updates_k[i];
                bool v = updates_v[i];
                vars[k] = v;
            }
            updates_k.length = 0;
            updates_v.length = 0;

            
if (state == 0) {
	if (!vars[0] && !vars[2] && !vars[3] && !vars[4] && !vars[5]) {
		state = 0;
	} else if (!vars[0] && vars[2] && vars[5] || !vars[0] && vars[3] && vars[5] || !vars[0] && vars[4] && vars[5]) {
		state = 1;
	} else if (!vars[0] && !vars[2] && !vars[3] && !vars[4] && vars[5]) {
		state = 2;
	} else if (!vars[0] && vars[2] && !vars[5] || !vars[0] && vars[3] && !vars[5] || !vars[0] && vars[4] && !vars[5]) {
		state = 3;
	} else if (vars[0] && vars[1] && vars[2] && vars[5] || vars[0] && vars[1] && vars[3] && vars[5] || vars[0] && vars[1] && vars[4] && vars[5]) {
		state = 4;
	} else if (vars[0] && vars[1] && !vars[2] && !vars[3] && !vars[4] && vars[5]) {
		state = 5;
	} else if (vars[0] && vars[1] && vars[2] && !vars[5] || vars[0] && vars[1] && vars[3] && !vars[5] || vars[0] && vars[1] && vars[4] && !vars[5]) {
		state = 6;
	} else if (vars[0] && vars[1] && !vars[2] && !vars[3] && !vars[4] && !vars[5]) {
		state = 7;
	} else {
		revert("Invalid Buchi State");
	}
	return;
}
if (state == 1) {
	if (!vars[0] && vars[4] && vars[5]) {
		state = 1;
	} else if (vars[0] && vars[1] && vars[4] && vars[5]) {
		state = 4;
	} else if (vars[0] && vars[1] && vars[4] && !vars[5]) {
		state = 6;
	} else {
		revert("Invalid Buchi State");
	}
	return;
}
if (state == 2) {
	if (!vars[0] && vars[4] && vars[5]) {
		state = 1;
	} else if (!vars[0] && vars[4] && !vars[5]) {
		state = 3;
	} else if (vars[0] && vars[1] && vars[4] && vars[5]) {
		state = 4;
	} else if (vars[0] && vars[1] && vars[4] && !vars[5]) {
		state = 6;
	} else {
		revert("Invalid Buchi State");
	}
	return;
}
if (state == 3) {
	if (!vars[0] && vars[2] && vars[5] || !vars[0] && vars[3] && vars[5] || !vars[0] && vars[4] && vars[5]) {
		state = 1;
	} else if (!vars[0] && !vars[2] && !vars[3] && !vars[4] && vars[5]) {
		state = 2;
	} else if (vars[0] && vars[1] && vars[2] && vars[5] || vars[0] && vars[1] && vars[3] && vars[5] || vars[0] && vars[1] && vars[4] && vars[5]) {
		state = 4;
	} else if (vars[0] && vars[1] && !vars[2] && !vars[3] && !vars[4] && vars[5]) {
		state = 5;
	} else if (vars[0] && vars[1] && vars[2] && !vars[5] || vars[0] && vars[1] && vars[3] && !vars[5] || vars[0] && vars[1] && vars[4] && !vars[5]) {
		state = 6;
	} else if (vars[0] && vars[1] && !vars[2] && !vars[3] && !vars[4] && !vars[5]) {
		state = 7;
	} else {
		revert("Invalid Buchi State");
	}
	return;
}
if (state == 4) {
	if (!vars[0] && vars[2] && vars[4] && vars[5] || !vars[0] && vars[3] && vars[4] && vars[5]) {
		state = 1;
	} else if (vars[0] && vars[1] && vars[2] && vars[4] && vars[5] || vars[0] && vars[1] && vars[3] && vars[4] && vars[5]) {
		state = 4;
	} else if (vars[0] && vars[1] && vars[2] && vars[4] && !vars[5] || vars[0] && vars[1] && vars[3] && vars[4] && !vars[5]) {
		state = 6;
	} else {
		revert("Invalid Buchi State");
	}
	return;
}
if (state == 5) {
	if (!vars[0] && vars[2] && vars[4] && vars[5] || !vars[0] && vars[3] && vars[4] && vars[5]) {
		state = 1;
	} else if (!vars[0] && vars[2] && vars[4] && !vars[5] || !vars[0] && vars[3] && vars[4] && !vars[5]) {
		state = 3;
	} else if (vars[0] && vars[1] && vars[2] && vars[4] && vars[5] || vars[0] && vars[1] && vars[3] && vars[4] && vars[5]) {
		state = 4;
	} else if (vars[0] && vars[1] && vars[2] && vars[4] && !vars[5] || vars[0] && vars[1] && vars[3] && vars[4] && !vars[5]) {
		state = 6;
	} else {
		revert("Invalid Buchi State");
	}
	return;
}
if (state == 6) {
	if (!vars[0] && vars[2] && vars[5] || !vars[0] && vars[3] && vars[5]) {
		state = 1;
	} else if (vars[0] && vars[1] && vars[2] && vars[5] || vars[0] && vars[1] && vars[3] && vars[5]) {
		state = 4;
	} else if (vars[0] && vars[1] && vars[2] && !vars[5] || vars[0] && vars[1] && vars[3] && !vars[5]) {
		state = 6;
	} else {
		revert("Invalid Buchi State");
	}
	return;
}
if (state == 7) {
	if (!vars[0] && vars[2] && vars[5] || !vars[0] && vars[3] && vars[5]) {
		state = 1;
	} else if (!vars[0] && vars[2] && !vars[5] || !vars[0] && vars[3] && !vars[5]) {
		state = 3;
	} else if (vars[0] && vars[1] && vars[2] && vars[5] || vars[0] && vars[1] && vars[3] && vars[5]) {
		state = 4;
	} else if (vars[0] && vars[1] && vars[2] && !vars[5] || vars[0] && vars[1] && vars[3] && !vars[5]) {
		state = 6;
	} else {
		revert("Invalid Buchi State");
	}
	return;
} 
        }
}
    

contract TestCasino is Casino {

	constructor() payable {
		BuchiChecker bc = new BuchiChecker();
		buchi_checker_address =	 address(bc);
	}


  function echidna_dummy() public view returns(bool){
       return true;
  }
}
