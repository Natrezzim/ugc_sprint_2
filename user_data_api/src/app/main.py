import motor
import sentry_sdk
import uvicorn
from elasticapm.contrib.starlette import make_apm_client, ElasticAPM
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware

from app.api.v1 import likes, review, bookmarks
from app.core.config import Settings
from app.db import mongo_db

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
    client = motor.motor_asyncio.AsyncIOMotorClient(
        'mongodb://{}:{}'.format(settings.mongo_host, settings.mongo_port)
    )
    mongo_db.mongo = client[settings.mongo_db_name]


@app.on_event('shutdown')
async def shutdown() -> None:
    mongo_db.mongo.close()


@app.get("/")
async def read_root():
    return {"Hello": "World!"}


app.include_router(likes.router, prefix='/api/v1/likes', tags=['Likes'])
app.include_router(review.router, prefix='/api/v1/review')
app.include_router(bookmarks.router, prefix='/api/v1/bookmarks', tags=["Bookmarks"])

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)  # noqa S104
