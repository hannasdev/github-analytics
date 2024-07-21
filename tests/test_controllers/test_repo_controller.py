# /tests/test_controllers/test_repo_controller.py
import pytest
from unittest.mock import Mock, patch
from controllers.repo_controller import RepoController
from models.repo import Repo
from services.github_service import GitHubService


@pytest.fixture
def mock_github_service():
    return Mock(spec=GitHubService)


@pytest.fixture
def repo_controller(mock_github_service):
    return RepoController('test_user', mock_github_service)


@pytest.fixture
def sample_repo_data():
    return [
        {'name': 'repo1', 'stargazers_count': 10, 'forks_count': 5, 'size': 100, 'updated_at': '2023-01-01T00:00:00Z', 'language': 'Python'},
        {'name': 'repo2', 'stargazers_count': 20, 'forks_count': 15, 'size': 200, 'updated_at': '2023-02-01T00:00:00Z', 'language': 'JavaScript'},
        {'name': 'repo3', 'stargazers_count': 5, 'forks_count': 2, 'size': 50, 'updated_at': '2023-03-01T00:00:00Z', 'language': 'Python'},
    ]


@pytest.mark.asyncio
async def test_get_repos(repo_controller, mock_github_service, sample_repo_data):
    mock_github_service.get_user_repos.return_value = sample_repo_data
    mock_progress_callback = Mock()

    repos = await repo_controller.get_repos(mock_progress_callback)

    assert len(repos) == 3
    assert all(isinstance(repo, Repo) for repo in repos)
    assert repos[0].name == 'repo1'
    assert repos[1].stars == 20
    assert repos[2].language == 'Python'
    assert mock_progress_callback.call_count == 4  # Once for fetching repos, and once for each of the 3 repos' contributors


@pytest.mark.asyncio
async def test_analyze_repos(repo_controller, sample_repo_data):
    repos = [Repo.from_dict(data) for data in sample_repo_data]
    mock_progress_callback = Mock()

    with patch('controllers.repo_controller.chart_utils.create_bar_chart') as mock_create_bar_chart, \
         patch('models.repo.Repo.create_language_breakdown_chart') as mock_create_language_chart, \
         patch('models.repo.Repo.create_repo_size_distribution_chart') as mock_create_size_chart:

        analysis = repo_controller.analyze_repos(repos, mock_progress_callback)

        assert 'top_starred' in analysis
        assert 'top_forked' in analysis
        assert 'recent_activity' in analysis
        assert 'language_breakdown' in analysis
        assert 'chart_files' in analysis

        assert len(analysis['top_starred']) == 3
        assert analysis['top_starred'][0].name == 'repo2'
        assert len(analysis['top_forked']) == 3
        assert analysis['top_forked'][0].name == 'repo2'
        assert len(analysis['recent_activity']) == 3
        assert analysis['recent_activity'][0].name == 'repo3'
        assert analysis['language_breakdown'] == {'Python': 2, 'JavaScript': 1}

        assert mock_create_bar_chart.call_count == 3  # For top starred, top forked, and top contributors
        assert mock_create_language_chart.call_count == 1
        assert mock_create_size_chart.call_count == 1
        assert mock_progress_callback.call_count == 9  # Called for each step in analyze_repos (8 steps now)


@pytest.mark.asyncio
async def test_run_analysis(repo_controller, mock_github_service, sample_repo_data):
    mock_github_service.get_user_repos.return_value = sample_repo_data
    mock_progress_callback = Mock()

    with patch('controllers.repo_controller.chart_utils.create_bar_chart'), \
         patch('models.repo.Repo.create_language_breakdown_chart'), \
         patch('models.repo.Repo.create_repo_size_distribution_chart'):

        analysis = await repo_controller.run_analysis(mock_progress_callback)

        assert 'top_starred' in analysis
        assert 'top_forked' in analysis
        assert 'recent_activity' in analysis
        assert 'language_breakdown' in analysis
        assert 'chart_files' in analysis
        assert mock_progress_callback.call_count > 0  # Ensure the callback was called at least once

if __name__ == '__main__':
    pytest.main()
