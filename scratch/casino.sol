pragma solidity 0.4.26;

contract Casino{

    mapping(uint => mapping (uint => address[])) placedBets;
    mapping(uint => mapping(address => uint)) potShare;

    uint[] numbersGuessed;
    
    uint pot;

    uint tableID;
    uint tableOpenTime;

    address owner;

    constructor() public{
        owner = msg.sender;
    }

    function openTable() public{
        require(msg.sender == owner);
        require(tableOpenTime == 0);

        tableOpenTime = now;
        tableID++;
    }

    function closeTable() public{
        require(msg.sender == owner);
        require(pot == 0);

        delete numbersGuessed;
    }

    function timeoutBet() public{
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

    function placeBet(uint guessNo) payable public{
        require(msg.value > 1 ether);

        potShare[tableID][msg.sender] += msg.value;
        placedBets[tableID][guessNo].push(msg.sender);
        numbersGuessed.push(guessNo);
        pot += msg.value;
    }

    //we assume owner is trusted
    function resolveBet(uint _secretNumber) public{
        require(msg.sender == owner);

        uint l = placedBets[tableID][_secretNumber].length;
        if(l != 0){
            for (uint i = 0; i < l; i++) {
                placedBets[tableID][_secretNumber][i].transfer(pot/l);
            }
        }

        pot = 0;

        closeTable();
    }
}
