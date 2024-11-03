import json
import time
from web3 import Web3
from web3.middleware import geth_poa_middleware
with open('rpc.json', 'r') as rpc_file:
    rpc_config = json.load(rpc_file)
    apechain_rpc_url = rpc_config['apechain_rpc']
w3 = Web3(Web3.HTTPProvider(apechain_rpc_url))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)

if w3.is_connected():
    print("Successfully connected to ApeChain.")
else:
    print("Failed to connect to ApeChain.")
    exit()
with open('abi.json', 'r') as abi_file:
    nft_abi = json.load(abi_file)

if not isinstance(nft_abi, list):
    print("Invalid ABI format. Ensure the ABI is a JSON array.")
    exit()
with open('data.json', 'r') as file:
    data = json.load(file)
def load_private_keys(file_path):
    try:
        with open(file_path, 'r') as pk_file:
            private_keys = [line.strip() for line in pk_file if line.strip()]
        return private_keys
    except Exception as e:
        print(f"Failed to load private keys: {str(e)}")
        return []
def claim_nft(account_address, private_key, updated_data, tx_number):
    try:
        account_nonce = w3.eth.get_transaction_count(account_address)
        transaction = contract.functions.claim(
            updated_data["_receiver"],
            updated_data["_quantity"],
            updated_data["_currency"],
            updated_data["_pricePerToken"],
            (
                updated_data["_allowlistProof"]["proof"],
                updated_data["_allowlistProof"]["quantityLimitPerWallet"],
                updated_data["_allowlistProof"]["pricePerToken"],
                updated_data["_allowlistProof"]["currency"]
            ),
            updated_data["_data"]
        ).build_transaction({
            'from': account_address,
            'nonce': account_nonce,
            'gas': 400000,
            'maxFeePerGas': w3.to_wei(26, 'gwei'),
            'maxPriorityFeePerGas': w3.to_wei(26, 'gwei'),
            'chainId': 33139,
            'value': w3.to_wei(updated_data["_value"], 'ether')
        })
        signed_tx = w3.eth.account.sign_transaction(transaction, private_key=private_key)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        print(f"Claim transaction {tx_number} successful! Transaction hash: {tx_hash.hex()}")
        return receipt
    except Exception as e:
        print(f"Error in claim transaction {tx_number}: {str(e)}")
        return None
if __name__ == '__main__':
    private_keys = load_private_keys('pk.txt')
    if not private_keys:
        print("No private keys found.")
        exit()

    nft_contract_address = data["nft_contract_address"]
    contract = w3.eth.contract(address=nft_contract_address, abi=nft_abi)

    for idx, private_key in enumerate(private_keys, start=1):
        account = w3.eth.account.from_key(private_key)
        account_address = account.address

        data["_receiver"] = account_address
        data["_allowlistProof"]["currency"] = account_address

        print(f"\nProcessing claim NFT for Wallet {idx} ({account_address})...")
        claim_nft(account_address, private_key, data, idx)
