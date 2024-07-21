# controllers/pr_controller.py
from typing import List, Dict, Any, Callable
from models.pull_request import PullRequest
from services.github_service import GitHubService


class PRController:
    def __init__(self, username: str, github_service: GitHubService):
        self.username = username
        self.github_service = github_service

    async def get_pull_requests(self, progress_callback: Callable[[int], None]) -> List[PullRequest]:
        repos = await self.github_service.get_user_repos(self.username)
        progress_callback(1)  # Step 1: Fetched user repositories

        all_pull_requests = []
        for repo in repos:
            try:
                repo_prs = await self.github_service.get_repo_pull_requests(self.username, repo['name'])
                all_pull_requests.extend([PullRequest.from_dict(pr) for pr in repo_prs])

                # Update progress after processing each repository
                progress_callback(1)
            except Exception as e:
                print(f"Warning: Error processing pull requests for repository {repo['name']}: {str(e)}")

        return all_pull_requests

    def analyze_pull_requests(self, pull_requests: List[PullRequest], progress_callback: Callable[[int], None]) -> Dict[str, Any]:
        pr_stats = PullRequest.get_pr_stats(pull_requests)
        progress_callback(1)  # Step 3: Calculated PR stats

        total_prs = len(pull_requests)
        progress_callback(1)  # Step 4: Counted total PRs

        return {
            "pr_stats": pr_stats,
            "total_prs": total_prs
        }

    async def run_analysis(self, progress_callback: Callable[[int], None] = lambda x: None) -> Dict[str, Any]:
        pull_requests = await self.get_pull_requests(progress_callback)
        return self.analyze_pull_requests(pull_requests, progress_callback)
