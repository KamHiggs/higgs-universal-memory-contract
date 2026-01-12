#!/usr/bin/env python3
"""
Slime Mold Organism - Cognitive Architecture Breeding Engine
Version: 0.1.2

PURPOSE:
Implements evolutionary breeding of Cogni Map variants using:
- Crossover (recombination of parent maps)
- Mutation (parameter adjustments)
- Fitness-based selection
- Genetic diversity preservation

USAGE:
    from slimemold_breeding_engine import breed_variants, mutate_map, crossover_maps

    # Breed new generation
    offspring = breed_variants(
        parent_maps=[map1, map2],
        breeding_config=config,
        generation=1
    )
"""

import json
import hashlib
import random
import copy
from typing import Dict, List, Any, Tuple
from datetime import datetime
import uuid


# ============================================================================
# MUTATION OPERATORS
# ============================================================================

class MutationOperators:
    """Collection of mutation operations for Cogni Maps"""

    @staticmethod
    def adjust_threshold(map_json: Dict, path: str, magnitude_pct: float = 20.0) -> Tuple[Dict, Dict]:
        """
        Adjust numerical threshold by ±magnitude_pct

        Example: high_value_threshold: 10000 -> 8000 or 12000
        """
        keys = path.strip('$.').split('.')
        current = map_json

        # Navigate to the value
        for key in keys[:-1]:
            if key not in current:
                return map_json, {'op': 'adjust_threshold', 'path': path, 'status': 'path_not_found'}
            current = current[key]

        final_key = keys[-1]
        if final_key not in current or not isinstance(current[final_key], (int, float)):
            return map_json, {'op': 'adjust_threshold', 'path': path, 'status': 'not_numeric'}

        old_value = current[final_key]
        adjustment = random.uniform(-magnitude_pct/100, magnitude_pct/100)
        new_value = old_value * (1 + adjustment)

        # Round to appropriate precision
        if isinstance(old_value, int):
            new_value = int(round(new_value))
        else:
            new_value = round(new_value, 2)

        current[final_key] = new_value

        mutation_record = {
            'op': 'adjust_threshold',
            'path': path,
            'old_value': old_value,
            'new_value': new_value,
            'adjustment_pct': round(adjustment * 100, 2)
        }

        return map_json, mutation_record

    @staticmethod
    def change_timing(map_json: Dict, path: str, magnitude_pct: float = 20.0) -> Tuple[Dict, Dict]:
        """
        Adjust timing parameter (hours, days, intervals)

        Example: dedupe_window_hours: 48 -> 38 or 58
        """
        return MutationOperators.adjust_threshold(map_json, path, magnitude_pct)

    @staticmethod
    def swap_channel_priority(map_json: Dict, path: str) -> Tuple[Dict, Dict]:
        """
        Swap priority order of channels (e.g., email-first vs SMS-first)

        Example: [email, sms, voice] -> [sms, email, voice]
        """
        keys = path.strip('$.').split('.')
        current = map_json

        for key in keys[:-1]:
            if key not in current:
                return map_json, {'op': 'swap_channel', 'path': path, 'status': 'path_not_found'}
            current = current[key]

        final_key = keys[-1]
        if final_key not in current or not isinstance(current[final_key], list):
            return map_json, {'op': 'swap_channel', 'path': path, 'status': 'not_list'}

        channels = current[final_key].copy()
        if len(channels) < 2:
            return map_json, {'op': 'swap_channel', 'path': path, 'status': 'insufficient_items'}

        # Swap first two items
        old_order = channels.copy()
        channels[0], channels[1] = channels[1], channels[0]
        current[final_key] = channels

        mutation_record = {
            'op': 'swap_channel_priority',
            'path': path,
            'old_order': old_order,
            'new_order': channels
        }

        return map_json, mutation_record

    @staticmethod
    def adjust_stage_weights(map_json: Dict, path: str, magnitude_pct: float = 20.0) -> Tuple[Dict, Dict]:
        """
        Adjust escalation stage weights/thresholds

        Example: stage_1_days: 7 -> 6 or 8
        """
        return MutationOperators.adjust_threshold(map_json, path, magnitude_pct)

    @staticmethod
    def toggle_feature_flag(map_json: Dict, path: str) -> Tuple[Dict, Dict]:
        """
        Toggle boolean feature flag

        Example: enable_voice_escalation: false -> true
        """
        keys = path.strip('$.').split('.')
        current = map_json

        for key in keys[:-1]:
            if key not in current:
                return map_json, {'op': 'toggle_flag', 'path': path, 'status': 'path_not_found'}
            current = current[key]

        final_key = keys[-1]
        if final_key not in current or not isinstance(current[final_key], bool):
            return map_json, {'op': 'toggle_flag', 'path': path, 'status': 'not_boolean'}

        old_value = current[final_key]
        new_value = not old_value
        current[final_key] = new_value

        mutation_record = {
            'op': 'toggle_feature_flag',
            'path': path,
            'old_value': old_value,
            'new_value': new_value
        }

        return map_json, mutation_record


