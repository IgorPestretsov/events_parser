# Windows Sysmon Events Parser

## Introduction:
This project is designed to parse and store specific events from Windows Sysmon logs. These logs are read from JSON files in a specified directory and then written to a ClickHouse database for persistence.

## Usage:

### 1. **Prerequisites:**
- Docker and Docker Compose installed on the host machine.

### 2. **Configuration:**
For Dockerized deployments, you should use the provided `.env` file for environment-specific settings.

**Changing Passwords:**
To change the password, you need to modify the credentials in both `clickhouse_cfg/users.xml` and the `.env` file to ensure they match.

### 3. **Running the Parser:**
- Place the Sysmon event logs (in JSON format) in the `input_dir`.
- Start the services using Docker Compose:
  ```bash
  docker-compose up -d --build
  ```
- For testing purposes, you can rename the files in the `input_dir` by removing the trailing underscore (if present).

### 4. **Accessing the ClickHouse Database:**
- You can access the ClickHouse database on the default ports:
    - HTTP Interface: 8123
    - Native Interface: 9000

### 5. **Logs and Data Persistence:**
- The application logs are stored in the `logs` directory.
- The ClickHouse data is persisted in the `clickhouse_data` directory.
- Custom user configurations for ClickHouse can be placed in `clickhouse_cfg/users.xml`.
