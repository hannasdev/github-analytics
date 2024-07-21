# main.py
import asyncio
import aiohttp
from tqdm.asyncio import tqdm
import matplotlib.pyplot as plt
from datetime import datetime
from typing import List, Dict, Any, Tuple
from github_api.client import GitHubClient
from repo_stats import get_repo_stats, most_starred_forked, most_recent_activity, repo_size_distribution, get_language_breakdown
from commit_analysis import get_commit_time_distribution, get_average_commit_frequency, get_longest_streak
from collaboration_metrics import get_pull_requests_stats, get_contributor_count
from config import GITHUB_USERNAME
from chart_utils import create_bar_chart, create_pr_stats_chart, create_commit_patterns_chart


async def process_repo(session: aiohttp.ClientSession, client: GitHubClient, username: str, repo: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], bool]:
    try:
        repo_commits = await client.get_repo_commits_async(session, username, repo['name'])
        return repo_commits, True
    except Exception as e:
        print(f"Error processing commits for {repo['name']}: {str(e)}")
        return [], False


async def process_repos(client: GitHubClient, username: str, repos: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], int, int]:
    all_commits = []
    processed_repos = 0
    skipped_repos = 0

    async with aiohttp.ClientSession() as session:
        tasks = [process_repo(session, client, username, repo) for repo in repos]
        results = await tqdm.gather(*tasks, desc="Processing repositories")

    for commits, success in results:
        if success:
            all_commits.extend(commits)
            processed_repos += 1
        else:
            skipped_repos += 1

    return all_commits, processed_repos, skipped_repos


async def process_pull_requests(client: GitHubClient, username: str, repos: List[Dict[str, Any]]) -> Tuple[int, int]:
    total_prs_opened = 0
    total_prs_closed = 0

    async with aiohttp.ClientSession() as session:
        tasks = [client.get_pull_requests_async(session, username, repo['name']) for repo in repos]
        results = await tqdm.gather(*tasks, desc="Processing pull requests")

    for pull_requests in results:
        pr_stats = {'opened': 0, 'closed': 0}
        for pr in pull_requests:
            if pr['state'] == 'open':
                pr_stats['opened'] += 1
            elif pr['state'] == 'closed':
                pr_stats['closed'] += 1
        total_prs_opened += pr_stats['opened']
        total_prs_closed += pr_stats['closed']

    return total_prs_opened, total_prs_closed


async def run_analysis(username: str, verbose: bool = False) -> None:
    """
    Run the GitHub repository analysis for the given username.

    :param username: GitHub username to analyze
    :param verbose: Whether to print verbose output
    """
    if not username:
        print("Error: GitHub username not provided")
        return

    client = GitHubClient()
    repos = await client.get_user_repos_async(username)

    if not repos:
        print(f"No repositories found for user: {username}")
        return

    repo_stats = get_repo_stats(repos)

    # Repository statistics
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

    # Language breakdown
    language_breakdown, lang_plot = get_language_breakdown(repos, plot=True)
    with open('language_breakdown.png', 'wb') as f:
        f.write(lang_plot.getvalue())

    # Commit analysis
    all_commits, processed_repos, skipped_repos = await process_repos(client, username, repos)

    if not all_commits:
        print("No commits found for analysis.")
        return

    commit_time_distribution = get_commit_time_distribution(all_commits)
    create_bar_chart(list(commit_time_distribution.items()),
                     "Commit Time Distribution",
                     "Day of Week", "Number of Commits", "commit_distribution.png")

    avg_commit_frequency = get_average_commit_frequency(all_commits)
    longest_streak = get_longest_streak(all_commits)

    create_commit_patterns_chart(avg_commit_frequency, longest_streak)

    # Collaboration metrics
    total_prs_opened, total_prs_closed = await process_pull_requests(client, username, repos)

    print(f"\nPull Request Statistics:")
    print(f"Total PRs opened: {total_prs_opened}")
    print(f"Total PRs closed: {total_prs_closed}")

    create_pr_stats_chart(total_prs_opened, total_prs_closed)

    try:
        total_contributors, repos_without_contributors = await get_contributor_count(client, username, [repo['name'] for repo in repos], verbose)
        print(f"\nTotal unique contributors across all repositories: {total_contributors}")
    except Exception as e:
        print(f"Error calculating total contributors: {str(e)}")
        total_contributors = "Unable to calculate"

    print_analysis_summary(len(repos), processed_repos, skipped_repos, repos_without_contributors,
                           len(all_commits), avg_commit_frequency, longest_streak, total_contributors)


def print_analysis_summary(total_repos: int, processed_repos: int, skipped_repos: int,
                           repos_without_contributors: int, total_commits: int,
                           avg_commit_frequency: float, longest_streak: int,
                           total_contributors: int) -> None:
    """
    Print a summary of the analysis results.
    """
    print("\nAnalysis Summary:")
    print(f"Total repositories: {total_repos}")
    print(f"Processed repositories: {processed_repos}")
    print(f"Skipped repositories: {skipped_repos}")
    print(f"Repositories without contributors: {repos_without_contributors}")
    print(f"Total commits analyzed: {total_commits}")
    print(f"Average commit frequency: {avg_commit_frequency:.2f} commits per day")
    print(f"Longest commit streak: {longest_streak} days")
    print(f"Total unique contributors: {total_contributors}")
    print("\nAnalysis complete. All graphs have been saved as PNG files.")


if __name__ == "__main__":
    asyncio.run(run_analysis(GITHUB_USERNAME, verbose=False))
