import json
import uuid
from typing import List

import backoff
from clickhouse_driver import Client
from config import Settings
from kafka import KafkaConsumer, OffsetAndMetadata, TopicPartition
from kafka.errors import NoBrokersAvailable

settings = Settings()

MESSAGES_COUNT = settings.messages_count


def create_table(client: Client) -> None:
    """
    Create table in Clickhouse.

    :param client: Clickhouse connection
    """
    client.execute(
        """CREATE TABLE IF NOT EXISTS views (
            id String,
            user_id String,
            movie_id String,
            timestamp_movie Int64,
            time Int64
            ) Engine=MergeTree() ORDER BY id
     """)


@backoff.on_exception(backoff.expo, Exception, max_tries=3)
def insert_in_clickhouse(client: Client, data: List[str]) -> None:
    """
    Insert data in clickhouse.

    :param client: Clickhouse connection
    :param data: Data for load
    """
    client.execute(
        """
        INSERT INTO views (
        id, user_id, movie_id, timestamp_movie, time)  VALUES {0}
        """.format(', '.join(i for i in data)))


def etl(consumer: KafkaConsumer, clickhouse_client: Client) -> None:
    """
    Transform data and load to Clickhouse.

    :param consumer: Kafka consumer connection
    :param clickhouse_client: Clickhouse connection
    """
    data = []
    for message in consumer:
        one_msg = (str(uuid.uuid4()), *str(message.key.decode('utf-8')).split('+'), message.value, message.timestamp)
        data.append(str(one_msg))
        if len(data) == MESSAGES_COUNT:
            insert_in_clickhouse(clickhouse_client, data)
            data.clear()
            tp = TopicPartition(settings.kafka_topic, message.partition)
            options = {tp: OffsetAndMetadata(message.offset + 1, None)}
            consumer.commit(options)


@backoff.on_exception(backoff.expo, NoBrokersAvailable)
def main() -> None:
    """Make etl process method."""
    consumer = KafkaConsumer(
        settings.kafka_topic,
        bootstrap_servers=[f'{settings.kafka_host}:{settings.kafka_port}'],
        auto_offset_reset='earliest',
        enable_auto_commit=False,
        group_id='movies',
        value_deserializer=lambda x: json.loads(x.decode('utf-8')),
    )
    clickhouse_client = Client(host=settings.clickhouse_host, port=settings.clickhouse_port)

    create_table(clickhouse_client)
    etl(consumer, clickhouse_client)


if __name__ == "__main__":
    main()
