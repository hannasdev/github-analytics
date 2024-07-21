# collaboration_metrics.py
from github_api.client import GitHubClient
from typing import Dict, Union, List, Tuple


def get_pull_requests_stats(username: str, repo_name: str) -> Dict[str, int]:
    client = GitHubClient()
    pull_requests = client.get_pull_requests(username, repo_name)

    stats = {'opened': 0, 'closed': 0}
    for pr in pull_requests:
        if pr['state'] == 'open':
            stats['opened'] += 1
        elif pr['state'] == 'closed':
            stats['closed'] += 1

    return stats


def get_contributor_count(username: str, repo_names: Union[str, List[str]], verbose: bool = False) -> Tuple[int, int]:
    client = GitHubClient()

    if isinstance(repo_names, str):
        repo_names = [repo_names]

    all_contributors = set()
    repos_without_contributors = 0
    for repo_name in repo_names:
        contributors = client.get_repo_contributors(username, repo_name, verbose)
        if not contributors:
            repos_without_contributors += 1
        all_contributors.update(contributor['login'] for contributor in contributors)

    return len(all_contributors), repos_without_contributors
