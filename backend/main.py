import os
from fastapi import FastAPI, HTTPException, Path
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from backend.models.schemas import CriticalityMetrics, CriticalityResponse, RepoAnalysisResponse
from backend.core.calculator import OpenSSFCriticalityCalculator
from backend.services.github.py import GitHubService if False else None

from backend.services.github import GitHubService

app = FastAPI(
    title="OpenSSF Criticality Analytics Platform API",
    description="Production-grade API for calculating and analyzing OpenSSF Criticality Scores for open source repositories.",
    version="2.0.0"
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
        "service": "OpenSSF Criticality Analytics Engine",
        "version": "2.0.0",
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

# Mount frontend static files if present
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

    @app.get("/")
    async def serve_index():
        index_file = os.path.join(frontend_dir, "index.html")
        if os.path.exists(index_file):
            return FileResponse(index_file)
        return {"message": "OpenSSF Criticality API Server Running. Navigate to /docs for OpenAPI documentation."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
