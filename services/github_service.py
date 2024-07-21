# services/github_service.py
import aiohttp
import asyncio
from typing import List, Dict, Any, Optional
import logging
from cachetools import TTLCache
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
                    if response.status == 409:
                        self.logger.info(f"Resource not available or empty: {url}")
                        return None
                    response.raise_for_status()
                    content_type = response.headers.get('Content-Type', '')
                    if 'application/json' in content_type:
                        return await response.json()
                    elif 'text/plain' in content_type:
                        return await response.text()
                    else:
                        return await response.read()
            except aiohttp.ClientResponseError as e:
                if e.status == 409:
                    self.logger.info(f"Resource not available or empty: {url}")
                    return None
                raise  # Re-raise the exception without logging
            except aiohttp.ClientError as e:
                raise  # Re-raise the exception without logging

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
        commits: List[Dict[str, Any]] = []
        page: int = 1
        while True:
            url: str = f"{self.base_url}/repos/{username}/{repo_name}/commits"
            try:
                page_commits = await self._make_request(url, params={"page": page, "per_page": 100})
                if page_commits is None:
                    self.logger.info(f"Repository {username}/{repo_name} is empty or has no commits.")
                    break
                if not page_commits or not isinstance(page_commits, list):
                    break
                commits.extend(page_commits)
                if len(page_commits) < 100:
                    break
                page += 1
            except aiohttp.ClientError as e:
                self.logger.error(f"Error fetching commits for {repo_name}: {str(e)}")
                break  # Exit the loop on error
        return commits  # Return the commits we've managed to fetch, even if it's an empty list

    async def get_repo_pull_requests(self, username: str, repo_name: str) -> List[Dict[str, Any]]:
        pull_requests: List[Dict[str, Any]] = []
        page: int = 1
        while True:
            url: str = f"{self.base_url}/repos/{username}/{repo_name}/pulls"
            page_prs: List[Dict[str, Any]] = await self._make_request(url, params={"state": "all", "page": page, "per_page": 100})
            if not page_prs:
                break
            pull_requests.extend(page_prs)
            if len(page_prs) < 100:
                break
            page += 1
        return pull_requests

    async def get_repo_contributors(self, username: str, repo_name: str) -> List[Dict[str, Any]]:
        contributors: List[Dict[str, Any]] = []
        page: int = 1
        while True:
            url: str = f"{self.base_url}/repos/{username}/{repo_name}/contributors"
            try:
                page_contributors: List[Dict[str, Any]] = await self._make_request(url, params={"page": page, "per_page": 100})
                if not page_contributors or not isinstance(page_contributors, list):
                    break
                contributors.extend(page_contributors)
                if len(page_contributors) < 100:
                    break
                page += 1
            except aiohttp.ContentTypeError:
                self.logger.warning(f"Unable to fetch contributors for {username}/{repo_name}. The repository might be empty or not exist.")
                break
            except Exception as e:
                self.logger.error(f"Error fetching contributors for {username}/{repo_name}: {str(e)}")
                break
        return contributors

    async def get_user_repo_count(self, username: str) -> int:
        url: str = f"{self.base_url}/users/{username}"
        user_data: Dict[str, Any] = await self._make_request(url)
        return user_data['public_repos']
