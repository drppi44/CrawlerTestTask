from crawler.parsers import BaseParser
from crawler.parsers import IssuesParser
from crawler.parsers import RepositoryParser
from crawler.parsers import WikisParser

MAX_WORKERS = 10


class GitHubCrawler:
    """
    Main class for crawling GitHub based on the specified search type.

    Attributes:
        parser (BaseParser): An instance of a parser class appropriate for the search type.

    Methods:
        search():
            Executes the search using the selected parser and returns the results.
    """
    # noinspection HttpUrlsUsage
    def __init__(self, keywords: list[str], proxies: list[str], search_type: str, ) -> None:
        """
        Initializes the GitHubCrawler with the given keywords, proxies, and search type.

        Args:
            keywords (list[str]): A list of keywords to search for.
            proxies (list[str]): A list of proxy servers to use.
            search_type (str): The type of search ('repositories', 'wikis', or 'issues').

        Raises:
            Exception: If an unknown search type is provided.
        """
        search_type = search_type.lower()

        match search_type:
            case RepositoryParser.search_type:
                parser_cls = RepositoryParser
            case WikisParser.search_type:
                parser_cls = WikisParser
            case IssuesParser.search_type:
                parser_cls = IssuesParser
            case _:
                raise Exception(f"Unknown search_type: {search_type}")

        self.parser: BaseParser = parser_cls(keywords=keywords, proxies=proxies)

    def search(self):
        """
        Executes the search using the selected parser.

        Returns:
            list[dict[str, str]]: A list of search results from the parser.
        """
        return self.parser.search()
