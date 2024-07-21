# /tests/test_collaboration_metrics.py
import pytest
from datetime import datetime
from models.pull_request import PullRequest


@pytest.mark.asyncio
class TestPullRequestModel:
    @pytest.fixture
    def sample_prs(self):
        return [
            PullRequest(number=1, title="PR 1", state="open", created_at=datetime(2023, 1, 1), closed_at=None),
            PullRequest(number=2, title="PR 2", state="closed", created_at=datetime(2023, 1, 2), closed_at=datetime(2023, 1, 3)),
            PullRequest(number=3, title="PR 3", state="closed", created_at=datetime(2023, 1, 4), closed_at=datetime(2023, 1, 5)),
            PullRequest(number=4, title="PR 4", state="open", created_at=datetime(2023, 1, 6), closed_at=None)
        ]

    def test_from_dict(self):
        pr_dict = {
            'number': 1,
            'title': 'Test PR',
            'state': 'open',
            'created_at': '2023-01-01T10:00:00Z',
            'closed_at': None
        }
        pr = PullRequest.from_dict(pr_dict)
        assert pr.number == 1
        assert pr.title == 'Test PR'
        assert pr.state == 'open'
        assert pr.created_at == datetime(2023, 1, 1, 10, 0)
        assert pr.closed_at is None

    async def test_create_from_api(self):
        pr_dict = {
            'number': 1,
            'title': 'Test PR',
            'state': 'open',
            'created_at': '2023-01-01T10:00:00Z',
            'closed_at': None
        }
        pr = await PullRequest.create_from_api(pr_dict)
        assert pr.number == 1
        assert pr.title == 'Test PR'
        assert pr.state == 'open'
        assert pr.created_at == datetime(2023, 1, 1, 10, 0)
        assert pr.closed_at is None

    def test_get_pr_stats(self, sample_prs):
        stats = PullRequest.get_pr_stats(sample_prs)
        assert stats == {'opened': 2, 'closed': 2}

    async def test_get_pull_requests_stats(self, mocker):
        mock_client = mocker.AsyncMock()
        mock_session = mocker.AsyncMock()
        mock_client.get_pull_requests_async.return_value = [
            {'number': 1, 'title': 'PR 1', 'state': 'open', 'created_at': '2023-01-01T10:00:00Z', 'closed_at': None},
            {'number': 2, 'title': 'PR 2', 'state': 'closed', 'created_at': '2023-01-02T10:00:00Z', 'closed_at': '2023-01-03T10:00:00Z'}
        ]

        stats = await PullRequest.get_pull_requests_stats(mock_client, mock_session, 'test_user', 'test_repo')
        assert stats == {'opened': 1, 'closed': 1}

    async def test_get_contributor_count(self, mocker):
        mock_client = mocker.AsyncMock()
        mock_client.get_repo_contributors_async.side_effect = [
            [{'login': 'user1'}, {'login': 'user2'}],
            [{'login': 'user2'}, {'login': 'user3'}],
            [{'login': 'user1'}, {'login': 'user3'}, {'login': 'user4'}]
        ]

        count, empty_repos = await PullRequest.get_contributor_count(mock_client, 'test_user', ['repo1', 'repo2', 'repo3'])
        assert count == 4
        assert empty_repos == 0

    async def test_get_contributor_count_with_empty_repo(self, mocker):
        mock_client = mocker.AsyncMock()
        mock_client.get_repo_contributors_async.side_effect = [
            [{'login': 'user1'}, {'login': 'user2'}],
            [],  # Empty repo
            [{'login': 'user1'}, {'login': 'user3'}]
        ]

        count, empty_repos = await PullRequest.get_contributor_count(mock_client, 'test_user', ['repo1', 'repo2', 'repo3'])
        assert count == 3
        assert empty_repos == 1
