#!/usr/bin/env python3
"""
Slime Mold Organism - Genesis OS Integration v1.0.0
GENESIS-POWERED MULTI-DOMAIN SIMULATION

WHAT'S NEW:
- Replaces naive void implementation with proper 4-phase Genesis control loop
- DISCOVER: Monte Carlo exploration finds unexplored parameter/topology regions
- EXPLOIT: Slime Mold optimization allocates resources to high-energy voids
- DETECT: Emergence detection finds convergent patterns across domains
- CONVERGE: Void-intelligent-architecture learns meta-routing rules

PURPOSE:
- Demonstrate Genesis OS void architecture in action
- Compare naive domain-picking vs. intelligent void navigation
- Extract meta-patterns that work across business models
- Show compounding advantage of proper void architecture

Run:
  python3 slimemold_genesis_integrated_simulation.py
"""

import random
import statistics
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from collections import defaultdict
import sys

# Import Genesis void architecture
from genesis_void_architecture import (
    GenesisControlLoop,
    ComputationalVoid,
    print_genesis_status
)


# ============================================================================
# DOMAIN DEFINITIONS (Same as v2 simulation)
# ============================================================================

@dataclass
class DomainConfig:
    """Configuration for a business domain"""
    domain_id: str
    domain_name: str
    revenue_model: str

    # Economics
    base_conversion_rate: float
    base_revenue_per_conversion: float
    base_cost_per_attempt: float

    # Characteristics
    volatility: float
    time_to_close_days: float
    customer_lifetime_months: float

    # Risks
    compliance_risk: float
    reputation_risk: float
    churn_risk: float

    # Evolvable parameters
    default_threshold: float
    default_timing_hours: float
    default_channel_mix: List[str]
    default_touch_intensity: float


DOMAINS = {
    "technical_consulting": DomainConfig(
        domain_id="technical_consulting",
        domain_name="Technical Consulting (Hourly Billing)",
        revenue_model="hourly",
        base_conversion_rate=0.35,
        base_revenue_per_conversion=4800.0,
        base_cost_per_attempt=25.0,
        volatility=0.35,
        time_to_close_days=14.0,
        customer_lifetime_months=6.0,
        compliance_risk=0.0002,
        reputation_risk=0.02,
        churn_risk=0.0,
        default_threshold=2000.0,
        default_timing_hours=24.0,
        default_channel_mix=['email', 'call', 'video'],
        default_touch_intensity=0.8
    ),

    "product_development": DomainConfig(
        domain_id="product_development",
        domain_name="Product Development (Fixed-Price Projects)",
        revenue_model="fixed",
        base_conversion_rate=0.15,
        base_revenue_per_conversion=25000.0,
        base_cost_per_attempt=50.0,
        volatility=0.5,
        time_to_close_days=45.0,
        customer_lifetime_months=12.0,
        compliance_risk=0.0001,
        reputation_risk=0.03,
        churn_risk=0.0,
        default_threshold=15000.0,
        default_timing_hours=72.0,
        default_channel_mix=['email', 'video', 'in_person'],
        default_touch_intensity=0.9
    ),

    "training_workshops": DomainConfig(
        domain_id="training_workshops",
        domain_name="Training/Workshops (Cohort Events)",
        revenue_model="one_time",
        base_conversion_rate=0.08,
        base_revenue_per_conversion=1500.0,
        base_cost_per_attempt=8.0,
        volatility=0.6,
        time_to_close_days=21.0,
        customer_lifetime_months=3.0,
        compliance_risk=0.0001,
        reputation_risk=0.02,
        churn_risk=0.0,
        default_threshold=0.0,
        default_timing_hours=168.0,
        default_channel_mix=['email', 'webinar', 'social'],
        default_touch_intensity=0.5
    ),

    "maintenance_contracts": DomainConfig(
        domain_id="maintenance_contracts",
        domain_name="Maintenance Contracts (Recurring MRR)",
        revenue_model="recurring",
        base_conversion_rate=0.25,
        base_revenue_per_conversion=800.0,
        base_cost_per_attempt=15.0,
        volatility=0.2,
        time_to_close_days=30.0,
        customer_lifetime_months=24.0,
        compliance_risk=0.0003,
        reputation_risk=0.015,
        churn_risk=0.05,
        default_threshold=500.0,
        default_timing_hours=48.0,
        default_channel_mix=['email', 'call'],
        default_touch_intensity=0.7
    ),

    "api_platform": DomainConfig(
        domain_id="api_platform",
        domain_name="API/Platform (Usage-Based Pricing)",
        revenue_model="usage",
        base_conversion_rate=0.40,
        base_revenue_per_conversion=350.0,
        base_cost_per_attempt=2.0,
        volatility=0.7,
        time_to_close_days=3.0,
        customer_lifetime_months=18.0,
        compliance_risk=0.001,
        reputation_risk=0.01,
        churn_risk=0.08,
        default_threshold=0.0,
        default_timing_hours=4.0,
        default_channel_mix=['email', 'docs', 'slack'],
        default_touch_intensity=0.3
    ),

    "digital_products": DomainConfig(
        domain_id="digital_products",
        domain_name="Digital Products (One-Time Purchase)",
        revenue_model="one_time",
        base_conversion_rate=0.05,
        base_revenue_per_conversion=299.0,
        base_cost_per_attempt=1.5,
        volatility=0.4,
        time_to_close_days=1.0,
        customer_lifetime_months=1.0,
        compliance_risk=0.0002,
        reputation_risk=0.02,
        churn_risk=0.0,
        default_threshold=0.0,
        default_timing_hours=0.5,
        default_channel_mix=['email', 'retarget', 'social'],
        default_touch_intensity=0.2
    ),
}


