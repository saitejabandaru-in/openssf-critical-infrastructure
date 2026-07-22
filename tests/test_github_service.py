import pytest
from backend.services.github import GitHubService

@pytest.mark.asyncio
async def test_github_service_analyze_public_repo():
    service = GitHubService()
    # Test with a known public repository
    result = await service.analyze_repo("torvalds", "linux")
    assert result.owner == "torvalds"
    assert result.repo == "linux"
    assert result.metrics.contributor_count > 10
    assert result.criticality.score >= 0.400
    assert result.criticality.is_critical is True
