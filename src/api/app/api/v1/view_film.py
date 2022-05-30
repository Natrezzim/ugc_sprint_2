from http import HTTPStatus
from uuid import UUID

from aiokafka import AIOKafkaProducer
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPBasicCredentials
from pydantic import BaseModel

from app.db.kafka_producer import get_producer
from app.service.auth import Auth

security = HTTPBearer()
auth_handler = Auth()

router = APIRouter()


class Viewed(BaseModel):
    movie_id: UUID
    viewed_time: int


@router.post('/',
             summary='Добавление данных по фильму',
             description='Добавление статистики, просмотра фильма',
             response_description='Id, название, рейтинг, описание, жары, '
                                  'актеры, сценаристы, режиссеры фильма.',
             tags=['viewed']
             )
async def film_views(
        viewed: Viewed,
        producer: AIOKafkaProducer = Depends(get_producer),
        credentials: HTTPBasicCredentials = Depends(security)
):
    token = credentials.credentials
    user_id = auth_handler.decode_token(token)
    try:
        await producer.send_and_wait(
            "views",
            key='{}+{}'.format(user_id, viewed.movie_id).encode(),
            value='{}'.format(viewed.viewed_time).encode()
        )
        return {"saved": 'ok'}

    except Exception as ex:
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=ex.args[0].str())
