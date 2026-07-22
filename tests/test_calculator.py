import pytest
from backend.models.schemas import CriticalityMetrics
from backend.core.calculator import OpenSSFCriticalityCalculator, CRITICAL_THRESHOLD

def test_criticality_calculator_high_score():
    high_metrics = CriticalityMetrics(
        created_since=60,
        updated_since=0,
        contributor_count=150,
        org_count=10,
        commit_frequency=25,
        recent_releases_count=12,
        updated_issues_count=500,
        closed_issues_count=450,
        comment_frequency=6.5,
        dependents_count=5000
    )
    result = OpenSSFCriticalityCalculator.calculate(high_metrics)
    assert result.score >= CRITICAL_THRESHOLD
    assert result.is_critical is True
    assert result.status == "Critical Infrastructure"
    assert "contributor_count" in result.breakdown

def test_criticality_calculator_low_score():
    low_metrics = CriticalityMetrics(
        created_since=2,
        updated_since=10,
        contributor_count=1,
        org_count=1,
        commit_frequency=0.1,
        recent_releases_count=0,
        updated_issues_count=1,
        closed_issues_count=0,
        comment_frequency=0.5,
        dependents_count=0
    )
    result = OpenSSFCriticalityCalculator.calculate(low_metrics)
    assert result.score < CRITICAL_THRESHOLD
    assert result.is_critical is False
    assert result.status == "Standard Project"
    assert len(result.recommendations) > 0
