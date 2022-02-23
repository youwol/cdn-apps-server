import asyncio
import itertools

import uvicorn
from fastapi import FastAPI, Depends
from starlette.requests import Request

from youwol_cdn_apps_server.configurations import get_configuration, Configuration
from youwol_cdn_apps_server.root_paths import router as router
from youwol_utils import (YouWolException, log_info, youwol_exception_handler)
from youwol_utils.context import DeployedContextLogger
from youwol_utils.middlewares.root_middleware import RootMiddleware
from youwol_utils.utils_paths import matching_files, FileListing, files_check_sum

flatten = itertools.chain.from_iterable

configuration: Configuration = asyncio.get_event_loop().run_until_complete(get_configuration())

app = FastAPI(
    title="cdn-apps-server",
    description="CDN applications server",
    openapi_prefix=configuration.open_api_prefix)


@app.exception_handler(YouWolException)
async def exception_handler(request: Request, exc: YouWolException):
    return await youwol_exception_handler(request, exc)


app.add_middleware(RootMiddleware, ctx_logger=DeployedContextLogger())
app.add_middleware(RootMiddleware, ctx_logger=configuration.ctx_logger)

app.include_router(
    router,
    prefix=configuration.base_path,
    dependencies=[Depends(get_configuration)],
    tags=[]
)

files_src_check_sum = matching_files(
    folder="./",
    patterns=FileListing(
        include=['*'],
        # when deployed using dockerfile there is additional files in ./src: a couple of .* files and requirements.txt
        ignore=["requirements.txt", ".*", "*.pyc"]
    )
)

log_info(f"./src check sum: {files_check_sum(files_src_check_sum)} ({len(files_src_check_sum)} files)")

if __name__ == "__main__":
    # app: incorrect type. More here: https://github.com/tiangolo/fastapi/issues/3927
    # noinspection PyTypeChecker
    uvicorn.run(app, host="0.0.0.0", port=configuration.http_port)
