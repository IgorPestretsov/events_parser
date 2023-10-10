from datetime import datetime
from logging import Logger

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
        grouped_data = {}
        for event in data:
            event_id = int(event.get('EventID'))
            if 'UtcTime' in event:
                event['UtcTime'] = datetime.strptime(event['UtcTime'], '%Y-%m-%d %H:%M:%S.%f')

            if event_id not in grouped_data:
                grouped_data[event_id] = []

            grouped_data[event_id].append(event)

        for event_id, events in grouped_data.items():
            keys = events[0].keys()
            columns = ', '.join(keys)

            query = (f'INSERT INTO {self.config.database}.sysmon{event_id} '
                     f'({columns}) VALUES')
            self.logger.debug(query)

            values = [tuple(event[key] for key in keys) for event in events]
            self.client.execute(query, values)