# ============================================================================
# CROSSOVER OPERATOR
# ============================================================================

def crossover_maps(parent1: Dict, parent2: Dict, crossover_points: List[str] = None) -> Tuple[Dict, Dict]:
    """
    Combine two parent Cogni Maps by mixing their components

    Strategy:
    - Inherit structure from parent1
    - Selectively incorporate rules/parameters from parent2
    - Preserve epistemic coherence (don't break relationships)

    Args:
        parent1: First parent cogni map
        parent2: Second parent cogni map
        crossover_points: List of JSON paths to crossover (e.g., ['$.rules', '$.escalation_stages'])

    Returns:
        (offspring_map, crossover_record)
    """
    offspring = copy.deepcopy(parent1)
    crossover_record = {
        'op': 'crossover',
        'parent1_id': parent1.get('map_id', 'unknown'),
        'parent2_id': parent2.get('map_id', 'unknown'),
        'crossover_points': []
    }

    # Default crossover points if not specified
    if crossover_points is None:
        crossover_points = [
            '$.rules',
            '$.escalation_stages',
            '$.thresholds',
            '$.channels',
            '$.timing'
        ]

    for path in crossover_points:
        keys = path.strip('$.').split('.')

        # Navigate to crossover point in both parents
        p1_current = offspring
        p2_current = parent2

        valid = True
        for key in keys[:-1]:
            if key not in p1_current or key not in p2_current:
                valid = False
                break
            p1_current = p1_current[key]
            p2_current = p2_current[key]

        if not valid:
            continue

        final_key = keys[-1]
        if final_key in p2_current:
            # 50% chance to inherit from parent2
            if random.random() < 0.5:
                old_value = p1_current.get(final_key, 'none')
                p1_current[final_key] = copy.deepcopy(p2_current[final_key])
                crossover_record['crossover_points'].append({
                    'path': path,
                    'inherited_from': 'parent2',
                    'old_value_type': type(old_value).__name__
                })

    # Update metadata
    offspring['map_id'] = f"{parent1.get('map_id', 'map')}_X_{parent2.get('map_id', 'map')}_gen"
    offspring['version'] = f"crossover_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"

    return offspring, crossover_record


# ============================================================================
# MUTATION OPERATOR
# ============================================================================

def mutate_map(cogni_map: Dict, mutation_rate: float = 15.0, magnitude_pct: float = 20.0,
               allowed_ops: List[str] = None) -> Tuple[Dict, List[Dict]]:
    """
    Apply random mutations to a Cogni Map

    Args:
        cogni_map: The cogni map to mutate
        mutation_rate: Probability (%) that each mutable parameter mutates
        magnitude_pct: How much to adjust numerical parameters (±%)
        allowed_ops: List of allowed mutation operations

    Returns:
        (mutated_map, mutation_records)
    """
    if allowed_ops is None:
        allowed_ops = ['adjust_threshold', 'change_timing', 'swap_channel', 'adjust_stage_weights']

    mutated = copy.deepcopy(cogni_map)
    mutations_applied = []

    # Identify mutable paths in the cogni map
    mutable_paths = discover_mutable_paths(mutated)

    for path_info in mutable_paths:
        path = path_info['path']
        path_type = path_info['type']

        # Apply mutation with mutation_rate probability
        if random.random() * 100 < mutation_rate:
            # Select appropriate mutation operator
            if path_type == 'numeric' and 'adjust_threshold' in allowed_ops:
                mutated, mutation_rec = MutationOperators.adjust_threshold(mutated, path, magnitude_pct)
                mutations_applied.append(mutation_rec)

            elif path_type == 'timing' and 'change_timing' in allowed_ops:
                mutated, mutation_rec = MutationOperators.change_timing(mutated, path, magnitude_pct)
                mutations_applied.append(mutation_rec)

            elif path_type == 'list' and 'swap_channel' in allowed_ops:
                mutated, mutation_rec = MutationOperators.swap_channel_priority(mutated, path)
                mutations_applied.append(mutation_rec)

            elif path_type == 'boolean' and 'toggle_flag' in allowed_ops:
                mutated, mutation_rec = MutationOperators.toggle_feature_flag(mutated, path)
                mutations_applied.append(mutation_rec)

    # Update metadata
    if mutations_applied:
        mutated['version'] = f"{mutated.get('version', 'v1.0.0')}_mut_{len(mutations_applied)}"

    return mutated, mutations_applied


