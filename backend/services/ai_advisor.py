from typing import Dict, List, Any
from backend.models.schemas import CriticalityMetrics, CriticalityResponse

class OpenSSFAIAdvisor:
    """
    AI Security & Criticality Advisory Engine:
    Performs deep diagnostic evaluations on OpenSSF metrics to generate risk assessments,
    security posture ratings, and phased milestone roadmaps.
    """

    @staticmethod
    def generate_advisory(metrics: CriticalityMetrics, criticality: CriticalityResponse) -> Dict[str, Any]:
        score = criticality.score
        norm_scores = {k: v.normalized_score for k, v in criticality.breakdown.items()}

        # 1. Category Sub-scores
        community_health = round((norm_scores['contributor_count'] * 2 + norm_scores['org_count']) / 3.0, 3)
        activity_velocity = round((norm_scores['commit_frequency'] + norm_scores['recent_releases_count'] + (1 - norm_scores['updated_since'])) / 3.0, 3)
        ecosystem_reach = round(norm_scores['dependents_count'], 3)
        issue_resolution = round((norm_scores['updated_issues_count'] + norm_scores['closed_issues_count'] + norm_scores['comment_frequency']) / 3.0, 3)

        # 2. Risk Level Assessment
        if score >= 0.400:
            risk_level = "LOW (Critical Infrastructure Tier)"
            summary = "The repository exhibits high ecosystem criticality, robust maintainer engagement, and strong activity metrics."
        elif score >= 0.250:
            risk_level = "MEDIUM (Elevated Tier)"
            summary = "The repository is gaining traction but requires broader multi-organizational contribution and structured release cadences."
        else:
            risk_level = "HIGH (Single-Point of Failure Risk)"
            summary = "The repository is at risk of single-maintainer bottleneck and low downstream adoption."

        # 3. Phased Milestone Roadmap
        roadmap = []
        if norm_scores['contributor_count'] < 0.4:
            roadmap.append({
                "phase": "Phase 1: Maintainer Diversification",
                "target": "Increase distinct contributors to >= 30",
                "impact": "+0.080 Criticality Score Increase",
                "action": "Adopt GOOD_FIRST_ISSUE tags, document developer onboarding in CONTRIBUTING.md, and invite active pull request reviewers to core maintainer team."
            })
        if norm_scores['recent_releases_count'] < 0.4:
            roadmap.append({
                "phase": "Phase 2: Automated Release Pipeline",
                "target": "Publish semantic releases monthly",
                "impact": "+0.045 Criticality Score Increase",
                "action": "Integrate GitHub Actions release workflows with SLSA level 3 provenance attestation and automated changelog generation."
            })
        if norm_scores['dependents_count'] < 0.4:
            roadmap.append({
                "phase": "Phase 3: Package Ecosystem Distribution",
                "target": "Expand downstream package usage to >= 1,000 dependents",
                "impact": "+0.110 Criticality Score Increase",
                "action": "Publish official release packages to PyPI, npm, Docker Hub, and GitHub Packages registry."
            })

        if not roadmap:
            roadmap.append({
                "phase": "Continuous Maintenance",
                "target": "Sustain Critical Infrastructure Status",
                "impact": "Score >= 0.400 Maintained",
                "action": "Perform weekly security triage, maintain OpenSSF Scorecard badges, and audit dependencies via Dependabot."
            })

        return {
            "criticality_score": score,
            "risk_level": risk_level,
            "executive_summary": summary,
            "sub_scores": {
                "community_health": community_health,
                "activity_velocity": activity_velocity,
                "ecosystem_reach": ecosystem_reach,
                "issue_resolution": issue_resolution
            },
            "roadmap": roadmap
        }
