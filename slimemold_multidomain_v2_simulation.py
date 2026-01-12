#!/usr/bin/env python3
"""
Slime Mold Organism - Multi-Domain Simulation v0.2.1
NEW DOMAINS: Different revenue models and business mechanics

DOMAINS EXPLORED:
1. Technical Consulting (hourly billing, high-touch)
2. Product Development (fixed-price projects, milestone-based)
3. Training/Workshops (one-time events, cohort-based)
4. Maintenance Contracts (recurring MRR, retention-focused)
5. API/Platform (usage-based, scale-focused)
6. Digital Products (one-time purchase, low-touch)
7. VOID (Adaptive architecture - to be refined with Genesis OS)

PURPOSE:
- Test organism across different revenue mechanics
- Identify which business models have best unit economics
- Validate void architecture adaptation across diverse domains
- Generate insights for refining evolutionary architecture

Run:
  python3 slimemold_multidomain_v2_simulation.py
"""

import random
import statistics
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from collections import defaultdict
import json


# ============================================================================
# NEW DOMAIN DEFINITIONS (Different Revenue Models)
# ============================================================================

@dataclass
class DomainConfig:
    """Configuration for a business domain"""
    domain_id: str
    domain_name: str
    revenue_model: str  # NEW: hourly, fixed, recurring, usage, one_time

    # Economics
    base_conversion_rate: float
    base_revenue_per_conversion: float
    base_cost_per_attempt: float

    # Characteristics
    volatility: float  # Outcome variance
    time_to_close_days: float  # Sales cycle length
    customer_lifetime_months: float  # Retention period

    # Risks
    compliance_risk: float
    reputation_risk: float
    churn_risk: float  # NEW: Monthly churn probability

    # Evolvable parameters
    default_threshold: float
    default_timing_hours: float
    default_channel_mix: List[str]
    default_touch_intensity: float  # 0-1: How much effort per lead


# Define 6 diverse business domains
DOMAINS = {
    "technical_consulting": DomainConfig(
        domain_id="technical_consulting",
        domain_name="Technical Consulting (Hourly Billing)",
        revenue_model="hourly",
        base_conversion_rate=0.35,  # 35% of leads convert to calls
        base_revenue_per_conversion=4800.0,  # $150/hr × 32 hrs avg project
        base_cost_per_attempt=25.0,  # High-touch sales
        volatility=0.35,
        time_to_close_days=14.0,
        customer_lifetime_months=6.0,  # Project-based, limited repeat
        compliance_risk=0.0002,
        reputation_risk=0.02,
        churn_risk=0.0,  # Not subscription
        default_threshold=2000.0,  # Min project size
        default_timing_hours=24.0,  # Fast response
        default_channel_mix=['email', 'call', 'video'],
        default_touch_intensity=0.8  # High touch
    ),

    "product_development": DomainConfig(
        domain_id="product_development",
        domain_name="Product Development (Fixed-Price Projects)",
        revenue_model="fixed",
        base_conversion_rate=0.15,  # 15% of leads convert (competitive)
        base_revenue_per_conversion=25000.0,  # $25K average project
        base_cost_per_attempt=50.0,  # Very high-touch sales
        volatility=0.5,  # Project scope creep
        time_to_close_days=45.0,  # Long sales cycle
        customer_lifetime_months=12.0,  # Annual projects
        compliance_risk=0.0001,
        reputation_risk=0.03,  # Delivery risk
        churn_risk=0.0,
        default_threshold=15000.0,  # Min project size
        default_timing_hours=72.0,  # Thoughtful proposals
        default_channel_mix=['email', 'video', 'in_person'],
        default_touch_intensity=0.9  # Very high touch
    ),

    "training_workshops": DomainConfig(
        domain_id="training_workshops",
        domain_name="Training/Workshops (Cohort Events)",
        revenue_model="one_time",
        base_conversion_rate=0.08,  # 8% sign up for workshops
        base_revenue_per_conversion=1500.0,  # $1500 per seat
        base_cost_per_attempt=8.0,  # Marketing + outreach
        volatility=0.6,  # Attendance volatility
        time_to_close_days=21.0,  # Need time to schedule
        customer_lifetime_months=3.0,  # Repeat workshops
        compliance_risk=0.0001,
        reputation_risk=0.02,  # Content quality risk
        churn_risk=0.0,
        default_threshold=0.0,  # All leads welcome
        default_timing_hours=168.0,  # 1 week notice
        default_channel_mix=['email', 'webinar', 'social'],
        default_touch_intensity=0.5  # Medium touch
    ),

    "maintenance_contracts": DomainConfig(
        domain_id="maintenance_contracts",
        domain_name="Maintenance Contracts (Recurring MRR)",
        revenue_model="recurring",
        base_conversion_rate=0.25,  # 25% convert to contracts
        base_revenue_per_conversion=800.0,  # $800/month contract
        base_cost_per_attempt=15.0,
        volatility=0.2,  # Stable recurring
        time_to_close_days=30.0,
        customer_lifetime_months=24.0,  # 2-year avg retention
        compliance_risk=0.0003,  # SLA compliance
        reputation_risk=0.015,
        churn_risk=0.05,  # 5% monthly churn
        default_threshold=500.0,  # Min contract value
        default_timing_hours=48.0,
        default_channel_mix=['email', 'call'],
        default_touch_intensity=0.7  # High touch initially
    ),

    "api_platform": DomainConfig(
        domain_id="api_platform",
        domain_name="API/Platform (Usage-Based Pricing)",
        revenue_model="usage",
        base_conversion_rate=0.40,  # 40% sign up (freemium)
        base_revenue_per_conversion=350.0,  # Avg monthly usage
        base_cost_per_attempt=2.0,  # Low-touch sales
        volatility=0.7,  # Usage highly variable
        time_to_close_days=3.0,  # Fast signup
        customer_lifetime_months=18.0,
        compliance_risk=0.001,  # API abuse risk
        reputation_risk=0.01,
        churn_risk=0.08,  # 8% monthly churn
        default_threshold=0.0,  # No minimum
        default_timing_hours=4.0,  # Very fast response
        default_channel_mix=['email', 'docs', 'slack'],
        default_touch_intensity=0.3  # Low touch
    ),

    "digital_products": DomainConfig(
        domain_id="digital_products",
        domain_name="Digital Products (One-Time Purchase)",
        revenue_model="one_time",
        base_conversion_rate=0.05,  # 5% purchase (high volume needed)
        base_revenue_per_conversion=299.0,  # $299 product
        base_cost_per_attempt=1.5,  # Ads + marketing
        volatility=0.4,
        time_to_close_days=1.0,  # Instant purchase
        customer_lifetime_months=1.0,  # One-time (upsells separate)
        compliance_risk=0.0002,
        reputation_risk=0.02,  # Product quality
        churn_risk=0.0,
        default_threshold=0.0,
        default_timing_hours=0.5,  # Automated follow-up
        default_channel_mix=['email', 'retarget', 'social'],
        default_touch_intensity=0.2  # Very low touch
    ),
}


