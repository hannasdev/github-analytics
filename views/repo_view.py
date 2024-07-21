# views/repo_view.py
from typing import Dict, Any


class RepoView:
    @staticmethod
    def display_analysis(analysis: Dict[str, Any]):
        print("\nRepository Analysis Results:")
        print("=============================")

        print("\nTop Starred Repositories:")
        for repo in analysis['top_starred']:
            print(f"- {repo.name}: {repo.stars} stars")

        print("\nTop Forked Repositories:")
        for repo in analysis['top_forked']:
            print(f"- {repo.name}: {repo.forks} forks")

        print("\nMost Recent Activity:")
        for repo in analysis['recent_activity']:
            print(f"- {repo.name}: last updated on {repo.last_updated}")

        print("\nLanguage Breakdown:")
        for language, count in analysis['language_breakdown'].items():
            print(f"- {language}: {count}")

        print("\nCharts generated:")
        for chart_file in analysis['chart_files']:
            print(f"- {chart_file}")

        print("\nPlease check the generated PNG files for visual representations of the data.")
