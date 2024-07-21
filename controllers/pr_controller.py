# controllers/pr_controller.py
from typing import List, Dict, Any
from models.pull_request import PullRequest
from services.github_service import GitHubService


class PRController:
    def __init__(self, username: str, github_service: GitHubService):
        self.username = username
        self.github_service = github_service

    async def get_pull_requests(self) -> List[PullRequest]:
        repos = await self.github_service.get_user_repos(self.username)
        all_pull_requests = []
        for repo in repos:
            try:
                repo_prs = await self.github_service.get_repo_pull_requests(self.username, repo['name'])
                all_pull_requests.extend([PullRequest.from_dict(pr) for pr in repo_prs])
            except Exception as e:
                print(f"Warning: Error processing pull requests for repository {repo['name']}: {str(e)}")
        return all_pull_requests

    def analyze_pull_requests(self, pull_requests: List[PullRequest]) -> Dict[str, Any]:
        return {
            "pr_stats": PullRequest.get_pr_stats(pull_requests),
            "total_prs": len(pull_requests)
        }

    async def run_analysis(self) -> Dict[str, Any]:
        pull_requests = await self.get_pull_requests()
        return self.analyze_pull_requests(pull_requests)
