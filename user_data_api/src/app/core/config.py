from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    project_name: str = Field('app kafka', env='PROJECT_NAME')

    jwt_secret_key: str = Field('test', env='JWT_SECRET_KEY')

    sentry_dsn: str = Field('123', env='SENTRY_DSN')

    apm_server_host: str = Field('http://localhost', env='APM_SERVER_HOST')
    apm_server_port: str = Field('8200', env='APM_SERVER_PORT')

    mongo_db_name: str = Field('someDb', env='MONGO_DB')
    mongo_host: str = Field('mongos1', env='MONGO_HOST')
    mongo_port: str = Field('27017', env='MONGO_PORT')


    class Config:
        env_file = ".env"