# ============================================================================
# PATH DISCOVERY
# ============================================================================

def discover_mutable_paths(cogni_map: Dict, current_path: str = '$') -> List[Dict]:
    """
    Recursively discover mutable paths in a Cogni Map

    Returns list of dicts: [{'path': '$.rules.high_value_threshold', 'type': 'numeric'}, ...]
    """
    mutable_paths = []

    # Common mutable parameter patterns
    mutable_patterns = {
        'threshold': 'numeric',
        'amount': 'numeric',
        'limit': 'numeric',
        'max': 'numeric',
        'min': 'numeric',
        'days': 'timing',
        'hours': 'timing',
        'interval': 'timing',
        'window': 'timing',
        'channels': 'list',
        'priority': 'list',
        'stages': 'list',
        'enable': 'boolean',
        'allow': 'boolean'
    }

    if isinstance(cogni_map, dict):
        for key, value in cogni_map.items():
            new_path = f"{current_path}.{key}"

            # Check if this key matches mutable pattern
            key_lower = key.lower()
            for pattern, path_type in mutable_patterns.items():
                if pattern in key_lower:
                    if path_type == 'numeric' and isinstance(value, (int, float)):
                        mutable_paths.append({'path': new_path, 'type': 'numeric'})
                    elif path_type == 'timing' and isinstance(value, (int, float)):
                        mutable_paths.append({'path': new_path, 'type': 'timing'})
                    elif path_type == 'list' and isinstance(value, list):
                        mutable_paths.append({'path': new_path, 'type': 'list'})
                    elif path_type == 'boolean' and isinstance(value, bool):
                        mutable_paths.append({'path': new_path, 'type': 'boolean'})
                    break

            # Recurse into nested structures
            if isinstance(value, (dict, list)):
                mutable_paths.extend(discover_mutable_paths(value, new_path))

    elif isinstance(cogni_map, list):
        for idx, item in enumerate(cogni_map):
            new_path = f"{current_path}[{idx}]"
            if isinstance(item, (dict, list)):
                mutable_paths.extend(discover_mutable_paths(item, new_path))

    return mutable_paths


# ============================================================================
# VARIANT GENERATION
# ============================================================================

def generate_variant_id() -> str:
    """Generate unique variant ID"""
    return f"VAR-{uuid.uuid4().hex[:12]}"


def compute_map_hash(cogni_map: Dict) -> str:
    """Compute SHA-256 hash of cogni map for deduplication"""
    map_str = json.dumps(cogni_map, sort_keys=True)
    return hashlib.sha256(map_str.encode()).hexdigest()


def breed_variants(parent_maps: List[Dict], breeding_config: Dict, generation: int = 1) -> List[Dict]:
    """
    Breed new generation of variants from parent maps

    Args:
        parent_maps: List of top-performing parent cogni maps
        breeding_config: Configuration from organism_breeding_config table
        generation: Generation number

    Returns:
        List of offspring variants with metadata
    """
    offspring = []

    mutation_rate = breeding_config.get('mutation_rate', 15.0)
    crossover_rate = breeding_config.get('crossover_rate', 60.0)
    novel_variant_rate = breeding_config.get('novel_variant_rate', 5.0)
    mutation_magnitude = breeding_config.get('mutation_magnitude_pct', 20.0)
    max_variants = breeding_config.get('max_variants_per_tendril', 10)

    variants_to_generate = max_variants - len(parent_maps)

    for i in range(variants_to_generate):
        breeding_method = None
        parent_ids = []
        mutations = []
        new_map = None

        # Determine breeding method
        rand = random.random() * 100

        if rand < novel_variant_rate:
            # Generate novel variant (random parent + heavy mutation)
            breeding_method = 'novel'
            parent = random.choice(parent_maps)
            parent_ids = [parent.get('map_id')]
            new_map, mutations = mutate_map(parent, mutation_rate=50.0, magnitude_pct=40.0)

        elif rand < (novel_variant_rate + crossover_rate):
            # Crossover two parents
            if len(parent_maps) >= 2:
                breeding_method = 'crossover'
                parent1, parent2 = random.sample(parent_maps, 2)
                parent_ids = [parent1.get('map_id'), parent2.get('map_id')]
                new_map, crossover_rec = crossover_maps(parent1, parent2)

                # Apply light mutation after crossover
                new_map, mutations = mutate_map(new_map, mutation_rate=mutation_rate/2, magnitude_pct=mutation_magnitude)
                mutations.insert(0, crossover_rec)
            else:
                # Fall back to mutation if not enough parents
                breeding_method = 'mutation'
                parent = random.choice(parent_maps)
                parent_ids = [parent.get('map_id')]
                new_map, mutations = mutate_map(parent, mutation_rate=mutation_rate, magnitude_pct=mutation_magnitude)

        else:
            # Pure mutation
            breeding_method = 'mutation'
            parent = random.choice(parent_maps)
            parent_ids = [parent.get('map_id')]
            new_map, mutations = mutate_map(parent, mutation_rate=mutation_rate, magnitude_pct=mutation_magnitude)

        # Add variant metadata
        variant_id = generate_variant_id()
        map_hash = compute_map_hash(new_map)

        variant_package = {
            'variant_id': variant_id,
            'map_id': f"{new_map.get('map_id', 'map')}_gen{generation}_{variant_id}",
            'cogni_map': new_map,
            'map_hash': map_hash,
            'generation': generation,
            'breeding_method': breeding_method,
            'parent_map_ids': parent_ids,
            'mutations': mutations,
            'created_at': datetime.utcnow().isoformat()
        }

        offspring.append(variant_package)

    return offspring


