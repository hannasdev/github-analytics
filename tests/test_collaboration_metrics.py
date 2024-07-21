# /tests/test_collaboration_metrics.py
import pytest
from unittest.mock import AsyncMock
from collaboration_metrics import get_pull_requests_stats, get_contributor_count

pytestmark = pytest.mark.asyncio


class TestCollaborationMetrics:

    async def test_get_pull_requests_stats(self):
        mock_client = AsyncMock()
        mock_session = AsyncMock()
        mock_client.get_pull_requests_async.return_value = [
            {'state': 'open'},
            {'state': 'closed'},
            {'state': 'closed'},
            {'state': 'open'}
        ]

        result = await get_pull_requests_stats(mock_client, mock_session, 'test_user', 'test_repo')
        assert result == {'opened': 2, 'closed': 2}

    async def test_get_contributor_count(self):
        mock_client = AsyncMock()
        mock_client.get_repo_contributors_async.return_value = [
            {'login': 'user1'},
            {'login': 'user2'},
            {'login': 'user3'}
        ]

        result = await get_contributor_count(mock_client, 'test_user', 'test_repo')
        assert result == (3, 0)

    async def test_get_contributor_count_multiple_repos(self):
        mock_client = AsyncMock()
        mock_client.get_repo_contributors_async.side_effect = [
            [{'login': 'user1'}, {'login': 'user2'}],
            [{'login': 'user2'}, {'login': 'user3'}],
            [{'login': 'user1'}, {'login': 'user3'}, {'login': 'user4'}]
        ]

        result = await get_contributor_count(mock_client, 'test_user', ['repo1', 'repo2', 'repo3'])
        assert result == (4, 0)

    async def test_get_contributor_count_with_empty_repo(self):
        mock_client = AsyncMock()
        mock_client.get_repo_contributors_async.side_effect = [
            [{'login': 'user1'}, {'login': 'user2'}],
            [],  # Empty repo
            [{'login': 'user1'}, {'login': 'user3'}]
        ]

        result = await get_contributor_count(mock_client, 'test_user', ['repo1', 'repo2', 'repo3'])
        assert result == (3, 1)
