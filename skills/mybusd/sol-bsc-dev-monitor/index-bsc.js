#!/usr/bin/env node

const { ethers } = require('ethers');
const axios = require('axios');
const fs = require('fs');
const path = require('path');
const { getPrivateKey } = require('./utils.js');

const CONFIG = {
  BSC_RPC: process.env.BSC_RPC || 'https://bsc-dataseed.binance.org',
  PANKCAKESWAP_ROUTER: '0x10ED43C718714eb63d5aA57B78B54704E256024E',
  WBNB_ADDRESS: '0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c',
  MONITOR_INTERVAL: 3000,
  DEFAULT_DURATION: 3600
};

const LOG_DIR = path.join(__dirname, 'logs-bsc');
const DETECTIONS_DIR = path.join(__dirname, 'detections-bsc');

if (!fs.existsSync(LOG_DIR)) fs.mkdirSync(LOG_DIR, { recursive: true });
if (!fs.existsSync(DETECTIONS_DIR)) fs.mkdirSync(DETECTIONS_DIR, { recursive: true });

function loadDetections() {
  const detectionsFile = path.join(DETECTIONS_DIR, 'detections.json');
  if (fs.existsSync(detectionsFile)) {
    try {
      const data = fs.readFileSync(detectionsFile, 'utf8');
      return JSON.parse(data);
    } catch (error) {
      return [];
    }
  }
  return [];
}

function saveDetections(detections) {
  const detectionsFile = path.join(DETECTIONS_DIR, 'detections.json');
  const trimmedDetections = detections.slice(-1000);
  try {
    fs.writeFileSync(
      detectionsFile,
      JSON.stringify(trimmedDetections, null, 2)
    );
  } catch (error) {
    console.log(`Error saving detections: ${error.message}`);
  }
}

function log(message, level = 'INFO') {
  const timestamp = new Date().toISOString();
  const logMessage = `[${timestamp}] [${level}] ${message}`;
  console.log(logMessage);
  
  const logFile = path.join(LOG_DIR, 'bsc-monitor.log');
  fs.appendFileSync(logFile, logMessage + '\n');
}

async function monitorBSC(input) {
  const { address, duration, autoBuy } = input;
  const monitorDuration = duration || CONFIG.DEFAULT_DURATION;
  const startTime = Date.now();
  
  log(`📊 Starting BSC monitoring for address: ${address}`);
  log(`📊 Monitoring duration: ${monitorDuration} seconds`);
  
  const provider = new ethers.JsonRpcProvider(CONFIG.BSC_RPC);
  const autoBuyEnabled = autoBuy?.enabled === true;
  
  if (autoBuyEnabled) {
    log(`🛒 Auto-Buy enabled`);
    log(`💰 Amount: ${autoBuy.amount || '0.1'} BNB`);
    log(`⚡ Slippage: ${autoBuy.slippage || 5}%`);
  }
  
  let lastBlockNumber = await provider.getBlockNumber();
  log(`📊 Starting block number: ${lastBlockNumber}`);
  
  const endTime = startTime + (monitorDuration * 1000);
  let blocksScanned = 0;
  let detections = loadDetections();
  let autoBuys = [];
  
  while (Date.now() < endTime) {
    try {
      const currentBlock = await provider.getBlock('latest');
      const currentBlockNumber = currentBlock.number;
      
      if (currentBlockNumber > lastBlockNumber) {
        for (let i = lastBlockNumber + 1; i <= currentBlockNumber; i++) {
          const block = await provider.getBlock(i, true);
          
          if (block && block.transactions) {
            for (const tx of block.transactions) {
              if (tx.from.toLowerCase() === address.toLowerCase()) {
                const detected = await checkTransaction(tx, address);
                
                if (detected) {
                  log(`🎉 Detection found! Block: ${i}, Hash: ${tx.hash}`);
                  
                  const detection = {
                    chain: 'BSC',
                    blockNumber: i,
                    hash: tx.hash,
                    from: tx.from,
                    to: tx.to,
                    tokenAddress: tx.to,
                    timestamp: new Date().toISOString()
                  };
                  
                  detections.push(detection);
                  saveDetections(detections);
                  
                  if (autoBuyEnabled && tx.to) {
                    log(`🛒 Attempting auto-buy...`);
                    const autoBuyResult = await autoBuyToken(
                      tx.to,
                      autoBuy.amount || '10',
                      autoBuy.slippage || 5
                    );
                    
                    autoBuys.push({
                      detectionHash: tx.hash,
                      autoBuy: autoBuyResult
                    });
                  }
                }
              }
            }
          }
        }
        
        lastBlockNumber = currentBlockNumber;
        blocksScanned += currentBlockNumber - lastBlockNumber;
      }
      
      await new Promise(resolve => setTimeout(resolve, CONFIG.MONITOR_INTERVAL));
      
    } catch (error) {
      log(`❌ Error checking block ${lastBlockNumber}: ${error.message}`);
      lastBlockNumber++;
    }
  }
  
  const actualDuration = ((Date.now() - startTime) / 1000).toFixed(2);
  
  log(`📊 BSC monitoring completed`);
  log(`📊 Duration: ${actualDuration} seconds`);
  log(`📊 Blocks scanned: ${blocksScanned}`);
  log(`📊 Total detections: ${detections.length}`);
  log(`📊 Auto-buys executed: ${autoBuys.length}`);
  
  return {
    success: true,
    chain: 'BSC',
    monitoring: {
      address,
      startTime: new Date(startTime).toISOString(),
      endTime: new Date().toISOString(),
      duration: monitorDuration,
      actualDuration,
      blocksScanned,
      detections,
      autoBuys
    }
  };
}

