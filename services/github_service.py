# services/github_service.py
import aiohttp
import asyncio
from typing import List, Dict, Union, Any, Optional
from models import Repo, Commit, PullRequest
import json
import logging
from cachetools import TTLCache
from datetime import datetime, timedelta
from config import (
    GITHUB_API_BASE_URL,
    GITHUB_API_VERSION,
    CACHE_MAX_SIZE,
    CACHE_TTL,
    LOG_LEVEL,
    LOG_FORMAT
)


class GitHubService:
    def __init__(self, token: str) -> None:
        self.base_url: str = GITHUB_API_BASE_URL
        self.headers: Dict[str, str] = {
            "Authorization": f"token {token}",
            "Accept": f"application/vnd.github.{GITHUB_API_VERSION}+json"
        }
        self.cache: TTLCache = TTLCache(maxsize=CACHE_MAX_SIZE, ttl=CACHE_TTL)
        logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)
        self.logger: logging.Logger = logging.getLogger(__name__)

    async def _make_request(self, url: str, params: Optional[Dict[str, Any]] = None) -> Any:
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, headers=self.headers, params=params) as response:
                    await self._check_rate_limit(response)
                    response.raise_for_status()
                    return await response.json()
            except aiohttp.ClientError as e:
                self.logger.error(f"Error making request to {url}: {str(e)}")
                raise

    async def _check_rate_limit(self, response: aiohttp.ClientResponse) -> None:
        remaining: int = int(response.headers.get('X-RateLimit-Remaining', 0))
        if remaining <= 10:
            reset_time: int = int(response.headers.get('X-RateLimit-Reset', 0))
            wait_time: float = max(reset_time - asyncio.get_event_loop().time(), 0)
            self.logger.warning(f"Rate limit nearly exceeded. Waiting for {wait_time} seconds.")
            await asyncio.sleep(wait_time)

    async def get_user_repos(self, username: str) -> List[Dict[str, Any]]:
        cache_key: str = f"user_repos_{username}"
        if cache_key in self.cache:
            return self.cache[cache_key]

        repos: List[Dict[str, Any]] = []
        page: int = 1
        while True:
            url: str = f"{self.base_url}/users/{username}/repos"
            page_repos: List[Dict[str, Any]] = await self._make_request(url, params={"page": page, "per_page": 100})
            if not page_repos:
                break
            repos.extend(page_repos)
            page += 1

        self.cache[cache_key] = repos
        return repos

    async def get_repo_commits(self, username: str, repo_name: str) -> List[Dict[str, Any]]:
        async with aiohttp.ClientSession() as session:
            commits: List[Dict[str, Any]] = []
            page: int = 1
            while True:
                try:
                    async with session.get(
                        f"{self.base_url}/repos/{username}/{repo_name}/commits",
                        headers=self.headers,
                        params={"page": page, "per_page": 100}
                    ) as response:
                        if response.status == 409:
                            self.logger.warning(f"Repository {repo_name} is empty or has been moved. Skipping.")
                            break
                        response.raise_for_status()
                        page_commits: List[Dict[str, Any]] = await response.json()
                        if not page_commits or not isinstance(page_commits, list):
                            break
                        commits.extend(page_commits)
                        if len(page_commits) < 100:
                            break
                        page += 1
                except aiohttp.ClientError as e:
                    self.logger.error(f"Error fetching commits for {repo_name}: {str(e)}")
                    break
            return commits

    async def get_repo_pull_requests(self, username: str, repo_name: str) -> List[Dict[str, Any]]:
        async with aiohttp.ClientSession() as session:
            pull_requests: List[Dict[str, Any]] = []
            page: int = 1
            while True:
                try:
                    async with session.get(
                        f"{self.base_url}/repos/{username}/{repo_name}/pulls",
                        headers=self.headers,
                        params={"state": "all", "page": page, "per_page": 100}
                    ) as response:
                        response.raise_for_status()
                        data: List[Dict[str, Any]] = await response.json()
                        if not data:
                            break
                        pull_requests.extend(data)
                        page += 1
                except aiohttp.ClientError as e:
                    self.logger.error(f"Error fetching pull requests for {repo_name}: {str(e)}")
                    break
            return pull_requests

    async def get_pull_requests_stats(self, username: str, repo_name: str) -> Dict[str, int]:
        pull_requests: List[Dict[str, Any]] = await self.get_repo_pull_requests(username, repo_name)
        return {
            "total": len(pull_requests),
            "opened": sum(1 for pr in pull_requests if pr['state'] == "open"),
            "closed": sum(1 for pr in pull_requests if pr['state'] == "closed")
        }

    async def get_repo_contributors(self, username: str, repo_name: str, verbose: bool = False) -> List[Dict[str, Any]]:
        async with aiohttp.ClientSession() as session:
            contributors: List[Dict[str, Any]] = []
            page: int = 1
            while True:
                try:
                    async with session.get(
                        f"{self.base_url}/repos/{username}/{repo_name}/contributors",
                        headers=self.headers,
                        params={"page": page, "per_page": 100}
                    ) as response:
                        if response.status == 204:
                            if verbose:
                                self.logger.info(f"No contributors found for {repo_name}")
                            break

                        response.raise_for_status()

                        if verbose:
                            self.logger.info(f"Response status code for {repo_name}: {response.status}")
                            content: str = await response.text()
                            self.logger.info(f"Response content for {repo_name}: {content[:100]}...")

                        data: List[Dict[str, Any]] = await response.json()
                        if not data:
                            break
                        contributors.extend(data)
                        page += 1
                except json.JSONDecodeError as e:
                    if verbose:
                        self.logger.error(f"Error decoding JSON for {repo_name}: {str(e)}")
                        self.logger.error(f"Response content: {await response.text()}")
                    break
                except aiohttp.ClientError as e:
                    if verbose:
                        self.logger.error(f"Error fetching contributors for {repo_name}: {str(e)}")
                    break
            return contributors

    async def get_contributor_count(self, username: str, repo_names: Union[str, List[str]], verbose: bool = False) -> int:
        if isinstance(repo_names, str):
            repo_names = [repo_names]

        unique_contributors: set = set()
        for repo_name in repo_names:
            contributors: List[Dict[str, Any]] = await self.get_repo_contributors(username, repo_name, verbose)
            unique_contributors.update(contributor['login'] for contributor in contributors)

        return len(unique_contributors)

    async def analyze_repo(self, username: str, repo_name: str) -> Dict[str, Any]:
        commits: List[Dict[str, Any]] = await self.get_repo_commits(username, repo_name)
        pull_requests: List[Dict[str, Any]] = await self.get_repo_pull_requests(username, repo_name)

        commit_time_distribution: Dict[str, int] = self.get_commit_time_distribution(commits)
        avg_commit_frequency: float = self.get_average_commit_frequency(commits)
        longest_streak: int = self.get_longest_streak(commits)
        pr_stats: Dict[str, int] = await self.get_pull_requests_stats(username, repo_name)

        return {
            "commit_time_distribution": commit_time_distribution,
            "avg_commit_frequency": avg_commit_frequency,
            "longest_streak": longest_streak,
            "pr_stats": pr_stats
        }

    async def analyze_all_repos(self, username: str) -> List[Dict[str, Any]]:
        repos: List[Dict[str, Any]] = await self.get_user_repos(username)
        tasks: List[asyncio.Task] = [self.analyze_repo(username, repo['name']) for repo in repos]
        return await asyncio.gather(*tasks)

    @staticmethod
    def get_commit_time_distribution(commits: List[Dict[str, Any]]) -> Dict[str, int]:
        distribution: Dict[str, int] = {day: 0 for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']}
        for commit in commits:
            commit_date: datetime = datetime.strptime(commit['commit']['author']['date'], "%Y-%m-%dT%H:%M:%SZ")
            day: str = commit_date.strftime("%A")
            distribution[day] += 1
        return distribution

    @staticmethod
    def get_average_commit_frequency(commits: List[Dict[str, Any]]) -> float:
        if not commits:
            return 0.0
        first_commit: datetime = datetime.strptime(commits[-1]['commit']['author']['date'], "%Y-%m-%dT%H:%M:%SZ")
        last_commit: datetime = datetime.strptime(commits[0]['commit']['author']['date'], "%Y-%m-%dT%H:%M:%SZ")
        days: int = (last_commit - first_commit).days + 1
        return len(commits) / days if days > 0 else 0

    @staticmethod
    def get_longest_streak(commits: List[Dict[str, Any]]) -> int:
        if not commits:
            return 0
        dates: List[datetime] = [datetime.strptime(commit['commit']['author']['date'], "%Y-%m-%dT%H:%M:%SZ").date() for commit in commits]
        dates.sort()
        longest_streak: int = 1
        current_streak: int = 1
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
                    user_data: Dict[str, Any] = await response.json()
                    return user_data['public_repos']
            except aiohttp.ClientError as e:
                self.logger.error(f"Error fetching user data: {str(e)}")
                return 0
