import logging
import json

import aiohttp

from beekeeper_client.client_settings import BeekeeperClientSettings
from beekeeper_client.models.conversation import Conversation
from beekeeper_client.exceptions import BeekeeperClientException

logger = logging.getLogger(__name__)


API_VERSION = 2


class BeekeeperClient:
    def __init__(self, client_settings):
        """
        Args:
            client_settings (BeekeeperClientSettings):
        """
        self._client_settings = client_settings
        self._session = aiohttp.ClientSession()

        self.user_config = None

    async def __aenter__(self):
        await self._retrieve_user_config()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._session.close()

    async def _retrieve_user_config(self):
        """
        Download user config via /config/client
        Returns:
            None
        """
        self.user_config = await self.get('/config/client')
        logger.info("Client config successfully downloaded")

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
            raise BeekeeperClientException('URL is invalid')
        if endpoint[0] != '/':
            endpoint = f'/{endpoint}'

        return f'https://{self._client_settings.subdomain}.beekeeper.io/api/{API_VERSION}{endpoint}'

    def _get_headers(self):
        """
        Generates headers to use with HTTP requests
        Returns:
            dict[str, str]: headers
        """
        return {
            'Authorization': f'Token {self._client_settings.access_token}',
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
            result = await self._session.get(url, params=params, headers=headers)
        elif method == "POST":
            result = await self._session.post(url, json=data, params=params, headers=headers)
        else:
            raise BeekeeperClientException(f'Unknown method: {method}')

        result_json = await result.json(encoding='utf-8')
        if result.status >= 400:
            raise BeekeeperClientException(f'Error while {method}\'ing {endpoint}: {json.dumps(result_json)}')

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

    async def get_conversations(self, **kwargs):
        """
        Retrieves list of conversations
        Returns:
            list[Conversation]: conversations
        """
        result = await self.get('/conversations', params=kwargs)
        return [Conversation.from_dict(client=self, data=conv_raw) for conv_raw in result]
