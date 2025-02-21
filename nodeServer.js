// nodeServer.js
const express = require('express');
const bodyParser = require('body-parser');
const axios = require('axios');
const app = express();
const PORT = process.env.PORT || 3000;

app.use(bodyParser.json());

// In-memory blockchain (for demo purposes)
let blockchain = [{
  index: 0,
  previousHash: '0',
  transactions: ['Genesis Block'],
  validator: 'Network'
}];

// In-memory staking pool: { validatorAddress: stakeAmount }
let stakingPool = {};

// Endpoint to retrieve the blockchain
app.get('/chain', (req, res) => {
  res.json(blockchain);
});

// Endpoint to retrieve current staking pool
app.get('/staking-pool', (req, res) => {
  res.json(stakingPool);
});

// Endpoint to allow staking: expects JSON payload: { "validator": "Validator-1", "amount": 50 }
app.post('/stake', (req, res) => {
  const { validator, amount } = req.body;
  if (!validator || !amount) {
    return res.status(400).json({ error: "Validator and amount are required" });
  }
  
  const numericAmount = Number(amount);
  if (isNaN(numericAmount) || numericAmount <= 0) {
    return res.status(400).json({ error: "Amount must be a positive number" });
  }
  
  if (stakingPool[validator]) {
    stakingPool[validator] += numericAmount;
  } else {
    stakingPool[validator] = numericAmount;
  }
  
  res.json({ message: `Validator ${validator} staked ${numericAmount} tokens`, stakingPool });
});

// List of peer nodes (set via environment variable, e.g., "3002,3003")
const peers = process.env.PEERS ? process.env.PEERS.split(',') : [];

// Weighted random selection algorithm for validators
function selectValidatorWeighted() {
  const entries = Object.entries(stakingPool);
  if (entries.length === 0) {
    return null; // Fallback if no validator has staked yet
  }
  const totalStake = entries.reduce((sum, [, stake]) => sum + stake, 0);
  let randomValue = Math.random() * totalStake;
  for (const [validator, stake] of entries) {
    randomValue -= stake;
    if (randomValue <= 0) {
      return validator;
    }
  }
  return null;
}

// Endpoint to receive a new block from peers
app.post('/block', (req, res) => {
  const newBlock = req.body;
  // In production, add proper validation here!
  blockchain.push(newBlock);
  console.log(`Block added: ${newBlock.index}`);
  res.sendStatus(200);
});

// Endpoint to simulate creating a new block (PoS simulation)
app.post('/create-block', (req, res) => {
  const lastBlock = blockchain[blockchain.length - 1];
  
  // Select validator using weighted stake selection; fallback to environment variable if no stake exists
  const selectedValidator = selectValidatorWeighted() || process.env.VALIDATOR || `Validator-${PORT}`;
  
  const newBlock = {
    index: lastBlock.index + 1,
    previousHash: lastBlock.hash || 'dummy-hash', // Simplified hash for demonstration
    transactions: req.body.transactions || ["Dummy Transaction"],
    validator: selectedValidator
  };
  
  blockchain.push(newBlock);
  
  // Broadcast new block to peers
  peers.forEach(peer => {
    axios.post(`http://localhost:${peer}/block`, newBlock)
      .then(() => console.log(`Broadcasted block to ${peer}`))
      .catch(err => console.error(`Error broadcasting to ${peer}: ${err.message}`));
  });
  
  res.json(newBlock);
});

app.listen(PORT, () => {
  console.log(`Node running on port ${PORT}`);
});
