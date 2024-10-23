import os, json, requests, logging
from web3 import Web3
logger = logging.getLogger(__name__)

# Connect to the local Hardhat blockchain running in Docker
blockchain_url = "http://127.0.0.1:8545"  # Hardhat default RPC URL
web3 = Web3(Web3.HTTPProvider(blockchain_url))

# Check if the connection is successful
if web3.isConnected():
    logger.debug("Connected to the blockchain.")
else:
    logger.error("Failed to connect to the blockchain.")

# Get the latest block number
latest_block = web3.eth.block_number
logger.debug(f"Latest block number: {latest_block}")