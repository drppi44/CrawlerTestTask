import random
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


class GitHubCrawler:
    """
    A class to crawl GitHub search results for repositories, issues, or wikis based on keywords.

    Attributes:
        keywords (list): A list of keywords to search for.
        proxies (list): A list of proxy servers to use for requests.
        search_type (str): The type of search to perform. Must be one of 'repositories', 'wikis', or 'issues'.
        base_url (str): The base URL for GitHub.

    Methods:
        _get_random_proxy() -> dict:
            Selects a random proxy from the provided list of proxies.

        _get_user_agent_headers() -> dict:
            Returns headers to be used in HTTP requests to mimic a browser.

        search() -> list[dict]:
            Executes the search on GitHub based on the initialized keywords and search type.
            Returns a list of dictionaries, each containing the URL of a search result.

        parse_results(html: str) -> list[dict]:
            Parses the HTML content returned from a GitHub search to extract relevant links.
            Returns a list of dictionaries, each containing the URL of a search result.
    """

    # noinspection HttpUrlsUsage
    def __init__(self, keywords: list[str], proxies: list[str], search_type: str, ) -> None:
        """
        Initializes the GitHubCrawler with keywords, proxies, and search type.

        Args:
            keywords (list[str]): A list of keywords to use for the search query.
            proxies (list[str]): A list of proxy servers to rotate through when making requests.
            search_type (str): The type of search to conduct. Should be 'repositories', 'wikis', or 'issues'.

        Raises:
            Exception: If an invalid search type is provided.
        """
        self.keywords: list[str] = keywords
        self.proxies: list[str] = proxies
        self.search_type = search_type.lower()
        self.base_url = "http://github.com"

        if self.search_type not in ('repositories', 'wikis', 'issues'):
            raise Exception(f"Unknown search_type: {self.search_type}")

    def _get_random_proxy(self) -> dict[str, str]:
        """
        Selects a random proxy from the list of proxies.

        Returns:
            dict: A dictionary with the selected proxy server.
        """
        return {'http': random.choice(self.proxies)}

    @staticmethod
    def _get_user_agent_headers() -> dict[str, str]:
        """
        Generates HTTP headers that simulate a request from a web browser.

        Returns:
            dict: A dictionary containing HTTP headers for the request.
        """
        return {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/"
                      "webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Content-Type": "text/html; charset=utf-8",
        }

    def _get_query_params(self) -> dict[str, str]:
        return {
            'q': '+'.join(self.keywords),
            'type': self.search_type
        }

    def search(self) -> list[dict[str, str]]:
        """
        Executes a search on GitHub based on the provided keywords and search type.

        Returns:
            list[dict]: A list of dictionaries, where each dictionary contains the URL of a search result.

        Raises:
            Exception: If the HTTP request to GitHub fails (status code != 200).
        """
        response = requests.get(
            url=urljoin(self.base_url, 'search'),
            proxies=self._get_random_proxy(),
            headers=self._get_user_agent_headers(),
            params=self._get_query_params()
        )

        if response.status_code != 200:
            raise Exception(f"Failed to fetch data. HTTP Status Code: {response.status_code}")

        return self.parse_results(response.text)

    def parse_results(self, html) -> list[dict[str, str]]:
        """
        Parses the HTML content of the GitHub search results page.

        Args:
            html (str): The HTML content returned from a GitHub search.

        Returns:
            list[dict]: A list of dictionaries, where each dictionary contains the URL of a search result.
        """
        soup = BeautifulSoup(html, 'html.parser')
        link_tags = soup.select('div.search-title > a')

        return [{'url': urljoin(self.base_url, link['href'])} for link in link_tags]
