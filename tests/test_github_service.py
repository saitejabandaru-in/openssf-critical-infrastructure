import os
import pytest
from backend.services.github import GitHubService

@pytest.mark.asyncio
async def test_github_service_analyze_public_repo():
    token = None
    env_file = "/Users/saitejabandaru/.gemini/antigravity/scratch/.env"
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                if line.startswith("GITHUB_TOKEN="):
                    token = line.split("=")[1].strip()
                    
    service = GitHubService(token=token)
    result = await service.analyze_repo("torvalds", "linux")
    assert result.owner == "torvalds"
    assert result.repo == "linux"
    assert result.metrics.contributor_count >= 1
    assert result.criticality.score >= 0.400
    assert result.criticality.is_critical is True
