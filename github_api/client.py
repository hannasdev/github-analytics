# github_api/client.py
import requests
from typing import List, Dict, Any
from config import GITHUB_TOKEN


class GitHubClient:
    def __init__(self):
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json"
        }

    def get_user_repos(self, username: str) -> List[Dict[str, Any]]:
        repos = []
        page = 1
        while True:
            try:
                response = requests.get(
                    f"{self.base_url}/users/{username}/repos",
                    headers=self.headers,
                    params={"page": page, "per_page": 100}
                )
                response.raise_for_status()
                page_repos = response.json()
                if not page_repos:
                    break
                repos.extend(page_repos)
                page += 1
            except requests.RequestException as e:
                raise Exception(f"Error fetching repositories: {str(e)}")
        return repos

    def get_repo_commits(self, username: str, repo_name: str) -> List[Dict[str, Any]]:
        commits = []
        page = 1
        while True:
            try:
                response = requests.get(
                    f"{self.base_url}/repos/{username}/{repo_name}/commits",
                    headers=self.headers,
                    params={"page": page, "per_page": 100}
                )
                response.raise_for_status()
                page_commits = response.json()
                if not page_commits or not isinstance(page_commits, list):
                    break
                commits.extend(page_commits)
                if len(page_commits) < 100:
                    break
                page += 1
            except requests.RequestException as e:
                raise Exception(f"Error fetching commits for {repo_name}: {str(e)}")
        return commits
