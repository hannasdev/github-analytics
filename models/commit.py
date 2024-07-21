# models/commit.py
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from dataclasses import dataclass
from typing import List, Dict


@dataclass
class Commit:
    sha: str
    author: str
    date: datetime
    message: str

    @classmethod
    def from_dict(cls, data: Dict) -> 'Commit':
        return cls(
            sha=data['sha'],
            author=data['commit']['author']['name'],
            date=datetime.strptime(data['commit']['author']['date'], '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=ZoneInfo("UTC")),
            message=data['commit']['message']
        )

    @staticmethod
    def get_commit_time_distribution(commits: List['Commit']) -> Dict[str, int]:
        day_counts = {day: 0 for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']}
        for commit in commits:
            day_name = commit.date.strftime('%A')
            day_counts[day_name] += 1
        return dict(day_counts)

    @staticmethod
    def get_average_commit_frequency(commits: List['Commit']) -> float:
        if not commits:
            return 0
        commit_dates = [commit.date.date() for commit in commits]
        first_commit = min(commit_dates)
        last_commit = max(commit_dates)
        total_days = (last_commit - first_commit).days + 1
        return len(commits) / total_days

    @staticmethod
    def get_longest_streak(commits: List['Commit']) -> int:
        if not commits:
            return 0
        commit_dates = sorted(set(commit.date.date() for commit in commits))
        longest_streak = current_streak = 1
        for i in range(1, len(commit_dates)):
            if (commit_dates[i] - commit_dates[i-1]) == timedelta(days=1):
                current_streak += 1
                longest_streak = max(longest_streak, current_streak)
            else:
                current_streak = 1
        return longest_streak
