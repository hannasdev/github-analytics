# main.py
import asyncio
from tqdm import tqdm
from services.github_service import GitHubService
from controllers.commit_controller import CommitController
from controllers.pr_controller import PRController
from controllers.repo_controller import RepoController
from views.commit_view import CommitView
from views.pr_view import PRView
from views.repo_view import RepoView
from config import GITHUB_TOKEN, GITHUB_USERNAME


async def run_analysis_with_progress(controller, total_steps):
    progress_bar = tqdm(total=total_steps, desc=f"{controller.__class__.__name__}")
    results = await controller.run_analysis(progress_callback=progress_bar.update)
    progress_bar.close()
    return results


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
        # Get repository count first
        repo_count = await github_service.get_user_repo_count(GITHUB_USERNAME)

        # Run analyses concurrently with estimated total steps
        analyses = await asyncio.gather(
            run_analysis_with_progress(commit_controller, total_steps=5 + repo_count),
            run_analysis_with_progress(pr_controller, total_steps=4 + repo_count),
            run_analysis_with_progress(repo_controller, total_steps=8)
        )

        commit_analysis_results, pr_analysis_results, repo_analysis_results = analyses

        # Display results
        commit_view.display_analysis(commit_analysis_results)
        pr_view.display_analysis(pr_analysis_results)
        repo_view.display_analysis(repo_analysis_results)
    except Exception as e:
        print(f"An error occurred during analysis: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
