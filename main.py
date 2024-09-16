import json
import logging

from crawler.crawler import GitHubCrawler

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


if __name__ == "__main__":
    input_data = {
        "keywords": ["openstack", "nova", "css"],
        "proxies": [
            "51.91.109.83:80",
        ],
        "type": "Repositories"
    }

    crawler = GitHubCrawler(
        keywords=input_data["keywords"],
        proxies=input_data["proxies"],
        search_type=input_data["type"]
    )

    try:
        results = crawler.search()

        logger.info(json.dumps(results, indent=4))
    except Exception as e:
        logger.error(f"An error occurred: {e}")