# ============================================================================
# VARIANT CLASS
# ============================================================================

@dataclass
class GenesisVariant:
    """
    Cognitive architecture variant with Genesis void tracking
    """
    variant_id: str
    domain_id: str
    generation: int
    parent_ids: List[str] = field(default_factory=list)

    # Strategy parameters (evolvable)
    threshold: float = 0.0
    timing_hours: float = 24.0
    channel_mix: List[str] = field(default_factory=lambda: ['email'])
    touch_intensity: float = 0.5  # 0-1

    # Tracking
    deployment_mode: str = 'shadow'  # shadow | production
    survival_status: str = 'active'  # active | pruned | promoted
    sample_size: int = 0
    nutrient_samples: List[float] = field(default_factory=list)
    revenue_samples: List[float] = field(default_factory=list)
    fitness_score: float = 0.0

    # Genesis tracking
    void_id: Optional[str] = None  # Which void spawned this variant
    void_space: Optional[str] = None  # parameter|topology|code|memory|network

    def compute_fitness(self):
        """Compute fitness score from samples"""
        if self.sample_size < 10:
            self.fitness_score = 0.0
            return

        mean_nutrient = statistics.mean(self.nutrient_samples[-100:])
        stddev_nutrient = statistics.stdev(self.nutrient_samples[-100:]) if len(self.nutrient_samples[-100:]) > 1 else 1.0
        self.fitness_score = mean_nutrient / (1 + stddev_nutrient)


# ============================================================================
# SIMULATION LOGIC
# ============================================================================