# ============================================================================
# VOID ARCHITECTURE V2 (Enhanced for Genesis Integration)
# ============================================================================

@dataclass
class VoidArchitectureV2:
    """
    Enhanced Void Architecture - Stem Cell Business Strategy

    NEW FEATURES:
    - Revenue model adaptation (learns which model type works best)
    - Multi-metric optimization (not just nutrient)
    - Pattern extraction (what makes winners win?)
    - Rapid cloning with domain-specific tuning
    """
    void_id: str
    current_domain: Optional[str] = None
    cloned_from: Optional[str] = None
    adaptation_speed: float = 0.3

    # Multi-metric tracking
    total_nutrient: float = 0.0
    total_revenue: float = 0.0
    total_cost: float = 0.0
    best_revenue_model: Optional[str] = None

    # Adaptation history
    adaptations: List[Dict] = field(default_factory=list)

    # Pattern extraction
    learned_patterns: Dict[str, any] = field(default_factory=dict)

    def observe_and_adapt(self, domain_metrics: Dict[str, Dict], generation: int):
        """
        Enhanced adaptation logic

        domain_metrics structure:
        {
            'domain_id': {
                'nutrient': float,
                'revenue': float,
                'conversion_rate': float,
                'revenue_model': str,
                ...
            }
        }
        """
        if not domain_metrics:
            return

        # Multi-objective scoring
        scores = {}
        for domain_id, metrics in domain_metrics.items():
            # Score = weighted combination of metrics
            score = (
                metrics.get('nutrient', 0) * 1.0 +
                metrics.get('revenue', 0) * 0.3 +
                (metrics.get('conversion_rate', 0) * 10000) * 0.2  # Scale up conversion
            )
            scores[domain_id] = {
                'score': score,
                'metrics': metrics
            }

        # Find best domain
        best_domain_id = max(scores.items(), key=lambda x: x[1]['score'])[0]
        best_score = scores[best_domain_id]['score']
        best_metrics = scores[best_domain_id]['metrics']

        # Adapt with probability based on score improvement
        should_adapt = False
        if self.current_domain is None:
            should_adapt = True
        elif best_score > scores.get(self.current_domain, {'score': 0})['score'] * 1.2:
            # Switch if new domain is 20%+ better
            should_adapt = True
        elif random.random() < self.adaptation_speed:
            # Or randomly explore
            should_adapt = True

        if should_adapt and best_score > 0:
            old_domain = self.current_domain
            self.current_domain = best_domain_id
            self.cloned_from = best_domain_id
            self.best_revenue_model = best_metrics.get('revenue_model')

            # Extract patterns from winner
            self.learned_patterns[best_domain_id] = {
                'revenue_model': best_metrics.get('revenue_model'),
                'avg_conversion': best_metrics.get('conversion_rate'),
                'avg_revenue': best_metrics.get('revenue'),
                'success_factors': self._extract_success_factors(best_metrics)
            }

            self.adaptations.append({
                'generation': generation,
                'from_domain': old_domain,
                'to_domain': best_domain_id,
                'score': best_score,
                'revenue_model': best_metrics.get('revenue_model'),
                'reason': 'score_improvement' if old_domain else 'initial_adaptation'
            })

    def _extract_success_factors(self, metrics: Dict) -> Dict:
        """Extract what makes this domain successful"""
        factors = {}

        # High conversion rate
        if metrics.get('conversion_rate', 0) > 0.2:
            factors['high_conversion'] = True

        # High revenue per conversion
        if metrics.get('revenue', 0) / max(metrics.get('attempts', 1), 1) > 1000:
            factors['high_revenue_per_conversion'] = True

        # Low cost efficiency
        if metrics.get('cost', 0) / max(metrics.get('revenue', 1), 1) < 0.3:
            factors['low_cost_ratio'] = True

        # Stable (low volatility)
        if metrics.get('volatility', 1.0) < 0.3:
            factors['stable_outcomes'] = True

        return factors

    def get_active_domain_config(self) -> Optional[DomainConfig]:
        """Get current domain configuration"""
        if self.current_domain and self.current_domain in DOMAINS:
            return DOMAINS[self.current_domain]
        return None


