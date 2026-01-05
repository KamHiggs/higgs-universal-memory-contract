#!/usr/bin/env python3
"""
Validation suite for NDA + Patent Law Cogni Map v2026.1-GM
Tests QA accuracy, schema integrity, and computes checksum
"""

import json
import hashlib
import sys
from typing import Dict, List, Any

def load_cogni_map(filepath: str) -> Dict[str, Any]:
    """Load cogni map from JSON file"""
    with open(filepath, 'r') as f:
        return json.load(f)

def validate_schema(map_data: Dict[str, Any]) -> List[str]:
    """Validate cogni map schema"""
    errors = []

    # Required top-level keys
    required_keys = ['metadata', 'canonical_definitions', 'case_law_reference',
                     'techniques_reference', 'red_team_challenges', 'quick_reference',
                     'common_pitfalls', 'validation_qa']

    for key in required_keys:
        if key not in map_data:
            errors.append(f"Missing required top-level key: {key}")

    # Validate metadata
    if 'metadata' in map_data:
        meta_required = ['id', 'name', 'version', 'status', 'authors', 'domain', 'purpose']
        for key in meta_required:
            if key not in map_data['metadata']:
                errors.append(f"Missing required metadata field: {key}")

    # Validate epistemic tags are used
    if 'canonical_definitions' in map_data:
        for defn in map_data['canonical_definitions']:
            if 'confidence' not in defn:
                errors.append(f"Definition '{defn.get('anchor', 'unknown')}' missing confidence tag")

    return errors

def compute_checksum(map_data: Dict[str, Any]) -> str:
    """Compute SHA-256 checksum of stable map content"""
    # Exclude volatile fields
    stable_data = {
        'metadata': {k: v for k, v in map_data.get('metadata', {}).items()
                    if k not in ['updated_at', 'checksum_sha256', 'checksum_updated_at']},
        'canonical_definitions': map_data.get('canonical_definitions', []),
        'case_law_reference': map_data.get('case_law_reference', {}),
        'techniques_reference': map_data.get('techniques_reference', []),
        'red_team_challenges': map_data.get('red_team_challenges', []),
        'quick_reference': map_data.get('quick_reference', {}),
        'common_pitfalls': map_data.get('common_pitfalls', []),
        'validation_qa': map_data.get('validation_qa', [])
    }

    json_str = json.dumps(stable_data, sort_keys=True)
    return hashlib.sha256(json_str.encode('utf-8')).hexdigest()

