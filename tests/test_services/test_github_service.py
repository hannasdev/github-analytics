# /tests/test_services/test_github_service.py
import pytest
from unittest.mock import Mock
from services.github_service import GitHubService
import aiohttp
from aioresponses import aioresponses


@pytest.fixture
def github_service():
    return GitHubService("fake_token")


@pytest.mark.asyncio
async def test_get_repo_commits_single_page(github_service):
    with aioresponses() as m:
        m.get(
            'https://api.github.com/repos/testuser/testrepo/commits?page=1&per_page=100',
            payload=[{'sha': 'abc123'}, {'sha': 'def456'}],
            status=200
        )

        commits = await github_service.get_repo_commits('testuser', 'testrepo')

        print(f"Single page test - Number of commits: {len(commits)}")

        assert len(commits) == 2
        assert commits[0]['sha'] == 'abc123'
        assert commits[1]['sha'] == 'def456'


@pytest.mark.asyncio
async def test_get_repo_commits_multiple_pages(github_service):
    with aioresponses() as m:
        m.get(
            'https://api.github.com/repos/testuser/testrepo/commits?page=1&per_page=100',
            payload=[{'sha': f'commit{i}'} for i in range(100)],
            status=200
        )
        m.get(
            'https://api.github.com/repos/testuser/testrepo/commits?page=2&per_page=100',
            payload=[{'sha': f'commit{i}'} for i in range(100, 150)],
            status=200
        )
        m.get(
            'https://api.github.com/repos/testuser/testrepo/commits?page=3&per_page=100',
            payload=[],
            status=200
        )

        commits = await github_service.get_repo_commits('testuser', 'testrepo')

        print(f"Multiple pages test - Number of commits: {len(commits)}")
        print(f"Multiple pages test - First commit: {commits[0]['sha']}")
        print(f"Multiple pages test - Last commit: {commits[-1]['sha']}")

        assert len(commits) == 150
        assert commits[0]['sha'] == 'commit0'
        assert commits[-1]['sha'] == 'commit149'


@pytest.mark.asyncio
async def test_get_repo_commits_error(github_service):
    # Mock the logger
    github_service.logger = Mock()

    with aioresponses() as m:
        m.get(
            'https://api.github.com/repos/testuser/testrepo/commits?page=1&per_page=100',
            exception=aiohttp.ClientError("API Error")
        )

        commits = await github_service.get_repo_commits('testuser', 'testrepo')

        assert commits == []  # Check that an empty list is returned

        # Check that the error was logged
        github_service.logger.error.assert_called_once_with(
            "Error fetching commits for testrepo: API Error"
        )

if __name__ == '__main__':
    pytest.main()
