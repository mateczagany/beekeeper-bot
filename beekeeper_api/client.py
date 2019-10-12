import logging
import json

import aiohttp

from beekeeper_api.client_settings import BeekeeperClientSettings
from beekeeper_api.conversation import Conversation
from beekeeper_api.exceptions import BeekeeperBotException

logger = logging.getLogger(__name__)


class BeekeeperClient:
    def __init__(self, client_settings):
        """
        Args:
            client_settings (BeekeeperClientSettings):
        """
        self.client_settings = client_settings
        self.session = aiohttp.ClientSession()

    async def __aenter__(self):
        await self._verify_settings()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()

    def _get_url(self, endpoint):
        """
        Creates a URL from an endpoint
        Args:
            endpoint (str): endpoint, e.g. `/status`

        Returns:
            str: full URL
        """
        endpoint = endpoint.strip()
        if not endpoint:
            raise BeekeeperBotException('URL is invalid')
        if endpoint[0] != '/':
            endpoint = f'/{endpoint}'

        return f'https://{self.client_settings.subdomain}.beekeeper.io/api/{self.client_settings.api_version}{endpoint}'

    def _get_headers(self):
        """
        Generates headers to use with HTTP requests
        Returns:
            dict[str, str]: headers
        """
        return {
            'Authorization': f'Token {self.client_settings.access_token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

    async def _request(self, method, endpoint, data=None, params=None):
        """
        Create a request to Beekeeper API
        Args:
            method (str): HTTP method
            endpoint (str): REST API url, e.g. `/status`
            data (dict[any, any]): data that will be sent as JSON payload
            params (dict[str, str]): query parameters
        Returns:
            dict: JSON result
        """
        url = self._get_url(endpoint)
        headers = self._get_headers()

        if method == "GET":
            result = await self.session.get(url, params=params, headers=headers)
        elif method == "POST":
            result = await self.session.post(url, json=data, params=params, headers=headers)
        else:
            raise BeekeeperBotException(f'Unknown method: {method}')

        result_json = await result.json(encoding='utf-8')
        if result.status >= 400:
            raise BeekeeperBotException(f'Error while {method}\'ing {endpoint}: {json.dumps(result_json)}')

        return result_json

    async def get(self, endpoint, params=None):
        """
        Create a GET request to Beekeeper API
        Args:
            endpoint (str): REST API url, e.g. `/status`
            params (dict[str, str]): query parameters
        Returns:
            dict: JSON result
        """
        return await self._request(method='GET', endpoint=endpoint, params=params)

    async def post(self, endpoint, params=None, data=None):
        """
        Create a GET request to Beekeeper API
        Args:
            endpoint (str): REST API url, e.g. `/status`
            params (dict[str, str]): query parameters
            data (dict[any, any]): data that will be sent as JSON payload
        Returns:
            dict: JSON result
        """
        return await self._request(method='POST', endpoint=endpoint, data=data, params=params)

    async def _verify_settings(self):
        """
        Verify if we can connect to the API
        Returns:
            bool: can we connect
        """
        if 'settings' not in await self.get(endpoint='/status'):
            raise BeekeeperBotException('Failed to get /status')

        logger.info("Settings successfully verified")

    async def get_conversations(self, **kwargs):
        """
        Retrieves list of conversations
        Returns:
            list[Conversation]: conversations
        """
        result = await self.get('/conversations', params=kwargs)
        return [Conversation.from_dict(client=self, data=conv_raw) for conv_raw in result]
