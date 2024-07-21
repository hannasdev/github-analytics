# services/github_service.py
import aiohttp
import asyncio
from typing import List, Dict, Union
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
                try:
                    async with session.get(
                        f"{self.base_url}/repos/{username}/{repo_name}/pulls",
                        headers=self.headers,
                        params={"state": "all", "page": page, "per_page": 100}
                    ) as response:
                        response.raise_for_status()
                        data = await response.json()
                        if not data:
                            break
                        pull_requests.extend(data)
                        page += 1
                except aiohttp.ClientError as e:
                    print(f"Error fetching pull requests for {repo_name}: {str(e)}")
                    break
            return pull_requests

    async def get_pull_requests_stats(self, username: str, repo_name: str) -> Dict[str, int]:
        pull_requests = await self.get_repo_pull_requests(username, repo_name)
        return {
            "total": len(pull_requests),
            "opened": sum(1 for pr in pull_requests if pr['state'] == "open"),
            "closed": sum(1 for pr in pull_requests if pr['state'] == "closed")
        }

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

    async def get_contributor_count(self, username: str, repo_names: Union[str, List[str]], verbose: bool = False) -> int:
        if isinstance(repo_names, str):
            repo_names = [repo_names]

        unique_contributors = set()
        for repo_name in repo_names:
            contributors = await self.get_repo_contributors(username, repo_name, verbose)
            unique_contributors.update(contributor['login'] for contributor in contributors)

        return len(unique_contributors)

    async def analyze_repo(self, username: str, repo_name: str) -> Dict:
        commits = await self.get_repo_commits(username, repo_name)
        pull_requests = await self.get_repo_pull_requests(username, repo_name)

        commit_time_distribution = self.get_commit_time_distribution(commits)
        avg_commit_frequency = self.get_average_commit_frequency(commits)
        longest_streak = self.get_longest_streak(commits)
        pr_stats = await self.get_pull_requests_stats(username, repo_name)

        return {
            "commit_time_distribution": commit_time_distribution,
            "avg_commit_frequency": avg_commit_frequency,
            "longest_streak": longest_streak,
            "pr_stats": pr_stats
        }

    async def analyze_all_repos(self, username: str) -> List[Dict]:
        repos = await self.get_user_repos(username)
        tasks = [self.analyze_repo(username, repo['name']) for repo in repos]
        return await asyncio.gather(*tasks)

    @staticmethod
    def get_commit_time_distribution(commits: List[Dict]) -> Dict[str, int]:
        from datetime import datetime
        distribution = {day: 0 for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']}
        for commit in commits:
            commit_date = datetime.strptime(commit['commit']['author']['date'], "%Y-%m-%dT%H:%M:%SZ")
            day = commit_date.strftime("%A")
            distribution[day] += 1
        return distribution

    @staticmethod
    def get_average_commit_frequency(commits: List[Dict]) -> float:
        if not commits:
            return 0.0
        from datetime import datetime
        first_commit = datetime.strptime(commits[-1]['commit']['author']['date'], "%Y-%m-%dT%H:%M:%SZ")
        last_commit = datetime.strptime(commits[0]['commit']['author']['date'], "%Y-%m-%dT%H:%M:%SZ")
        days = (last_commit - first_commit).days + 1
        return len(commits) / days if days > 0 else 0

    @staticmethod
    def get_longest_streak(commits: List[Dict]) -> int:
        from datetime import datetime, timedelta
        if not commits:
            return 0
        dates = [datetime.strptime(commit['commit']['author']['date'], "%Y-%m-%dT%H:%M:%SZ").date() for commit in commits]
        dates.sort()
        longest_streak = current_streak = 1
        for i in range(1, len(dates)):
            if dates[i] - dates[i-1] == timedelta(days=1):
                current_streak += 1
                longest_streak = max(longest_streak, current_streak)
            else:
                current_streak = 1
        return longest_streak

    async def get_user_repo_count(self, username: str) -> int:
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(
                    f"{self.base_url}/users/{username}",
                    headers=self.headers
                ) as response:
                    response.raise_for_status()
                    user_data = await response.json()
                    return user_data['public_repos']
            except aiohttp.ClientError as e:
                print(f"Error fetching user data: {str(e)}")
                return 0  # Return 0 if there's an error
