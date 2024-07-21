# main.py
import matplotlib.pyplot as plt
from datetime import datetime
from github_api.client import GitHubClient
from repo_stats import get_repo_stats, most_starred_forked, most_recent_activity, repo_size_distribution, get_language_breakdown
from commit_analysis import get_commit_time_distribution, get_average_commit_frequency, get_longest_streak
from collaboration_metrics import get_pull_requests_stats, get_contributor_count
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


def run_analysis(username, verbose=False):
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
    processed_repos = 0
    skipped_repos = 0
    for repo in repos:
        try:
            repo_commits = client.get_repo_commits(username, repo['name'])
            all_commits.extend(repo_commits)
            processed_repos += 1
        except Exception as e:
            print(f"Error processing commits for {repo['name']}: {str(e)}")
            skipped_repos += 1

    if not all_commits:
        print("No commits found for analysis.")
        return

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

    # New collaboration metrics
    total_prs_opened = 0
    total_prs_closed = 0
    repos_without_contributors = 0
    for repo in repos:
        try:
            pr_stats = get_pull_requests_stats(username, repo['name'])
            total_prs_opened += pr_stats['opened']
            total_prs_closed += pr_stats['closed']
        except Exception as e:
            print(f"Error processing pull requests for {repo['name']}: {str(e)}")

    print(f"\nPull Request Statistics:")
    print(f"Total PRs opened: {total_prs_opened}")
    print(f"Total PRs closed: {total_prs_closed}")

    # Create a simple bar chart for PR stats
    plt.figure(figsize=(10, 6))
    plt.bar(['Opened PRs', 'Closed PRs'], [total_prs_opened, total_prs_closed])
    plt.title("Pull Request Statistics")
    plt.savefig("pr_stats.png")
    plt.close()

    try:
        total_contributors, repos_without_contributors = get_contributor_count(username, [repo['name'] for repo in repos], verbose)
        print(f"\nTotal unique contributors across all repositories: {total_contributors}")
    except Exception as e:
        print(f"Error calculating total contributors: {str(e)}")
        total_contributors = "Unable to calculate"

    print("\nAnalysis Summary:")
    print(f"Total repositories: {len(repos)}")
    print(f"Processed repositories: {processed_repos}")
    print(f"Skipped repositories: {skipped_repos}")
    print(f"Repositories without contributors: {repos_without_contributors}")
    print(f"Total commits analyzed: {len(all_commits)}")
    print(f"Average commit frequency: {avg_commit_frequency:.2f} commits per day")
    print(f"Longest commit streak: {longest_streak} days")
    print(f"Total unique contributors: {total_contributors}")
    print("\nAnalysis complete. All graphs have been saved as PNG files.")


if __name__ == "__main__":
    run_analysis(GITHUB_USERNAME, verbose=False)
