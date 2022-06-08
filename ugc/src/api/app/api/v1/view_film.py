from http import HTTPStatus

from typing import Dict
from uuid import UUID

from aiokafka import AIOKafkaProducer
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBasicCredentials, HTTPBearer
from pydantic import BaseModel

from app.db.kafka_producer import get_producer
from app.service.auth import Auth

security = HTTPBearer()
auth_handler = Auth()
router = APIRouter()


class Viewed(BaseModel):
    movie_id: UUID
    viewed_time: int


@router.post(
    '/',
    summary='Добавление данных по фильму',
    description='Добавление статистики, просмотра фильма',
    response_description='Id, название, рейтинг, описание, жанры, актеры, сценаристы, режиссеры фильма.',
    tags=['viewed'],
)
async def film_views(
    viewed: Viewed,
    producer: AIOKafkaProducer = Depends(get_producer),
    credentials: HTTPBasicCredentials = Depends(security),
) -> Dict[str, str]:
    token = credentials.credentials  # type: ignore[attr-defined]
    user_id = auth_handler.decode_token(token)
    try:
        await producer.send_and_wait(
            "views",
            key='{0}+{1}'.format(user_id, viewed.movie_id).encode(),
            value='{0}'.format(viewed.viewed_time).encode(),

        )
        return {"saved": 'ok'}

    except Exception as ex:
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=ex.args[0].str())
