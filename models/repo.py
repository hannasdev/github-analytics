# models/repo.py
from collections import Counter
import matplotlib.pyplot as plt
from datetime import datetime
from dataclasses import dataclass
from typing import Any, List, Dict


class Repo:
    def __init__(self, name: str, stars: int, forks: int, language: str, size: int, updated_at: datetime):
        self.name = name
        self.stars = stars
        self.forks = forks
        self.language = language
        self.size = size
        self.updated_at = updated_at
        self.contributors: List[Dict[str, Any]] = []

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Repo':
        return cls(
            name=data['name'],
            stars=data['stargazers_count'],
            forks=data['forks_count'],
            language=data['language'] or 'Unknown',
            size=data['size'],
            updated_at=datetime.strptime(data['updated_at'], "%Y-%m-%dT%H:%M:%SZ")
        )

    def add_contributors(self, contributors: List[Dict[str, Any]]) -> None:
        self.contributors = contributors

    @property
    def contributor_count(self) -> int:
        return len(self.contributors)

    @property
    def last_updated(self) -> datetime:
        return self.updated_at

    @staticmethod
    def most_starred_and_forked(repos: List['Repo'], top_n: int = 5) -> Dict[str, List['Repo']]:
        sorted_by_stars = sorted(repos, key=lambda x: x.stars, reverse=True)[:top_n]
        sorted_by_forks = sorted(repos, key=lambda x: x.forks, reverse=True)[:top_n]
        return {
            'most_starred': sorted_by_stars,
            'most_forked': sorted_by_forks
        }

    @staticmethod
    def most_recent_activity(repos: List['Repo'], top_n: int = 5) -> List['Repo']:
        return sorted(repos, key=lambda x: x.last_updated, reverse=True)[:top_n]

    @staticmethod
    def get_language_breakdown(repos: List['Repo']) -> Dict[str, int]:
        languages = [repo.language for repo in repos if repo.language and repo.language != 'Unknown']
        return dict(Counter(languages))

    @staticmethod
    def create_language_breakdown_chart(repos: List['Repo'], filename: str):
        language_breakdown = Repo.get_language_breakdown(repos)
        plt.figure(figsize=(10, 6))
        plt.pie(language_breakdown.values(), labels=language_breakdown.keys(), autopct='%1.1f%%')
        plt.title('Repository Language Breakdown')
        plt.savefig(filename)
        plt.close()

    @staticmethod
    def create_repo_size_distribution_chart(repos: List['Repo'], filename: str):
        sizes = [repo.size for repo in repos]
        plt.figure(figsize=(10, 6))
        plt.hist(sizes, bins=20)
        plt.title('Distribution of Repository Sizes')
        plt.xlabel('Size (KB)')
        plt.ylabel('Number of Repositories')
        plt.savefig(filename)
        plt.close()

    @staticmethod
    def get_total_contributor_count(repos: List['Repo']) -> int:
        unique_contributors = set()
        for repo in repos:
            unique_contributors.update(contributor['login'] for contributor in repo.contributors)
        return len(unique_contributors)
