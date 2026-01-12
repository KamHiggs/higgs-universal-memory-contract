#!/usr/bin/env python3
"""
Slime Mold Organism - Multi-Domain Evolutionary Simulation with Void Architecture
Version: 0.2.0-ALPHA

PURPOSE:
Demonstrate how the organism evolves cognitive architectures across multiple
business domains simultaneously, with cross-domain learning and void architecture
for rapid strategy exploration.

VOID ARCHITECTURE CONCEPT:
- Empty cognitive space that can rapidly adapt/clone successful patterns
- Acts as "stem cells" for business strategy
- Can morph into any domain based on nutrient signals
- Enables rapid pivot and exploration

DOMAINS SIMULATED:
1. Invoice Chase (B2B Revenue Operations)
2. CogniMap Builder (B2B Service Delivery)
3. Customer Support (Retention/Satisfaction)
4. Content/SEO (Organic Traffic → Leads)
5. Ads Arbitrage (Paid Acquisition)
6. VOID (Adaptive strategy - finds best domain dynamically)

Run:
  python3 slimemold_multidomain_simulation.py
"""

import random
import statistics
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from collections import defaultdict
import json


# ============================================================================
# DOMAIN DEFINITIONS
# ============================================================================

@dataclass
class DomainConfig:
    """Configuration for a business domain"""
    domain_id: str
    domain_name: str
    base_conversion_rate: float
    base_revenue_per_conversion: float
    base_cost_per_attempt: float
    volatility: float  # How much variance in outcomes
    compliance_risk: float  # Probability of penalty
    reputation_risk: float

    # Genotype parameters that can evolve
    default_threshold: float
    default_timing_hours: float
    default_channel_mix: List[str]


# Define 5 distinct business domains + void
DOMAINS = {
    "invoice_chase": DomainConfig(
        domain_id="invoice_chase",
        domain_name="Invoice Chase Agent (B2B RevOps)",
        base_conversion_rate=0.18,
        base_revenue_per_conversion=500.0,
        base_cost_per_attempt=2.0,
        volatility=0.3,
        compliance_risk=0.001,
        reputation_risk=0.01,
        default_threshold=10000.0,
        default_timing_hours=48.0,
        default_channel_mix=['email', 'sms']
    ),

    "cognimap_builder": DomainConfig(
        domain_id="cognimap_builder",
        domain_name="CogniMap Builder (B2B Service)",
        base_conversion_rate=0.12,
        base_revenue_per_conversion=3500.0,
        base_cost_per_attempt=15.0,  # Higher touch sales
        volatility=0.4,
        compliance_risk=0.0001,
        reputation_risk=0.005,
        default_threshold=5000.0,
        default_timing_hours=168.0,  # 7 days
        default_channel_mix=['email', 'video_call']
    ),

    "customer_support": DomainConfig(
        domain_id="customer_support",
        domain_name="Customer Support Agent (Retention)",
        base_conversion_rate=0.85,  # High success rate
        base_revenue_per_conversion=150.0,  # Prevented churn value
        base_cost_per_attempt=5.0,
        volatility=0.2,
        compliance_risk=0.0005,
        reputation_risk=0.02,
        default_threshold=0.0,  # No threshold - help everyone
        default_timing_hours=4.0,  # Fast response
        default_channel_mix=['chat', 'email']
    ),

    "content_seo": DomainConfig(
        domain_id="content_seo",
        domain_name="Content/SEO Engine (Organic Traffic)",
        base_conversion_rate=0.03,  # Low conversion but high volume
        base_revenue_per_conversion=2500.0,  # Lead value
        base_cost_per_attempt=1.5,  # Content creation cost per impression
        volatility=0.6,  # Very volatile (SEO is unpredictable)
        compliance_risk=0.0001,
        reputation_risk=0.001,
        default_threshold=0.0,
        default_timing_hours=720.0,  # 30 days (SEO lag)
        default_channel_mix=['blog', 'video', 'social']
    ),

    "ads_arbitrage": DomainConfig(
        domain_id="ads_arbitrage",
        domain_name="Ads Arbitrage (Paid Acquisition)",
        base_conversion_rate=0.05,
        base_revenue_per_conversion=1200.0,
        base_cost_per_attempt=8.0,  # High ad cost
        volatility=0.5,
        compliance_risk=0.002,  # Platform policy risk
        reputation_risk=0.015,  # Ad fatigue
        default_threshold=0.0,
        default_timing_hours=24.0,
        default_channel_mix=['google_ads', 'linkedin_ads']
    ),
}


