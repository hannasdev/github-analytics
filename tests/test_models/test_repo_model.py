# tests/test_models/test_repo_model.py
import pytest
from datetime import datetime
from models.repo import Repo


class TestRepoModel:
    @pytest.fixture
    def sample_repos(self):
        return [
            Repo('repo1', 10, 5, 100, datetime(2023, 1, 1), 'Python'),
            Repo('repo2', 20, 15, 200, datetime(2023, 2, 1), 'JavaScript'),
            Repo('repo3', 5, 2, 50, datetime(2023, 3, 1), 'Python'),
            Repo('repo4', 30, 10, 150, datetime(2023, 4, 1), 'Java'),
            Repo('repo5', 15, 20, 300, datetime(2023, 5, 1), 'C++'),
        ]

    def test_from_dict(self):
        repo_dict = {
            'name': 'test_repo',
            'stargazers_count': 100,
            'forks_count': 50,
            'size': 1000,
            'updated_at': '2023-05-01T00:00:00Z',
            'language': 'Python'
        }
        repo = Repo.from_dict(repo_dict)
        assert repo.name == 'test_repo'
        assert repo.stars == 100
        assert repo.forks == 50
        assert repo.size == 1000
        assert repo.last_updated == datetime(2023, 5, 1)
        assert repo.language == 'Python'

    def test_most_starred_and_forked(self, sample_repos):
        top_repos = Repo.most_starred_and_forked(sample_repos, top_n=3)

        assert len(top_repos['most_starred']) == 3
        assert top_repos['most_starred'][0].name == 'repo4'
        assert top_repos['most_starred'][0].stars == 30
        assert top_repos['most_starred'][1].name == 'repo2'
        assert top_repos['most_starred'][2].name == 'repo5'

        assert len(top_repos['most_forked']) == 3
        assert top_repos['most_forked'][0].name == 'repo5'
        assert top_repos['most_forked'][0].forks == 20
        assert top_repos['most_forked'][1].name == 'repo2'
        assert top_repos['most_forked'][2].name == 'repo4'

    def test_most_recent_activity(self, sample_repos):
        recent = Repo.most_recent_activity(sample_repos, top_n=3)

        assert len(recent) == 3
        assert recent[0].name == 'repo5'
        assert recent[0].last_updated == datetime(2023, 5, 1)
        assert recent[-1].name == 'repo3'
        assert recent[-1].last_updated == datetime(2023, 3, 1)

    def test_get_language_breakdown(self, sample_repos):
        breakdown = Repo.get_language_breakdown(sample_repos)

        assert len(breakdown) == 4
        assert breakdown['Python'] == 2
        assert breakdown['JavaScript'] == 1
        assert breakdown['Java'] == 1
        assert breakdown['C++'] == 1

    @pytest.mark.skip(reason="This test requires matplotlib and saves a file")
    def test_create_language_breakdown_chart(self, sample_repos, tmp_path):
        filename = tmp_path / "language_breakdown.png"
        Repo.create_language_breakdown_chart(sample_repos, str(filename))
        assert filename.exists()

    @pytest.mark.skip(reason="This test requires matplotlib and saves a file")
    def test_create_repo_size_distribution_chart(self, sample_repos, tmp_path):
        filename = tmp_path / "repo_size_distribution.png"
        Repo.create_repo_size_distribution_chart(sample_repos, str(filename))
        assert filename.exists()
