# /tests/pr_controller.py
import pytest
from datetime import datetime
from controllers.pr_controller import PRController
from models.pull_request import PullRequest
from services.github_service import GitHubService


@pytest.mark.asyncio
class TestPRController:
    @pytest.fixture
    def mock_github_service(self, mocker):
        return mocker.Mock(spec=GitHubService)

    @pytest.fixture
    def pr_controller(self, mock_github_service):
        return PRController('test_user', mock_github_service)

    async def test_get_pull_requests(self, pr_controller, mock_github_service):
        mock_github_service.get_user_repos.return_value = [{'name': 'repo1'}, {'name': 'repo2'}]
        mock_github_service.get_repo_pull_requests.side_effect = [
            [{'number': 1, 'title': 'PR 1', 'state': 'open', 'created_at': '2023-01-01T10:00:00Z', 'closed_at': None}],
            [{'number': 2, 'title': 'PR 2', 'state': 'closed', 'created_at': '2023-01-02T10:00:00Z', 'closed_at': '2023-01-03T10:00:00Z'}]
        ]

        pull_requests = await pr_controller.get_pull_requests()
        assert len(pull_requests) == 2
        assert isinstance(pull_requests[0], PullRequest)
        assert isinstance(pull_requests[1], PullRequest)
        assert pull_requests[0].state == 'open'
        assert pull_requests[1].state == 'closed'

    def test_analyze_pull_requests(self, pr_controller):
        pull_requests = [
            PullRequest(number=1, title="PR 1", state="open", created_at=datetime(2023, 1, 1), closed_at=None),
            PullRequest(number=2, title="PR 2", state="closed", created_at=datetime(2023, 1, 2), closed_at=datetime(2023, 1, 3))
        ]

        analysis = pr_controller.analyze_pull_requests(pull_requests)
        assert analysis == {
            "pr_stats": {'opened': 1, 'closed': 1},
            "total_prs": 2
        }

    async def test_run_analysis(self, pr_controller, mock_github_service):
        mock_github_service.get_user_repos.return_value = [{'name': 'repo1'}]
        mock_github_service.get_repo_pull_requests.return_value = [
            {'number': 1, 'title': 'PR 1', 'state': 'open', 'created_at': '2023-01-01T10:00:00Z', 'closed_at': None},
            {'number': 2, 'title': 'PR 2', 'state': 'closed', 'created_at': '2023-01-02T10:00:00Z', 'closed_at': '2023-01-03T10:00:00Z'}
        ]

        analysis = await pr_controller.run_analysis()
        assert analysis == {
            "pr_stats": {'opened': 1, 'closed': 1},
            "total_prs": 2
        }
