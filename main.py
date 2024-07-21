# main.py
import asyncio
from config import GITHUB_USERNAME
from github_analyzer import GitHubAnalyzer


async def main():
    analyzer = GitHubAnalyzer(GITHUB_USERNAME)
    await analyzer.run_analysis()

if __name__ == "__main__":
    asyncio.run(main())
