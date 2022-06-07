from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    kafka_host: str = Field('localhost', env='KAFKA_HOST')
    kafka_port: str = Field('29092', env='KAFKA_PORT')
    project_name: str = Field('app kafka', env='PROJECT_NAME')

    jwt_secret_key: str = Field('test', env='JWT_SECRET_KEY')

    sentry_dsn: str = Field('123', env='SENTRY_DSN')

    apm_server_host: str = Field('http://localhost', env='APM_SERVER_HOST')
    apm_server_port: str = Field('8200', env='APM_SERVER_PORT')

    class Config:
        env_file = ".env"
