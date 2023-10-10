from pathlib import Path

from pydantic_settings import BaseSettings


class AppConfig(BaseSettings):
    """Configuraion for application."""

    timeout: int = 30

    class Config:
        env_prefix = "APP_"


class CollectorConfig(BaseSettings):
    """Configuration for collector class."""

    input_dir: str = "input_dir"
    processed_label: str = "PROCESSED_"
    allowed_events: dict = {
        1: [
            "EventID",
            "ParentProcessGuid",
            "Hashes",
            "UtcTime",
            "User",
            "CommandLine",
            "OriginalFileName",
            "ProcessGuid",
            "CurrentDirectory",
            "Hostname",
            "AccountName",
        ],
        # TODO add hostname to sysmon1
        3: [
            "EventID",
            "UtcTime",
            "ProcessGuid",
            "host",
            "User",
            "Protocol",
            "SourcePort",
            "DestinationPort",
            "SourceIp",
            "DestinationIp",
            "Initiated",
        ],
        12: [
            "EventID",
            "UtcTime",
            "ProcessGuid",
            "EventType",
            "Image",
            "Hostname",
            "TargetObject",
        ],
        13: [
            "EventID",
            "UtcTime",
            "ProcessGuid",
            "EventType",
            "Image",
            "Hostname",
            "TargetObject",
        ],
    }


class DatabaseConfig(BaseSettings):
    """Configuration for database client."""

    host: str
    port: int
    user: str
    password: str
    database: str

    class Config:
        env_prefix = "DB_"

    CREATE_DATABASE_QUERY: str = "CREATE DATABASE IF NOT EXISTS {dbname};"
    CREATE_TABLES_QUERIES: list = [
        "CREATE TABLE IF NOT EXISTS {dbname}.sysmon1("
        "EventID Int32,"
        "ParentProcessGuid String,"
        "Hashes String,"
        "UtcTime DateTime,"
        "User String,"
        "CommandLine String,"
        "OriginalFileName String,"
        "ProcessGuid String,"
        "CurrentDirectory String,"
        "Hostname String,"
        "AccountName String"
        ") ENGINE = MergeTree() ORDER BY ProcessGuid;",

        "CREATE TABLE IF NOT EXISTS {dbname}.sysmon12("
        "EventID Int32,"
        "UtcTime DateTime,"
        "ProcessGuid String,"
        "EventType String,"
        "Image String,"
        "Hostname String,"
        "TargetObject String"
        ") ENGINE = MergeTree() ORDER BY ProcessGuid;",

        "CREATE TABLE IF NOT EXISTS {dbname}.sysmon13("
        "EventID Int32,"
        "UtcTime DateTime,"
        "ProcessGuid String,"
        "EventType String,"
        "Image String,"
        "Hostname String,"
        "TargetObject String"
        ") ENGINE = MergeTree() ORDER BY ProcessGuid;",

        "CREATE TABLE IF NOT EXISTS {dbname}.sysmon3("
        "EventID Int32,"
        "UtcTime DateTime,"
        "ProcessGuid String,"
        "host String,"
        "User String,"
        "Protocol String,"
        "SourcePort String,"
        "DestinationPort String,"
        "SourceIp String,"
        "DestinationIp String,"
        "Initiated String"
        ") ENGINE = MergeTree() ORDER BY ProcessGuid;",
    ]


class LogConfig(BaseSettings):
    """Logging configuration to be set for the server."""

    name: str = "events_parser"
    format: str = "[%(asctime)s] %(levelname)s [%(filename)s:%(lineno)d] %(message)s"
    level: str = "INFO"
    path: Path = Path(f"logs/{name}.log")
    version: int = 1

    @property
    def log_config_dict(self) -> None:
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
        env_prefix = "LOG_"
        case_sensitive = False
