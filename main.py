# main.py
from github_api.client import GitHubClient
from repo_stats import get_repo_stats, most_starred_forked, most_recent_activity, repo_size_distribution
from config import GITHUB_USERNAME


def main():
    if not GITHUB_USERNAME:
        print("Error: GITHUB_USERNAME not set in .env file")
        return

    client = GitHubClient()
    repos = client.get_user_repos(GITHUB_USERNAME)

    if not repos:
        print(f"No repositories found for user: {GITHUB_USERNAME}")
        return

    repo_stats = get_repo_stats(repos)

    # 1. Most starred/forked repositories
    top_starred, top_forked = most_starred_forked(repo_stats)
    print(f"Top 5 Starred Repositories for {GITHUB_USERNAME}:")
    for repo in top_starred:
        print(f"{repo['name']}: {repo['stars']} stars")

    print(f"\nTop 5 Forked Repositories for {GITHUB_USERNAME}:")
    for repo in top_forked:
        print(f"{repo['name']}: {repo['forks']} forks")

    # 2. Repositories with the most recent activity
    recent_activity = most_recent_activity(repo_stats)
    print(f"\nTop 5 Recently Active Repositories for {GITHUB_USERNAME}:")
    for repo in recent_activity:
        print(f"{repo['name']}: Last updated on {repo['last_updated']}")

    # 3. Distribution of repository sizes
    repo_size_distribution(repo_stats)
    print(f"\nRepository size distribution plot for {GITHUB_USERNAME} saved as 'repo_size_distribution.png'")


def run_analysis(username):
    if not username:
        print("Error: GitHub username not provided")
        return

    client = GitHubClient()
    repos = client.get_user_repos(username)

    if not repos:
        print(f"No repositories found for user: {username}")
        return

    repo_stats = get_repo_stats(repos)

    top_starred, top_forked = most_starred_forked(repo_stats)
    recent_activity = most_recent_activity(repo_stats)
    repo_size_distribution(repo_stats)

    return {
        'top_starred': top_starred,
        'top_forked': top_forked,
        'recent_activity': recent_activity
    }

if __name__ == "__main__":
    results = run_analysis(GITHUB_USERNAME)
    if results:
        print(f"Top 5 Starred Repositories for {GITHUB_USERNAME}:")
        for repo in results['top_starred']:
            print(f"{repo['name']}: {repo['stars']} stars")

        print(f"\nTop 5 Forked Repositories for {GITHUB_USERNAME}:")
        for repo in results['top_forked']:
            print(f"{repo['name']}: {repo['forks']} forks")

        print(f"\nTop 5 Recently Active Repositories for {GITHUB_USERNAME}:")
        for repo in results['recent_activity']:
            print(f"{repo['name']}: Last updated on {repo['last_updated']}")

        print(f"\nRepository size distribution plot for {GITHUB_USERNAME} saved as 'repo_size_distribution.png'")


if __name__ == "__main__":
    main()
