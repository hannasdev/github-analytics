# controllers/commit_controller.py
from typing import List, Dict, Any, Callable
from models.commit import Commit
from services.github_service import GitHubService


class CommitController:
    def __init__(self, username: str, github_service: GitHubService):
        self.username = username
        self.github_service = github_service

    async def get_commits(self, progress_callback: Callable[[int], None]) -> List[Commit]:
        repos = await self.github_service.get_user_repos(self.username)
        progress_callback(1)  # Step 1: Fetched user repositories

        all_commits = []
        for i, repo in enumerate(repos):
            try:
                repo_commits = await self.github_service.get_repo_commits(self.username, repo['name'])
                all_commits.extend([Commit.from_dict(commit) for commit in repo_commits])

                # Update progress after processing each repository
                progress_callback(1)
            except Exception as e:
                print(f"Warning: Error processing repository {repo['name']}: {str(e)}")

        return all_commits

    def analyze_commits(self, commits: List[Commit], progress_callback: Callable[[int], None]) -> Dict[str, Any]:
        time_distribution = Commit.get_commit_time_distribution(commits)
        progress_callback(1)  # Step 3: Calculated time distribution

        avg_frequency = Commit.get_average_commit_frequency(commits)
        progress_callback(1)  # Step 4: Calculated average frequency

        longest_streak = Commit.get_longest_streak(commits)
        progress_callback(1)  # Step 5: Calculated longest streak

        return {
            "time_distribution": time_distribution,
            "avg_frequency": avg_frequency,
            "longest_streak": longest_streak
        }

    async def run_analysis(self, progress_callback: Callable[[int], None] = lambda x: None) -> Dict[str, Any]:
        commits = await self.get_commits(progress_callback)
        return self.analyze_commits(commits, progress_callback)