# ============================================================================
# FITNESS EVALUATION
# ============================================================================

def evaluate_fitness(nutrient_samples: List[float]) -> Dict[str, float]:
    """
    Compute fitness metrics from nutrient samples

    Returns:
        {
            'sample_size': int,
            'nutrient_mean': float,
            'nutrient_stddev': float,
            'nutrient_min': float,
            'nutrient_max': float,
            'fitness_score': float  # mean / (1 + stddev)
        }
    """
    if not nutrient_samples:
        return {
            'sample_size': 0,
            'nutrient_mean': 0.0,
            'nutrient_stddev': 0.0,
            'nutrient_min': 0.0,
            'nutrient_max': 0.0,
            'fitness_score': 0.0
        }

    import statistics

    mean = statistics.mean(nutrient_samples)
    stddev = statistics.stdev(nutrient_samples) if len(nutrient_samples) > 1 else 0.0

    fitness = mean / (1 + stddev)

    return {
        'sample_size': len(nutrient_samples),
        'nutrient_mean': round(mean, 2),
        'nutrient_stddev': round(stddev, 2),
        'nutrient_min': round(min(nutrient_samples), 2),
        'nutrient_max': round(max(nutrient_samples), 2),
        'fitness_score': round(fitness, 4)
    }


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == '__main__':
    print("🧬 Slime Mold Breeding Engine v0.1.2\n")

    # Example parent cogni map (simplified Invoice Chase Agent)
    example_parent = {
        'map_id': 'GM:invoice-chase-agent-v1.2.0',
        'map_name': 'Invoice Chase Agent',
        'version': 'v1.2.0',
        'rules': {
            'high_value_threshold': 10000,
            'dedupe_window_hours': 48,
            'max_attempts': 5
        },
        'escalation_stages': [
            {'stage': 1, 'days_overdue': 7, 'channels': ['email']},
            {'stage': 2, 'days_overdue': 14, 'channels': ['email', 'sms']},
            {'stage': 3, 'days_overdue': 30, 'channels': ['email', 'sms', 'voice']}
        ],
        'channels': {
            'priority_order': ['email', 'sms', 'voice'],
            'email_enabled': True,
            'sms_enabled': True,
            'voice_enabled': False
        }
    }

    # Test mutation
    print("Testing mutation...")
    mutated, mutations = mutate_map(example_parent, mutation_rate=30.0, magnitude_pct=20.0)
    print(f"Applied {len(mutations)} mutations:")
    for mut in mutations:
        print(f"  - {mut['op']} at {mut['path']}")
    print()

    # Test breeding
    print("Testing variant breeding...")
    breeding_config = {
        'mutation_rate': 15.0,
        'crossover_rate': 60.0,
        'novel_variant_rate': 5.0,
        'mutation_magnitude_pct': 20.0,
        'max_variants_per_tendril': 5
    }

    offspring = breed_variants([example_parent], breeding_config, generation=1)
    print(f"Generated {len(offspring)} offspring variants:")
    for variant in offspring:
        print(f"  - {variant['variant_id']}: {variant['breeding_method']} ({len(variant['mutations'])} mutations)")
    print()

    # Test fitness evaluation
    print("Testing fitness evaluation...")
    sample_nutrients = [450.0, 520.0, 480.0, 510.0, 490.0, 530.0, 470.0]
    fitness_metrics = evaluate_fitness(sample_nutrients)
    print(f"Fitness metrics: {fitness_metrics}")
    print(f"Fitness score: {fitness_metrics['fitness_score']:.4f}")
    print()

    print("✅ Breeding engine ready for deployment")
