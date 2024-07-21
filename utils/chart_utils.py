# utils/chart_utils.py
import matplotlib.pyplot as plt


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


def create_pr_stats_chart(total_prs_opened, total_prs_closed):
    plt.figure(figsize=(10, 6))
    plt.bar(['Opened PRs', 'Closed PRs'], [total_prs_opened, total_prs_closed])
    plt.title("Pull Request Statistics")
    plt.savefig("pr_stats.png")
    plt.close()


def create_commit_patterns_chart(avg_commit_frequency, longest_streak):
    plt.figure(figsize=(10, 6))
    plt.bar(['Avg. Daily Commits', 'Longest Streak (days)'], [avg_commit_frequency, longest_streak])
    plt.title("Commit Patterns")
    plt.savefig("commit_patterns.png")
    plt.close()
