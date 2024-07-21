# /tests/test_models/test_commit_model.py
import unittest
from datetime import datetime
from zoneinfo import ZoneInfo
from models.commit import Commit


class TestCommitModel(unittest.TestCase):
    def setUp(self):
        self.sample_commits = [
            Commit(
                sha=f'sha{i}',
                author='Test Author',
                date=datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=ZoneInfo("UTC")),
                message='Test commit'
            )
            for i, date_str in enumerate([
                '2023-07-01T10:00:00Z',
                '2023-07-02T14:30:00Z',
                '2023-07-03T09:15:00Z',
                '2023-07-03T18:45:00Z',
                '2023-07-05T11:30:00Z',
                '2023-07-06T16:00:00Z',
                '2023-07-07T13:20:00Z',
                '2023-07-10T09:00:00Z',
            ])
        ]

    def test_from_dict(self):
        commit_dict = {
            'sha': 'testsha',
            'commit': {
                'author': {
                    'name': 'Test Author',
                    'date': '2023-07-01T10:00:00Z'
                },
                'message': 'Test commit message'
            }
        }
        commit = Commit.from_dict(commit_dict)
        self.assertEqual(commit.sha, 'testsha')
        self.assertEqual(commit.author, 'Test Author')
        self.assertEqual(commit.date, datetime(2023, 7, 1, 10, 0, tzinfo=ZoneInfo("UTC")))
        self.assertEqual(commit.message, 'Test commit message')

    def test_get_commit_time_distribution(self):
        distribution = Commit.get_commit_time_distribution(self.sample_commits)
        self.assertEqual(len(distribution), 7)  # 7 days of the week
        self.assertEqual(sum(distribution.values()), 8)  # Total 8 commits
        self.assertEqual(distribution['Saturday'], 1)
        self.assertEqual(distribution['Monday'], 3)
        self.assertEqual(distribution['Sunday'], 1)

    def test_get_average_commit_frequency(self):
        frequency = Commit.get_average_commit_frequency(self.sample_commits)
        self.assertAlmostEqual(frequency, 0.8, places=1)  # 8 commits over 10 days (July 1 to July 10)

    def test_get_longest_streak(self):
        streak = Commit.get_longest_streak(self.sample_commits)
        self.assertEqual(streak, 3)  # Longest streak is 3 days (July 1-3)


if __name__ == '__main__':
    unittest.main()
