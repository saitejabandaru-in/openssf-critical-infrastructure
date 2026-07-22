from typing import Dict, List
from pydantic import BaseModel, Field

class CriticalityMetrics(BaseModel):
    created_since: float = Field(..., description="Age of project in months", ge=0)
    updated_since: float = Field(..., description="Months since last commit/update", ge=0)
    contributor_count: int = Field(..., description="Number of distinct contributors", ge=0)
    org_count: int = Field(..., description="Number of distinct contributor organizations", ge=0)
    commit_frequency: float = Field(..., description="Average commits per week in past year", ge=0)
    recent_releases_count: int = Field(..., description="Number of releases in past year", ge=0)
    updated_issues_count: int = Field(..., description="Updated issues in past year", ge=0)
    closed_issues_count: int = Field(..., description="Closed issues in past year", ge=0)
    comment_frequency: float = Field(..., description="Average comments per issue in past year", ge=0)
    dependents_count: int = Field(..., description="Number of dependent repos/packages", ge=0)

class MetricBreakdown(BaseModel):
    raw_value: float
    max_value: float
    weight: float
    normalized_score: float
    weighted_score: float

class CriticalityResponse(BaseModel):
    score: float
    status: str  # "Critical Infrastructure", "Elevated Importance", "Standard Project"
    is_critical: bool
    breakdown: Dict[str, MetricBreakdown]
    recommendations: List[str]

class RepoAnalysisResponse(BaseModel):
    owner: str
    repo: str
    metrics: CriticalityMetrics
    criticality: CriticalityResponse
    github_url: str
    stars: int
    forks: int
    open_issues: int

class RepoComparisonRequest(BaseModel):
    repo_a: str = Field(..., description="First repository in owner/name format")
    repo_b: str = Field(..., description="Second repository in owner/name format")

class RepoComparisonResponse(BaseModel):
    repo_a: RepoAnalysisResponse
    repo_b: RepoAnalysisResponse
    score_delta: float
    winner: str
