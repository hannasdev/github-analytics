# controllers/repo_controller.py
from typing import List, Dict, Any, Callable
from models.repo import Repo
from services.github_service import GitHubService
from utils import chart_utils


class RepoController:
    def __init__(self, username: str, github_service: GitHubService):
        self.username = username
        self.github_service = github_service

    async def get_repos(self, progress_callback: Callable[[int], None]) -> List[Repo]:
        repo_data = await self.github_service.get_user_repos(self.username)
        progress_callback(1)  # Step 1: Fetched user repositories
        return [Repo.from_dict(repo) for repo in repo_data]

    def analyze_repos(self, repos: List[Repo], progress_callback: Callable[[int], None]) -> Dict[str, Any]:
        top_repos = Repo.most_starred_and_forked(repos)
        progress_callback(1)  # Step 2: Calculated top repos

        recent_activity = Repo.most_recent_activity(repos)
        progress_callback(1)  # Step 3: Calculated recent activity

        language_breakdown = Repo.get_language_breakdown(repos)
        progress_callback(1)  # Step 4: Calculated language breakdown

        # Create charts
        chart_utils.create_bar_chart(
            [(repo.name, repo.stars) for repo in top_repos['most_starred']],
            "Top Starred Repositories",
            "Repository",
            "Stars",
            "top_starred.png"
        )
        progress_callback(1)  # Step 5: Created top starred chart

        chart_utils.create_bar_chart(
            [(repo.name, repo.forks) for repo in top_repos['most_forked']],
            "Top Forked Repositories",
            "Repository",
            "Forks",
            "top_forked.png"
        )
        progress_callback(1)  # Step 6: Created top forked chart

        Repo.create_language_breakdown_chart(repos, "language_breakdown.png")
        progress_callback(1)  # Step 7: Created language breakdown chart

        Repo.create_repo_size_distribution_chart(repos, "repo_size_distribution.png")
        progress_callback(1)  # Step 8: Created repo size distribution chart

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

    async def run_analysis(self, progress_callback: Callable[[int], None] = lambda x: None) -> Dict[str, Any]:
        repos = await self.get_repos(progress_callback)
        return self.analyze_repos(repos, progress_callback)
