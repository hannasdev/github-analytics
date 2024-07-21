# controllers/repo_controller.py
from typing import List, Dict, Any
from models.repo import Repo
from services.github_service import GitHubService
from utils import chart_utils


class RepoController:
    def __init__(self, username: str, github_service: GitHubService):
        self.username = username
        self.github_service = github_service

    async def get_repos(self) -> List[Repo]:
        repo_data = await self.github_service.get_user_repos(self.username)
        return [Repo.from_dict(repo) for repo in repo_data]

    def analyze_repos(self, repos: List[Repo]) -> Dict[str, Any]:
        top_repos = Repo.most_starred_and_forked(repos)
        recent_activity = Repo.most_recent_activity(repos)
        language_breakdown = Repo.get_language_breakdown(repos)

        # Create charts
        chart_utils.create_bar_chart(
            [(repo.name, repo.stars) for repo in top_repos['most_starred']],
            "Top Starred Repositories",
            "Repository",
            "Stars",
            "top_starred.png"
        )

        chart_utils.create_bar_chart(
            [(repo.name, repo.forks) for repo in top_repos['most_forked']],
            "Top Forked Repositories",
            "Repository",
            "Forks",
            "top_forked.png"
        )

        Repo.create_language_breakdown_chart(repos, "language_breakdown.png")
        Repo.create_repo_size_distribution_chart(repos, "repo_size_distribution.png")

        return {
            "top_starred": top_repos['most_starred'],
            "top_forked": top_repos['most_forked'],
            "recent_activity": recent_activity,
            "language_breakdown": language_breakdown,
            "chart_files": [
                "top_starred.png",
                "top_forked.png",
                "language_breakdown.png",
                "repo_size_distribution.png"
            ]
        }

    async def run_analysis(self) -> Dict[str, Any]:
        repos = await self.get_repos()
        return self.analyze_repos(repos)
