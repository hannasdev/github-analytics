# main.py
from github_api.client import GitHubClient
from repo_stats import get_repo_stats, most_starred_forked, most_recent_activity, repo_size_distribution, get_language_breakdown
from commit_analysis import get_commit_time_distribution, get_average_commit_frequency, get_longest_streak
from config import GITHUB_USERNAME


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

    language_breakdown, lang_plot = get_language_breakdown(repos, plot=True)

    with open('language_breakdown.png', 'wb') as f:
        f.write(lang_plot.getvalue())

    # New commit analysis features
    all_commits = []
    for repo in repos:
        all_commits.extend(client.get_repo_commits(username, repo['name']))

    commit_time_distribution = get_commit_time_distribution(all_commits)
    avg_commit_frequency = get_average_commit_frequency(all_commits)
    longest_streak = get_longest_streak(all_commits)

    return {
        'top_starred': top_starred,
        'top_forked': top_forked,
        'recent_activity': recent_activity,
        'language_breakdown': language_breakdown,
        'commit_time_distribution': commit_time_distribution,
        'avg_commit_frequency': avg_commit_frequency,
        'longest_streak': longest_streak
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

        print("\nLanguage Breakdown:")
        for lang, count in results['language_breakdown'].items():
            print(f"{lang}: {count} repositories")

        print("\nLanguage breakdown plot saved as 'language_breakdown.png'")

        print("\nCommit Time Distribution:")
        for day, count in results['commit_time_distribution'].items():
            print(f"{day}: {count} commits")

        print(f"\nAverage Commit Frequency: {results['avg_commit_frequency']:.2f} commits per day")

        print(f"\nLongest Daily Commit Streak: {results['longest_streak']} days")