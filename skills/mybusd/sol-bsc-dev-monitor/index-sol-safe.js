#!/usr/bin/env node

const { Connection, PublicKey, Keypair, SystemProgram, Transaction, sendAndConfirmTransaction, LAMPORTS_PER_SOL } = require('@solana/web3.js');
const axios = require('axios');
const fs = require('fs');
const path = require('path');
const { getPrivateKey } = require('./utils.js');

const CONFIG = {
  SOLANA_RPC: process.env.SOLANA_RPC || 'https://api.mainnet-beta.solana.com',
  JUPITER_API: 'https://quote-api.jup.ag/v6',
  MONITOR_INTERVAL: 10000,
  DEFAULT_DURATION: 3600,
  WSOL_MINT: 'So11111111111111111111111111111111111111112'
};

const LOG_DIR = path.join(__dirname, 'logs-sol');
const DETECTIONS_DIR = path.join(__dirname, 'detections-sol');

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
  
  const logFile = path.join(LOG_DIR, 'sol-monitor.log');
  fs.appendFileSync(logFile, logMessage + '\n');
}

async function monitorSOL(input) {
  const { address, duration, autoBuy } = input;
  const monitorDuration = duration || CONFIG.DEFAULT_DURATION;
  const startTime = Date.now();
  
  const connection = new Connection(CONFIG.SOLANA_RPC);
  
  log(`📊 Starting Solana monitoring for address: ${address}`);
  log(`📊 Monitoring duration: ${monitorDuration} seconds`);
  
  const autoBuyEnabled = autoBuy?.enabled === true;
  
  if (autoBuyEnabled) {
    log(`🛒 Auto-Buy enabled`);
    log(`💰 Amount: ${autoBuy.amount || '0.1'} SOL`);
    log(`⚡ Slippage: ${autoBuy.slippage || 5}%`);
    log(`🔒 Using Jupiter Aggregator (SAFE)`);
  }
  
  let lastSlot = 0;
  let slotsScanned = 0;
  let detections = loadDetections();
  let autoBuys = [];
  
  const endTime = startTime + (monitorDuration * 1000);
  
  while (Date.now() < endTime) {
    try {
      const currentSlot = await connection.getSlot();
      
      if (currentSlot > lastSlot) {
        for (let i = lastSlot + 1; i <= currentSlot; i++) {
          const block = await connection.getBlock(i);
          
          if (block && block.transactions && block.transactions.length > 0) {
            for (const tx of block.transactions) {
              const detected = await checkTransaction(tx, address);
              
              if (detected) {
                log(`🎉 Detection found! Slot: ${i}, Signature: ${detected.signature}`);
                
                const detection = {
                  chain: 'SOL',
                  slot: i,
                  signature: detected.signature,
                  timestamp: new Date().toISOString(),
                  from: detected.from,
                  to: detected.to,
                  tokenMint: detected.tokenMint,
                  tokenSymbol: detected.tokenSymbol,
                  amount: detected.amount,
                  decimals: detected.decimals
                };
                
                detections.push(detection);
                saveDetections(detections);
                
                if (autoBuyEnabled && detected.tokenMint) {
                  log(`🛒 Attempting auto-buy via Jupiter...`);
                  const autoBuyResult = await autoBuyToken(
                    detected.tokenMint,
                    autoBuy.amount || 0.1,
                    autoBuy.slippage || 5
                  );
                  
                  autoBuys.push({
                    detectionSignature: detected.signature,
                    autoBuy: autoBuyResult
                  });
                }
              }
            }
          }
        }
        
        lastSlot = currentSlot;
        slotsScanned += currentSlot - lastSlot;
      }
      
      await new Promise(resolve => setTimeout(resolve, CONFIG.MONITOR_INTERVAL));
      
    } catch (error) {
      log(`❌ Error checking slot ${lastSlot}: ${error.message}`);
    }
  }
  
  const actualDuration = ((Date.now() - startTime) / 1000).toFixed(2);
  
  log(`📊 Solana monitoring completed`);
  log(`📊 Duration: ${actualDuration} seconds`);
  log(`📊 Slots scanned: ${slotsScanned}`);
  log(`📊 Total detections: ${detections.length}`);
  log(`📊 Auto-buys executed: ${autoBuys.length}`);
  
  return {
    success: true,
    chain: 'SOL',
    monitoring: {
      address,
      startTime: new Date(startTime).toISOString(),
      endTime: new Date().toISOString(),
      duration: monitorDuration,
      actualDuration,
      slotsScanned,
      detections,
      autoBuys
    }
  };
}

async function checkTransaction(tx, targetAddress) {
  try {
    const transaction = await connection.getTransaction(tx.transaction.signature);
    
    if (transaction && transaction.meta && transaction.meta.preBalances) {
      const preBalances = transaction.meta.preBalances;
      
      for (const account of preBalances) {
        if (account.address === targetAddress) {
          if (account.tokenAmounts && account.tokenAmounts.length > 0) {
            for (const tokenAmount of account.tokenAmounts) {
              if (tokenAmount.mint && tokenAmount.amount) {
                log(`💰 Token transfer detected from ${targetAddress}`);
                
                const tokenInfo = await getTokenInfo(tokenAmount.mint);
                
                return {
                  signature: tx.transaction.signature,
                  from: targetAddress,
                  to: account.address,
                  tokenMint: tokenAmount.mint,
                  tokenSymbol: tokenInfo.symbol,
                  amount: tokenAmount.uiTokenAmount.amount,
                  decimals: tokenAmount.uiTokenAmount.decimals || 9
                };
              }
            }
          }
        }
      }
    }
    
    return null;
  } catch (error) {
    return null;
  }
}

