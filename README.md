# Path Analysis Service

This project is a Python-based service that performs path analysis on a set of predefined hostnames. It uses the `mtr` tool to trace the route and analyze network performance.

## Features

- Monitors a set of predefined hostnames.
- Analyzes the path to each host and logs any changes.
- Sends notifications when significant changes are detected.

## Requirements

- Python 3.11
- Pip 3.11
- `mtr` tool installed on your system
- Python packages: `requests`

## Installation

1. Clone the repository.
2. Run the `setup.sh` script to install Python 3.11, Pip 3.11, and the required Python packages.
3. The `setup.sh` script also sets up a systemd service for the path analysis service.

## Usage

After installation, the path analysis service will start automatically. It will run in the background and log any path changes to the predefined hostnames.

## Uninstallation

To uninstall the service, run the `uninstall.sh` script. This will stop the service and remove it from systemd.

## License

This project is licensed under the MIT License - see the LICENSE.md file for details