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

    def get_org_repos(self, org_name):
        response = requests.get(f"{self.base_url}/orgs/{org_name}/repos", headers=self.headers)
        return response.json()