from collections import Counter
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo  # Python 3.9+ only, use pytz for earlier versions


def get_commit_time_distribution(commits):
    day_counts = {day: 0 for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']}
    for commit in commits:
        commit_date = datetime.strptime(commit['commit']['author']['date'], '%Y-%m-%dT%H:%M:%SZ')
        commit_date = commit_date.replace(tzinfo=ZoneInfo("UTC"))
        day_name = commit_date.strftime('%A')
        day_counts[day_name] += 1
    return day_counts


def get_average_commit_frequency(commits):
    if not commits:
        return 0

    commit_dates = [datetime.strptime(commit['commit']['author']['date'], '%Y-%m-%dT%H:%M:%SZ').date() for commit in commits]
    first_commit = min(commit_dates)
    last_commit = max(commit_dates)
    total_days = (last_commit - first_commit).days + 1
    return len(commits) / total_days


def get_longest_streak(commits):
    if not commits:
        return 0

    commit_dates = sorted(set(datetime.strptime(commit['commit']['author']['date'][:10], '%Y-%m-%d').date() for commit in commits))
    longest_streak = current_streak = 1
    for i in range(1, len(commit_dates)):
        if (commit_dates[i] - commit_dates[i-1]).days == 1:
            current_streak += 1
            longest_streak = max(longest_streak, current_streak)
        else:
            current_streak = 1
    return longest_streak
