import logging
from logging.config import dictConfig
from time import sleep

from config import AppConfig, LogConfig
from db_client import DBClient
from events_collector import Collector

dictConfig(LogConfig().log_config_dict)
logger = logging.getLogger("events_parser")
cfg = AppConfig()
db_client = DBClient(logger)
collector = Collector(logger)


def main() -> None:
    """Continuously collects and processes events with pauses between runs."""
    while True:
        collector.run()
        sleep(cfg.timeout)


if __name__ == '__main__':
    main()
