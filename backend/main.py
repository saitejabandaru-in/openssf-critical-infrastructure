import os
from fastapi import FastAPI, HTTPException, Path
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, PlainTextResponse
from backend.models.schemas import (
    CriticalityMetrics, CriticalityResponse, RepoAnalysisResponse,
    RepoComparisonRequest, RepoComparisonResponse
)
from backend.core.calculator import OpenSSFCriticalityCalculator
from backend.services.github import GitHubService
from backend.services.ai_advisor import OpenSSFAIAdvisor

app = FastAPI(
    title="OpenSSF Criticality Analytics Platform & AI Advisory API",
    description="Enterprise-grade API for calculating OpenSSF Criticality Scores, fetching live GitHub metrics, comparing repositories, and generating AI security advisories.",
    version="2.1.0"
)

# CORS middleware setup for modern web clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

github_service = GitHubService()

@app.get("/api/v1/health")
async def health_check():
    return {
        "status": "online",
        "service": "OpenSSF Criticality Analytics & AI Advisory Engine",
        "version": "2.1.0",
        "threshold": 0.400
    }

@app.post("/api/v1/calculate", response_model=CriticalityResponse)
async def calculate_criticality(metrics: CriticalityMetrics):
    """
    Calculate OpenSSF Criticality Score from raw repository parameters.
    """
    return OpenSSFCriticalityCalculator.calculate(metrics)

@app.get("/api/v1/analyze/{owner}/{repo}", response_model=RepoAnalysisResponse)
async def analyze_github_repository(
    owner: str = Path(..., description="GitHub repository owner/organization"),
    repo: str = Path(..., description="GitHub repository name")
):
    """
    Fetch real-time repository statistics from GitHub REST API and calculate OpenSSF Criticality Score.
    """
    try:
        return await github_service.analyze_repo(owner, repo)
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@app.post("/api/v1/compare", response_model=RepoComparisonResponse)
async def compare_repositories(request: RepoComparisonRequest):
    """
    Compare two GitHub repositories side-by-side and calculate criticality delta.
    """
    try:
        owner_a, name_a = request.repo_a.strip().split("/")
        owner_b, name_b = request.repo_b.strip().split("/")

        res_a = await github_service.analyze_repo(owner_a, name_a)
        res_b = await github_service.analyze_repo(owner_b, name_b)

        delta = round(res_a.criticality.score - res_b.criticality.score, 5)
        winner = request.repo_a if delta >= 0 else request.repo_b

        return RepoComparisonResponse(
            repo_a=res_a,
            repo_b=res_b,
            score_delta=abs(delta),
            winner=winner
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to compare repositories: {str(e)}")

@app.get("/api/v1/advisory/{owner}/{repo}")
async def get_ai_advisory(
    owner: str = Path(..., description="GitHub repository owner/organization"),
    repo: str = Path(..., description="GitHub repository name")
):
    """
    Generate an AI Security & Optimization Advisory for a repository.
    """
    try:
        analysis = await github_service.analyze_repo(owner, repo)
        return OpenSSFAIAdvisor.generate_advisory(analysis.metrics, analysis.criticality)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate advisory: {str(e)}")

@app.get("/api/v1/report/{owner}/{repo}", response_class=PlainTextResponse)
async def export_markdown_report(
    owner: str = Path(..., description="GitHub repository owner/organization"),
    repo: str = Path(..., description="GitHub repository name")
):
    """
    Generate a full OpenSSF Criticality Audit Report in Markdown format.
    """
    try:
        analysis = await github_service.analyze_repo(owner, repo)
        advisory = OpenSSFAIAdvisor.generate_advisory(analysis.metrics, analysis.criticality)

        md = f"""# OpenSSF Criticality Audit Report: {owner}/{repo}

**Repository URL:** {analysis.github_url}  
**OpenSSF Criticality Score:** `{analysis.criticality.score:.5f}`  
**Status:** **{analysis.criticality.status}**  
**Risk Level:** {advisory['risk_level']}  

---

## Metric Breakdown
| Parameter | Raw Value | Max Value | Weight | Normalized Score |
| :--- | :---: | :---: | :---: | :---: |
"""
        for k, v in analysis.criticality.breakdown.items():
            md += f"| `{k}` | {v.raw_value} | {v.max_value} | {v.weight} | `{v.normalized_score:.4f}` |\n"

        md += "\n## Executive AI Summary\n"
        md += f"{advisory['executive_summary']}\n\n"

        md += "## Phased Milestone Roadmap\n"
        for item in advisory['roadmap']:
            md += f"- **{item['phase']}**: {item['target']} (*{item['impact']}*)\n  *Action:* {item['action']}\n"

        return md
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate report: {str(e)}")

# Mount frontend static files
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

    @app.get("/")
    async def serve_index():
        index_file = os.path.join(frontend_dir, "index.html")
        if os.path.exists(index_file):
            return FileResponse(index_file)
        return {"message": "OpenSSF Criticality API Server Running."}

def main():
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    main()