def simulate_outcome(variant: GenesisVariant, domain: DomainConfig, day: int) -> Dict:
    """Simulate single lead outcome"""
    base_conversion = domain.base_conversion_rate
    base_revenue = domain.base_revenue_per_conversion
    base_cost = domain.base_cost_per_attempt

    # Variant modifiers
    conversion_multiplier = 1.0
    cost_multiplier = 1.0
    penalty = 0.0

    # Touch intensity boosts conversion but increases cost
    conversion_multiplier += (variant.touch_intensity - 0.5) * 0.3
    cost_multiplier += (variant.touch_intensity - 0.5) * 0.5

    # Timing affects conversion
    if variant.timing_hours < domain.time_to_close_days * 24:
        conversion_multiplier += 0.1
    else:
        conversion_multiplier -= 0.05

    # Threshold filtering (only pursue high-value)
    if variant.threshold > base_revenue:
        return {'converted': False, 'revenue': 0, 'cost': 0, 'penalty': 0, 'nutrient': 0, 'conversion_rate': 0}

    # Add volatility
    volatility_factor = random.uniform(1 - domain.volatility, 1 + domain.volatility)
    conversion_multiplier *= volatility_factor

    # Simulate conversion
    effective_conversion = min(0.99, base_conversion * conversion_multiplier)
    converted = random.random() < effective_conversion

    revenue = base_revenue if converted else 0.0
    cost = base_cost * cost_multiplier

    # Risk penalties
    if converted and random.random() < domain.compliance_risk:
        penalty += 50000.0

    if random.random() < domain.reputation_risk:
        penalty += 3000.0

    nutrient = revenue - cost - penalty

    return {
        'converted': converted,
        'revenue': revenue,
        'cost': cost,
        'penalty': penalty,
        'nutrient': nutrient,
        'conversion_rate': effective_conversion
    }


def breed_variant_from_void_target(void_target: Dict, domain_id: str, generation: int) -> GenesisVariant:
    """Create variant from void exploration target"""
    return GenesisVariant(
        variant_id=f"VAR-{domain_id[:4]}-void-gen{generation}-{random.randint(1000, 9999)}",
        domain_id=domain_id,
        generation=generation,
        threshold=void_target['threshold'],
        timing_hours=void_target['timing_hours'],
        touch_intensity=void_target['touch_intensity'],
        channel_mix=['email', 'call'],  # Default
        deployment_mode='shadow',
        void_id=void_target['void_id'],
        void_space='parameter'
    )


def mutate_variant(parent: GenesisVariant, generation: int) -> GenesisVariant:
    """Create mutated offspring"""
    offspring = GenesisVariant(
        variant_id=f"VAR-{parent.domain_id[:4]}-gen{generation}-{random.randint(1000, 9999)}",
        domain_id=parent.domain_id,
        generation=generation,
        parent_ids=[parent.variant_id],
        threshold=parent.threshold,
        timing_hours=parent.timing_hours,
        channel_mix=parent.channel_mix.copy(),
        touch_intensity=parent.touch_intensity
    )

    if random.random() < 0.3:
        offspring.threshold *= random.uniform(0.8, 1.2)
    if random.random() < 0.3:
        offspring.timing_hours *= random.uniform(0.8, 1.2)
    if random.random() < 0.3:
        offspring.touch_intensity *= random.uniform(0.85, 1.15)
        offspring.touch_intensity = max(0.1, min(1.0, offspring.touch_intensity))

    return offspring


# ============================================================================
# MAIN SIMULATION WITH GENESIS INTEGRATION
# ============================================================================

