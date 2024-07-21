# controllers/commit_controller.py
from typing import List, Dict, Any
from models.commit import Commit
from services.github_service import GitHubService


class CommitController:
    def __init__(self, username: str, github_service: GitHubService):
        self.username = username
        self.github_service = github_service

    async def get_commits(self) -> List[Commit]:
        repos = await self.github_service.get_user_repos(self.username)
        all_commits = []
        for repo in repos:
            try:
                repo_commits = await self.github_service.get_repo_commits(self.username, repo['name'])
                all_commits.extend([Commit.from_dict(commit) for commit in repo_commits])
            except Exception as e:
                print(f"Warning: Error processing repository {repo['name']}: {str(e)}")
        return all_commits

    def analyze_commits(self, commits: List[Commit]) -> Dict[str, Any]:
        return {
            "time_distribution": Commit.get_commit_time_distribution(commits),
            "avg_frequency": Commit.get_average_commit_frequency(commits),
            "longest_streak": Commit.get_longest_streak(commits)
        }

    async def run_analysis(self) -> Dict[str, Any]:
        commits = await self.get_commits()
        return self.analyze_commits(commits)
