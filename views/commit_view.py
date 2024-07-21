from typing import Dict, Any


class CommitView:
    @staticmethod
    def display_analysis(analysis: Dict[str, Any]):
        print("\nCommit Analysis Results:")
        print("========================")

        print("\nCommit Time Distribution:")
        for day, count in analysis['time_distribution'].items():
            print(f"{day}: {count}")

        print(f"\nAverage Commit Frequency: {analysis['avg_frequency']:.2f} commits per day")
        print(f"Longest Commit Streak: {analysis['longest_streak']} days")
