# models/pull_request.py
import asyncio
import aiohttp
from typing import Dict, Union, List, Tuple, Set
from dataclasses import dataclass
from datetime import datetime


@dataclass
class PullRequest:
    number: int
    title: str
    state: str
    created_at: datetime
    closed_at: Union[datetime, None]

    @classmethod
    def from_dict(cls, data: Dict) -> 'PullRequest':
        return cls(
            number=data['number'],
            title=data['title'],
            state=data['state'],
            created_at=datetime.strptime(data['created_at'], '%Y-%m-%dT%H:%M:%SZ'),
            closed_at=datetime.strptime(data['closed_at'], '%Y-%m-%dT%H:%M:%SZ') if data['closed_at'] else None
        )

    @classmethod
    async def create_from_api(cls, data: Dict) -> 'PullRequest':
        return cls.from_dict(data)

    @staticmethod
    def get_pr_stats(pull_requests: List['PullRequest']) -> Dict[str, int]:
        stats = {'opened': 0, 'closed': 0}
        for pr in pull_requests:
            if pr.state == 'open':
                stats['opened'] += 1
            elif pr.state == 'closed':
                stats['closed'] += 1
        return stats

    @classmethod
    async def get_pull_requests_stats(cls, client, session: aiohttp.ClientSession, username: str, repo_name: str) -> Dict[str, int]:
        pull_requests = await client.get_pull_requests_async(session, username, repo_name)
        return cls.get_pr_stats([cls.from_dict(pr) for pr in pull_requests])

    @staticmethod
    async def get_contributor_count(client, username: str, repo_names: Union[str, List[str]], verbose: bool = False) -> Tuple[int, int]:
        if isinstance(repo_names, str):
            repo_names = [repo_names]

        all_contributors: Set[str] = set()
        repos_without_contributors = 0

        async with aiohttp.ClientSession() as session:
            tasks = [client.get_repo_contributors_async(session, username, repo_name, verbose) for repo_name in repo_names]
            results = await asyncio.gather(*tasks)

        for contributors in results:
            if not contributors:
                repos_without_contributors += 1
            all_contributors.update(contributor['login'] for contributor in contributors)

        return len(all_contributors), repos_without_contributors
