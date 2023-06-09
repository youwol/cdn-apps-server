
from youwol.utils.servers.fast_api import serve, FastApiApp, FastApiRouter, AppConfiguration, \
    select_configuration_from_command_line

from youwol.backends.cdn_apps_server import get_router

async def local() -> AppConfiguration:
    from config_local import get_configuration
    return await get_configuration()


async def prod() -> AppConfiguration:
    from config_prod import get_configuration
    return await get_configuration()


app_config = select_configuration_from_command_line(
    {
        "local": local,
        "prod": prod
    }
)

serve(
    FastApiApp(
        title="cdn-apps-server",
        description="CDN applications server",
        server_options=app_config.server,
        root_router=FastApiRouter(
            router=get_router(app_config.service)
        )
    )
)
