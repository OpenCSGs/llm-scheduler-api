import os

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    NAME: str = "fastapi"
    DEBUG: bool = False
    ENV: str = "production"

    BASE_PATH: str = os.path.dirname(os.path.dirname((os.path.abspath(__file__))))

    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = 8080
    SLURM_API: str = "http://localhost:6688"
    SLURM_REST_VERSION: str = "v0.0.40"
    CASDOOR_WEBHOOK_SECRET: str = "8be5e346afb56282c7b12b537466614d"

    URL: str = "http://localhost"
    TIME_ZONE: str = "RPC"
    AUTH_ENDPOINT: str = ""
    AUTH_CLIENTID: str = ""
    AUTH_CLIENTSECRET: str = ""
    AUTH_CERT: str = ""
    ORGNAME: str
    APPNAME: str
    UI_URL: str
    BASE_DN: str = ""
    BIND_DN: str = ""
    BIND_DN_PWD: str = ""
    LDAP_URI: str = ""
    HOME_DIRECTORY: str
    ON_PREMISE: bool = False
    OS_USER_SYNC_INTERVAL: int = 60
    SLURM_DEFAULT_PARTITION: str = "low"
    ADMINISTRATOR: str = "ocadmin"

    class Config:
        env_prefix = "APP_"
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
