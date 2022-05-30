import uvicorn
from aiokafka import AIOKafkaProducer
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

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


@app.on_event('startup')
async def startup():
    kafka_producer.aio_producer = AIOKafkaProducer(
        **{
            'bootstrap_servers': '{}:{}'.format(settings.kafka_host, settings.kafka_port)
        }
    )
    await kafka_producer.aio_producer.start()


@app.on_event('shutdown')
async def shutdown():
    await kafka_producer.aio_producer.stop()


app.include_router(view_film.router, prefix='/api/v1/view_film')

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