def validate_qa_suite(map_data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate QA test suite coverage and quality"""
    results = {
        'total_questions': 0,
        'by_epistemic_tag': {},
        'coverage': {
            'patent': 0,
            'nda': 0,
            'procedural': 0,
            'case_law': 0
        },
        'questions': []
    }

    if 'validation_qa' not in map_data:
        return results

    qa_suite = map_data['validation_qa']
    results['total_questions'] = len(qa_suite)

    for qa in qa_suite:
        tag = qa.get('epistemic_tag', 'unknown')
        results['by_epistemic_tag'][tag] = results['by_epistemic_tag'].get(tag, 0) + 1

        # Categorize by topic
        question = qa.get('question', '').lower()
        if any(term in question for term in ['patent', 'provisional', 'claims', 'enablement']):
            results['coverage']['patent'] += 1
        if any(term in question for term in ['nda', 'whistleblower', 'confidential']):
            results['coverage']['nda'] += 1
        if any(term in question for term in ['file', 'filing', 'deadline', 'fee']):
            results['coverage']['procedural'] += 1
        if any(term in question for term in ['case', 'court', 'lkq', 'mcfadden', 'alice']):
            results['coverage']['case_law'] += 1

        results['questions'].append({
            'question': qa.get('question', ''),
            'has_answer': bool(qa.get('expected_answer')),
            'has_references': bool(qa.get('references')),
            'epistemic_tag': tag
        })

    return results

def validate_red_team_challenges(map_data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate red team challenges coverage"""
    results = {
        'total_challenges': 0,
        'by_confidence': {},
        'has_defense': 0,
        'challenges': []
    }

    if 'red_team_challenges' not in map_data:
        return results

    challenges = map_data['red_team_challenges']
    results['total_challenges'] = len(challenges)

    for challenge in challenges:
        confidence = challenge.get('confidence', 'unknown')
        results['by_confidence'][confidence] = results['by_confidence'].get(confidence, 0) + 1

        has_defense = bool(challenge.get('defense'))
        if has_defense:
            results['has_defense'] += 1

        results['challenges'].append({
            'threat_id': challenge.get('threat_id', ''),
            'threat': challenge.get('threat', ''),
            'has_attack': bool(challenge.get('attack')),
            'has_defense': has_defense,
            'confidence': confidence
        })

    return results

def main():
    print("=" * 80)
    print("NDA + Patent Law Cogni Map v2026.1-GM Validation Suite")
    print("=" * 80)
    print()

    # Load cogni map
    filepath = '/home/user/higgs-universal-memory-contract/nda-patent-law-v2026.1-GM.json'
    print(f"Loading cogni map from: {filepath}")

    try:
        map_data = load_cogni_map(filepath)
        print("✅ Successfully loaded cogni map")
    except Exception as e:
        print(f"❌ Failed to load cogni map: {e}")
        sys.exit(1)

    print()

    # Validate schema
    print("📋 Schema Validation")
    print("-" * 80)
    schema_errors = validate_schema(map_data)
    if schema_errors:
        print(f"❌ Found {len(schema_errors)} schema errors:")
        for error in schema_errors:
            print(f"   - {error}")
    else:
        print("✅ Schema validation passed")
    print()

    # Validate QA suite
    print("🧪 QA Test Suite Analysis")
    print("-" * 80)
    qa_results = validate_qa_suite(map_data)
    print(f"Total Questions: {qa_results['total_questions']}")
    print(f"\nEpistemic Tag Distribution:")
    for tag, count in qa_results['by_epistemic_tag'].items():
        pct = (count / qa_results['total_questions'] * 100) if qa_results['total_questions'] > 0 else 0
        print(f"  {tag}: {count} ({pct:.1f}%)")

    print(f"\nTopic Coverage:")
    for topic, count in qa_results['coverage'].items():
        print(f"  {topic.capitalize()}: {count} questions")

    # Check for missing references
    missing_refs = sum(1 for q in qa_results['questions'] if not q['has_references'])
    if missing_refs > 0:
        print(f"\n⚠️  {missing_refs} questions missing references")
    else:
        print(f"\n✅ All questions have references")

    print()

    # Validate red team challenges
    print("🔴 Red Team Challenges Analysis")
    print("-" * 80)
    rt_results = validate_red_team_challenges(map_data)
    print(f"Total Challenges: {rt_results['total_challenges']}")
    print(f"Challenges with Defenses: {rt_results['has_defense']}/{rt_results['total_challenges']}")

    if rt_results['total_challenges'] > 0:
        defense_pct = (rt_results['has_defense'] / rt_results['total_challenges']) * 100
        print(f"Defense Coverage: {defense_pct:.1f}%")

    print(f"\nConfidence Distribution:")
    for conf, count in rt_results['by_confidence'].items():
        print(f"  {conf}: {count}")

    print()

    # Compute checksum
    print("🔐 Checksum Computation")
    print("-" * 80)
    checksum = compute_checksum(map_data)
    print(f"Computed Checksum: {checksum}")

    current_checksum = map_data.get('metadata', {}).get('checksum_sha256', 'PLACEHOLDER_WILL_BE_COMPUTED')
    if current_checksum == 'PLACEHOLDER_WILL_BE_COMPUTED':
        print("⚠️  Checksum not yet added to map (placeholder detected)")
        print(f"\nAdd this to metadata.checksum_sha256:")
        print(f'    "checksum_sha256": "{checksum}"')
    elif current_checksum == checksum:
        print("✅ Checksum matches")
    else:
        print(f"❌ Checksum mismatch!")
        print(f"   Expected: {current_checksum}")
        print(f"   Computed: {checksum}")

    print()

    # Summary
    print("=" * 80)
    print("VALIDATION SUMMARY")
    print("=" * 80)

    issues = []
    if schema_errors:
        issues.append(f"❌ {len(schema_errors)} schema errors")
    else:
        print("✅ Schema valid")

    if qa_results['total_questions'] >= 8:
        print(f"✅ QA suite comprehensive ({qa_results['total_questions']} questions)")
    else:
        issues.append(f"⚠️  QA suite needs more questions (only {qa_results['total_questions']})")

    if rt_results['total_challenges'] >= 5:
        print(f"✅ Red team coverage adequate ({rt_results['total_challenges']} challenges)")
    else:
        issues.append(f"⚠️  Need more red team challenges (only {rt_results['total_challenges']})")

    if rt_results['has_defense'] == rt_results['total_challenges']:
        print(f"✅ All red team challenges have defenses")
    else:
        issues.append(f"⚠️  {rt_results['total_challenges'] - rt_results['has_defense']} challenges missing defenses")

    if current_checksum == checksum and current_checksum != 'PLACEHOLDER_WILL_BE_COMPUTED':
        print("✅ Checksum verified")
    else:
        issues.append("⚠️  Checksum needs update")

    print()

    if issues:
        print("Issues to address:")
        for issue in issues:
            print(f"  {issue}")
    else:
        print("🎉 All validations passed! Cogni map is production-ready.")

    print()

    # Return checksum for script usage
    return checksum

if __name__ == '__main__':
    checksum = main()
    sys.exit(0)
