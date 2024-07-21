# controllers/repo_controller.py
from typing import List, Dict, Any, Callable
import logging
from models.repo import Repo
from services.github_service import GitHubService
from utils import chart_utils


class RepoController:
    def __init__(self, username: str, github_service: GitHubService):
        self.username = username
        self.github_service = github_service
        self.logger = logging.getLogger(__name__)

    async def get_repos(self, progress_callback: Callable[[int], None]) -> List[Repo]:
        repo_data = await self.github_service.get_user_repos(self.username)
        progress_callback(1)  # Step 1: Fetched user repositories
        repos = [Repo.from_dict(repo) for repo in repo_data]

        # Fetch contributors for each repo
        for repo in repos:
            try:
                contributors = await self.github_service.get_repo_contributors(self.username, repo.name)
                repo.add_contributors(contributors)
            except Exception as e:
                self.logger.warning(f"Error fetching contributors for {repo.name}: {str(e)}")
            progress_callback(1)  # Step: Fetched contributors for a repo (or attempted to)

        return repos

    def analyze_repos(self, repos: List[Repo], progress_callback: Callable[[int], None]) -> Dict[str, Any]:
        top_repos = Repo.most_starred_and_forked(repos)
        progress_callback(1)  # Step 2: Calculated top repos

        recent_activity = Repo.most_recent_activity(repos)
        progress_callback(1)  # Step 3: Calculated recent activity

        language_breakdown = Repo.get_language_breakdown(repos)
        progress_callback(1)  # Step 4: Calculated language breakdown

        total_contributor_count = Repo.get_total_contributor_count(repos)
        progress_callback(1)  # Step: Calculated total contributor count

          # Create a chart for repositories by contributor count
        chart_utils.create_bar_chart(
            [(repo.name, repo.contributor_count) for repo in sorted(repos, key=lambda r: r.contributor_count, reverse=True)[:10]],
            "Top 10 Repositories by Contributor Count",
            "Repository",
            "Contributors",
            "top_contributors.png"
        )
        progress_callback(1)  # Step: Created top contributors chart

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
                "repo_size_distribution.png",
                "top_contributors.png"
            ],
            "total_contributor_count": total_contributor_count,
        }

    async def run_analysis(self, progress_callback: Callable[[int], None] = lambda x: None) -> Dict[str, Any]:
        repos = await self.get_repos(progress_callback)
        return self.analyze_repos(repos, progress_callback)
