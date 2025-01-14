# KeePass SSH Connection Manager

A Python utility that helps you securely connect to SSH servers using credentials stored in a KeePass database. This tool provides a convenient way to manage and use your server credentials while keeping them secure.

## Features

- Load server credentials from KeePass database
- Support for KeePass key file authentication
- Interactive server selection
- Secure SSH connection handling
- Command-line interface for server interaction

## Prerequisites

- Python 3.x
- KeePass database with server credentials
- Required Python packages (see requirements.txt)
- For Windows: PuTTY installed (make sure plink.exe is in your system PATH)
- For Unix-like systems: sshpass installed (e.g., `apt-get install sshpass` on Debian/Ubuntu)

## Setup

1. Clone the repository
2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```
3. Update the provided `.env` file with your database paths:
   ```
   KEEPASS_DB_PATH=your_database.kdbx
   KEEPASS_KEY_PATH=your_keyfile.keyx  # Optional
   ```
4. Add your server credentials to KeePass with the following format:
   - Title: Server name
   - Username: SSH username
   - Password: SSH password
   - URL: hostname:port (e.g., server.example.com:22)

## Configuration

Create a `.env` file with the following variables:
```
KEEPASS_DB_PATH=/path/to/your/database.kdbx
KEEPASS_KEY_PATH=/path/to/your/key.keyx
KEEPASS_GROUP_PATH=Root/Servers/Production  # Optional: filter entries by group
```

The `KEEPASS_GROUP_PATH` variable can be:
- Not set: show all entries
- A group path: show only entries from that group (e.g., "Root/Servers/Production")
- "root": show only entries without a group (root-level entries)

## Server Entry Format

Server entries in the KeePass database should have:
- Title: Server name
- Username: SSH username
- Password: SSH password
- URL: Server hostname with optional port (e.g., "example.com:2222" or just "example.com" for default port 22)
- Notes: Server description (optional)

The script will:
1. Load entries from the specified group (if KEEPASS_GROUP_PATH is set) or all entries
2. Display available servers with their details
3. Connect to the selected server using SSH

## Status
![Tests](https://github.com/grzes-94/keepass-sb/actions/workflows/test.yml/badge.svg)
[![codecov](https://codecov.io/gh/grzes-94/keepass-sb/branch/main/graph/badge.svg)](https://codecov.io/gh/grzes-94/keepass-sb)

## Usage

Run the script:
```bash
python server_connect.py
```

1. The script will display available servers from your KeePass database
2. Select a server by entering its number
3. The script will establish an SSH connection
4. Enter commands to execute on the server
5. Type 'exit' to close the connection


## Dependencies

- pykeepass: KeePass database handling
- python-dotenv: Environment variable management
- colorama: Colored terminal output

## Testing

The project uses pytest for testing. To run the tests locally:

1. Run all tests with coverage and reports:
```bash
pytest
```
This will:
- Run all tests
- Generate an HTML test report (`report.html`)
- Generate a coverage report (`htmlcov/index.html`)
- Show test results in the terminal

2. Run tests with more detailed output:
```bash
pytest -v
```

3. Show coverage in terminal:
```bash
pytest --cov=keepass_ssh --cov-report=term-missing
```

Test configuration is stored in `pytest.ini`, and the following reports are generated:
- `report.html`: Detailed test results
- `htmlcov/index.html`: Code coverage report with line-by-line analysis

Note: Test reports are excluded from git tracking and can be found in your local directory after running the tests.
