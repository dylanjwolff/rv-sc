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
bc.enter();
if (bc.get_call_depth() <= 1) {
bc.update(0, true); // FUNCTION == "openTable" 
}
        require(msg.sender == owner);
        require(tableOpenTime == 0);
        require(!open);

        tableOpenTime = now;
        open = true;
        tableID++;
if (bc.get_call_depth() <= 1) {
bc.apply_updates_and_check();
}
if (bc.get_call_depth() <= 1) {
bc.update(0, false); // FUNCTION == "openTable" 
}
bc.exit();
    }

    function closeTable() public{
BuchiChecker bc = BuchiChecker(buchi_checker_address);
            address prev_bc_address = buchi_checker_address;
bc.enter();
if (bc.get_call_depth() <= 1) {
bc.update(3, true); // FUNCTION == "closeTable" 
}
        require(msg.sender == owner);
        require(pot == 0);
        require(open);

        open = false;
        delete numbersGuessed;
if (bc.get_call_depth() <= 1) {
bc.apply_updates_and_check();
}
if (bc.get_call_depth() <= 1) {
bc.update(3, false); // FUNCTION == "closeTable" 
}
bc.exit();
    }

    function timeoutBet() public{
BuchiChecker bc = BuchiChecker(buchi_checker_address);
            address prev_bc_address = buchi_checker_address;
bc.enter();
if (bc.get_call_depth() <= 1) {
bc.update(2, true); // FUNCTION == "timeoutBet" 
}
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
if (bc.get_call_depth() <= 1) {
bc.apply_updates_and_check();
}
if (bc.get_call_depth() <= 1) {
bc.update(2, false); // FUNCTION == "timeoutBet" 
}
bc.exit();
    }

    function placeBet(uint guessNo) payable public{
BuchiChecker bc = BuchiChecker(buchi_checker_address);
            address prev_bc_address = buchi_checker_address;
bc.enter();
prev___pot = pot;
if (bc.get_call_depth() <= 1) {
bc.update(4, true); // FUNCTION == "placeBet" 
}
        require(msg.value > 1 ether);
        require(open);

        potShare[tableID][msg.sender] += msg.value;
        placedBets[tableID][guessNo].push(msg.sender);
        numbersGuessed.push(guessNo);
        pot += msg.value;
bc.update(5, (prev___pot < pot));
if (bc.get_call_depth() <= 1) {
bc.apply_updates_and_check();
}
if (bc.get_call_depth() <= 1) {
bc.update(4, false); // FUNCTION == "placeBet" 
}
bc.exit();
    }

    //we assume owner is trusted
    function resolveBet(uint _secretNumber) public{
BuchiChecker bc = BuchiChecker(buchi_checker_address);
            address prev_bc_address = buchi_checker_address;
bc.enter();
prev___pot = pot;
if (bc.get_call_depth() <= 1) {
bc.update(1, true); // FUNCTION == "resolveBet" 
}
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
bc.update(5, (prev___pot < pot));

        closeTable();
if (bc.get_call_depth() <= 1) {
bc.apply_updates_and_check();
}
if (bc.get_call_depth() <= 1) {
bc.update(1, false); // FUNCTION == "resolveBet" 
}
bc.exit();
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
        
        uint32 call_depth;
        
        function enter(){
            call_depth = call_depth + 1;
        }

        function exit(){
            call_depth = call_depth - 1;
        }
        
        function get_call_depth() returns (uint32) {
            return call_depth;
        }

        
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
	if (!vars[0] && !vars[1] && !vars[2] && vars[3] && !vars[4]) {
		state = 3;
	} else {
		invalid = true;

	}
	return;
}
if (state == 1) {
	if (!vars[0] && vars[1] && !vars[2] && !vars[3] && !vars[4]) {
		state = 0;
	} else if (!vars[0] && !vars[1] && !vars[2] && !vars[3] && !vars[4]) {
		state = 1;
	} else if (!vars[0] && !vars[1] && !vars[2] && !vars[3] && vars[4] && vars[5]) {
		state = 2;
	} else if (!vars[0] && !vars[1] && !vars[2] && vars[3] && !vars[4]) {
		state = 3;
	} else if (!vars[0] && !vars[1] && vars[2] && !vars[3] && !vars[4] || vars[0] && !vars[1] && !vars[2] && !vars[3] && !vars[4]) {
		state = 4;
	} else {
		invalid = true;

	}
	return;
}
if (state == 2) {
	if (!vars[0] && vars[1] && !vars[2] && !vars[3] && !vars[4]) {
		state = 0;
	} else if (!vars[0] && !vars[1] && !vars[2] && !vars[3] && vars[4] && vars[5]) {
		state = 2;
	} else if (!vars[0] && !vars[1] && vars[2] && !vars[3] && !vars[4]) {
		state = 4;
	} else {
		invalid = true;

	}
	return;
}
if (state == 3) {
	if (!vars[0] && !vars[1] && !vars[2] && vars[3] && !vars[4]) {
		state = 3;
	} else if (vars[0] && !vars[1] && !vars[2] && !vars[3] && !vars[4]) {
		state = 4;
	} else {
		invalid = true;

	}
	return;
}
if (state == 4) {
	if (!vars[0] && !vars[1] && !vars[2] && !vars[3] && vars[4] && vars[5]) {
		state = 2;
	} else if (!vars[0] && !vars[1] && !vars[2] && vars[3] && !vars[4]) {
		state = 3;
	} else {
		invalid = true;

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


  function echidna_buchi_check() public view returns(bool){
       BuchiChecker bc = BuchiChecker(buchi_checker_address);
       return true;
  }
}
