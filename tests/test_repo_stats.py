# test_repo_stats.py
import unittest
from datetime import datetime
from repo_stats import get_repo_stats, most_starred_forked, most_recent_activity


class TestRepoStats(unittest.TestCase):
    def setUp(self):
        self.sample_repos = [
            {'name': 'repo1', 'stargazers_count': 10, 'forks_count': 5, 'size': 100, 'updated_at': '2023-01-01T00:00:00Z'},
            {'name': 'repo2', 'stargazers_count': 20, 'forks_count': 15, 'size': 200, 'updated_at': '2023-02-01T00:00:00Z'},
            {'name': 'repo3', 'stargazers_count': 5, 'forks_count': 2, 'size': 50, 'updated_at': '2023-03-01T00:00:00Z'},
        ]

    def test_get_repo_stats(self):
        stats = get_repo_stats(self.sample_repos)
        self.assertEqual(len(stats), 3)
        self.assertEqual(stats[0]['name'], 'repo1')
        self.assertEqual(stats[0]['stars'], 10)
        self.assertEqual(stats[0]['forks'], 5)
        self.assertEqual(stats[0]['size'], 100)
        self.assertEqual(stats[0]['last_updated'], datetime(2023, 1, 1))

    def test_most_starred_forked(self):
        stats = get_repo_stats(self.sample_repos)
        top_starred, top_forked = most_starred_forked(stats, top_n=2)
        self.assertEqual(len(top_starred), 2)
        self.assertEqual(top_starred[0]['name'], 'repo2')
        self.assertEqual(top_starred[1]['name'], 'repo1')
        self.assertEqual(top_forked[0]['name'], 'repo2')
        self.assertEqual(top_forked[1]['name'], 'repo1')

    def test_most_recent_activity(self):
        stats = get_repo_stats(self.sample_repos)
        recent = most_recent_activity(stats, top_n=2)
        self.assertEqual(len(recent), 2)
        self.assertEqual(recent[0]['name'], 'repo3')
        self.assertEqual(recent[1]['name'], 'repo2')
