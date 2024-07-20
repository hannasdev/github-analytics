import unittest
from datetime import datetime, timedelta
from commit_analysis import get_commit_time_distribution, get_average_commit_frequency, get_longest_streak


class TestCommitAnalysis(unittest.TestCase):
    def setUp(self):
        self.sample_commits = [
            {'commit': {'author': {'date': '2023-07-01T10:00:00Z'}}},
            {'commit': {'author': {'date': '2023-07-02T14:30:00Z'}}},
            {'commit': {'author': {'date': '2023-07-03T09:15:00Z'}}},
            {'commit': {'author': {'date': '2023-07-03T18:45:00Z'}}},
            {'commit': {'author': {'date': '2023-07-05T11:30:00Z'}}},
            {'commit': {'author': {'date': '2023-07-06T16:00:00Z'}}},
            {'commit': {'author': {'date': '2023-07-07T13:20:00Z'}}},
            {'commit': {'author': {'date': '2023-07-10T09:00:00Z'}}},
        ]

    def test_get_commit_time_distribution(self):
        distribution = get_commit_time_distribution(self.sample_commits)
        self.assertEqual(len(distribution), 7)  # 7 days of the week
        self.assertEqual(sum(distribution.values()), 8)  # Total 8 commits
        self.assertEqual(distribution['Saturday'], 1)
        self.assertEqual(distribution['Monday'], 3)
        self.assertEqual(distribution['Sunday'], 1)

    def test_get_average_commit_frequency(self):
        frequency = get_average_commit_frequency(self.sample_commits)
        self.assertAlmostEqual(frequency, 0.8, places=1)  # 8 commits over 10 days (July 1 to July 10)

    def test_get_longest_streak(self):
        streak = get_longest_streak(self.sample_commits)
        self.assertEqual(streak, 3)  # Longest streak is 3 days (July 1-3)


if __name__ == '__main__':
    unittest.main()
