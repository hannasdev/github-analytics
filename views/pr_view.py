# views/pr_view.py
from typing import Dict, Any


class PRView:
    @staticmethod
    def display_analysis(analysis: Dict[str, Any]):
        print("\nPull Request Analysis Results:")
        print("===============================")

        print(f"\nTotal Pull Requests: {analysis['total_prs']}")
        print(f"Opened Pull Requests: {analysis['pr_stats']['opened']}")
        print(f"Closed Pull Requests: {analysis['pr_stats']['closed']}")

        if analysis['total_prs'] > 0:
            open_percentage = (analysis['pr_stats']['opened'] / analysis['total_prs']) * 100
            closed_percentage = (analysis['pr_stats']['closed'] / analysis['total_prs']) * 100
            print(f"\nOpen PR Percentage: {open_percentage:.2f}%")
            print(f"Closed PR Percentage: {closed_percentage:.2f}%")
