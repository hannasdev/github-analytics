# services/github_service.py
import aiohttp
import asyncio
from typing import List, Dict, Union, Tuple
from models import Repo, Commit, PullRequest
import json


class GitHubService:
    def __init__(self, token: str):
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }

    async def get_user_repos(self, username: str) -> List[Repo]:
        async with aiohttp.ClientSession() as session:
            repos = []
            page = 1
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

    async def get_repo_commits(self, username: str, repo_name: str) -> List[Commit]:
        async with aiohttp.ClientSession() as session:
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

    async def get_repo_pull_requests(self, username: str, repo_name: str) -> List[PullRequest]:
        async with aiohttp.ClientSession() as session:
            pull_requests = []
            page = 1
            while True:
                async with session.get(
                    f"{self.base_url}/repos/{username}/{repo_name}/pulls",
                    headers=self.headers,
                    params={"state": "all", "page": page, "per_page": 100}
                ) as response:
                    data = await response.json()
                    if not data:
                        break
                    pull_requests.extend([await PullRequest.create_from_api(pr_data) for pr_data in data])
                    page += 1
            return pull_requests

    async def get_pull_requests_stats(self, username: str, repo_name: str) -> Dict[str, int]:
        pull_requests = await self.get_repo_pull_requests(username, repo_name)
        return PullRequest.get_pr_stats(pull_requests)

    async def get_repo_contributors(self, username: str, repo_name: str, verbose: bool = False) -> List[Dict]:
        async with aiohttp.ClientSession() as session:
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

                        data = await response.json()
                        if not data:
                            break
                        contributors.extend(data)
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

    async def get_contributor_count(self, username: str, repo_names: Union[str, List[str]], verbose: bool = False) -> Tuple[int, int]:
        return await PullRequest.get_contributor_count(self, username, repo_names, verbose)

    async def analyze_repo(self, username: str, repo_name: str) -> Dict:
        commits = await self.get_repo_commits(username, repo_name)
        pull_requests = await self.get_repo_pull_requests(username, repo_name)

        commit_time_distribution = Commit.get_commit_time_distribution(commits)
        avg_commit_frequency = Commit.get_average_commit_frequency(commits)
        longest_streak = Commit.get_longest_streak(commits)
        pr_stats = PullRequest.get_pr_stats(pull_requests)

        return {
            "commit_time_distribution": commit_time_distribution,
            "avg_commit_frequency": avg_commit_frequency,
            "longest_streak": longest_streak,
            "pr_stats": pr_stats
        }

    async def analyze_all_repos(self, username: str) -> List[Dict]:
        repos = await self.get_user_repos(username)
        tasks = [self.analyze_repo(username, repo.name) for repo in repos]
        return await asyncio.gather(*tasks)
