import os
import math
from datetime import datetime, timezone
import httpx
from typing import Dict, Any, Tuple
from backend.models.schemas import CriticalityMetrics, RepoAnalysisResponse
from backend.core.calculator import OpenSSFCriticalityCalculator

GITHUB_API_BASE = "https://api.github.com"

class GitHubService:
    def __init__(self, token: str = None):
        self.token = token or os.environ.get("GITHUB_TOKEN")
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "OpenSSF-Criticality-Suite/2.0"
        }
        if self.token:
            self.headers["Authorization"] = f"token {self.token}"

    async def analyze_repo(self, owner: str, repo: str) -> RepoAnalysisResponse:
        async with httpx.AsyncClient(headers=self.headers, timeout=10.0, follow_redirects=True) as client:
            # 1. Fetch main repo details
            repo_res = await client.get(f"{GITHUB_API_BASE}/repos/{owner}/{repo}")
            if repo_res.status_code != 200:
                raise ValueError(f"GitHub API Error ({repo_res.status_code}): Repository '{owner}/{repo}' not found or rate limited.")
            
            repo_data = repo_res.json()

            # 2. Fetch contributors count
            contrib_res = await client.get(f"{GITHUB_API_BASE}/repos/{owner}/{repo}/contributors?per_page=100&anon=1")
            contributor_count = len(contrib_res.json()) if contrib_res.status_code == 200 and isinstance(contrib_res.json(), list) else 1

            # 3. Fetch releases count
            rel_res = await client.get(f"{GITHUB_API_BASE}/repos/{owner}/{repo}/releases?per_page=100")
            recent_releases_count = len(rel_res.json()) if rel_res.status_code == 200 and isinstance(rel_res.json(), list) else 0

            # 4. Calculate Age and Inactivity
            now = datetime.now(timezone.utc)
            created_at = datetime.fromisoformat(repo_data["created_at"].replace("Z", "+00:00"))
            pushed_at = datetime.fromisoformat(repo_data["pushed_at"].replace("Z", "+00:00"))

            created_since_months = max(1.0, (now - created_at).days / 30.4375)
            updated_since_months = max(0.0, (now - pushed_at).days / 30.4375)

            # Estimate commit frequency and org count based on stars/forks & network activity
            open_issues_count = repo_data.get("open_issues_count", 0)
            subscribers_count = repo_data.get("subscribers_count", repo_data.get("stargazers_count", 10) // 5)
            forks_count = repo_data.get("forks_count", 0)
            network_factor = max(1, math.log10(max(10, forks_count + repo_data.get("stargazers_count", 0))))

            org_count = max(1, min(10, int(contributor_count * 0.2) + 1))
            commit_frequency = round(max(0.5, (contributor_count * 0.8 + forks_count * 0.05)), 1)
            updated_issues = max(open_issues_count, int(network_factor * 15))
            closed_issues = int(updated_issues * 0.75)
            comment_freq = round(min(15.0, max(1.5, network_factor * 1.2)), 1)
            dependents = int(math.pow(forks_count, 1.35) * 2 + subscribers_count * 3)

            metrics = CriticalityMetrics(
                created_since=round(created_since_months, 1),
                updated_since=round(updated_since_months, 1),
                contributor_count=contributor_count,
                org_count=org_count,
                commit_frequency=commit_frequency,
                recent_releases_count=recent_releases_count,
                updated_issues_count=updated_issues,
                closed_issues_count=closed_issues,
                comment_frequency=comment_freq,
                dependents_count=dependents
            )

            criticality_response = OpenSSFCriticalityCalculator.calculate(metrics)

            return RepoAnalysisResponse(
                owner=owner,
                repo=repo,
                metrics=metrics,
                criticality=criticality_response,
                github_url=repo_data.get("html_url", f"https://github.com/{owner}/{repo}"),
                stars=repo_data.get("stargazers_count", 0),
                forks=forks_count,
                open_issues=open_issues_count
            )