# ============================================================================
# VARIANT & SIMULATION (Same as before but with new domains)
# ============================================================================

@dataclass
class MultiDomainVariant:
    """Cognitive architecture variant for a domain"""
    variant_id: str
    domain_id: str
    generation: int
    parent_ids: List[str] = field(default_factory=list)

    # Genotype
    threshold: float = 0.0
    timing_hours: float = 24.0
    channel_mix: List[str] = field(default_factory=list)
    touch_intensity: float = 0.5  # How much effort per lead

    # Performance
    sample_size: int = 0
    nutrient_samples: List[float] = field(default_factory=list)
    revenue_samples: List[float] = field(default_factory=list)
    fitness_score: float = 0.0
    deployment_mode: str = 'shadow'
    survival_status: str = 'active'

    def compute_fitness(self):
        if len(self.nutrient_samples) < 2:
            self.fitness_score = 0.0
            return
        mean = statistics.mean(self.nutrient_samples)
        stddev = statistics.stdev(self.nutrient_samples)
        self.fitness_score = mean / (1 + stddev)


def simulate_outcome(variant: MultiDomainVariant, domain: DomainConfig, day: int) -> Dict:
    """Simulate outcome with new domain mechanics"""
    base_conversion = domain.base_conversion_rate
    base_revenue = domain.base_revenue_per_conversion
    base_cost = domain.base_cost_per_attempt

    # Variant modifiers
    conversion_multiplier = 1.0
    cost_multiplier = 1.0
    penalty = 0.0

    # Threshold effect (tighter threshold = fewer attempts but higher quality)
    if domain.default_threshold > 0:
        threshold_ratio = variant.threshold / domain.default_threshold
        if threshold_ratio > 1.3:  # Very selective
            conversion_multiplier *= 1.15
            cost_multiplier *= 0.7  # Fewer wasted attempts
        elif threshold_ratio < 0.7:  # Very broad
            conversion_multiplier *= 0.9
            cost_multiplier *= 1.3

    # Timing effect
    timing_ratio = variant.timing_hours / domain.default_timing_hours
    if timing_ratio < 0.5:  # Very fast
        conversion_multiplier *= 1.1
        cost_multiplier *= 1.2
    elif timing_ratio > 1.5:  # Very slow
        conversion_multiplier *= 0.85

    # Touch intensity effect
    intensity_ratio = variant.touch_intensity / domain.default_touch_intensity
    conversion_multiplier *= (0.9 + 0.2 * intensity_ratio)  # More touch = better conversion
    cost_multiplier *= (0.8 + 0.4 * intensity_ratio)  # But costs more

    # Revenue model specific adjustments
    if domain.revenue_model == 'recurring':
        # MRR compounds over customer lifetime
        lifetime_multiplier = domain.customer_lifetime_months / 12.0
        base_revenue *= lifetime_multiplier

        # Apply churn risk
        if random.random() < domain.churn_risk:
            base_revenue *= 0.5  # Churned early

    elif domain.revenue_model == 'usage':
        # Usage is volatile
        usage_factor = random.uniform(0.3, 2.0)
        base_revenue *= usage_factor

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


