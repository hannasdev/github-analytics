# main.py
import matplotlib.pyplot as plt
from datetime import datetime
from github_api.client import GitHubClient
from repo_stats import get_repo_stats, most_starred_forked, most_recent_activity, repo_size_distribution, get_language_breakdown
from commit_analysis import get_commit_time_distribution, get_average_commit_frequency, get_longest_streak
from config import GITHUB_USERNAME


def create_bar_chart(data, title, xlabel, ylabel, filename):
    plt.figure(figsize=(10, 6))
    plt.bar(range(len(data)), [item[1] for item in data], align='center')
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.xticks(range(len(data)), [item[0] for item in data], rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()


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
    create_bar_chart([(repo['name'], repo['stars']) for repo in top_starred],
                     f"Top 5 Starred Repositories for {username}",
                     "Repository", "Stars", "top_starred.png")
    create_bar_chart([(repo['name'], repo['forks']) for repo in top_forked],
                     f"Top 5 Forked Repositories for {username}",
                     "Repository", "Forks", "top_forked.png")

    recent_activity = most_recent_activity(repo_stats)
    create_bar_chart([(repo['name'], (datetime.now() - repo['last_updated']).days) for repo in recent_activity], 
                     f"Top 5 Most Recently Active Repositories for {username}",
                     "Repository", "Days since last update", "recent_activity.png")

    repo_size_distribution(repo_stats)

    language_breakdown, lang_plot = get_language_breakdown(repos, plot=True)
    with open('language_breakdown.png', 'wb') as f:
        f.write(lang_plot.getvalue())

    all_commits = []
    for repo in repos:
        all_commits.extend(client.get_repo_commits(username, repo['name']))

    commit_time_distribution = get_commit_time_distribution(all_commits)
    create_bar_chart(list(commit_time_distribution.items()),
                     "Commit Time Distribution",
                     "Day of Week", "Number of Commits", "commit_distribution.png")

    avg_commit_frequency = get_average_commit_frequency(all_commits)
    longest_streak = get_longest_streak(all_commits)

    # Create a simple bar chart for avg commit frequency and longest streak
    plt.figure(figsize=(10, 6))
    plt.bar(['Avg. Daily Commits', 'Longest Streak (days)'], [avg_commit_frequency, longest_streak])
    plt.title("Commit Patterns")
    plt.savefig("commit_patterns.png")
    plt.close()

    print("Analysis complete. All graphs have been saved as PNG files.")


if __name__ == "__main__":
    run_analysis(GITHUB_USERNAME)
