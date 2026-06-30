from unittest.mock import AsyncMock, Mock

import pytest
from httpx import AsyncClient, Client, HTTPStatusError, RequestError, Response

from oidc_discovery.clients import (
    AsyncOIDCDiscoverer,
    OIDCDiscoverer,
    OIDCDiscoveryError,
)


class TestOIDCDiscoverer:
    issuer: str = "http://keycloak:8002/realms/oidc-discovery"

    def test_raises_on_request_error(self) -> None:
        client = Client()
        client.get = Mock(side_effect=RequestError("Something went wrong!"))
        client.close = Mock()
        discover = OIDCDiscoverer(client, self.issuer)

        with pytest.raises(OIDCDiscoveryError):
            discover()

        client.close.assert_called_once()

    def test_raises_on_status_code_error(self) -> None:
        response = Mock(Response)
        response.raise_for_status = Mock(
            side_effect=HTTPStatusError(
                "Something went wrong!",
                request=Mock(),
                response=response,
            ),
        )
        client = Client()
        client.get = Mock(return_value=response)
        client.close = Mock()
        discover = OIDCDiscoverer(client, self.issuer)

        with pytest.raises(OIDCDiscoveryError):
            discover()

        client.close.assert_called_once()

    def test_raises_on_validation_error(self) -> None:
        response = Mock(Response)

        client = Client()
        client.get = Mock(return_value=response)
        client.close = Mock()
        discover = OIDCDiscoverer(client, self.issuer)

        with pytest.raises(OIDCDiscoveryError) as exc_info:
            discover()

        assert (str(exc_info.value)
                .startswith("1 validation error for OIDCProviderMetadata"))
        client.close.assert_called_once()

    def test_discovers_oidc_configuration(self) -> None:
        client = Client()
        discover = OIDCDiscoverer(client, self.issuer)

        metadata = discover()

        assert str(metadata.issuer) == self.issuer
        assert str(metadata.authorization_endpoint) == "http://keycloak:8002/realms/oidc-discovery/protocol/openid-connect/auth"
        assert str(metadata.token_endpoint) == "http://keycloak:8002/realms/oidc-discovery/protocol/openid-connect/token"
        assert str(metadata.jwks_uri) == "http://keycloak:8002/realms/oidc-discovery/protocol/openid-connect/certs"
        assert str(metadata.end_session_endpoint) == "http://keycloak:8002/realms/oidc-discovery/protocol/openid-connect/logout"
        assert client.is_closed


class TestAsyncOIDCDiscoverer:
    issuer: str = "http://keycloak:8002/realms/oidc-discovery"

    @pytest.mark.anyio
    async def test_raises_on_request_error(self) -> None:
        client = AsyncClient()
        client.get = Mock(side_effect=RequestError("Something went wrong!"))
        client.aclose = AsyncMock()
        discover = AsyncOIDCDiscoverer(client, self.issuer)

        with pytest.raises(OIDCDiscoveryError):
            await discover()

        client.aclose.assert_awaited_once()

    @pytest.mark.anyio
    async def test_raises_on_status_code_error(self) -> None:
        response = Mock(Response)
        response.raise_for_status = Mock(
            side_effect=HTTPStatusError(
                "Something went wrong!",
                request=Mock(),
                response=response,
            ),
        )
        client = AsyncClient()
        client.get = AsyncMock(return_value=response)
        client.aclose = AsyncMock()
        discover = AsyncOIDCDiscoverer(client, self.issuer)

        with pytest.raises(OIDCDiscoveryError):
            await discover()

        client.aclose.assert_awaited_once()

    @pytest.mark.anyio
    async def test_raises_on_validation_error(self) -> None:
        response = Mock(Response)

        client = AsyncClient()
        client.get = AsyncMock(return_value=response)
        client.aclose = AsyncMock()
        discover = AsyncOIDCDiscoverer(client, self.issuer)

        with pytest.raises(OIDCDiscoveryError) as exc_info:
            await discover()

        assert (str(exc_info.value)
                .startswith("1 validation error for OIDCProviderMetadata"))

        client.aclose.assert_awaited_once()

    @pytest.mark.anyio
    async def test_discovers_oidc_configuration(self) -> None:
        client = AsyncClient()
        discover = AsyncOIDCDiscoverer(client, self.issuer)

        metadata = await discover()

        assert str(metadata.issuer) == self.issuer
        assert str(metadata.authorization_endpoint) == "http://keycloak:8002/realms/oidc-discovery/protocol/openid-connect/auth"
        assert str(metadata.token_endpoint) == "http://keycloak:8002/realms/oidc-discovery/protocol/openid-connect/token"
        assert str(metadata.jwks_uri) == "http://keycloak:8002/realms/oidc-discovery/protocol/openid-connect/certs"
        assert str(metadata.end_session_endpoint) == "http://keycloak:8002/realms/oidc-discovery/protocol/openid-connect/logout"
        assert client.is_closed
