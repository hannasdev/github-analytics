# github_analyzer.py
import aiohttp
import asyncio
from tqdm.asyncio import tqdm
from typing import List, Dict, Any, Tuple
from github_api.client import GitHubClient
import repo_stats
import commit_analysis
import collaboration_metrics
import chart_utils


class GitHubAnalyzer:
    def __init__(self, username: str, verbose: bool = False):
        self.username = username
        self.verbose = verbose
        self.client = GitHubClient()

    async def run_analysis(self):
        repos = await self.client.get_user_repos_async(self.username)
        if not repos:
            print(f"No repositories found for user: {self.username}")
            return

        repo_stats_data = repo_stats.get_repo_stats(repos)
        self.generate_repo_stats_charts(repo_stats_data, repos)

        all_commits, processed_repos, skipped_repos = await self.process_repos(repos)
        if not all_commits:
            print("No commits found for analysis.")
            return

        self.analyze_commits(all_commits)

        collaboration_metrics_data = await self.analyze_collaboration_metrics(repos)

        self.print_analysis_summary(len(repos), processed_repos, skipped_repos,
                                    collaboration_metrics_data, all_commits)

    async def process_repos(self, repos: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], int, int]:
        async with aiohttp.ClientSession() as session:
            tasks = [self.process_repo(session, repo) for repo in repos]
            results = await tqdm.gather(*tasks, desc="Processing repositories")

        all_commits = []
        processed_repos = 0
        skipped_repos = 0

        for commits, success in results:
            if success:
                all_commits.extend(commits)
                processed_repos += 1
            else:
                skipped_repos += 1

        return all_commits, processed_repos, skipped_repos

    async def process_repo(self, session: aiohttp.ClientSession, repo: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], bool]:
        try:
            repo_commits = await self.client.get_repo_commits_async(session, self.username, repo['name'])
            return repo_commits, True
        except Exception as e:
            print(f"Error processing commits for {repo['name']}: {str(e)}")
            return [], False

    def generate_repo_stats_charts(self, repo_stats_data: List[Dict[str, Any]], repos: List[Dict[str, Any]]):
        top_starred, top_forked = repo_stats.most_starred_forked(repo_stats_data)
        recent_activity = repo_stats.most_recent_activity(repo_stats_data)

        chart_utils.create_bar_chart([(repo['name'], repo['stars']) for repo in top_starred],
                                     "Top Starred Repositories",
                                     "Repository",
                                     "Stars",
                                     "top_starred.png")

        chart_utils.create_bar_chart([(repo['name'], repo['forks']) for repo in top_forked],
                                     "Top Forked Repositories",
                                     "Repository",
                                     "Forks",
                                     "top_forked.png")

        repo_stats.repo_size_distribution(repo_stats_data)
        repo_stats.get_language_breakdown(repos, plot=True)

    def analyze_commits(self, all_commits: List[Dict[str, Any]]):
        commit_time_distribution = commit_analysis.get_commit_time_distribution(all_commits)
        avg_commit_frequency = commit_analysis.get_average_commit_frequency(all_commits)
        longest_streak = commit_analysis.get_longest_streak(all_commits)

        chart_utils.create_bar_chart(list(commit_time_distribution.items()),
                                     "Commit Time Distribution",
                                     "Day of Week",
                                     "Number of Commits",
                                     "commit_distribution.png")

        chart_utils.create_commit_patterns_chart(avg_commit_frequency, longest_streak)

    async def analyze_collaboration_metrics(self, repos: List[Dict[str, Any]]) -> Dict[str, Any]:
        async with aiohttp.ClientSession() as session:
            pr_stats_tasks = [collaboration_metrics.get_pull_requests_stats(self.client, session, self.username, repo['name']) for repo in repos]
            pr_stats_results = await asyncio.gather(*pr_stats_tasks)

        total_pr_stats = {'opened': 0, 'closed': 0}
        for stats in pr_stats_results:
            total_pr_stats['opened'] += stats['opened']
            total_pr_stats['closed'] += stats['closed']

        total_contributors, repos_without_contributors = await collaboration_metrics.get_contributor_count(
            self.client, self.username, [repo['name'] for repo in repos], self.verbose
        )

        chart_utils.create_pr_stats_chart(total_pr_stats['opened'], total_pr_stats['closed'])

        return {
            "pr_stats": total_pr_stats,
            "total_contributors": total_contributors,
            "repos_without_contributors": repos_without_contributors
        }

    def print_analysis_summary(self, total_repos: int, processed_repos: int, skipped_repos: int,
                               collaboration_metrics_data: Dict[str, Any], all_commits: List[Dict[str, Any]]):
        print("\nAnalysis Summary:")
        print(f"Total repositories: {total_repos}")
        print(f"Processed repositories: {processed_repos}")
        print(f"Skipped repositories: {skipped_repos}")
        print(f"Total commits analyzed: {len(all_commits)}")
        print(f"Average commit frequency: {commit_analysis.get_average_commit_frequency(all_commits):.2f} commits per day")
        print(f"Longest commit streak: {commit_analysis.get_longest_streak(all_commits)} days")
        print(f"Total unique contributors: {collaboration_metrics_data['total_contributors']}")
        print(f"Repositories without contributors: {collaboration_metrics_data['repos_without_contributors']}")
        print(f"Total pull requests opened: {collaboration_metrics_data['pr_stats']['opened']}")
        print(f"Total pull requests closed: {collaboration_metrics_data['pr_stats']['closed']}")
        print("\nAnalysis complete. All graphs have been saved as PNG files.")