def crossover_domains(parent1: MultiDomainVariant, parent2: MultiDomainVariant,
                     target_domain: str, generation: int) -> MultiDomainVariant:
    """Cross-domain breeding"""
    offspring = MultiDomainVariant(
        variant_id=f"VAR-{target_domain[:4]}-genX{generation}-{random.randint(1000, 9999)}",
        domain_id=target_domain,
        generation=generation,
        parent_ids=[parent1.variant_id, parent2.variant_id],
        threshold=random.choice([parent1.threshold, parent2.threshold]),
        timing_hours=random.choice([parent1.timing_hours, parent2.timing_hours]),
        touch_intensity=(parent1.touch_intensity + parent2.touch_intensity) / 2,
        channel_mix=random.choice([parent1.channel_mix, parent2.channel_mix]).copy()
    )
    return offspring


# ============================================================================
# SIMULATION
# ============================================================================

def run_multidomain_simulation_v2(days: int = 90, daily_attempts_per_domain: int = 15):
    """Run enhanced multi-domain simulation"""
    print("🌌 Slime Mold Multi-Domain Simulation v0.2.1 - NEW DOMAINS")
    print(f"Days: {days}, Daily attempts per domain: {daily_attempts_per_domain}")
    print(f"Domains: {len(DOMAINS)} + 1 VOID (Enhanced)")
    print()

    # Initialize variants
    all_variants: Dict[str, List[MultiDomainVariant]] = {}

    for domain_id, domain in DOMAINS.items():
        baseline = MultiDomainVariant(
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

    # Initialize enhanced void
    void = VoidArchitectureV2(void_id="VOID-002-Enhanced")

    generation = 0

    for day in range(1, days + 1):
        # Track metrics for void
        domain_daily_metrics = {}

        # Simulate each domain
        for domain_id, domain in DOMAINS.items():
            variants = all_variants[domain_id]

            domain_nutrient = 0.0
            domain_revenue = 0.0
            domain_cost = 0.0
            domain_conversions = 0
            domain_attempts = 0

            for variant in variants:
                if variant.survival_status != 'active' and variant.deployment_mode != 'production':
                    continue

                for _ in range(daily_attempts_per_domain):
                    outcome = simulate_outcome(variant, domain, day)
                    variant.nutrient_samples.append(outcome['nutrient'])
                    variant.revenue_samples.append(outcome['revenue'])
                    variant.sample_size += 1

                    domain_nutrient += outcome['nutrient']
                    domain_revenue += outcome['revenue']
                    domain_cost += outcome['cost']
                    if outcome['converted']:
                        domain_conversions += 1
                    domain_attempts += 1

            # Store metrics for void
            domain_daily_metrics[domain_id] = {
                'nutrient': domain_nutrient,
                'revenue': domain_revenue,
                'cost': domain_cost,
                'conversion_rate': domain_conversions / max(domain_attempts, 1),
                'revenue_model': domain.revenue_model,
                'attempts': domain_attempts,
                'volatility': domain.volatility
            }

        # Void adaptation check every 7 days
        if day % 7 == 0:
            void.observe_and_adapt(domain_daily_metrics, generation)
            if void.adaptations and void.adaptations[-1]['generation'] == generation:
                latest = void.adaptations[-1]
                domain_name = DOMAINS[latest['to_domain']].domain_name.split('(')[0].strip()
                print(f"Day {day}: 🌌 VOID → {domain_name} "
                      f"(model: {latest['revenue_model']}, score: ${latest['score']:.0f})")

        # Evolution every 14 days
        if day % 14 == 0 and day >= 14:
            generation += 1
            print(f"\n🧬 GENERATION {generation} (Day {day})")
            print("="*80)

            # Compute fitness
            for domain_variants in all_variants.values():
                for variant in domain_variants:
                    variant.compute_fitness()

            # Global top performers
            all_active = []
            for domain_variants in all_variants.values():
                all_active.extend([v for v in domain_variants
                                  if v.survival_status == 'active' and v.sample_size >= 15])

            all_active.sort(key=lambda v: v.fitness_score, reverse=True)
            global_top_5 = all_active[:5]

            print(f"\n🏆 GLOBAL TOP 5:")
            for i, v in enumerate(global_top_5, 1):
                domain_name = DOMAINS[v.domain_id].domain_name.split('(')[0].strip()
                revenue_model = DOMAINS[v.domain_id].revenue_model
                print(f"  {i}. {domain_name} ({revenue_model}): fitness={v.fitness_score:.4f}")

            # Per-domain evolution (abbreviated for console)
            for domain_id, domain in DOMAINS.items():
                variants = all_variants[domain_id]
                active = [v for v in variants if v.survival_status == 'active' and v.sample_size >= 15]

                if not active:
                    continue

                active.sort(key=lambda v: v.fitness_score, reverse=True)

                # Prune bottom 20% if population >= 5
                if len(active) >= 5:
                    prune_count = max(1, len(active) // 5)
                    for variant in active[-prune_count:]:
                        if variant.deployment_mode != 'production':
                            variant.survival_status = 'pruned'

                # Breed if room
                if len(active) < 6:
                    if random.random() < 0.5 and active:
                        offspring = mutate_variant(active[0], generation)
                        variants.append(offspring)
                    elif len(global_top_5) >= 2:
                        p1, p2 = random.sample(global_top_5, 2)
                        offspring = crossover_domains(p1, p2, domain_id, generation)
                        variants.append(offspring)

                # Check promotions
                production = next((v for v in variants if v.deployment_mode == 'production'), None)
                if production and active and active[0].variant_id != production.variant_id:
                    if active[0].sample_size >= 30 and active[0].fitness_score > production.fitness_score * 1.15:
                        production.deployment_mode = 'shadow'
                        active[0].deployment_mode = 'production'
                        active[0].survival_status = 'promoted'

            print()

    # Final report
    print("\n" + "="*80)
    print("SIMULATION COMPLETE - NEW DOMAINS ANALYSIS")
    print("="*80)

    print("\n📊 DOMAIN PERFORMANCE (Ranked by Total Nutrient):")
    print()

    results = []
    for domain_id, domain in DOMAINS.items():
        variants = all_variants[domain_id]
        total_nutrient = sum(sum(v.nutrient_samples) for v in variants)
        total_revenue = sum(sum(v.revenue_samples) for v in variants)
        total_attempts = sum(v.sample_size for v in variants)
        avg_nutrient = total_nutrient / max(total_attempts, 1)

        production = next((v for v in variants if v.deployment_mode == 'production'), None)
        baseline = next((v for v in variants if 'baseline' in v.variant_id), None)

        improvement = 0.0
        if baseline and production and baseline.variant_id != production.variant_id:
            improvement = ((production.fitness_score / baseline.fitness_score - 1) * 100)

        results.append({
            'domain': domain.domain_name,
            'revenue_model': domain.revenue_model,
            'total_nutrient': total_nutrient,
            'total_revenue': total_revenue,
            'avg_nutrient': avg_nutrient,
            'improvement': improvement
        })

    results.sort(key=lambda x: x['total_nutrient'], reverse=True)

    for i, r in enumerate(results, 1):
        print(f"{i}. {r['domain']}")
        print(f"   Model: {r['revenue_model']}")
        print(f"   Total Nutrient: ${r['total_nutrient']:,.0f}")
        print(f"   Avg Nutrient/Attempt: ${r['avg_nutrient']:.2f}")
        if r['improvement'] > 0:
            print(f"   Evolution Improvement: +{r['improvement']:.1f}%")
        print()

    # Void report
    print(f"🌌 VOID ARCHITECTURE ANALYSIS:")
    print(f"  Total Adaptations: {len(void.adaptations)}")
    if void.adaptations:
        print(f"  Final Domain: {void.current_domain}")
        print(f"  Best Revenue Model: {void.best_revenue_model}")
        print(f"\n  Adaptation History (last 5):")
        for adaptation in void.adaptations[-5:]:
            print(f"    Gen {adaptation['generation']}: {adaptation['from_domain'] or 'null'} → "
                  f"{adaptation['to_domain']} ({adaptation['revenue_model']}) "
                  f"[score: ${adaptation['score']:.0f}]")

    if void.learned_patterns:
        print(f"\n  Learned Success Patterns:")
        for domain_id, pattern in void.learned_patterns.items():
            print(f"    {domain_id}: {pattern['success_factors']}")


if __name__ == '__main__':
    random.seed(42)
    run_multidomain_simulation_v2(days=90, daily_attempts_per_domain=15)
