# Data Engineering API Exercise

This project is a Python-based application designed to interact with the KrakenFlex API. The program retrieves outage data, processes it, and sends it to a specified site endpoint. It uses the provided API to demonstrate how to work with JSON data, error handling, and API communication using HTTP requests.

## Project Overview

The script performs the following tasks:

1. Retrieves all outages from the `GET /outages` endpoint.
2. Retrieves site information from the `GET /site-info/{siteId}` endpoint for the site with the ID `norwich-pear-tree`.
3. Filters the outages by:
   - Ensuring the outage start time is after `2022-01-01T00:00:00.000Z`.
   - Ensuring the outage’s ID matches the devices listed for the site.
4. Attaches the device's display name to the filtered outages.
5. Sends the filtered outages to the `POST /site-outages/{siteId}` endpoint for the site `norwich-pear-tree`.

## Requirements

- Python 3.7 or higher
- `requests` library for API calls.
- `unittest2`, `pytest` and `mock` libraries for testing.

## Installation and Usage

1. Clone the repository:

```
git clone https://github.com/faisalm1997/Data_Engineering_API_Exercise.git
```

2. Create and activate a virtual environment

```
python3 -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

3. Configuration 

1. Create a .env file in the project root
2. Add your API key:
```
KRAKENFLEX_API_KEY=your_api_key_here
```

4. Use the makefile to run the programme, test the programme, clean temp files and install dependencies

### Install dependencies and set up virtual environment
make install

### Run the script
make run

### Run tests
make test

### Lint the code
make lint

### Clean up
make clean

## Directory Structure 
```
krakenflex-outage-processor/
│
├── .env                    # Environment variables (gitignored)
├── .gitignore              # Git ignore file
├── Makefile                # Automation and development tasks
├── README.md               # Project documentation
├── requirements.txt        # Programme dependencies
│
├── src/
│   └── main.py        # Main processing logic
│
├── tests/
│   └── tests_main.py   # Unit tests (only file in tests)
```

## Notes

- The script defaults to processing the 'norwich-pear-tree' site
- API key must be provided via environment variable in the .env file