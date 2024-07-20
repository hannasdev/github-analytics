# github_api/client.py

import requests
from config import GITHUB_TOKEN


class GitHubClient:
    def __init__(self):
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json"
        }

    def get_user_repos(self, username):
        response = requests.get(f"{self.base_url}/users/{username}/repos", headers=self.headers)
        return response.json()

    def get_repo_commits(self, username, repo_name):
        url = f"{self.base_url}/repos/{username}/{repo_name}/commits"
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error fetching commits for {repo_name}: {response.status_code}")
            return []
