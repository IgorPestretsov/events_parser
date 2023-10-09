from logging import Logger
from datetime import datetime

from clickhouse_driver import Client

from config import DatabaseConfig


class DBClient:
    def __init__(self, logger: Logger):
        self.logger = logger
        self.config = DatabaseConfig()
        self.client = Client(host=self.config.host,
                             port=self.config.port,
                             user=self.config.user,
                             password=self.config.password,
                             verify=False,
                             )
        self._setup_database()
        self._setup_tables()

    def _setup_database(self):
        query = self.config.CREATE_DATABASE_QUERY.format(dbname=self.config.database)
        self.client.execute(query)

    def _setup_tables(self):
        for query_template in self.config.CREATE_TABLES_QUERIES:
            query = query_template.format(dbname=self.config.database)
            self.logger.debug(query)
            self.client.execute(query)

    def write_parsed_data(self, data):
        for event in data:
            event['TimeCreated'] = datetime.strptime(event['TimeCreated'], '%Y-%m-%dT%H:%M:%S.%fZ')

        query = (f'INSERT INTO {self.config.database}.sysmon1 '
                 '(EventID, '
                 'ParentProcessGuid, '
                 'Hashes, '
                 'TimeCreated, '
                 'User, '
                 'CommandLine, '
                 'OriginalFileName, '
                 'ProcessGuid, '
                 'CurrentDirectory'
                 ') VALUES')
        self.client.execute(query, data)
