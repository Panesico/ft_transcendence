import os, json, requests, logging
from django.utils import timezone
from django.http import JsonResponse
from web3 import Web3
logger = logging.getLogger(__name__)

web3 = Web3(Web3.HTTPProvider("http://blockchain:8545"))

def create_tournament_in_blockchain(tournament_id, users_ids):
  logger.debug("")
  logger.debug("create_tournament_in_blockchain")

  # Get the contract's account
  # logger.debug(f"Account: {account}")
  contract = get_blockchain_contract()
  if contract is None:
    logger.error("Failed to load the contract.")
    raise Exception("Failed to load the contract.")
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

def update_user_score_in_blockchain(tournament_id, user_id, score):
  logger.debug("")
  logger.debug("update_user_score_in_blockchain")

  # Get the contract's account
  contract = get_blockchain_contract()
  if contract is None:
    logger.error("Failed to load the contract.")
    raise Exception("Failed to load the contract.")
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

# def connect_to_blockchain(request):
#     logger.debug("")
#     logger.debug("connect_to_blockchain")

#     if web3.is_connected():
#         logger.debug("Connected to the blockchain.")

#         # Recover the contract address from a local json file
#         with open('/usr/src/app/blockchain_app/deployedAddress.json') as f:
#           data = json.load(f)
#           contract_address = data['contractAddress']
#         logger.debug(f"Contract address: {contract_address}")

#         # Load the contract ABI from the JSON file
#         with open(os.getenv('CONTRACT_ABI')) as f:
#           contract_json = json.load(f)
#           contract_abi = contract_json['abi']
#         logger.debug(f"Contract ABI: {contract_abi}")

#         # Load the contract ABI from the JSON file
#         contract = web3.eth.contract(address=contract_address, abi=contract_abi)

#         # Create a tournament into the blockchain
#         create_tournament_in_blockchain(contract, 0, [1, 2, 3, 4])

#         # Update score of each users in the blockchain
#         update_user_score_in_blockchain(contract, 0, 1, 2)

#         # Get user score from the blockchain
#         get_user_score_from_blockchain(contract, 0, 1, web3)

#         return JsonResponse({'status': 'success', 'message': 'Connected to the blockchain.'})
#     else:
#         logger.error("Failed to connect to the blockchain.")
#         return JsonResponse({'status': 'error', 'message': 'Failed to connect to the blockchain.'})
  

def get_blockchain_contract():
    logger.debug("")
    logger.debug("connect_to_blockchain")

    if web3.is_connected():
        logger.debug("Connected to the blockchain.")
        try:
          # Recover the contract address from a local json file
          with open('/usr/src/app/blockchain_app/deployedAddress.json') as f:
            data = json.load(f)
            contract_address = data['contractAddress']
            logger.debug(f"Contract address: {contract_address}")

          # Load the contract ABI from the JSON file
          with open(os.getenv('CONTRACT_ABI')) as f:
            contract_json = json.load(f)
            contract_abi = contract_json['abi']
          logger.debug(f"Contract ABI: {contract_abi}")

          # Load the contract ABI from the JSON file
          contract = web3.eth.contract(address=contract_address, abi=contract_abi)

          return contract
        except Exception as e:
          logger.error(f"Failed to load the contract: {e}")
          return None
    else:
      return None

def save_tournament_results_in_blockchain(tournament, game_winner_id):
  logger.debug("")
  logger.debug("save_tournament_results_in_blockchain")

  # Get the contract's account
  contract = get_blockchain_contract()
  if contract is None:
    logger.error("Failed to load the contract.")
    return JsonResponse({'status': 'error', 'message': 'Failed to save results in the blockchain.'})
  try:
    tournament_id = tournament.id
    user_id_1 = tournament.t_p1_id
    user_id_2 = tournament.t_p2_id
    user_id_3 = tournament.t_p3_id
    user_id_4 = tournament.t_p4_id

    # If a user id is equal to 0, we do not save it in the blockchain
    if user_id_1 == 0 or user_id_2 == 0 or user_id_3 == 0 or user_id_4 == 0:
      logger.error("Tournament results are only saved in the blockchain if all users are registered.")
      return json.dumps({'status': 'success', 'message': 'Tournament ended.'})

    # Create the tournament in the blockchain
    create_tournament_in_blockchain(tournament.id, [user_id_1, user_id_2, user_id_3, user_id_4])
    logger.debug(f"Tournament {tournament_id} created in the blockchain.")

    # Save winner score in blockchain
    update_user_score_in_blockchain(tournament.id, game_winner_id, 2)
    logger.debug(f"Winner score saved in the blockchain for tournament {tournament_id}, winner: {game_winner_id}")

    # Save finalist score in blockchain
    if game_winner_id == tournament.semifinal1.game_winner_id:
      finalist_id = tournament.semifinal2.game_winner_id
    else:
      finalist_id = tournament.semifinal1.game_winner_id      
    update_user_score_in_blockchain(tournament.id, finalist_id, 1)
    logger.debug(f"Finalist score saved in the blockchain for tournament {tournament_id}, finalist: {finalist_id}")

    # Save losers score in blockchain
    for user_id in [user_id_1, user_id_2, user_id_3, user_id_4]:
      if user_id != game_winner_id and user_id != finalist_id:
        logger.debug(f"Save losers score in blockchain > User: {user_id}")
        update_user_score_in_blockchain(tournament.id, user_id, 0)
        logger.debug(f"User {user_id} score saved in the blockchain for tournament {tournament_id}")
    logger.debug(f"Results saved in the blockchain for tournament {tournament_id}, winner: {game_winner_id}")
    success_message = _('Tournament ended, results saved in the blockchain.')
    return json.dumps({'status': 'success', 'message': success_message})

  except Exception as e:
    logger.error(f"saveTournamentResults function reverted : {e}")
    return json.dumps({'status': 'bug', 'message': 'Tournament ended, failed to save results in the blockchain.'})