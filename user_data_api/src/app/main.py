from typing import Union

import sentry_sdk
import uvicorn
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
from elasticapm.contrib.starlette import make_apm_client, ElasticAPM

from app.core.config import Settings

settings = Settings()

app = FastAPI(
    title=f'{settings.project_name}',
    docs_url='/app/openapi',
    openapi_url='/app/openapi.json',
    default_response_class=ORJSONResponse,
    description='Сбор и редактирование лайков, рецензий и закладок фильмов',
    version='1.0.0',
)

sentry_sdk.init(dsn=settings.sentry_dsn, traces_sample_rate=1.0)

app.add_middleware(SentryAsgiMiddleware)

apm_config = {
    "SERVICE_NAME": "user-data-app",
    "SERVER_URL": f"http://{settings.apm_server_host}:{settings.apm_server_port}",
    "ENVIRONMENT": "dev",
    "GLOBAL_LABELS": "platform=localhost, application=user-data-app",
    "TRANSACTION_MAX_SPANS": 250,
    "STACK_TRACE_LIMIT": 250,
    "TRANSACTION_SAMPLE_RATE": 0.5,
    "APTURE_HEADERS": "false",
    "CAPTURE_BODY": "all",
}

apm = make_apm_client(apm_config)

app.add_middleware(ElasticAPM, client=apm)


@app.on_event('startup')
async def startup():
    return print('Hello World!')


@app.on_event('shutdown')
async def shutdown() -> None:
    return print('Bye World!')


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)  # noqa S104