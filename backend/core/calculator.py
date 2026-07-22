import math
from typing import Dict, List
from backend.models.schemas import CriticalityMetrics, CriticalityResponse, MetricBreakdown

# Official OpenSSF Criticality Score Parameter Parameters
PARAM_CONFIGS = {
    'created_since': {'weight': 1.0, 'max': 120.0, 'alpha': 1.0, 'inverted': False, 'label': 'Project Age (Months)'},
    'updated_since': {'weight': 1.0, 'max': 120.0, 'alpha': 1.0, 'inverted': True, 'label': 'Inactivity (Months)'},
    'contributor_count': {'weight': 2.0, 'max': 5000.0, 'alpha': 0.001, 'inverted': False, 'label': 'Contributors'},
    'org_count': {'weight': 1.0, 'max': 10.0, 'alpha': 0.1, 'inverted': False, 'label': 'Organizations'},
    'commit_frequency': {'weight': 1.0, 'max': 1000.0, 'alpha': 0.01, 'inverted': False, 'label': 'Commits / Week'},
    'recent_releases_count': {'weight': 0.5, 'max': 26.0, 'alpha': 0.1, 'inverted': False, 'label': 'Releases (Yearly)'},
    'updated_issues_count': {'weight': 0.5, 'max': 5000.0, 'alpha': 0.001, 'inverted': False, 'label': 'Updated Issues'},
    'closed_issues_count': {'weight': 0.5, 'max': 5000.0, 'alpha': 0.001, 'inverted': False, 'label': 'Closed Issues'},
    'comment_frequency': {'weight': 1.0, 'max': 15.0, 'alpha': 0.1, 'inverted': False, 'label': 'Comments / Issue'},
    'dependents_count': {'weight': 2.0, 'max': 500000.0, 'alpha': 0.00001, 'inverted': False, 'label': 'Dependents Count'}
}

CRITICAL_THRESHOLD = 0.400

class OpenSSFCriticalityCalculator:
    """
    Pure Python implementation of the OpenSSF Securing Critical Projects Working Group logarithmic criticality formula:
    S_i = ln(1 + alpha_i * x_i) / ln(1 + alpha_i * max_i)
    Criticality = sum(w_i * S_i) / sum(w_i)
    """

    @staticmethod
    def calculate(metrics: CriticalityMetrics) -> CriticalityResponse:
        metrics_dict = metrics.model_dump()
        total_weighted_score = 0.0
        total_weight = 0.0
        breakdown: Dict[str, MetricBreakdown] = {}
        recommendations: List[str] = []

        for key, config in PARAM_CONFIGS.items():
            raw_val = float(metrics_dict.get(key, 0.0))
            bounded_val = max(0.0, min(raw_val, config['max']))

            num = math.log(1.0 + config['alpha'] * bounded_val)
            den = math.log(1.0 + config['alpha'] * config['max'])

            norm_score = num / den if den > 0 else 0.0
            if config['inverted']:
                norm_score = 1.0 - norm_score

            weight = config['weight']
            weighted_score = weight * norm_score

            total_weighted_score += weighted_score
            total_weight += weight

            breakdown[key] = MetricBreakdown(
                raw_value=raw_val,
                max_value=config['max'],
                weight=weight,
                normalized_score=round(norm_score, 4),
                weighted_score=round(weighted_score, 4)
            )

        final_score = total_weighted_score / total_weight if total_weight > 0 else 0.0
        final_score = round(final_score, 5)

        is_critical = final_score >= CRITICAL_THRESHOLD

        if final_score >= CRITICAL_THRESHOLD:
            status = "Critical Infrastructure"
        elif final_score >= 0.250:
            status = "Elevated Importance"
        else:
            status = "Standard Project"

        # Generate Actionable Recommendations if below threshold or optimizing
        if metrics.contributor_count < 25:
            recommendations.append("Increase contributor diversity: Onboard external maintainers to boost contributor count & org count.")
        if metrics.commit_frequency < 10:
            recommendations.append("Maintain active development velocity: Aim for regular weekly commits to elevate commit frequency.")
        if metrics.recent_releases_count < 6:
            recommendations.append("Establish a predictable release cadence: Publish semantic releases regularly (e.g. monthly or bi-weekly).")
        if metrics.dependents_count < 1000:
            recommendations.append("Expand package ecosystem reach: Publish package distribution artifacts to PyPI/npm to increase downstream dependents.")
        if metrics.updated_since > 1:
            recommendations.append("Reduce inactivity window: Commit patches or merge pull requests to decrease updated_since lag.")

        if not recommendations:
            recommendations.append("Project meets or exceeds critical infrastructure benchmarks across all key metrics!")

        return CriticalityResponse(
            score=final_score,
            status=status,
            is_critical=is_critical,
            breakdown=breakdown,
            recommendations=recommendations
        )