# ============================================================================
# VOID ARCHITECTURE
# ============================================================================

@dataclass
class VoidArchitecture:
    """
    Void Architecture: Empty cognitive space that adapts based on nutrient signals

    Concept:
    - Starts with no fixed domain
    - Observes which domains produce most nutrient
    - Rapidly clones successful patterns from top performers
    - Acts as "stem cell" for business strategy
    - Enables rapid pivot and exploration
    """
    void_id: str
    current_domain: Optional[str] = None
    cloned_from: Optional[str] = None
    adaptation_speed: float = 0.3  # How fast it adapts (0-1)

    # Performance tracking
    total_nutrient: float = 0.0
    adaptations: List[Dict] = field(default_factory=list)

    def observe_and_adapt(self, domain_nutrients: Dict[str, float], generation: int):
        """
        Observe domain performance and adapt to best performer
        """
        if not domain_nutrients:
            return

        # Find top nutrient domain
        best_domain = max(domain_nutrients.items(), key=lambda x: x[1])
        best_domain_id, best_nutrient = best_domain

        # Adapt with probability based on nutrient difference
        if self.current_domain is None or random.random() < self.adaptation_speed:
            if best_nutrient > 0:
                old_domain = self.current_domain
                self.current_domain = best_domain_id
                self.cloned_from = best_domain_id

                self.adaptations.append({
                    'generation': generation,
                    'from_domain': old_domain,
                    'to_domain': best_domain_id,
                    'nutrient_signal': best_nutrient
                })

    def get_active_domain_config(self) -> Optional[DomainConfig]:
        """Get current domain configuration"""
        if self.current_domain and self.current_domain in DOMAINS:
            return DOMAINS[self.current_domain]
        return None


# ============================================================================
# VARIANT (Cognitive Architecture)
# ============================================================================

@dataclass
class MultiDomainVariant:
    """Represents a cognitive architecture variant for a specific domain"""
    variant_id: str
    domain_id: str
    generation: int
    parent_ids: List[str] = field(default_factory=list)

    # Genotype (strategy parameters)
    threshold: float = 10000.0
    timing_hours: float = 48.0
    channel_mix: List[str] = field(default_factory=lambda: ['email', 'sms'])
    aggression_factor: float = 1.0  # Multiplier on effort

    # Performance tracking
    sample_size: int = 0
    nutrient_samples: List[float] = field(default_factory=list)
    fitness_score: float = 0.0
    deployment_mode: str = 'shadow'
    survival_status: str = 'active'

    def compute_fitness(self):
        """Compute fitness score: mean / (1 + stddev)"""
        if len(self.nutrient_samples) < 2:
            self.fitness_score = 0.0
            return

        mean = statistics.mean(self.nutrient_samples)
        stddev = statistics.stdev(self.nutrient_samples)
        self.fitness_score = mean / (1 + stddev)


# ============================================================================
# OUTCOME SIMULATION
# ============================================================================

