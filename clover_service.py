"""
Clover POS Integration Service
Handles OAuth authentication and POS operations
"""

import requests
import json
import base64
import hashlib
import secrets
from urllib.parse import urlencode, parse_qs
from typing import Dict, Optional, Any
from config import Config

class CloverService:
    """Service class for Clover POS integration"""

    def __init__(self):
        self.app_id = Config.CLOVER_APP_ID
        self.app_secret = Config.CLOVER_APP_SECRET
        self.base_url = Config.CLOVER_BASE_URL
        self.redirect_uri = Config.CLOVER_REDIRECT_URI
        self.access_token = None
        self.merchant_id = None
        self.refresh_token = None

    def get_authorization_url(self, state: str = None) -> str:
        """
        Generate Clover OAuth authorization URL

        Args:
            state: Optional state parameter for security

        Returns:
            Authorization URL for merchant to visit
        """
        if not state:
            state = secrets.token_urlsafe(32)

        params = {
            'client_id': self.app_id,
            'redirect_uri': self.redirect_uri,
            'response_type': 'code',
            'state': state
        }

        auth_url = f"{self.base_url}/oauth/authorize?" + urlencode(params)
        return auth_url

    def exchange_code_for_token(self, authorization_code: str) -> Dict[str, Any]:
        """
        Exchange authorization code for access token

        Args:
            authorization_code: Code received from OAuth callback

        Returns:
            Dictionary containing access token and merchant info
        """
        token_url = f"{self.base_url}/oauth/v2/token"

        data = {
            'client_id': self.app_id,
            'client_secret': self.app_secret,
            'code': authorization_code
        }

        headers = {
            'Content-Type': 'application/json'
        }

        try:
            response = requests.post(token_url, json=data, headers=headers)
            response.raise_for_status()

            token_data = response.json()

            # Store tokens
            self.access_token = token_data.get('access_token')
            self.refresh_token = token_data.get('refresh_token')

            # Extract merchant ID from the token response or make a separate call
            if 'merchant_id' in token_data:
                self.merchant_id = token_data['merchant_id']
            else:
                # Get merchant info using the access token
                merchant_info = self.get_merchant_info()
                if merchant_info:
                    self.merchant_id = merchant_info.get('id')

            return {
                'success': True,
                'access_token': self.access_token,
                'refresh_token': self.refresh_token,
                'merchant_id': self.merchant_id,
                'expires_in': token_data.get('expires_in')
            }

        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f"Token exchange failed: {str(e)}"
            }

    def get_merchant_info(self) -> Optional[Dict[str, Any]]:
        """
        Get merchant information using access token

        Returns:
            Merchant information dictionary
        """
        if not self.access_token:
            return None

        url = f"{self.base_url}/v3/merchants/me"
        headers = {
            'Authorization': f'Bearer {self.access_token}'
        }

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException:
            return None

    def create_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new order in Clover POS

        Args:
            order_data: Order information including items, customer, etc.

        Returns:
            Created order information
        """
        if not self.access_token or not self.merchant_id:
            return {'success': False, 'error': 'Not authenticated with Clover'}

        url = f"{self.base_url}/v3/merchants/{self.merchant_id}/orders"
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }

        try:
            response = requests.post(url, json=order_data, headers=headers)
            response.raise_for_status()
            return {
                'success': True,
                'order': response.json()
            }
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f"Failed to create order: {str(e)}"
            }

    def create_payment(self, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a payment through Clover POS

        Args:
            payment_data: Payment information including amount, order ID, etc.

        Returns:
            Payment processing result
        """
        if not self.access_token or not self.merchant_id:
            return {'success': False, 'error': 'Not authenticated with Clover'}

        url = f"{self.base_url}/v3/merchants/{self.merchant_id}/payments"
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }

        try:
            response = requests.post(url, json=payment_data, headers=headers)
            response.raise_for_status()
            return {
                'success': True,
                'payment': response.json()
            }
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f"Failed to process payment: {str(e)}"
            }

    def create_atomic_checkout(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create an atomic checkout in Clover.

        Docs endpoint: /v3/merchants/{mId}/atomic_order/checkouts

        Args:
            payload: The full checkout payload as required by Clover

        Returns:
            Result of the checkout operation
        """
        if not self.access_token or not self.merchant_id:
            return {'success': False, 'error': 'Not authenticated with Clover'}

        url = f"{self.base_url}/v3/merchants/{self.merchant_id}/atomic_order/checkouts"
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            return {
                'success': True,
                'checkout': response.json()
            }
        except requests.exceptions.RequestException as e:
            # Include Clover response text if present for easier debugging
            error_detail = getattr(e.response, 'text', str(e)) if hasattr(e, 'response') and e.response is not None else str(e)
            return {
                'success': False,
                'error': f"Failed to create atomic checkout: {error_detail}"
            }

    def get_inventory_items(self) -> Dict[str, Any]:
        """
        Get inventory items from Clover POS

        Returns:
            List of inventory items
        """
        if not self.access_token or not self.merchant_id:
            return {'success': False, 'error': 'Not authenticated with Clover'}

        url = f"{self.base_url}/v3/merchants/{self.merchant_id}/items"
        headers = {
            'Authorization': f'Bearer {self.access_token}'
        }

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return {
                'success': True,
                'items': response.json()
            }
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f"Failed to get inventory: {str(e)}"
            }

    def sync_menu_with_clover(self, restaurant_menu: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sync restaurant menu items with Clover POS inventory

        Args:
            restaurant_menu: Menu data from restaurant_data.py

        Returns:
            Sync operation result
        """
        if not self.access_token or not self.merchant_id:
            return {'success': False, 'error': 'Not authenticated with Clover'}

        # Get existing items
        existing_items = self.get_inventory_items()
        if not existing_items['success']:
            return existing_items

        # Convert restaurant menu to Clover format
        clover_items = []
        for category, items in restaurant_menu.items():
            for item in items:
                clover_item = {
                    'name': item['name'],
                    'price': int(item['price'] * 100),  # Convert to cents
                    'description': item['description'],
                    'category': {
                        'name': category.title()
                    },
                    'tags': item.get('allergens', [])
                }
                clover_items.append(clover_item)

        # Create items in Clover (simplified - in production, check for existing items)
        created_items = []
        for item in clover_items:
            url = f"{self.base_url}/v3/merchants/{self.merchant_id}/items"
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }

            try:
                response = requests.post(url, json=item, headers=headers)
                if response.status_code == 200:
                    created_items.append(response.json())
            except requests.exceptions.RequestException:
                continue

        return {
            'success': True,
            'created_items': len(created_items),
            'items': created_items
        }

    def is_authenticated(self) -> bool:
        """Check if service is authenticated with Clover"""
        return self.access_token is not None and self.merchant_id is not None

    def get_auth_status(self) -> Dict[str, Any]:
        """Get current authentication status"""
        return {
            'authenticated': self.is_authenticated(),
            'merchant_id': self.merchant_id,
            'has_access_token': self.access_token is not None
        }

# Global Clover service instance
clover_service = CloverService()
