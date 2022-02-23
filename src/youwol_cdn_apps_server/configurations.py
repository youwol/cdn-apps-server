import os
import sys
from dataclasses import dataclass
from typing import Union, Any, Coroutine, Dict

from youwol_utils import (
    find_platform_path, get_headers_auth_admin_from_env,
    get_headers_auth_admin_from_secrets_file, log_info, auto_port_number,
)
from youwol_utils.clients.assets_gateway.assets_gateway import AssetsGatewayClient
from youwol_utils.context import ContextLogger, DeployedContextLogger


@dataclass(frozen=True)
class Configuration:
    open_api_prefix: str
    http_port: int
    base_path: str

    gtw_client: AssetsGatewayClient

    admin_headers: Union[Coroutine[Any, Any, Dict[str, str]], None]

    ctx_logger: ContextLogger = DeployedContextLogger()


async def get_tricot_config() -> Configuration:
    required_env_vars = ["AUTH_HOST", "AUTH_CLIENT_ID", "AUTH_CLIENT_SECRET", "AUTH_CLIENT_SCOPE"]
    not_founds = [v for v in required_env_vars if not os.getenv(v)]
    if not_founds:
        raise RuntimeError(f"Missing environments variable: {not_founds}")
    openid_host = os.getenv("AUTH_HOST")

    log_info("Use tricot configuration", openid_host=openid_host)

    gtw_client = AssetsGatewayClient(url_base="http://assets-gateway")

    return Configuration(
        open_api_prefix='/applications',
        http_port=8080,
        base_path="",
        gtw_client=gtw_client,
        admin_headers=get_headers_auth_admin_from_env()
    )


async def get_remote_clients_config(url_cluster) -> Configuration:
    openid_host = "gc.auth.youwol.com"
    gtw_client = AssetsGatewayClient(url_base="http://localhost:2000/api/assets-gateway")
    return Configuration(
        open_api_prefix='/applications',
        http_port=2066,
        base_path="",
        gtw_client=gtw_client,
        admin_headers=get_headers_auth_admin_from_secrets_file(
            file_path=find_platform_path() / "secrets" / "tricot.json",
            url_cluster=url_cluster,
            openid_host=openid_host)
    )


async def get_remote_clients_gc_config() -> Configuration:
    return await get_remote_clients_config("gc.platform.youwol.com")


async def get_full_local_config() -> Configuration:
    gtw_client = AssetsGatewayClient(url_base="http://localhost:2000/api/assets-gateway")

    return Configuration(
        open_api_prefix='',
        http_port=auto_port_number('cdn-apps-server'),
        base_path="",
        gtw_client=gtw_client,
        admin_headers=None
    )


configurations = {
    'tricot': get_tricot_config,
    'remote-clients': get_remote_clients_gc_config,
    'full-local': get_full_local_config,
}

current_configuration = None


async def get_configuration():
    global current_configuration
    if current_configuration:
        return current_configuration

    current_configuration = await configurations[sys.argv[1]]()
    return current_configuration