def run_genesis_integrated_simulation(days: int = 90, daily_attempts_per_domain: int = 15):
    """
    Run simulation with proper Genesis void architecture
    """
    print("="*80)
    print("🌌 GENESIS OS - VOID-INTELLIGENT MULTI-DOMAIN SIMULATION")
    print("="*80)
    print(f"Duration: {days} days")
    print(f"Domains: {len(DOMAINS)}")
    print(f"Daily attempts per domain: {daily_attempts_per_domain}")
    print(f"Genesis Control Loop: 4-phase (DISCOVER → EXPLOIT → DETECT → CONVERGE)")
    print()

    # Define parameter bounds for Monte Carlo exploration
    param_bounds = {
        'threshold': (0, 30000),
        'timing_hours': (0.5, 168),
        'touch_intensity': (0.1, 1.0)
    }

    # Initialize Genesis Control Loop
    genesis = GenesisControlLoop(DOMAINS, param_bounds)

    # Initialize baseline variants for each domain
    all_variants: Dict[str, List[GenesisVariant]] = {}

    for domain_id, domain in DOMAINS.items():
        baseline = GenesisVariant(
            variant_id=f"VAR-{domain_id[:4]}-baseline",
            domain_id=domain_id,
            generation=0,
            threshold=domain.default_threshold,
            timing_hours=domain.default_timing_hours,
            channel_mix=domain.default_channel_mix.copy(),
            touch_intensity=domain.default_touch_intensity,
            deployment_mode='production'
        )
        all_variants[domain_id] = [baseline]

    generation = 0
    genesis_cycles_run = 0

    # Daily simulation loop
    for day in range(1, days + 1):
        # Simulate each domain
        for domain_id, domain in DOMAINS.items():
            variants = all_variants[domain_id]

            for variant in variants:
                if variant.survival_status != 'active' and variant.deployment_mode != 'production':
                    continue

                for _ in range(daily_attempts_per_domain):
                    outcome = simulate_outcome(variant, domain, day)
                    variant.nutrient_samples.append(outcome['nutrient'])
                    variant.revenue_samples.append(outcome['revenue'])
                    variant.sample_size += 1

            # Compute fitness
            for variant in variants:
                variant.compute_fitness()

        # Run Genesis control loop every 7 days
        if day % 7 == 0:
            generation += 1
            genesis_cycles_run += 1

            print(f"\n{'='*80}")
            print(f"📅 DAY {day} - GENESIS CONTROL LOOP CYCLE {genesis_cycles_run}")
            print(f"{'='*80}")

            # Run 4-phase Genesis cycle
            cycle_results = genesis.run_cycle(all_variants, exploration_budget=50)

            print(f"\n✅ Cycle Complete:")
            print(f"   Voids discovered: {cycle_results['voids_discovered']}")
            print(f"   Voids exploited: {cycle_results['voids_exploited']}")
            print(f"   Emergence signals: {cycle_results['emergence_signals']}")
            print(f"   Routing rules learned: {cycle_results['routing_rules_learned']}")

            # Show emergence signals
            if cycle_results['details'].get('signals'):
                print(f"\n   🔬 Emergence Signals:")
                for signal in cycle_results['details']['signals']:
                    print(f"      - Pattern: {signal['pattern']}")
                    print(f"        Domains: {', '.join(signal['domains'])}")
                    print(f"        Strength: {signal['strength']:.2f}")

            # Get void allocation targets
            void_targets = genesis.get_void_allocation_targets()
            if void_targets:
                print(f"\n   🎯 Spawning {len(void_targets)} variants from high-priority voids:")
                for target in void_targets[:3]:
                    # Pick best performing domain to spawn in
                    best_domain = max(all_variants.items(),
                                    key=lambda x: max([v.fitness_score for v in x[1] if v.deployment_mode == 'production'], default=0))[0]

                    new_variant = breed_variant_from_void_target(target, best_domain, generation)
                    all_variants[best_domain].append(new_variant)
                    print(f"      - {new_variant.variant_id} in {best_domain}")
                    print(f"        threshold=${target['threshold']:.0f}, timing={target['timing_hours']:.1f}h, "
                          f"touch={target['touch_intensity']:.2f}")

            # Standard evolutionary breeding (complement Genesis)
            for domain_id, variants in all_variants.items():
                active = [v for v in variants if v.survival_status == 'active']
                if len(active) >= 2:
                    # Breed 2 mutations from top performer
                    top = max(active, key=lambda v: v.fitness_score)
                    for _ in range(2):
                        offspring = mutate_variant(top, generation)
                        all_variants[domain_id].append(offspring)

            # Prune poor performers
            for domain_id, variants in all_variants.items():
                if len(variants) > 10:
                    sorted_variants = sorted([v for v in variants if v.deployment_mode == 'shadow'],
                                           key=lambda v: v.fitness_score)
                    for variant in sorted_variants[:2]:
                        variant.survival_status = 'pruned'

            # Check promotions
            for domain_id, variants in all_variants.items():
                production = [v for v in variants if v.deployment_mode == 'production'][0]
                shadows = [v for v in variants if v.deployment_mode == 'shadow'
                          and v.survival_status == 'active' and v.sample_size >= 100]

                for shadow in shadows:
                    if shadow.fitness_score > production.fitness_score * 1.1:
                        print(f"\n   🚀 PROMOTION: {shadow.variant_id} → production in {domain_id}")
                        print(f"      Fitness: {production.fitness_score:.2f} → {shadow.fitness_score:.2f} "
                              f"(+{((shadow.fitness_score / production.fitness_score - 1) * 100):.1f}%)")
                        production.deployment_mode = 'shadow'
                        production.survival_status = 'replaced'
                        shadow.deployment_mode = 'production'

    # ========================================================================
    # FINAL RESULTS
    # ========================================================================

    print(f"\n{'='*80}")
    print("📊 FINAL SIMULATION RESULTS")
    print(f"{'='*80}")

    results = []
    for domain_id, domain in DOMAINS.items():
        variants = all_variants[domain_id]
        production = [v for v in variants if v.deployment_mode == 'production'][0]
        baseline = [v for v in variants if 'baseline' in v.variant_id][0]

        total_nutrient = sum(production.nutrient_samples)
        total_revenue = sum(production.revenue_samples)
        avg_nutrient = statistics.mean(production.nutrient_samples) if production.nutrient_samples else 0

        baseline_fitness = baseline.fitness_score
        production_fitness = production.fitness_score
        fitness_improvement = ((production_fitness / baseline_fitness - 1) * 100) if baseline_fitness > 0 else 0

        results.append({
            'domain_id': domain_id,
            'domain_name': domain.domain_name,
            'revenue_model': domain.revenue_model,
            'total_nutrient': total_nutrient,
            'total_revenue': total_revenue,
            'avg_nutrient': avg_nutrient,
            'baseline_fitness': baseline_fitness,
            'production_fitness': production_fitness,
            'fitness_improvement_pct': fitness_improvement,
            'generation': production.generation,
            'variants_created': len(variants)
        })

    # Sort by total nutrient
    results.sort(key=lambda x: x['total_nutrient'], reverse=True)

    print("\nRanked by Total Nutrient (90 days):")
    print(f"{'Rank':<6} {'Domain':<35} {'Rev Model':<12} {'Total Nutrient':<18} {'Fitness Δ':<12} {'Gen':<6}")
    print("-" * 105)

    for i, r in enumerate(results, 1):
        domain_short = r['domain_name'][:35]
        nutrient_str = f"${r['total_nutrient']:,.0f}"
        fitness_str = f"+{r['fitness_improvement_pct']:.1f}%" if r['fitness_improvement_pct'] >= 0 else f"{r['fitness_improvement_pct']:.1f}%"
        print(f"{i:<6} {domain_short:<35} {r['revenue_model']:<12} {nutrient_str:<18} {fitness_str:<12} {r['generation']:<6}")

    # Genesis status
    print_genesis_status(genesis)

    print("\n" + "="*80)
    print("✅ Genesis-integrated simulation complete!")
    print("="*80)
    print(f"\nKey Insights:")
    print(f"  - Genesis cycles run: {genesis_cycles_run}")
    print(f"  - Active voids: {len(genesis.active_voids)}")
    print(f"  - Routing rules learned: {len(genesis.architecture.routing_rules)}")
    print(f"  - Emergence signals detected: {len(genesis.detector.detected_signals)}")
    print(f"  - Best domain: {results[0]['domain_name']} (${results[0]['total_nutrient']:,.0f})")
    print(f"  - Highest evolution: {max(results, key=lambda x: x['fitness_improvement_pct'])['domain_name']} "
          f"(+{max(results, key=lambda x: x['fitness_improvement_pct'])['fitness_improvement_pct']:.1f}%)")


if __name__ == '__main__':
    random.seed(42)  # Reproducibility
    run_genesis_integrated_simulation(days=90, daily_attempts_per_domain=15)