def simulate_outcome(variant: MultiDomainVariant, domain: DomainConfig, day: int) -> Dict:
    """
    Simulate one outcome for a variant in a domain
    """
    # Base performance
    base_conversion = domain.base_conversion_rate
    base_revenue = domain.base_revenue_per_conversion
    base_cost = domain.base_cost_per_attempt

    # Variant modifiers
    conversion_multiplier = variant.aggression_factor
    cost_multiplier = 1.0
    penalty = 0.0

    # Threshold effect
    threshold_ratio = variant.threshold / domain.default_threshold if domain.default_threshold > 0 else 1.0
    if threshold_ratio < 0.7:  # Very aggressive
        conversion_multiplier *= 1.25
        cost_multiplier *= 1.4
        penalty += random.uniform(0, 10)
    elif threshold_ratio > 1.3:  # Very conservative
        conversion_multiplier *= 0.85
        cost_multiplier *= 0.8

    # Timing effect
    timing_ratio = variant.timing_hours / domain.default_timing_hours if domain.default_timing_hours > 0 else 1.0
    if timing_ratio < 0.6:  # Very fast
        conversion_multiplier *= 1.15
        cost_multiplier *= 1.3
    elif timing_ratio > 1.5:  # Very slow
        conversion_multiplier *= 0.9
        cost_multiplier *= 0.85

    # Channel mix effect (simplified)
    if 'sms' in variant.channel_mix and domain.domain_id in ['invoice_chase', 'customer_support']:
        conversion_multiplier *= 1.1
        cost_multiplier *= 1.4

    # Add volatility
    volatility_factor = random.uniform(1 - domain.volatility, 1 + domain.volatility)
    conversion_multiplier *= volatility_factor

    # Simulate conversion
    effective_conversion_rate = min(0.99, base_conversion * conversion_multiplier)
    converted = random.random() < effective_conversion_rate

    revenue = base_revenue if converted else 0.0
    cost = base_cost * cost_multiplier

    # Risk penalties
    if converted and random.random() < domain.compliance_risk:
        penalty += 100000.0  # Compliance violation

    if random.random() < domain.reputation_risk:
        penalty += 5000.0  # Reputation damage

    nutrient = revenue - cost - penalty

    return {
        'converted': converted,
        'revenue': revenue,
        'cost': cost,
        'penalty': penalty,
        'nutrient': nutrient
    }


# ============================================================================
# EVOLUTIONARY OPERATORS
# ============================================================================

def mutate_variant(parent: MultiDomainVariant, generation: int) -> MultiDomainVariant:
    """Create mutated offspring"""
    offspring = MultiDomainVariant(
        variant_id=f"VAR-{parent.domain_id[:4]}-gen{generation}-{random.randint(1000, 9999)}",
        domain_id=parent.domain_id,
        generation=generation,
        parent_ids=[parent.variant_id],
        threshold=parent.threshold,
        timing_hours=parent.timing_hours,
        channel_mix=parent.channel_mix.copy(),
        aggression_factor=parent.aggression_factor
    )

    # Apply mutations (20% change)
    if random.random() < 0.3:
        offspring.threshold *= random.uniform(0.8, 1.2)

    if random.random() < 0.3:
        offspring.timing_hours *= random.uniform(0.8, 1.2)

    if random.random() < 0.2:
        offspring.aggression_factor *= random.uniform(0.85, 1.15)

    if random.random() < 0.2 and len(offspring.channel_mix) >= 2:
        offspring.channel_mix[0], offspring.channel_mix[1] = \
            offspring.channel_mix[1], offspring.channel_mix[0]

    return offspring


def crossover_domains(parent1: MultiDomainVariant, parent2: MultiDomainVariant,
                     target_domain: str, generation: int) -> MultiDomainVariant:
    """
    Cross-domain breeding: Take parameters from two different domains
    This is the key innovation - learning transfers across business models
    """
    offspring = MultiDomainVariant(
        variant_id=f"VAR-{target_domain[:4]}-genX{generation}-{random.randint(1000, 9999)}",
        domain_id=target_domain,
        generation=generation,
        parent_ids=[parent1.variant_id, parent2.variant_id],

        # Mix genotypes from both parents
        threshold=random.choice([parent1.threshold, parent2.threshold]),
        timing_hours=random.choice([parent1.timing_hours, parent2.timing_hours]),
        aggression_factor=(parent1.aggression_factor + parent2.aggression_factor) / 2,
        channel_mix=random.choice([parent1.channel_mix, parent2.channel_mix]).copy()
    )

    return offspring


# ============================================================================
# MULTI-DOMAIN SIMULATION
# ============================================================================

