import json
import os
from logging import Logger
from typing import Dict, List, Optional

from config import CollectorConfig
from db_client import DBClient


class Collector:
    """Parses event data from JSON files in a specified directory and writes the necessary events to a database."""

    def __init__(self, logger: Logger) -> None:
        """
        Initialize the Collector with logger.

        :param logger: The logger instance used for logging messages.
        """
        self.logger = logger
        self.config = CollectorConfig()
        self.db_client = DBClient(logger)

    def run(self) -> None:
        """Walk through the input directory and process all applicable files."""
        for root, dirs, files in os.walk(self.config.input_dir):
            for file in files:
                if self._should_process(file):
                    self._process_file(root, file)
                else:
                    self.logger.debug(f"Skipping file: {file}")

    def _process_file(self, root: str, file: str) -> None:
        """
        Process the given file.

        :param root: Root directory of the file.
        :param file: Name of the file to process.
        """
        self.logger.debug(f"Processing file: {file}")
        full_path = os.path.join(root, file)
        extracted_data = self._parse_json_file(full_path)
        if extracted_data:
            self.db_client.write_parsed_data(extracted_data)

        self._rename_and_log(root, file, full_path)

    def _rename_and_log(self, root: str, file: str, fullpath: str) -> None:
        """
        Rename the processed file and log the action.

        :param root: Root directory of the file.
        :param file: Name of the file to rename.
        :param fullpath: Full path to the file.
        """
        new_file_name = self.config.processed_label + file
        new_full_path = os.path.join(root, new_file_name)

        os.rename(fullpath, new_full_path)
        self.logger.debug(f"File {file} processed. Renamed to {new_file_name}.")

    def _should_process(self, filename: str) -> bool:
        """
        Determine if the given file should be processed.

        :param filename: Name of the file to check.
        :return: True if the file should be processed, False otherwise.
        """
        return filename.endswith(".json") and not filename.startswith(
            self.config.processed_label
        )

    def _filter_event(self, event: Dict[str, str]) -> Optional[Dict[str, str]]:
        """
        Filter the event data based on allowed events in the configuration.

        :param event: The event data to filter.
        :return: Filtered event data or None if the event is not allowed.
        """
        if event.get("EventID") not in self.config.allowed_events.keys():
            return None

        return {
            field: event[field]
            for field in self.config.allowed_events[event["EventID"]]
            if field in event
        }

    def _parse_json_file(self, file_path: str) -> List[Dict]:
        """
        Parse the JSON file and return filtered events.

        :param file_path: Path to the JSON file.
        :return: List of parsed and filtered events.
        """
        parsed_data = []
        with open(file_path, "r") as file:
            for line_number, line in enumerate(file, 1):
                try:
                    record = json.loads(line)
                    filtered_record = self._filter_event(record)
                    if filtered_record:
                        parsed_data.append(filtered_record)
                except json.JSONDecodeError as e:
                    self.logger.error(
                        f"Error decoding JSON on line {line_number} in {file_path}: {e}"
                    )
        return parsed_data
