import os

from youwol.backends.cdn_apps_server import Configuration
from youwol.utils import RedisCacheClient
from youwol.utils.clients.assets_gateway.assets_gateway import AssetsGatewayClient
from youwol.utils.clients.oidc.oidc_config import OidcInfos, PrivateClient
from youwol.utils.context import DeployedContextReporter
from youwol.utils.middlewares import AuthMiddleware, redirect_to_login
from youwol.utils.middlewares import JwtProviderCookie
from youwol.utils.servers.env import OPENID_CLIENT, REDIS, Env
from youwol.utils.servers.fast_api import AppConfiguration, ServerOptions, FastApiMiddleware


async def get_configuration():
    required_env_vars = OPENID_CLIENT + REDIS

    not_founds = [v for v in required_env_vars if not os.getenv(v)]
    if not_founds:
        raise RuntimeError(f"Missing environments variable: {not_founds}")

    gtw_client = AssetsGatewayClient(url_base="http://assets-gateway")
    service_config = Configuration(
        assets_gtw_client=gtw_client
    )

    openid_base_url = os.getenv(Env.OPENID_BASE_URL)
    openid_infos = OidcInfos(
        base_uri=openid_base_url,
        client=PrivateClient(
            client_id=os.getenv(Env.OPENID_CLIENT_ID),
            client_secret=os.getenv(Env.OPENID_CLIENT_SECRET)
        )
    )

    server_options = ServerOptions(
        root_path='/applications',
        http_port=8080,
        base_path="",
        middlewares=[
            FastApiMiddleware(
                AuthMiddleware, {
                    'openid_base_uri': openid_base_url,
                    'predicate_public_path': lambda url:
                    url.path.endswith("/healthz"),
                    'jwt_providers': [
                        JwtProviderCookie(
                            auth_cache=RedisCacheClient(
                                host=os.getenv(Env.REDIS_HOST),
                                prefix='auth_cache'
                            ),
                            openid_infos=openid_infos)],
                    'on_missing_token': redirect_to_login,
                }
            )

        ],
        ctx_logger=DeployedContextReporter()
    )
    return AppConfiguration(
        server=server_options,
        service=service_config
    )
