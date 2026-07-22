from backend.models.schemas import CriticalityMetrics
from backend.core.calculator import OpenSSFCriticalityCalculator, CRITICAL_THRESHOLD
from backend.services.ai_advisor import OpenSSFAIAdvisor

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

def test_ai_advisor_generation():
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
    advisory = OpenSSFAIAdvisor.generate_advisory(high_metrics, result)
    assert advisory["criticality_score"] >= CRITICAL_THRESHOLD
    assert "sub_scores" in advisory
    assert len(advisory["roadmap"]) > 0
