// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

contract LotteryFindNumber {
    address public deployer;
    uint256 public maxPrize;
    uint256 private hiddenNumber;
    
    event GuessAttempt(address indexed player, uint256 guess, bool success);
    event Winner(address indexed player, uint256 prize);
    event MaxPrizeUpdated(uint256 newMaxPrize);
    event HiddenNumberUpdated(uint256 newHiddenNumber);
    event FundsWithdrawn(address indexed deployer, uint256 amount);

    modifier onlyDeployer() {
        require(msg.sender == deployer, "Only deployer can call this function");
        _;
    }

    constructor(uint256 _maxPrize, uint256 _hiddenNumber) payable {
        require(msg.value > 0, "Contract must be initialized with ETH");
        deployer = msg.sender;
        maxPrize = _maxPrize;
        hiddenNumber = _hiddenNumber;
    }

    function updateMaxPrize(uint256 _newMaxPrize) external onlyDeployer {
        require(_newMaxPrize >= address(this).balance / 2, "maxPrize must be at least balance / 2");
        maxPrize = _newMaxPrize;
        emit MaxPrizeUpdated(_newMaxPrize);
    }

    function updateHiddenNumber(uint256 _newHiddenNumber) external onlyDeployer {
        hiddenNumber = _newHiddenNumber;
        emit HiddenNumberUpdated(_newHiddenNumber);
    }

    function withdrawFunds(uint256 _amount) external onlyDeployer {
        require(maxPrize >= address(this).balance / 2, "maxPrize must be valid after withdrawal");
        require(_amount <= address(this).balance, "Insufficient contract balance");
        payable(deployer).transfer(_amount);
        emit FundsWithdrawn(deployer, _amount);
    }

    function viewMaxPrize() external view returns (uint256) {
        return maxPrize;
    }

    function playLottery(uint256 _guess) external payable {
        require(msg.value > 0, "Must send ETH to play");
        
        bool isWinner = (_guess == hiddenNumber);
        
        if (isWinner) {
            uint256 prize = msg.value * 2;
            if (prize > maxPrize) {
                prize = maxPrize;
            }
            payable(msg.sender).transfer(prize);
            hiddenNumber = uint256(keccak256(abi.encodePacked(block.timestamp, msg.sender))) % 1000;
            emit Winner(msg.sender, prize);
        }
        
        emit GuessAttempt(msg.sender, _guess, isWinner);
    }
}
