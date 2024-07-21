# github_api/client.py
import aiohttp
import asyncio
import requests
import json
from typing import List, Dict, Any
from config import GITHUB_TOKEN


class GitHubClient:
    def __init__(self):
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json"
        }

    async def get_user_repos_async(self, username: str) -> List[Dict[str, Any]]:
        repos = []
        page = 1
        async with aiohttp.ClientSession() as session:
            while True:
                try:
                    async with session.get(
                        f"{self.base_url}/users/{username}/repos",
                        headers=self.headers,
                        params={"page": page, "per_page": 100}
                    ) as response:
                        response.raise_for_status()
                        page_repos = await response.json()
                        if not page_repos:
                            break
                        repos.extend(page_repos)
                        page += 1
                except aiohttp.ClientError as e:
                    raise Exception(f"Error fetching repositories: {str(e)}")
        return repos

    async def get_repo_commits_async(self, session: aiohttp.ClientSession, username: str, repo_name: str) -> List[Dict[str, Any]]:
        commits = []
        page = 1
        while True:
            try:
                async with session.get(
                    f"{self.base_url}/repos/{username}/{repo_name}/commits",
                    headers=self.headers,
                    params={"page": page, "per_page": 100}
                ) as response:
                    if response.status == 409:
                        print(f"Warning: Repository {repo_name} is empty or has been moved. Skipping.")
                        break
                    response.raise_for_status()
                    page_commits = await response.json()
                    if not page_commits or not isinstance(page_commits, list):
                        break
                    commits.extend(page_commits)
                    if len(page_commits) < 100:
                        break
                    page += 1
            except aiohttp.ClientError as e:
                print(f"Error fetching commits for {repo_name}: {str(e)}")
                break
        return commits

    async def get_pull_requests_async(self, session: aiohttp.ClientSession, username: str, repo_name: str) -> List[Dict[str, Any]]:
        pull_requests = []
        page = 1
        while True:
            try:
                async with session.get(
                    f"{self.base_url}/repos/{username}/{repo_name}/pulls",
                    headers=self.headers,
                    params={"state": "all", "page": page, "per_page": 100}
                ) as response:
                    response.raise_for_status()
                    page_prs = await response.json()
                    if not page_prs:
                        break
                    pull_requests.extend(page_prs)
                    page += 1
            except aiohttp.ClientError as e:
                print(f"Error fetching pull requests for {repo_name}: {str(e)}")
                break
        return pull_requests

    async def get_repo_contributors_async(self, session: aiohttp.ClientSession, username: str, repo_name: str, verbose: bool = False) -> List[Dict[str, Any]]:
        contributors = []
        page = 1
        while True:
            try:
                async with session.get(
                    f"{self.base_url}/repos/{username}/{repo_name}/contributors",
                    headers=self.headers,
                    params={"page": page, "per_page": 100}
                ) as response:
                    if response.status == 204:
                        if verbose:
                            print(f"No contributors found for {repo_name}")
                        break

                    response.raise_for_status()

                    if verbose:
                        print(f"Response status code for {repo_name}: {response.status}")
                        content = await response.text()
                        print(f"Response content for {repo_name}: {content[:100]}...")  # Print first 100 characters

                    page_contributors = await response.json()
                    if not page_contributors:
                        break
                    contributors.extend(page_contributors)
                    page += 1
            except json.JSONDecodeError as e:
                if verbose:
                    print(f"Error decoding JSON for {repo_name}: {str(e)}")
                    print(f"Response content: {await response.text()}")
                break
            except aiohttp.ClientError as e:
                if verbose:
                    print(f"Error fetching contributors for {repo_name}: {str(e)}")
                break
        return contributors

    # Synchronous methods for backwards compatibility
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
                if response.status_code == 409:
                    print(f"Warning: Repository {repo_name} is empty or has been moved. Skipping.")
                    break
                response.raise_for_status()
                page_commits = response.json()
                if not page_commits or not isinstance(page_commits, list):
                    break
                commits.extend(page_commits)
                if len(page_commits) < 100:
                    break
                page += 1
            except requests.RequestException as e:
                print(f"Error fetching commits for {repo_name}: {str(e)}")
                break
        return commits

    def get_pull_requests(self, username: str, repo_name: str) -> List[Dict[str, Any]]:
        pull_requests = []
        page = 1
        while True:
            try:
                response = requests.get(
                    f"{self.base_url}/repos/{username}/{repo_name}/pulls",
                    headers=self.headers,
                    params={"state": "all", "page": page, "per_page": 100}
                )
                response.raise_for_status()
                page_prs = response.json()
                if not page_prs:
                    break
                pull_requests.extend(page_prs)
                page += 1
            except requests.RequestException as e:
                print(f"Error fetching pull requests for {repo_name}: {str(e)}")
                break
        return pull_requests

    def get_repo_contributors(self, username: str, repo_name: str, verbose: bool = False) -> List[Dict[str, Any]]:
        contributors = []
        page = 1
        while True:
            try:
                response = requests.get(
                    f"{self.base_url}/repos/{username}/{repo_name}/contributors",
                    headers=self.headers,
                    params={"page": page, "per_page": 100}
                )

                if response.status_code == 204:
                    if verbose:
                        print(f"No contributors found for {repo_name}")
                    break

                response.raise_for_status()

                if verbose:
                    print(f"Response status code for {repo_name}: {response.status_code}")
                    print(f"Response content for {repo_name}: {response.text[:100]}...")  # Print first 100 characters

                page_contributors = response.json()
                if not page_contributors:
                    break
                contributors.extend(page_contributors)
                page += 1
            except json.JSONDecodeError as e:
                if verbose:
                    print(f"Error decoding JSON for {repo_name}: {str(e)}")
                    print(f"Response content: {response.text}")
                break
            except requests.RequestException as e:
                if verbose:
                    print(f"Error fetching contributors for {repo_name}: {str(e)}")
                break
        return contributors
