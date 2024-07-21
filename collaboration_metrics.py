# collaboration_metrics.py
import asyncio
import aiohttp
from typing import Dict, Union, List, Tuple
from github_api.client import GitHubClient


async def get_pull_requests_stats(client: GitHubClient, session: aiohttp.ClientSession, username: str, repo_name: str) -> Dict[str, int]:
    pull_requests = await client.get_pull_requests_async(session, username, repo_name)

    stats = {'opened': 0, 'closed': 0}
    for pr in pull_requests:
        if pr['state'] == 'open':
            stats['opened'] += 1
        elif pr['state'] == 'closed':
            stats['closed'] += 1

    return stats


async def get_contributor_count(client: GitHubClient, username: str, repo_names: Union[str, List[str]], verbose: bool = False) -> Tuple[int, int]:
    if isinstance(repo_names, str):
        repo_names = [repo_names]

    all_contributors = set()
    repos_without_contributors = 0

    async with aiohttp.ClientSession() as session:
        tasks = [client.get_repo_contributors_async(session, username, repo_name, verbose) for repo_name in repo_names]
        results = await asyncio.gather(*tasks)

    for contributors in results:
        if not contributors:
            repos_without_contributors += 1
        all_contributors.update(contributor['login'] for contributor in contributors)

    return len(all_contributors), repos_without_contributors
