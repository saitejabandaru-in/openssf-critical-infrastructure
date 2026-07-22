#!/usr/bin/env python3
import math
import argparse
import json
import sys

# Official OpenSSF Criticality Score Parameter Model
PARAMS = {
    'created_since': {'weight': 1.0, 'max': 120, 'alpha': 1.0, 'inverted': False, 'label': 'Project Age (Months)'},
    'updated_since': {'weight': 1.0, 'max': 120, 'alpha': 1.0, 'inverted': True, 'label': 'Inactivity (Months)'},
    'contributor_count': {'weight': 2.0, 'max': 5000, 'alpha': 0.001, 'inverted': False, 'label': 'Contributors'},
    'org_count': {'weight': 1.0, 'max': 10, 'alpha': 0.1, 'inverted': False, 'label': 'Organizations'},
    'commit_frequency': {'weight': 1.0, 'max': 1000, 'alpha': 0.01, 'inverted': False, 'label': 'Commits / Week'},
    'recent_releases_count': {'weight': 0.5, 'max': 26, 'alpha': 0.1, 'inverted': False, 'label': 'Releases (Yearly)'},
    'updated_issues_count': {'weight': 0.5, 'max': 5000, 'alpha': 0.001, 'inverted': False, 'label': 'Updated Issues'},
    'closed_issues_count': {'weight': 0.5, 'max': 5000, 'alpha': 0.001, 'inverted': False, 'label': 'Closed Issues'},
    'comment_frequency': {'weight': 1.0, 'max': 15, 'alpha': 0.1, 'inverted': False, 'label': 'Comments / Issue'},
    'dependents_count': {'weight': 2.0, 'max': 500000, 'alpha': 0.00001, 'inverted': False, 'label': 'Dependents Count'}
}

BANNER = r"""
  ___                    ____ ____  _____  ____  _       _   __                    
 / _ \ _ __  ___ _ __   / ___/ ___||  ___|/ ___|| | ___ | |_/ _| __ _ _ __ ___  ___ 
| | | | '_ \/ _ \ '_ \  \___ \___ \| |_  | |  _ | |/ _ \|  _| |_ / _` | '__/ _ \/ __|
| |_| | |_) |  __/ | | |  ___) |__) |  _| | |_| || | (_) | | |  _| (_| | | |  __/\__ \
 \___/| .__/ \___|_| |_| |____/____/|_|    \____||_|\___/|_| |_|  \__,_|_|  \___||___/
      |_|                                                                              
                 Enterprise Criticality Engine & Analytics Platform v2.2
"""

def calculate_score(metrics):
    total_weight = 0.0
    total_score = 0.0
    breakdown = {}
    
    for key, p in PARAMS.items():
        val = metrics.get(key, 0)
        bounded_val = max(0, min(val, p['max']))
        
        num = math.log(1.0 + p['alpha'] * bounded_val)
        den = math.log(1.0 + p['alpha'] * p['max'])
        
        s = num / den if den > 0 else 0
        if p['inverted']:
            s = 1.0 - s
            
        weighted = p['weight'] * s
        total_score += weighted
        total_weight += p['weight']

        breakdown[key] = {
            'label': p['label'],
            'raw': val,
            'norm': round(s, 4),
            'weight': p['weight']
        }
        
    final_score = total_score / total_weight if total_weight > 0 else 0.0
    return round(final_score, 5), breakdown

def print_terminal_table(score, breakdown):
    print(BANNER)
    print("=" * 72)
    print(f"  OPENSSF CRITICALITY SCORE: {score:.5f}")
    status = "CRITICAL INFRASTRUCTURE ✓" if score >= 0.400 else "STANDARD PROJECT"
    print(f"  STATUS:                    {status}")
    print("=" * 72)
    print(f"{'PARAMETER':<25} | {'RAW VALUE':<10} | {'WEIGHT':<6} | {'NORM SCORE':<10}")
    print("-" * 72)
    for k, v in breakdown.items():
        print(f"{v['label']:<25} | {str(v['raw']):<10} | {v['weight']:<6} | {v['norm']:<10.4f}")
    print("=" * 72)
    print("\n💡 Target Benchmark: Score >= 0.400 qualifies as Critical Infrastructure.\n")

def main():
    parser = argparse.ArgumentParser(description="OpenSSF Criticality Engine CLI")
    parser.add_argument("--demo", action="store_true", help="Run terminal demo with score >= 0.400")
    parser.add_argument("--json", type=str, help="Calculate score from JSON metrics file")
    
    args = parser.parse_args()
    
    if args.demo or len(sys.argv) == 1:
        demo_metrics = {
            'created_since': 60,
            'updated_since': 0,
            'contributor_count': 150,
            'org_count': 10,
            'commit_frequency': 25,
            'recent_releases_count': 12,
            'updated_issues_count': 500,
            'closed_issues_count': 450,
            'comment_frequency': 6.5,
            'dependents_count': 5000
        }
        score, breakdown = calculate_score(demo_metrics)
        print_terminal_table(score, breakdown)
        return
        
    if args.json:
        with open(args.json, 'r') as f:
            metrics = json.load(f)
        score, breakdown = calculate_score(metrics)
        print(json.dumps({"criticality_score": score, "breakdown": breakdown}, indent=2))
        return

if __name__ == "__main__":
    main()