def run_multidomain_simulation(days: int = 90, daily_attempts_per_domain: int = 20):
    """
    Run multi-domain evolutionary simulation with void architecture
    """
    print("🌌 Slime Mold Multi-Domain Evolutionary Simulation v0.2.0")
    print(f"Days: {days}, Daily attempts per domain: {daily_attempts_per_domain}")
    print(f"Domains: {len(DOMAINS)} + 1 VOID")
    print()

    # Initialize variants for each domain
    all_variants: Dict[str, List[MultiDomainVariant]] = {}

    for domain_id, domain in DOMAINS.items():
        baseline = MultiDomainVariant(
            variant_id=f"VAR-{domain_id[:4]}-baseline",
            domain_id=domain_id,
            generation=0,
            threshold=domain.default_threshold,
            timing_hours=domain.default_timing_hours,
            channel_mix=domain.default_channel_mix.copy(),
            deployment_mode='production'
        )
        all_variants[domain_id] = [baseline]

    # Initialize void architecture
    void = VoidArchitecture(void_id="VOID-001")

    # Simulation loop
    generation = 0

    for day in range(1, days + 1):
        # Track domain performance for void
        domain_daily_nutrients = defaultdict(float)

        # Simulate outcomes for each domain
        for domain_id, domain in DOMAINS.items():
            variants = all_variants[domain_id]

            for variant in variants:
                if variant.survival_status != 'active' and variant.deployment_mode != 'production':
                    continue

                # Run multiple attempts per day
                for _ in range(daily_attempts_per_domain):
                    outcome = simulate_outcome(variant, domain, day)
                    variant.nutrient_samples.append(outcome['nutrient'])
                    variant.sample_size += 1
                    domain_daily_nutrients[domain_id] += outcome['nutrient']

        # Void architecture observes and adapts
        if day % 7 == 0:  # Weekly adaptation check
            void.observe_and_adapt(domain_daily_nutrients, generation)
            if void.current_domain:
                print(f"Day {day}: 🌌 VOID adapted to {void.current_domain} "
                      f"(nutrient signal: ${domain_daily_nutrients[void.current_domain]:.2f})")

        # Evolutionary cycle every 14 days
        if day % 14 == 0 and day >= 14:
            generation += 1
            print(f"\n🧬 GENERATION {generation} (Day {day})")
            print("="*80)

            # Compute fitness scores
            for domain_id in all_variants:
                for variant in all_variants[domain_id]:
                    variant.compute_fitness()

            # Find global top performers across ALL domains
            all_active_variants = []
            for domain_variants in all_variants.values():
                all_active_variants.extend([v for v in domain_variants
                                           if v.survival_status == 'active'
                                           and v.sample_size >= 20])

            all_active_variants.sort(key=lambda v: v.fitness_score, reverse=True)
            global_top_5 = all_active_variants[:5]

            print(f"\n🏆 GLOBAL TOP 5 PERFORMERS:")
            for i, v in enumerate(global_top_5, 1):
                domain_name = DOMAINS[v.domain_id].domain_name.split('(')[0].strip()
                print(f"  {i}. {v.variant_id}: {domain_name}")
                print(f"     Fitness: {v.fitness_score:.4f}, Samples: {v.sample_size}")

            # Per-domain evolution
            for domain_id, domain in DOMAINS.items():
                variants = all_variants[domain_id]
                active_variants = [v for v in variants
                                  if v.survival_status == 'active'
                                  and v.sample_size >= 20]

                if not active_variants:
                    continue

                active_variants.sort(key=lambda v: v.fitness_score, reverse=True)

                print(f"\n  📊 {domain.domain_name}")
                print(f"     Active variants: {len(active_variants)}")

                # Top performer in this domain
                if active_variants:
                    top = active_variants[0]
                    print(f"     Top: {top.variant_id} (fitness: {top.fitness_score:.4f})")

                # Prune bottom 20%
                if len(active_variants) >= 5:
                    bottom_20_pct = max(1, len(active_variants) // 5)
                    for variant in active_variants[-bottom_20_pct:]:
                        if variant.deployment_mode != 'production':
                            variant.survival_status = 'pruned'
                            print(f"     ❌ Pruned {variant.variant_id}")

                # Breed new variants
                if len(active_variants) < 8:
                    # Intra-domain mutation (60%)
                    if random.random() < 0.6 and active_variants:
                        parent = active_variants[0]
                        offspring = mutate_variant(parent, generation)
                        variants.append(offspring)
                        print(f"     🧬 Bred {offspring.variant_id} via mutation")

                    # Cross-domain breeding (40%) - KEY INNOVATION
                    elif len(global_top_5) >= 2:
                        parent1, parent2 = random.sample(global_top_5, 2)
                        offspring = crossover_domains(parent1, parent2, domain_id, generation)
                        variants.append(offspring)
                        print(f"     🌐 Cross-domain breed: {offspring.variant_id}")
                        print(f"        Parents: {parent1.domain_id} × {parent2.domain_id}")

                # Check for promotions
                production_variant = next((v for v in variants
                                          if v.deployment_mode == 'production'), None)

                if production_variant and active_variants:
                    best_shadow = active_variants[0]
                    if (best_shadow.variant_id != production_variant.variant_id
                        and best_shadow.sample_size >= 40
                        and best_shadow.fitness_score > production_variant.fitness_score * 1.15):

                        print(f"     ⭐ PROMOTING {best_shadow.variant_id} to production!")
                        print(f"        Old: {production_variant.fitness_score:.4f}")
                        print(f"        New: {best_shadow.fitness_score:.4f}")
                        print(f"        Lift: {((best_shadow.fitness_score / production_variant.fitness_score - 1) * 100):.1f}%")

                        production_variant.deployment_mode = 'shadow'
                        best_shadow.deployment_mode = 'production'
                        best_shadow.survival_status = 'promoted'

            print()

    # Final report
    print("\n" + "="*80)
    print("MULTI-DOMAIN SIMULATION COMPLETE")
    print("="*80)

    # Domain-level summary
    print("\n📊 DOMAIN PERFORMANCE SUMMARY:")
    print()

    domain_results = []

    for domain_id, domain in DOMAINS.items():
        variants = all_variants[domain_id]
        production = next((v for v in variants if v.deployment_mode == 'production'), None)
        baseline = next((v for v in variants if 'baseline' in v.variant_id), None)

        total_nutrient = sum(sum(v.nutrient_samples) for v in variants)
        total_attempts = sum(v.sample_size for v in variants)
        avg_nutrient = total_nutrient / total_attempts if total_attempts > 0 else 0

        improvement = 0.0
        if baseline and production and baseline.variant_id != production.variant_id:
            improvement = ((production.fitness_score / baseline.fitness_score - 1) * 100)

        domain_results.append({
            'domain': domain.domain_name.split('(')[0].strip(),
            'total_nutrient': total_nutrient,
            'avg_nutrient': avg_nutrient,
            'variants_created': len(variants),
            'improvement': improvement
        })

        print(f"{domain.domain_name}")
        print(f"  Total Nutrient: ${total_nutrient:,.2f}")
        print(f"  Avg Nutrient: ${avg_nutrient:.2f}/attempt")
        print(f"  Variants Created: {len(variants)}")
        if improvement > 0:
            print(f"  Evolutionary Improvement: {improvement:.1f}%")
        print()

    # Sort by total nutrient
    domain_results.sort(key=lambda x: x['total_nutrient'], reverse=True)

    print("\n🏆 DOMAIN RANKING BY TOTAL NUTRIENT:")
    for i, result in enumerate(domain_results, 1):
        print(f"{i}. {result['domain']}: ${result['total_nutrient']:,.2f}")
        if result['improvement'] > 0:
            print(f"   Evolution improved this domain by {result['improvement']:.1f}%")

    # Void architecture report
    print(f"\n🌌 VOID ARCHITECTURE REPORT:")
    print(f"  Total Adaptations: {len(void.adaptations)}")
    if void.adaptations:
        print(f"  Adaptation History:")
        for adaptation in void.adaptations[-5:]:  # Last 5
            print(f"    Gen {adaptation['generation']}: "
                  f"{adaptation['from_domain'] or 'null'} → {adaptation['to_domain']} "
                  f"(signal: ${adaptation['nutrient_signal']:.2f})")

    # Cross-domain learning insights
    print(f"\n🌐 CROSS-DOMAIN LEARNING INSIGHTS:")
    cross_domain_variants = []
    for domain_id, variants in all_variants.items():
        for v in variants:
            if len(v.parent_ids) == 2:  # Crossover
                cross_domain_variants.append(v)

    print(f"  Total cross-domain variants created: {len(cross_domain_variants)}")
    if cross_domain_variants:
        avg_fitness = statistics.mean(v.fitness_score for v in cross_domain_variants if v.fitness_score > 0)
        print(f"  Average fitness of cross-domain variants: {avg_fitness:.4f}")


# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    random.seed(42)  # Reproducible results
    run_multidomain_simulation(days=90, daily_attempts_per_domain=20)
