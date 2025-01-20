# KeePass SSH Connect

[![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/grzes-94/keepass-ssh-connect/test.yml?label=Tests)](https://github.com/grzes-94/keepass-ssh-connect/actions)
[![Codecov](https://img.shields.io/codecov/c/github/grzes-94/keepass-ssh-connect)](https://codecov.io/gh/grzes-94/keepass-ssh-connect)
[![GitHub License](https://img.shields.io/github/license/grzes-94/keepass-ssh-connect)](https://github.com/grzes-94/keepass-ssh-connect/blob/master/LICENSE)

A Python utility that helps you securely connect to SSH servers using credentials stored in a KeePass database. This tool provides a convenient way to manage and use your server credentials while keeping them secure.

## Features

- 🔐 Securely store SSH server credentials in KeePass
- 🚀 Easy command-line interface for server connections
- 🔍 Flexible server filtering and selection
- 📋 List and manage server entries
- 🔑 Support for key files and environment variables

## Installation

Install using pip:

```bash
pip install keepass-ssh-connect
```

## Prerequisites

- Python 3.8+
- KeePass database with SSH server entries
- Required Python packages (installed automatically):
  - pykeepass
  - paramiko
  - python-dotenv
  - colorama

## Usage

### Basic Usage

```bash
# List all servers
keepass-ssh-connect -l

# Connect to a specific server
keepass-ssh-connect -s "production"

# Specify database and group
keepass-ssh-connect -d /path/to/database.kdbx -g "/Servers/Production"
```

### Full CLI Options

```
usage: keepass-ssh-connect [-h] [-d DATABASE] [-k KEY_FILE] [-g GROUP] 
                            [-s SERVER] [-l] [-v]

KeePass SSH Connection Utility

optional arguments:
  -h, --help            show this help message and exit
  -d DATABASE, --database DATABASE
                        Path to the KeePass database file
  -k KEY_FILE, --key-file KEY_FILE
                        Path to the KeePass key file (optional)
  -g GROUP, --group GROUP
                        KeePass group path to filter server entries
  -s SERVER, --server SERVER
                        Specific server name or partial match to connect to
  -l, --list            List available servers without connecting
  -v, --verbose         Enable verbose output
```

## Environment Variables

You can also use environment variables for default settings:

- `KEEPASS_DB_PATH`: Path to the KeePass database
- `KEEPASS_KEY_PATH`: Path to the key file
- `KEEPASS_GROUP_PATH`: Default group path for server entries

## Local File Discovery

If no database path is specified through command-line parameters or environment variables, the utility will automatically search the current directory for KeePass files:

- It looks for `.kdbx` files for the database
- It looks for `.keyx` files for the key file

When local files are discovered, the utility will print the paths of the files being used, helping you understand which files are being automatically selected.

### Example

```bash
# If you have 'mypasswords.kdbx' and 'mykey.keyx' in the current directory
keepass-ssh-connect
# This will print:
# Using local database file: mypasswords.kdbx
# Using local key file: mykey.keyx
```

**Note**: Local file discovery provides convenience but should be used carefully to avoid unintended file selection.

## Configuration in KeePass

1. Create a group for SSH servers
2. For each server, add an entry with:
   - Title: Server name
   - Username: SSH username
   - Password: SSH password
   - URL: Server hostname or IP
   - Notes: Additional connection details

## Security

- Credentials are never stored in plain text
- Supports KeePass key files for additional security
- Uses environment variables to avoid hardcoding sensitive information

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/grzes-94/keepass-ssh-connect/blob/master/LICENSE) file for details.

## Author

[Grzes-94](https://github.com/grzes-94)
