"""
This module provides configuration settings for connecting to the Blockfrost API.
Applications:

- blockchain_integration
- crypto_wallets
- nft_marketplace
"""
from django.conf import settings
import requests

BLOCKFROST_API_KEY = settings.BLOCKFROST_API_KEY

# Preview URL for Blockfrost API (use Cardano preview testnet)
BLOCKFROST_API_URL = "https://cardano-preview.blockfrost.io/api/v0"


class BlockfrostConfig:
    """Configuration class for Blockfrost API integration."""

    def __init__(self):
        self.api_key = BLOCKFROST_API_KEY
        self.api_url = BLOCKFROST_API_URL

    def get_headers(self):
        """Returns the headers required for Blockfrost API requests."""
        return {
            "project_id": self.api_key,
            "Content-Type": "application/json"
        }

    def get_wallet_balance(self, wallet_address):
        """Fetches UTXOs and returns total balance in lovelace and ADA."""
        url = f"{self.api_url}/addresses/{wallet_address}/utxos"
        try:
            resp = requests.get(url, headers=self.get_headers(), timeout=10)
            resp.raise_for_status()
        except requests.RequestException as e:
            raise RuntimeError(f"Blockfrost request failed: {e}")
        utxos = resp.json()
        total_lovelace = 0
        for utxo in utxos:
            for amount in utxo.get("amount", []):
                if amount.get("unit") == "lovelace":
                    total_lovelace += int(amount.get("quantity", 0))
        return {"lovelace": total_lovelace, "ada": total_lovelace / 1_000_000}


    def get_transaction_endpoint(self, tx_hash):
        """Returns the endpoint URL for fetching transaction details."""
        return f"{self.api_url}/txs/{tx_hash}"
