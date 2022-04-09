from config_common import get_py_youwol_env
from youwol_cdn_apps_server import Configuration
from youwol_utils.clients.assets_gateway.assets_gateway import AssetsGatewayClient
from youwol_utils.context import ConsoleContextLogger
from youwol_utils.middlewares.authentication_local import AuthLocalMiddleware
from youwol_utils.servers.fast_api import FastApiMiddleware, AppConfiguration, ServerOptions


async def get_configuration():
    env = await get_py_youwol_env()
    service_config = Configuration(
        assets_gtw_client=AssetsGatewayClient(url_base=f"http://localhost:{env['httpPort']}/api/assets-gateway")
    )

    server_options = ServerOptions(
        root_path="",
        http_port=env['portsBook']['cdn-apps-server'],
        base_path="",
        middlewares=[FastApiMiddleware(AuthLocalMiddleware, {})],
        ctx_logger=ConsoleContextLogger()
    )
    return AppConfiguration(
        server=server_options,
        service=service_config
    )
