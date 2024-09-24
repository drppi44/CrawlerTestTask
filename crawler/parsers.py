import random
from abc import ABC
from abc import abstractmethod
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


# noinspection HttpUrlsUsage
class BaseParser(ABC):
    """
    Abstract base class for GitHub parsers.

    Attributes:
        base_url (str): The base URL for GitHub.
        search_type (str): The type of search to perform (to be defined in subclasses).
        keywords (list[str]): List of keywords to search for.
        proxies (list[str]): List of proxy servers to use for requests.

    Methods:
        _get_random_proxy() -> dict[str, str]:
            Returns a random proxy from the list.

        _get_user_agent_headers() -> dict[str, str]:
            Returns HTTP headers to mimic a browser.

        _get_query_params() -> dict[str, str]:
            Constructs the query parameters for the search.

        search() -> list[dict[str, str]]:
            Abstract method to perform the search (must be implemented in subclasses).

        _parse_results(html: str) -> list[dict[str, str]]:
            Abstract method to parse the search results (must be implemented in subclasses).
    """
    base_url = "https://github.com"
    search_type = None

    def __init__(self, keywords: list[str], proxies: list[str]) -> None:
        """
        Initializes the BaseParser with keywords and proxies.

        Args:
            keywords (list[str]): The keywords to search for.
            proxies (list[str]): The list of proxy servers to use.
        """
        self.keywords: list[str] = keywords
        self.proxies: list[str] = proxies
        self.current_proxy: dict[str, str] | None = None

    def _get_random_proxy(self) -> dict[str, str]:
        """
        Returns a random proxy server from the list.

        Returns:
            dict[str, str]: A dictionary with the proxy configuration.
        """
        return {'https': random.choice(self.proxies)}

    @staticmethod
    def _get_user_agent_headers() -> dict[str, str]:
        """
        Returns HTTP headers that mimic a browser user agent.

        Returns:
            dict[str, str]: A dictionary of HTTP headers.
        """
        return {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/"
                      "webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Content-Type": "text/html; charset=utf-8",
        }

    def _get_query_params(self) -> dict[str, str]:
        """
        Constructs the query parameters for the search.

        Returns:
            dict[str, str]: A dictionary of query parameters.
        """
        return {
            'q': '+'.join(self.keywords),
            'type': self.search_type
        }

    @abstractmethod
    def search(self) -> list[dict[str, str]]:
        """
        Performs the search on GitHub.

        Returns:
            list[dict[str, str]]: A list of search results.

        Raises:
            NotImplementedError: If the method is not implemented in a subclass.
        """
        ...

    @abstractmethod
    def _parse_results(self, html: str) -> list[dict[str, str]]:
        """
        Parses the HTML content of the search results.

        Args:
            html (str): The HTML content of the search results page.

        Returns:
            list[dict[str, str]]: A list of parsed search results.

        Raises:
            NotImplementedError: If the method is not implemented in a subclass.
        """
        ...


class RepositoryParser(BaseParser):
    """
    Parser for searching GitHub repositories.

    Attributes:
        search_type (str): The type of search ('repositories').

    Methods:
        search() -> list[dict[str, str]]:
            Performs the repository search and fetches additional information.

        _parse_results(html: str) -> list[dict[str, str]]:
            Parses the repository search results.

        _fetch_repo_language(item: dict[str, str]) -> None:
            Fetches programming language statistics for a repository.
    """
    search_type = 'repositories'

    def search(self) -> list[dict[str, str]]:
        """
        Performs the repository search and processes the results.

        Returns:
            list[dict[str, str]]: A list of repositories with additional information.

        Raises:
            Exception: If the search request fails.
        """
        from crawler.crawler import MAX_WORKERS

        self.current_proxy = self._get_random_proxy()
        response = requests.get(
            url=urljoin(self.base_url, 'search'),
            proxies=self.current_proxy,
            headers=self._get_user_agent_headers(),
            params=self._get_query_params()
        )

        if response.status_code != 200:
            raise Exception(f"Failed to fetch repository data. HTTP Status Code: {response.status_code}")

        results = self._parse_results(response.text)

        #  may be done with asyncio, will be faster for
        #  big amount of links
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            executor.map(self._fetch_repo_language, results)

        return results

    def _parse_results(self, html: str) -> list[dict[str, str]]:
        """
        Parses the repository search results.

        Args:
            html (str): The HTML content of the search results page.

        Returns:
            list[dict[str, str]]: A list of repositories with basic information.
        """
        soup = BeautifulSoup(html, 'html.parser')
        link_tags = soup.select('div.search-title > a')
        return [{
            'url': urljoin(self.base_url, link['href']),
            'extra': {
                'owner': link['href'].strip('/').split('/')[0],
                "language_stats": {}
            }
        } for link in link_tags]

    def _fetch_repo_language(self, item: dict) -> None:
        """
        Fetches programming language statistics for a repository.

        Args:
            item (dict[str, str]): A dictionary containing repository information.

        Raises:
            Exception: If the request to the repository page fails.
        """
        response = requests.get(
            url=urljoin(self.base_url, item['url']),
            proxies=self.current_proxy,
            headers=self._get_user_agent_headers(),
        )

        if response.status_code != 200:
            raise Exception(f"Failed to fetch language data. HTTP Status Code: {response.status_code}")

        soup = BeautifulSoup(response.text, 'html.parser')
        h2_languages = soup.find('h2', string='Languages')
        span_languages = h2_languages.find_parent('div').select('span.Progress > span')

        for span in span_languages:
            language, percentage = span['aria-label'].rsplit(' ', 1)
            item['extra']['language_stats'][language] = f'{percentage}%'


class WikisIssuesBaseParser(BaseParser):
    """
    Base parser for searching GitHub wikis and issues.

    Methods:
        search() -> list[dict[str, str]]:
            Performs the search and parses the results.

        _parse_results(html: str) -> list[dict[str, str]]:
            Parses the search results.
    """

    def search(self) -> list[dict[str, str]]:
        """
        Performs the search and parses the results.

        Returns:
            list[dict[str, str]]: A list of search results.

        Raises:
            Exception: If the search request fails.
        """
        self.current_proxy = self._get_random_proxy()
        response = requests.get(
            url=urljoin(self.base_url, 'search'),
            proxies=self.current_proxy,
            headers=self._get_user_agent_headers(),
            params=self._get_query_params()
        )

        if response.status_code != 200:
            raise Exception(f"Failed to fetch data. HTTP Status Code: {response.status_code}")

        return self._parse_results(response.text)

    def _parse_results(self, html) -> list[dict[str, str]]:
        """
        Parses the search results for wikis and issues.

        Args:
            html (str): The HTML content of the search results page.

        Returns:
            list[dict[str, str]]: A list of results with URLs.
        """
        soup = BeautifulSoup(html, 'html.parser')
        link_tags = soup.select('div.search-title > a')
        return [{'url': urljoin(self.base_url, link['href'])} for link in link_tags]


class IssuesParser(WikisIssuesBaseParser):
    """
    Parser for searching GitHub issues.

    Attributes:
        search_type (str): The type of search ('issues').
    """
    search_type = 'issues'


class WikisParser(WikisIssuesBaseParser):
    """
    Parser for searching GitHub wikis.

    Attributes:
        search_type (str): The type of search ('wikis').
    """
    search_type = 'wikis'
