
import sentry_sdk
import uvicorn
from aiokafka import AIOKafkaProducer
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
from elasticapm.contrib.starlette import make_apm_client, ElasticAPM

from app.api.v1 import view_film
from app.core.config import Settings
from app.db import kafka_producer

settings = Settings()

app = FastAPI(
    # Конфигурируем название проекта. Оно будет отображаться в документации
    title=f'{settings.project_name}',
    # Адрес документации в красивом интерфейсе
    docs_url='/api/openapi',
    # Адрес документации в формате OpenAPI
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
    description='Сбор статистики пользователей',
    version='1.0.0',
)


sentry_sdk.init(dsn=settings.sentry_dsn, traces_sample_rate=1.0)

app.add_middleware(SentryAsgiMiddleware)

apm_config = {
    "SERVICE_NAME": "ugc-api",
    "SERVER_URL": f"http://{settings.apm_server_host}:{settings.apm_server_port}",
    "ENVIRONMENT": "dev",
    "GLOBAL_LABELS": "platform=localhost, application=ugc-api",
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
    kafka_producer.aio_producer = AIOKafkaProducer(
        **{
            'bootstrap_servers': '{}:{}'.format(settings.kafka_host, settings.kafka_port)
        }

    )
    await kafka_producer.aio_producer.start()


@app.on_event('shutdown')
async def shutdown() -> None:
    await kafka_producer.aio_producer.stop()  # type: ignore[union-attr]


app.include_router(view_film.router, prefix='/api/v1/view_film')

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)  # noqa S104
