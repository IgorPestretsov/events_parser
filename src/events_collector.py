import json
import logging
import os
from logging import Logger

from config import CollectorConfig
from db_client import DBClient


class Collector:
    def __init__(self, logger: Logger):
        self.logger = logger
        self.config = CollectorConfig()
        self.db_client = DBClient(logger)

    def __call__(self):
        logging.debug("entering call method")
        for root, dirs, files in os.walk(self.config.input_dir):
            for file in files:
                if self._should_process(file):
                    self.logger.debug(f"Processing file: {file}")
                    full_path = os.path.join(root, file)
                    extracted_data = self._parse_json_file(full_path)
                    if extracted_data:
                        self.db_client.write_parsed_data(extracted_data)

                    prefix = self.config.success_label if extracted_data else self.config.failed_label
                    new_file_name = prefix + file
                    new_full_path = os.path.join(root, new_file_name)

                    os.rename(full_path, new_full_path)
                    self.logger.info(f"File {file} processed. Renamed to {new_file_name}.")
                else:
                    self.logger.debug(f"Skipping file: {file}")

    def _should_process(self, filename):
        return filename.endswith(".json") and not (
                filename.startswith(self.config.success_label)
                or filename.startswith(self.config.failed_label))

    def _filter_event(self, event):
        if event.get('EventID') not in self.config.allowed_event_ids:
            return None

        return {field: event[field] for field in self.config.allowed_fields[event['EventID']] if field in event}

    def _parse_json_file(self, file_path):
        parsed_data = []
        with open(file_path, 'r') as file:
            for line in file:
                try:
                    record = json.loads(line)
                    filtered_record = self._filter_event(record)
                    if filtered_record:
                        parsed_data.append(filtered_record)
                except json.JSONDecodeError:
                    return None
        return parsed_data
