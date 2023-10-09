from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings


class AppConfig(BaseSettings):
    timeout: int = 30

    class Config:
        env_prefix = 'APP_'


class CollectorConfig(BaseSettings):
    input_dir: str = 'input_dir'
    success_label: str = 'SUCCESS_'
    failed_label: str = 'FAILED_'
    allowed_event_ids: list = [1]
    allowed_fields: dict = {
        1: [
            'EventID',
            'ParentProcessGuid',
            "Hashes",
            "TimeCreated",
            "User",
            "CommandLine",
            "OriginalFileName",
            "ProcessGuid",
            "CurrentDirectory",
        ]
    }


class DatabaseConfig(BaseSettings):
    host: str
    port: int
    user: str
    password: str
    database: str

    class Config:
        env_prefix = 'DB_'

    CREATE_DATABASE_QUERY: str = "CREATE DATABASE IF NOT EXISTS {dbname};"
    CREATE_TABLES_QUERIES: list = [
        "CREATE TABLE IF NOT EXISTS {dbname}.sysmon1("
        "EventID Int8,"
        "ParentProcessGuid String,"
        "Hashes String,"
        "TimeCreated DateTime,"
        "User String,"
        "CommandLine String,"
        "OriginalFileName String,"
        "ProcessGuid String,"
        "CurrentDirectory String"
        ") ENGINE = MergeTree() ORDER BY ProcessGuid;",
    ]

    @field_validator('port')
    def validate_port(cls, port):
        if port <= 0 or port > 65535:
            raise ValueError('Invalid port number')
        return port


class LogConfig(BaseSettings):
    """Logging configuration to be set for the server."""

    name: str = "events_parser"
    format: str = (
        "[%(asctime)s] %(levelname)s [%(filename)s:%(lineno)d] %(message)s"
    )
    level: str = "INFO"
    path: Path = Path(f"logs/{name}.log")
    version: int = 1

    @property
    def log_config_dict(self):
        return {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": self.format,
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                },
            },
            "handlers": {
                "streamHandler": {
                    "formatter": "default",
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stderr",
                },
                "fileHandler": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "formatter": "default",
                    "filename": self.path,
                    "backupCount": 10,
                    "maxBytes": 1024 * 1024 * 10,
                },
            },
            "loggers": {
                self.name: {
                    "handlers": ["streamHandler", "fileHandler"],
                    "level": self.level,
                },
            },
        }

    class Config:
        env_prefix = 'LOG_'
        case_sensitive = False
