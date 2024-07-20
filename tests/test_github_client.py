import unittest
from unittest.mock import patch, Mock
from github_api.client import GitHubClient


class TestGitHubClient(unittest.TestCase):
    def setUp(self):
        self.client = GitHubClient()

    @patch('github_api.client.requests.get')
    def test_get_user_repos(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = [{'name': 'repo1'}, {'name': 'repo2'}]
        mock_get.return_value = mock_response

        repos = self.client.get_user_repos('testuser')

        self.assertEqual(len(repos), 2)
        self.assertEqual(repos[0]['name'], 'repo1')
        self.assertEqual(repos[1]['name'], 'repo2')
        mock_get.assert_called_once_with(
            'https://api.github.com/users/testuser/repos',
            headers=self.client.headers
        )
