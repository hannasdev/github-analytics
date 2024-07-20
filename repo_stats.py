# repo_stats.py

from github_api.client import GitHubClient
from datetime import datetime
import matplotlib.pyplot as plt


def get_repo_stats(repos):
    repo_stats = []
    for repo in repos:
        repo_stats.append({
            'name': repo['name'],
            'stars': repo['stargazers_count'],
            'forks': repo['forks_count'],
            'size': repo['size'],
            'last_updated': datetime.strptime(repo['updated_at'], '%Y-%m-%dT%H:%M:%SZ')
        })
    return repo_stats


def most_starred_forked(repo_stats, top_n=5):
    sorted_by_stars = sorted(repo_stats, key=lambda x: x['stars'], reverse=True)[:top_n]
    sorted_by_forks = sorted(repo_stats, key=lambda x: x['forks'], reverse=True)[:top_n]
    return sorted_by_stars, sorted_by_forks


def most_recent_activity(repo_stats, top_n=5):
    return sorted(repo_stats, key=lambda x: x['last_updated'], reverse=True)[:top_n]


def repo_size_distribution(repo_stats):
    sizes = [repo['size'] for repo in repo_stats]
    plt.figure(figsize=(10, 6))
    plt.hist(sizes, bins=20)
    plt.title('Distribution of Repository Sizes')
    plt.xlabel('Size (KB)')
    plt.ylabel('Number of Repositories')
    plt.savefig('repo_size_distribution.png')
    plt.close()