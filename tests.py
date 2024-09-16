import unittest
from unittest.mock import Mock
from unittest.mock import patch

from crawler import GitHubCrawler


# noinspection HttpUrlsUsage
class TestGitHubCrawler(unittest.TestCase):
    def setUp(self):
        self.keywords = ["openstack", "nova", "css"]
        self.proxies = ["194.126.37.94:8080", "13.78.125.167:8080"]
        self.search_type = "Repositories"

    @staticmethod
    def _get_mock_html(links):
        mock_response = Mock()
        mock_html = '''
        <html>
            <body>
        '''

        for link in links:
            mock_html += f'<div class="search-title"><a href="{link}"></a></div>'

        mock_html += '''
            </body>
        </html>
        '''
        mock_response.text = mock_html.encode('utf-8')
        mock_response.status_code = 200

        return mock_response

    def test_wrong_search_type_raises_error(self):
        with self.assertRaises(Exception) as cm:
            GitHubCrawler(
                keywords=self.keywords,
                proxies=self.proxies,
                search_type="wrong-type"
            )

        self.assertEqual(str(cm.exception), 'Unknown search_type: wrong-type')

    @patch('crawler.crawler.requests.get')
    def test_raises_error_on_non_200_response(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 429
        mock_get.return_value = mock_response

        with self.assertRaises(Exception) as cm:
            GitHubCrawler(
                keywords=self.keywords,
                proxies=self.proxies,
                search_type=self.search_type
            ).search()

        self.assertEqual(str(cm.exception), "Failed to fetch data. HTTP Status Code: 429")

    @patch('crawler.crawler.requests.get')
    def test_get_repositories(self, mock_get):
        mock_get.return_value = self._get_mock_html((
            '/atuldjadhav/DropBox-Cloud-Storage',
            '/michealbalogun/Horizon-dashboard'
        ))

        result = GitHubCrawler(
            keywords=self.keywords,
            proxies=self.proxies,
            search_type="Repositories"
        ).search()

        self.assertEqual(result, [
            {'url': 'http://github.com/atuldjadhav/DropBox-Cloud-Storage'},
            {'url': 'http://github.com/michealbalogun/Horizon-dashboard'}])

    @patch('crawler.crawler.requests.get')
    def test_get_issues(self, mock_get):
        mock_get.return_value = self._get_mock_html((
            '/altai/nova-billing/issues/1',
            '/sfPPP/openstack-note/issues/8'
        ))

        result = GitHubCrawler(
            keywords=self.keywords,
            proxies=self.proxies,
            search_type="Issues"
        ).search()

        self.assertEqual(result, [
            {'url': 'http://github.com/altai/nova-billing/issues/1'},
            {'url': 'http://github.com/sfPPP/openstack-note/issues/8'}])

    @patch('crawler.crawler.requests.get')
    def test_get_wikis(self, mock_get):
        mock_get.return_value = self._get_mock_html((
            '/vault-team/vault-website/wiki/Quick-installation-guide',
            '/escrevebastante/tongue/wiki/Home'
        ))

        result = GitHubCrawler(
            keywords=self.keywords,
            proxies=self.proxies,
            search_type="Wikis"
        ).search()

        self.assertEqual(result, [
            {'url': 'http://github.com/vault-team/vault-website/wiki/Quick-installation-guide'},
            {'url': 'http://github.com/escrevebastante/tongue/wiki/Home'}])
