from youwol_cdn_apps_server import Configuration
from youwol_utils.clients.assets_gateway.assets_gateway import AssetsGatewayClient
from youwol_utils.context import DeployedContextReporter
from youwol_utils.servers.fast_api import AppConfiguration, ServerOptions


async def get_configuration():

    gtw_client = AssetsGatewayClient(url_base="http://assets-gateway")
    service_config = Configuration(
        assets_gtw_client=gtw_client
    )
    server_options = ServerOptions(
        root_path='/applications',
        http_port=8080,
        base_path="",
        middlewares=[],
        ctx_logger=DeployedContextReporter()
    )
    return AppConfiguration(
        server=server_options,
        service=service_config
    )
