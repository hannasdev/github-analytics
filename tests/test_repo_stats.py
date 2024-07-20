# tests/test_repo_stats.py
import unittest
from datetime import datetime
from repo_stats import get_repo_stats, most_starred_forked, most_recent_activity


class TestRepoStats(unittest.TestCase):
    def setUp(self):
        self.sample_repos = [
            {'name': 'repo1', 'stargazers_count': 10, 'forks_count': 5, 'size': 100, 'updated_at': '2023-01-01T00:00:00Z', 'language': 'Python'},
            {'name': 'repo2', 'stargazers_count': 20, 'forks_count': 15, 'size': 200, 'updated_at': '2023-02-01T00:00:00Z', 'language': 'JavaScript'},
            {'name': 'repo3', 'stargazers_count': 5, 'forks_count': 2, 'size': 50, 'updated_at': '2023-03-01T00:00:00Z', 'language': 'Python'},
            {'name': 'repo4', 'stargazers_count': 30, 'forks_count': 10, 'size': 150, 'updated_at': '2023-04-01T00:00:00Z', 'language': 'Java'},
            {'name': 'repo5', 'stargazers_count': 15, 'forks_count': 20, 'size': 300, 'updated_at': '2023-05-01T00:00:00Z', 'language': 'C++'},
        ]

    def test_get_repo_stats(self):
        stats = get_repo_stats(self.sample_repos)
        self.assertEqual(len(stats), 5)
        self.assertEqual(stats[0]['name'], 'repo1')
        self.assertEqual(stats[0]['stars'], 10)
        self.assertEqual(stats[0]['forks'], 5)
        self.assertEqual(stats[0]['size'], 100)
        self.assertEqual(stats[0]['last_updated'], datetime(2023, 1, 1))
        self.assertEqual(stats[0]['language'], 'Python')

    def test_most_starred_forked(self):
        stats = get_repo_stats(self.sample_repos)
        top_starred, top_forked = most_starred_forked(stats)

        # Test top starred repositories
        self.assertEqual(len(top_starred), 5)
        self.assertEqual(top_starred[0]['name'], 'repo4')
        self.assertEqual(top_starred[0]['stars'], 30)
        self.assertEqual(top_starred[-1]['name'], 'repo3')
        self.assertEqual(top_starred[-1]['stars'], 5)

        # Test top forked repositories
        self.assertEqual(len(top_forked), 5)
        self.assertEqual(top_forked[0]['name'], 'repo5')
        self.assertEqual(top_forked[0]['forks'], 20)
        self.assertEqual(top_forked[-1]['name'], 'repo3')
        self.assertEqual(top_forked[-1]['forks'], 2)

    def test_most_recent_activity(self):
        stats = get_repo_stats(self.sample_repos)
        recent = most_recent_activity(stats)

        self.assertEqual(len(recent), 5)
        self.assertEqual(recent[0]['name'], 'repo5')
        self.assertEqual(recent[0]['last_updated'], datetime(2023, 5, 1))
        self.assertEqual(recent[-1]['name'], 'repo1')
        self.assertEqual(recent[-1]['last_updated'], datetime(2023, 1, 1))

    def test_most_starred_forked_with_limit(self):
        stats = get_repo_stats(self.sample_repos)
        top_starred, top_forked = most_starred_forked(stats, top_n=3)

        self.assertEqual(len(top_starred), 3)
        self.assertEqual(len(top_forked), 3)
        self.assertEqual(top_starred[0]['name'], 'repo4')
        self.assertEqual(top_forked[0]['name'], 'repo5')

    def test_most_recent_activity_with_limit(self):
        stats = get_repo_stats(self.sample_repos)
        recent = most_recent_activity(stats, top_n=2)

        self.assertEqual(len(recent), 2)
        self.assertEqual(recent[0]['name'], 'repo5')
        self.assertEqual(recent[1]['name'], 'repo4')


if __name__ == '__main__':
    unittest.main()
