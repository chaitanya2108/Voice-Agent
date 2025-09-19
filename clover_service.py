"""
Clover POS Integration Service
Handles OAuth authentication and POS operations
"""

import requests
import json
from typing import Dict, Optional, Any
from config import Config
import logging

logger = logging.getLogger(__name__)

class CloverService:
    """Service class for Clover POS integration"""

    def __init__(self):
        self.app_id = Config.CLOVER_APP_ID
        self.app_secret = Config.CLOVER_APP_SECRET
        self.base_url = Config.CLOVER_BASE_URL
        self.oauth_url = Config.CLOVER_OAUTH_URL
        self.token_url = Config.CLOVER_TOKEN_URL

        # Store tokens in memory (in production, use secure storage)
        self.access_token = None
        self.refresh_token = None
        self.merchant_id = None
        self.merchant_info = None

    def get_oauth_authorization_url(self, redirect_uri: str) -> str:
        """
        Generate OAuth authorization URL for Clover

        Args:
            redirect_uri: The callback URL where Clover will redirect after authorization

        Returns:
            Authorization URL
        """
        print("=" * 30)
        print("CLOVER SERVICE - Generating OAuth URL")
        print("=" * 30)
        print(f"App ID: {self.app_id}")
        print(f"App Secret: {self.app_secret[:10]}..." if self.app_secret else "None")
        print(f"OAuth URL: {self.oauth_url}")
        print(f"Redirect URI: {redirect_uri}")

        params = {
            'client_id': self.app_id,
            'redirect_uri': redirect_uri,
            'response_type': 'code'
        }

        print(f"OAuth parameters: {params}")

        # Build query string
        query_string = '&'.join([f'{k}={v}' for k, v in params.items()])
        final_url = f"{self.oauth_url}?{query_string}"

        print(f"Final OAuth URL: {final_url}")
        print("=" * 30)

        return final_url

    def exchange_code_for_tokens(self, authorization_code: str, redirect_uri: str) -> Dict[str, Any]:
        """
        Exchange authorization code for access and refresh tokens

        Args:
            authorization_code: The authorization code from Clover callback
            redirect_uri: The redirect URI used in the authorization request

        Returns:
            Dictionary containing tokens and merchant info
        """
        try:
            payload = {
                'client_id': self.app_id,
                'client_secret': self.app_secret,
                'code': authorization_code,
                'redirect_uri': redirect_uri
            }

            headers = {
                'Content-Type': 'application/json'
            }

            response = requests.post(
                self.token_url,
                json=payload,
                headers=headers,
                timeout=30
            )

            if response.status_code == 200:
                token_data = response.json()

                # Store tokens
                self.access_token = token_data.get('access_token')
                self.refresh_token = token_data.get('refresh_token')

                # Get merchant info
                merchant_info = self.get_merchant_info()

                return {
                    'success': True,
                    'access_token': self.access_token,
                    'refresh_token': self.refresh_token,
                    'merchant_info': merchant_info,
                    'merchant_id': self.merchant_id
                }
            else:
                logger.error(f"Token exchange failed: {response.status_code} - {response.text}")
                return {
                    'success': False,
                    'error': f"Token exchange failed: {response.status_code}",
                    'details': response.text
                }

        except requests.exceptions.RequestException as e:
            logger.error(f"Request error during token exchange: {e}")
            return {
                'success': False,
                'error': f"Request error: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Unexpected error during token exchange: {e}")
            return {
                'success': False,
                'error': f"Unexpected error: {str(e)}"
            }

    def get_merchant_info(self) -> Optional[Dict[str, Any]]:
        """
        Get merchant information using the access token

        Returns:
            Merchant information dictionary or None if failed
        """
        if not self.access_token:
            logger.error("No access token available")
            return None

        try:
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }

            response = requests.get(
                f"{self.base_url}/v3/merchants/me",
                headers=headers,
                timeout=30
            )

            if response.status_code == 200:
                merchant_data = response.json()
                self.merchant_info = merchant_data
                self.merchant_id = merchant_data.get('id')
                return merchant_data
            else:
                logger.error(f"Failed to get merchant info: {response.status_code} - {response.text}")
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Request error getting merchant info: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error getting merchant info: {e}")
            return None

    def refresh_access_token(self) -> bool:
        """
        Refresh the access token using the refresh token

        Returns:
            True if successful, False otherwise
        """
        if not self.refresh_token:
            logger.error("No refresh token available")
            return False

        try:
            payload = {
                'client_id': self.app_id,
                'client_secret': self.app_secret,
                'refresh_token': self.refresh_token
            }

            headers = {
                'Content-Type': 'application/json'
            }

            response = requests.post(
                self.token_url,
                json=payload,
                headers=headers,
                timeout=30
            )

            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data.get('access_token')
                # Refresh token might be updated too
                if 'refresh_token' in token_data:
                    self.refresh_token = token_data.get('refresh_token')
                return True
            else:
                logger.error(f"Token refresh failed: {response.status_code} - {response.text}")
                return False

        except requests.exceptions.RequestException as e:
            logger.error(f"Request error during token refresh: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during token refresh: {e}")
            return False

    def is_authenticated(self) -> bool:
        """
        Check if we have valid authentication

        Returns:
            True if authenticated, False otherwise
        """
        return self.access_token is not None and self.merchant_id is not None

    def get_auth_status(self) -> Dict[str, Any]:
        """
        Get current authentication status

        Returns:
            Dictionary with authentication status and merchant info
        """
        return {
            'authenticated': self.is_authenticated(),
            'merchant_id': self.merchant_id,
            'merchant_info': self.merchant_info,
            'has_access_token': self.access_token is not None,
            'has_refresh_token': self.refresh_token is not None
        }

    def make_authenticated_request(self, method: str, endpoint: str, **kwargs) -> Optional[Dict[str, Any]]:
        """
        Make an authenticated request to Clover API

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint (without base URL)
            **kwargs: Additional arguments for requests

        Returns:
            Response data or None if failed
        """
        if not self.is_authenticated():
            logger.error("Not authenticated with Clover")
            return None

        try:
            headers = kwargs.get('headers', {})
            headers.update({
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            })
            kwargs['headers'] = headers

            url = f"{self.base_url}{endpoint}"
            response = requests.request(method, url, timeout=30, **kwargs)

            if response.status_code == 401:
                # Token might be expired, try to refresh
                if self.refresh_access_token():
                    # Retry the request with new token
                    headers['Authorization'] = f'Bearer {self.access_token}'
                    response = requests.request(method, url, timeout=30, **kwargs)
                else:
                    logger.error("Failed to refresh token")
                    return None

            if response.status_code in [200, 201, 204]:
                if response.content:
                    return response.json()
                return {'success': True}
            else:
                logger.error(f"API request failed: {response.status_code} - {response.text}")
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return None

# Global Clover service instance
clover_service = CloverService()