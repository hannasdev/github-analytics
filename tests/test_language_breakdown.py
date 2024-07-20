# tests/test_language_breakdown.py
import unittest
from unittest.mock import patch, Mock
from io import BytesIO
import matplotlib.pyplot as plt
import importlib
import sys
import repo_stats

print("Python version:", sys.version)
print("Python path:", sys.path)
print("Imported repo_stats")
print("repo_stats file:", repo_stats.__file__)
print("repo_stats attributes:", dir(repo_stats))

# Force reload of the module
importlib.reload(repo_stats)

print("Reloaded repo_stats")
print("repo_stats attributes after reload:", dir(repo_stats))


class TestLanguageBreakdown(unittest.TestCase):
    def setUp(self):
        self.sample_repos = [
            {'name': 'repo1', 'language': 'Python'},
            {'name': 'repo2', 'language': 'JavaScript'},
            {'name': 'repo3', 'language': 'Python'},
            {'name': 'repo4', 'language': 'Java'},
            {'name': 'repo5', 'language': 'JavaScript'},
        ]

    def test_get_language_breakdown(self):
        print("Starting test_get_language_breakdown")
        breakdown = repo_stats.get_language_breakdown(self.sample_repos)
        print("Breakdown result:", breakdown)
        self.assertEqual(len(breakdown), 3)
        self.assertEqual(breakdown['Python'], 2)
        self.assertEqual(breakdown['JavaScript'], 2)
        self.assertEqual(breakdown['Java'], 1)

    @patch('matplotlib.pyplot.savefig')
    def test_language_breakdown_plot(self, mock_savefig):
        print("Starting test_language_breakdown_plot")

        # Mock the savefig function to write some dummy data
        def mock_save(buf, format=None, **kwargs):
            buf.write(b'dummy image data')
        mock_savefig.side_effect = mock_save

        breakdown, img_buf = repo_stats.get_language_breakdown(self.sample_repos, plot=True)
        print(f"Breakdown: {breakdown}")
        print(f"Image buffer type: {type(img_buf)}")
        print(f"Image buffer length: {len(img_buf.getvalue())}")

        mock_savefig.assert_called_once()

        args, kwargs = mock_savefig.call_args
        print(f"mock_savefig args: {args}")
        print(f"mock_savefig kwargs: {kwargs}")

        img_buf.seek(0)
        img_data = img_buf.read()
        print(f"Image data length: {len(img_data)}")

        self.assertGreater(len(img_data), 0)
        self.assertEqual(img_data, b'dummy image data')
