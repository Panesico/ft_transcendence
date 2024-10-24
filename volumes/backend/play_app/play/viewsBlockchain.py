import os, json, requests, logging
from django.utils import timezone
from django.http import JsonResponse
from web3 import Web3
logger = logging.getLogger(__name__)

web3 = Web3(Web3.HTTPProvider("http://blockchain:8545"))

def create_tournament_in_blockchain(contract, tournament_id, users_ids, web3):
  logger.debug("")
  logger.debug("create_tournament_in_blockchain")

  # Get the contract's account
  # logger.debug(f"Account: {account}")
  try:
    account = web3.eth.account.from_key(os.getenv('CONTRACT_PRIVATE_KEY')).address
    tx = contract.functions.createTournament(tournament_id, users_ids).build_transaction({
        'from': account,
        'gas': 1000000,
        'nonce': web3.eth.get_transaction_count(account),
    })
    # logger.debug(f"Transaction: {tx}")

    # Sign and send the transaction
    signed_tx = web3.eth.account.sign_transaction(tx, private_key=os.getenv('CONTRACT_PRIVATE_KEY'))
    tx_hash = web3.eth.send_raw_transaction(signed_tx.raw_transaction)

    # Wait for the transaction to be mined
    tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
  # logger.debug(f"Transaction receipt: {tx_receipt}")
  except Exception as e:
    logger.error(f"createTournament function reverted : {e}")

def update_user_score_in_blockchain(contract, tournament_id, user_id, score, web3):
  logger.debug("")
  logger.debug("update_user_score_in_blockchain")

  try:
    account = web3.eth.account.from_key(os.getenv('CONTRACT_PRIVATE_KEY')).address
    tx = contract.functions.updateScore(tournament_id, user_id, score).build_transaction({
        'from': account,
        'gas': 1000000,
        'nonce': web3.eth.get_transaction_count(account),
    })

    # Sign and send the transaction
    signed_tx = web3.eth.account.sign_transaction(tx, private_key=os.getenv('CONTRACT_PRIVATE_KEY'))
    tx_hash = web3.eth.send_raw_transaction(signed_tx.raw_transaction)

    # Wait for the transaction to be mined
    tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
  except Exception as e:
    logger.error(f"updateScore function reverted : {e}")
  
def get_user_score_from_blockchain(contract, tournament_id, user_id, web3):
  logger.debug("")
  logger.debug("get_user_score_from_blockchain")

  try:
    account = web3.eth.account.from_key(os.getenv('CONTRACT_PRIVATE_KEY')).address
    score = contract.functions.getScore(tournament_id, user_id).call()
    logger.debug(f"User {user_id} score: {score}")
    return score
  except Exception as e:
    logger.error(f"getScore function reverted : {e}")

def connect_to_blockchain(request):
    logger.debug("")
    logger.debug("connect_to_blockchain")

    if web3.is_connected():
        logger.debug("Connected to the blockchain.")

        # Load the contract address from env variables
        contract_address = os.getenv('CONTRACT_ADDRESS')
        logger.debug(f"Contract address: {contract_address}")

        # Load the contract ABI from the JSON file
        with open(os.getenv('CONTRACT_ABI')) as f:
          contract_json = json.load(f)
          contract_abi = contract_json['abi']
        logger.debug(f"Contract ABI: {contract_abi}")

        # Load the contract ABI from the JSON file
        contract = web3.eth.contract(address=contract_address, abi=contract_abi)
        logger.debug(f"Contract: {contract}")

        # Create a tournament into the blockchain
        create_tournament_in_blockchain(contract, 0, [1, 2, 3, 4], web3)

        # Update score of each users in the blockchain
        update_user_score_in_blockchain(contract, 0, 1, 2, web3)

        # Get user score from the blockchain
        get_user_score_from_blockchain(contract, 0, 1, web3)

        return JsonResponse({'status': 'success', 'message': 'Connected to the blockchain.'})
    else:
        logger.error("Failed to connect to the blockchain.")
        return JsonResponse({'status': 'error', 'message': 'Failed to connect to the blockchain.'})