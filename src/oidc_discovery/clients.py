from abc import ABCMeta, abstractmethod
from typing import Literal

from httpx import AsyncClient, Client, HTTPStatusError, RequestError
from pydantic import ValidationError

from oidc_discovery.models import OIDCProviderMetadata

SUFFIX: Literal["/.well-known/openid-configuration"] = \
        "/.well-known/openid-configuration"


class OIDCDiscoveryError(Exception): ...


class OIDCDiscovererInterface(metaclass=ABCMeta):
    @abstractmethod
    def __call__(self) -> OIDCProviderMetadata: ...


class OIDCDiscoverer(OIDCDiscovererInterface):
    _client: Client
    _issuer: str

    def __init__(self, client: Client, issuer: str) -> None:
        self._client = client
        self._issuer = issuer

    def __call__(self) -> OIDCProviderMetadata:
        url = self._issuer + SUFFIX

        try:
            response = self._client.get(url)
            response.raise_for_status()
            return OIDCProviderMetadata.model_validate_json(response.text)
        except (RequestError, HTTPStatusError) as e:
            raise OIDCDiscoveryError from e
        except ValidationError as e:
            raise OIDCDiscoveryError(str(e)) from e
        finally:
            self._client.close()


class AsyncOIDCDiscovererInterface(metaclass=ABCMeta):
    @abstractmethod
    async def __call__(self) -> OIDCProviderMetadata: ...


class AsyncOIDCDiscoverer(AsyncOIDCDiscovererInterface):
    _client: AsyncClient
    _issuer: str

    def __init__(self, client: AsyncClient, issuer: str) -> None:
        self._client = client
        self._issuer = issuer

    async def __call__(self) -> OIDCProviderMetadata:
        url = self._issuer + SUFFIX

        try:
            response = await self._client.get(url)
            response.raise_for_status()
            return OIDCProviderMetadata.model_validate_json(response.text)
        except (RequestError, HTTPStatusError) as e:
            raise OIDCDiscoveryError from e
        except ValidationError as e:
            raise OIDCDiscoveryError(str(e)) from e
        finally:
            await self._client.aclose()
