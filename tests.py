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
    def _get_mock_html_search_result(links):
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

    @staticmethod
    def _get_mock_repo_page_with_languages(languages_str):
        mock_response = Mock()
        mock_html = '''
                <html>
                    <body>
                    <div>
                        <h2>Languages</h2>
                        <span class="Progress">
                '''

        for language_str in languages_str:
            mock_html += f'<span aria-label="{language_str}"></span>'

        mock_html += '''
                        </span>
                    </div>
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

    @patch('crawler.parsers.requests.get')
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

        self.assertEqual(str(cm.exception), "Failed to fetch repository data. HTTP Status Code: 429")

    @patch('crawler.parsers.requests.get')
    def test_get_repositories(self, mock_get):
        mock_search_response = self._get_mock_html_search_result((
            '/atuldjadhav/DropBox-Cloud-Storage',
            '/michealbalogun/Horizon-dashboard'))
        mock_repos_response = self._get_mock_repo_page_with_languages(
            ['Python 97.3', 'Other 2.7'])

        mock_get.side_effect = [mock_search_response, mock_repos_response]

        result = GitHubCrawler(
            keywords=self.keywords,
            proxies=self.proxies,
            search_type="Repositories"
        ).search()

        self.assertEqual(result, [
            {'extra': {'language_stats': {'Other': '2.7%', 'Python': '97.3%'},
                       'owner': 'atuldjadhav'},
             'url': 'https://github.com/atuldjadhav/DropBox-Cloud-Storage'},
            {'extra': {'language_stats': {}, 'owner': 'michealbalogun'},
             'url': 'https://github.com/michealbalogun/Horizon-dashboard'}])

    @patch('crawler.parsers.requests.get')
    def test_get_issues(self, mock_get):
        mock_get.return_value = self._get_mock_html_search_result((
            '/altai/nova-billing/issues/1',
            '/sfPPP/openstack-note/issues/8'
        ))

        result = GitHubCrawler(
            keywords=self.keywords,
            proxies=self.proxies,
            search_type="Issues"
        ).search()

        self.assertEqual(result, [
            {'url': 'https://github.com/altai/nova-billing/issues/1'},
            {'url': 'https://github.com/sfPPP/openstack-note/issues/8'}])

    @patch('crawler.parsers.requests.get')
    def test_get_wikis(self, mock_get):
        mock_get.return_value = self._get_mock_html_search_result((
            '/vault-team/vault-website/wiki/Quick-installation-guide',
            '/escrevebastante/tongue/wiki/Home'
        ))

        result = GitHubCrawler(
            keywords=self.keywords,
            proxies=self.proxies,
            search_type="Wikis"
        ).search()

        self.assertEqual(result, [
            {'url': 'https://github.com/vault-team/vault-website/wiki/Quick-installation-guide'},
            {'url': 'https://github.com/escrevebastante/tongue/wiki/Home'}])
