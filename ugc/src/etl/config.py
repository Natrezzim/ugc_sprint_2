from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    kafka_host: str = Field('localhost', env='KAFKA_HOST')
    kafka_port: str = Field('29092', env='KAFKA_PORT')
    kafka_topic: str = Field('views', env='KAFKA_TOPIC')
    clickhouse_host: str = Field('localhost', env='CLICKLHOUSE_HOST')
    clickhouse_port: int = Field('9000', env='CLICKLHOUSE_PORT')
    messages_count: int = Field('1000', env='MESSAGES_COUNT')

    class Config:
        env_file = ".env"
