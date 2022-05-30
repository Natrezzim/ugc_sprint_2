from typing import Optional

from aiokafka import AIOKafkaProducer

aio_producer: Optional[AIOKafkaProducer] = None


async def get_producer():
    return aio_producer