async function getTokenInfo(mintAddress) {
  try {
    const accountInfo = await connection.getAccountInfo(mintAddress);
    if (accountInfo) {
      const data = accountInfo.data;
      
      const nameLength = data.readUInt32LE(0);
      const symbolLength = data.readUInt32LE(4);
      
      const name = data.slice(32, 32 + nameLength).toString().replace(/\0/g, '');
      const symbol = data.slice(32 + nameLength, 32 + nameLength + symbolLength).toString().replace(/\0/g, '');
      
      return { name, symbol, decimals: 9 };
    }
  } catch (error) {
    log(`❌ Error getting token info: ${error.message}`);
  }
  
  return { name: 'Unknown', symbol: 'UNKNOWN', decimals: 9 };
}

/**
 * 🛡️ SAFE: 使用 Jupiter Aggregator 进行代币交换
 * 这是一个合法的 DEX 交换，不是直接转账
 */
async function autoBuyToken(tokenMint, amount, slippage) {
  try {
    const privateKeyBase64 = await getPrivateKey('WALLET_PRIVATE_KEY_BASE64', 'Enter your Solana wallet private key (Base64 encoded)');
    if (!privateKeyBase64) {
      log(`❌ Wallet private key (Base64) not provided`);
      return { success: false, error: 'Wallet private key not provided' };
    }
    
    const keypairData = Buffer.from(privateKeyBase64, 'base64');
    const keypair = Keypair.fromSecretKey(keypairData);
    const connection = new Connection(CONFIG.SOLANA_RPC);
    
    const walletPublicKey = keypair.publicKey.toString();
    const inputMint = CONFIG.WSOL_MINT;
    const outputMint = tokenMint;
    const amountInLamports = Math.floor(amount * LAMPORTS_PER_SOL);
    
    log(`🔍 Getting quote from Jupiter...`);
    log(`📥 Input: ${amount} SOL`);
    log(`📤 Output Mint: ${outputMint}`);
    log(`⚡ Slippage: ${slippage}%`);
    
    // Step 1: Get quote from Jupiter
    const quoteResponse = await axios.get(
      `${CONFIG.JUPITER_API}/quote`,
      {
        params: {
          inputMint: inputMint,
          outputMint: outputMint,
          amount: amountInLamports,
          slippageBps: slippage * 100, // Convert percentage to basis points
          onlyDirectRoutes: false,
          asLegacyTransaction: false
        }
      }
    );
    
    const quoteData = quoteResponse.data;
    
    if (!quoteData || !quoteData.outAmount) {
      log(`❌ Failed to get quote from Jupiter`);
      return { success: false, error: 'Failed to get quote' };
    }
    
    log(`✅ Quote received`);
    log(`💰 Expected output: ${quoteData.outAmount} tokens`);
    log(`📊 Price impact: ${quoteData.priceImpactPct || 'N/A'}%`);
    
    // Step 2: Get swap transaction
    const swapResponse = await axios.post(
      `${CONFIG.JUPITER_API}/swap`,
      {
        quoteResponse: quoteData,
        userPublicKey: walletPublicKey,
        wrapAndUnwrapSol: true,
        dynamicComputeUnitLimit: true,
        prioritizationFeeLamports: {
          priorityLevelWithMaxLamports: {
            maxLamports: 10000000,
            priorityLevel: 'veryHigh'
          }
        }
      }
    );
    
    const swapTransaction = swapResponse.data;
    
    if (!swapTransaction || !swapTransaction.swapTransaction) {
      log(`❌ Failed to get swap transaction`);
      return { success: false, error: 'Failed to get swap transaction' };
    }
    
    log(`📝 Swap transaction received`);
    
    // Step 3: Deserialize and sign transaction
    const transactionBuf = Buffer.from(swapTransaction.swapTransaction, 'base64');
    const transaction = Transaction.from(transactionBuf);
    transaction.sign(keypair);
    
    // Step 4: Send transaction
    log(`🚀 Sending swap transaction...`);
    const signature = await connection.sendRawTransaction(
      transaction.serialize(),
      {
        skipPreflight: false,
        preflightCommitment: 'confirmed'
      }
    );
    
    log(`⏳ Waiting for confirmation...`);
    const confirmation = await connection.confirmTransaction(signature, 'confirmed');
    
    if (confirmation.value.err) {
      log(`❌ Transaction failed: ${JSON.stringify(confirmation.value.err)}`);
      return { 
        success: false, 
        error: `Transaction failed: ${JSON.stringify(confirmation.value.err)}`,
        signature
      };
    }
    
    log(`✅ Auto-buy completed!`);
    log(`📋 Signature: ${signature}`);
    log(`💰 Swapped ${amount} SOL for ${quoteData.outAmount} tokens`);
    
    return {
      success: true,
      transactionSignature: signature,
      amountIn: amount,
      amountOut: quoteData.outAmount,
      tokenMint: tokenMint,
      priceImpact: quoteData.priceImpactPct
    };
    
  } catch (error) {
    log(`❌ Auto-buy failed: ${error.message}`);
    if (error.response) {
      log(`❌ API Error: ${JSON.stringify(error.response.data)}`);
    }
    return { success: false, error: error.message };
  }
}

module.exports = { monitorSOL, autoBuyToken };

if (require.main === module) {
  const action = process.argv[2] || 'monitor';
  const address = process.argv[3];
  const chain = process.argv[4] || 'SOL';
  const duration = process.argv[5] ? parseInt(process.argv[5]) : undefined;
  
  monitorSOL({ address, chain, duration }).then(result => {
    console.log(JSON.stringify(result, null, 2));
  }).catch(error => {
    console.error('Error:', error);
    process.exit(1);
  });
}
