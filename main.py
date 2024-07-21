# main.py
import asyncio
from services.github_service import GitHubService
from controllers.commit_controller import CommitController
from controllers.pr_controller import PRController
from controllers.repo_controller import RepoController
from views.commit_view import CommitView
from views.pr_view import PRView
from views.repo_view import RepoView
from config import GITHUB_TOKEN, GITHUB_USERNAME


async def main():
    if not GITHUB_TOKEN or not GITHUB_USERNAME:
        print("Error: GitHub token or username not found in environment variables.")
        print("Please ensure you have set GITHUB_TOKEN and GITHUB_USERNAME in your .env file.")
        return

    github_service = GitHubService(GITHUB_TOKEN)
    commit_controller = CommitController(GITHUB_USERNAME, github_service)
    pr_controller = PRController(GITHUB_USERNAME, github_service)
    repo_controller = RepoController(GITHUB_USERNAME, github_service)
    commit_view = CommitView()
    pr_view = PRView()
    repo_view = RepoView()

    try:
        commit_analysis_results = await commit_controller.run_analysis()
        pr_analysis_results = await pr_controller.run_analysis()
        repo_analysis_results = await repo_controller.run_analysis()

        commit_view.display_analysis(commit_analysis_results)
        pr_view.display_analysis(pr_analysis_results)
        repo_view.display_analysis(repo_analysis_results)
    except Exception as e:
        print(f"An error occurred during analysis: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