async function checkTransaction(tx, targetAddress) {
  try {
    if (tx.from.toLowerCase() === targetAddress.toLowerCase()) {
      if (tx.to && tx.to !== targetAddress) {
        const tokenInfo = await getTokenInfo(tx.to);
        
        log(`💰 Token transfer detected from ${tx.from} to ${tx.to}`);
        log(`📝 Token: ${tokenInfo.name || 'Unknown'} (${tokenInfo.symbol || 'UNKNOWN'})`);
        
        return {
          hash: tx.hash,
          from: tx.from,
          to: tx.to,
          tokenAddress: tx.to,
          tokenName: tokenInfo.name,
          tokenSymbol: tokenInfo.symbol,
          decimals: tokenInfo.decimals
        };
      }
    }
    
    return null;
  } catch (error) {
    log(`❌ Error checking transaction: ${error.message}`);
    return null;
  }
}

async function getTokenInfo(tokenAddress) {
  try {
    const tokenContract = new ethers.Contract(tokenAddress, [
      'function name() external view returns (string)',
      'function symbol() external view returns (string)',
      'function decimals() external view returns (uint8)'
    ], new ethers.JsonRpcProvider(CONFIG.BSC_RPC));
    
    const [name, symbol, decimals] = await Promise.all([
      tokenContract.name().catch(() => Promise.resolve('Unknown')),
      tokenContract.symbol().catch(() => Promise.resolve('UNKNOWN')),
      tokenContract.decimals().catch(() => Promise.resolve(18))
    ]);
    
    return { name, symbol, decimals };
  } catch (error) {
    log(`❌ Error getting token info: ${error.message}`);
    return { name: 'Unknown', symbol: 'UNKNOWN', decimals: 18 };
  }
}

async function autoBuyToken(tokenAddress, amount, slippage) {
  try {
    const privateKey = await getPrivateKey('WALLET_PRIVATE_KEY', 'Enter your BSC wallet private key (0x...)');
    if (!privateKey) {
      log(`❌ Wallet private key not provided`);
      return { success: false, error: 'Wallet private key not provided' };
    }
    
    const provider = new ethers.JsonRpcProvider(CONFIG.BSC_RPC);
    const wallet = new ethers.Wallet(privateKey, provider);
    
    const router = new ethers.Contract(
      CONFIG.PANKCAKESWAP_ROUTER,
      [
        'function swapExactETHForTokens(uint amountOutMin, address[] calldata path, address to, uint deadline) external payable returns (uint[] memory amounts)',
        'function getAmountsOut(uint amountIn, address[] calldata path) external view returns (uint[] memory amounts)'
      ],
      wallet
    );
    
    const amountIn = ethers.utils.parseEther(amount);
    const path = [CONFIG.WBNB_ADDRESS, tokenAddress];
    
    // Get expected output amount
    const amountsOut = await router.getAmountsOut(amountIn, path);
    const minAmountOut = amountsOut[1].mul(100 - slippage).div(100);
    
    log(`🛒 Swapping ${amount} BNB for token...`);
    
    const gasPrice = await provider.getGasPrice();
    const gasLimit = ethers.utils.hexlify(300000);
    
    const swapTx = await router.swapExactETHForTokens(
      minAmountOut,
      path,
      wallet.address,
      Math.floor(Date.now() / 1000) + 60 * 20,
      {
        value: amountIn,
        gasPrice: gasPrice,
        gasLimit: gasLimit
      }
    );
    
    const receipt = await swapTx.wait();
    log(`✅ Auto-buy completed! Hash: ${receipt.transactionHash}`);
    
    return {
      success: true,
      transactionHash: receipt.transactionHash,
      gasUsed: receipt.gasUsed.toString(),
      gasPrice: gasPrice.toString(),
      amountIn: amount,
      amountOut: minAmountOut.toString()
    };
    
  } catch (error) {
    log(`❌ Auto-buy failed: ${error.message}`);
    return { success: false, error: error.message };
  }
}

module.exports = { monitorBSC, autoBuyToken };

if (require.main === module) {
  const action = process.argv[2] || 'monitor';
  const address = process.argv[3];
  const chain = process.argv[4] || 'BSC';
  const duration = process.argv[5] ? parseInt(process.argv[5]) : undefined;
  
  monitorBSC({ address, chain, duration }).then(result => {
    console.log(JSON.stringify(result, null, 2));
  }).catch(error => {
    console.error('Error:', error);
    process.exit(1);
  });
}
