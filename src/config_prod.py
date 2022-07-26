import os

from youwol_cdn_apps_server import Configuration
from youwol_utils import RedisCacheClient
from youwol_utils.clients.assets_gateway.assets_gateway import AssetsGatewayClient
from youwol_utils.clients.oidc.oidc_config import OidcInfos, PrivateClient
from youwol_utils.context import DeployedContextReporter
from youwol_utils.middlewares import AuthMiddleware, redirect_to_login
from youwol_utils.middlewares import JwtProviderCookie
from youwol_utils.servers.env import OPENID_CLIENT, REDIS, Env
from youwol_utils.servers.fast_api import AppConfiguration, ServerOptions, FastApiMiddleware


async def get_configuration():
    required_env_vars = OPENID_CLIENT + REDIS

    not_founds = [v for v in required_env_vars if not os.getenv(v)]
    if not_founds:
        raise RuntimeError(f"Missing environments variable: {not_founds}")

    gtw_client = AssetsGatewayClient(url_base="http://assets-gateway")
    service_config = Configuration(
        assets_gtw_client=gtw_client
    )

    openid_infos = OidcInfos(
        base_uri=os.getenv(Env.OPENID_BASE_URL),
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
                    'openid_infos': openid_infos,
                    'predicate_public_path': lambda url:
                    url.path.endswith("/healthz"),
                    'jwt_providers': [
                        JwtProviderCookie(
                            jwt_cache=RedisCacheClient(
                                host=os.getenv(Env.REDIS_HOST),
                                prefix='jwt_cache'
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
