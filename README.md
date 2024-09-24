# GitHub Crawler

This project is a GitHub crawler implemented in Python, designed to search GitHub for repositories, issues, or wikis based on provided keywords. It supports the usage of proxy servers to make HTTP requests and mimics browser requests to avoid detection. The crawler is efficient, designed for low memory and CPU usage.

## Features

- **Search Types:** Supports searching for Repositories, Issues, and Wikis.
- **Proxy Support:** Allows random selection of proxy servers for requests.
- **Browser-like Requests:** Uses custom headers to mimic browser behavior.
- **HTML Parsing:** Extracts URLs directly from the raw HTML of the GitHub search results.

## Requirements

- Python 3.12
- Virtualenv

## Installation

Install the required packages using pip:

```bash
pip install -r requirements.txt
```

## Usage
To use the GitHubCrawler, you can follow the example below. 
This script will search GitHub for repositories related to the 
keywords, using a specified proxy. Also, feel free to use main.py 
for some experiments.

```python
from crawler import GitHubCrawler

input_data = {
    "keywords": ["openstack", "nova", "css"],
    "proxies": [
        "39.109.113.97:3128",
    ],
    "type": "Repositories"
}

crawler = GitHubCrawler(
    keywords=input_data["keywords"],
    proxies=input_data["proxies"],
    search_type=input_data["type"]
)

results = crawler.search()
```

## Testing
Unit tests are included in the project to ensure proper 
functionality. The tests are designed to mock `requests.get` 
so that they do not make actual HTTP requests.

To run the tests, use the following command:

```bash
python -m unittest tests
```

## Code Coverage
To check the test coverage of the project, use the following commands:
```bash
coverage run -m unittest discover
coverage report
```

The result looks like:
```bash
Name                  Stmts   Miss  Cover
-----------------------------------------
crawler/__init__.py       2      0   100%
crawler/crawler.py       19      0   100%
crawler/parsers.py       64      4    94%
tests.py                 58      0   100%
-----------------------------------------
TOTAL                   143      4    97%

```
## Notes
The crawler only processes the first page of search results.
The provided proxies in the example may not be available.
Unicode characters are supported in the search keywords.