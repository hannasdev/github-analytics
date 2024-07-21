# /tests/test_collaboration_metrics.py
import unittest
from unittest.mock import patch, MagicMock
from collaboration_metrics import get_pull_requests_stats, get_contributor_count


class TestCollaborationMetrics(unittest.TestCase):

    @patch('collaboration_metrics.GitHubClient')
    def test_get_pull_requests_stats(self, mock_client):
        # Mock the API response
        mock_client.return_value.get_pull_requests.return_value = [
            {'state': 'open'},
            {'state': 'closed'},
            {'state': 'closed'},
            {'state': 'open'}
        ]

        result = get_pull_requests_stats('test_user', 'test_repo')
        self.assertEqual(result, {'opened': 2, 'closed': 2})

    @patch('collaboration_metrics.GitHubClient')
    def test_get_contributor_count(self, mock_client):
        # Mock the API response
        mock_client.return_value.get_repo_contributors.return_value = [
            {'login': 'user1'},
            {'login': 'user2'},
            {'login': 'user3'}
        ]

        result = get_contributor_count('test_user', 'test_repo')
        self.assertEqual(result, (3, 0))  # 3 contributors, 0 repos without contributors

    @patch('collaboration_metrics.GitHubClient')
    def test_get_contributor_count_multiple_repos(self, mock_client):
        # Mock the API response for multiple repos
        mock_client.return_value.get_repo_contributors.side_effect = [
            [{'login': 'user1'}, {'login': 'user2'}],
            [{'login': 'user2'}, {'login': 'user3'}],
            [{'login': 'user1'}, {'login': 'user3'}, {'login': 'user4'}]
        ]

        result = get_contributor_count('test_user', ['repo1', 'repo2', 'repo3'])
        self.assertEqual(result, (4, 0))  # 4 unique contributors, 0 repos without contributors

    @patch('collaboration_metrics.GitHubClient')
    def test_get_contributor_count_with_empty_repo(self, mock_client):
        # Mock the API response for multiple repos, including an empty one
        mock_client.return_value.get_repo_contributors.side_effect = [
            [{'login': 'user1'}, {'login': 'user2'}],
            [],  # Empty repo
            [{'login': 'user1'}, {'login': 'user3'}]
        ]

        result = get_contributor_count('test_user', ['repo1', 'repo2', 'repo3'])
        self.assertEqual(result, (3, 1))  # 3 unique contributors, 1 repo without contributors


if __name__ == '__main__':
    unittest.main()
