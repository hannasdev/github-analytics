# /tests/test_github_client.py
import io
import sys
import unittest
from unittest.mock import patch, Mock
from github_api.client import GitHubClient
import requests


class TestGitHubClient(unittest.TestCase):
    def setUp(self):
        self.client = GitHubClient()

    @patch('github_api.client.requests.get')
    def test_get_repo_commits_single_page(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = [{'sha': 'abc123'}, {'sha': 'def456'}]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        commits = self.client.get_repo_commits('testuser', 'testrepo')

        print(f"Single page test - Number of commits: {len(commits)}")
        print(f"Single page test - API calls: {mock_get.call_count}")

        self.assertEqual(len(commits), 2)
        self.assertEqual(commits[0]['sha'], 'abc123')
        self.assertEqual(commits[1]['sha'], 'def456')
        mock_get.assert_called_once_with(
            'https://api.github.com/repos/testuser/testrepo/commits',
            headers=self.client.headers,
            params={'page': 1, 'per_page': 100}
        )

    @patch('github_api.client.requests.get')
    def test_get_repo_commits_multiple_pages(self, mock_get):
        mock_responses = [
            Mock(json=lambda: [{'sha': f'commit{i}'} for i in range(100)]),
            Mock(json=lambda: [{'sha': f'commit{i}'} for i in range(100, 150)]),
            Mock(json=lambda: [])  # This response should not be called
        ]
        for i, response in enumerate(mock_responses):
            response.raise_for_status.return_value = None
            print(f"Mock response {i + 1}: {len(response.json())}")
        mock_get.side_effect = mock_responses

        commits = self.client.get_repo_commits('testuser', 'testrepo')

        print(f"Multiple pages test - Number of commits: {len(commits)}")
        print(f"Multiple pages test - First commit: {commits[0]['sha']}")
        print(f"Multiple pages test - Last commit: {commits[-1]['sha']}")
        print(f"Multiple pages test - Number of API calls: {mock_get.call_count}")

        self.assertEqual(len(commits), 150)
        self.assertEqual(commits[0]['sha'], 'commit0')
        self.assertEqual(commits[-1]['sha'], 'commit149')
        self.assertEqual(mock_get.call_count, 2)  # Changed from 3 to 2

    @patch('github_api.client.requests.get')
    def test_get_repo_commits_error(self, mock_get):
        mock_get.side_effect = requests.RequestException("API Error")

        # Capture the printed output
        captured_output = io.StringIO()
        sys.stdout = captured_output

        commits = self.client.get_repo_commits('testuser', 'testrepo')

        # Restore stdout
        sys.stdout = sys.__stdout__

        self.assertEqual(commits, [])  # Check that an empty list is returned
        self.assertIn("Error fetching commits for testrepo: API Error", captured_output.getvalue())  # Check the error message


if __name__ == '__main__':
    unittest.main()
