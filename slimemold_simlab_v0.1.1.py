#!/usr/bin/env python3
"""
slimemold_simlab.py
HIGGS SlimeMold Business Organism — Simulation Harness (v0.1.1)

Purpose:
- Validate nutrient function + pheromone reinforcement before any live execution.
- Simulate a B2B offer funnel as a Physarum-like stigmergic optimizer.

Run:
  python slimemold_simlab.py

Optional args:
  python slimemold_simlab.py --leads 3000 --days 30 --seed 7
"""
from __future__ import annotations

import argparse
import math
import os
import random
from dataclasses import dataclass
from typing import Dict, List, Tuple

import pandas as pd

STATES = ["awareness", "interest", "discovery", "starter", "professional", "enterprise"]
EDGES = [
    ("awareness", "interest"),
    ("interest", "discovery"),
    ("discovery", "starter"),
    ("starter", "professional"),
    ("professional", "enterprise"),
]

@dataclass
class SimParams:
    seed: int = 7
    leads: int = 3000
    days: int = 30

    # Funnel conversion probabilities (per transition)
    p_awareness_to_interest: float = 0.25
    p_interest_to_discovery: float = 0.18
    p_discovery_to_starter: float = 0.40
    p_starter_to_professional: float = 0.30
    p_professional_to_enterprise: float = 0.15

    # Prices
    price_discovery: float = 500.0
    price_starter: float = 2500.0
    price_professional: float = 7500.0
    price_enterprise: float = 25000.0

    # Costs
    cost_delivery_starter: float = 350.0   # labor/time proxy
    cost_delivery_professional: float = 900.0
    cost_delivery_enterprise: float = 2500.0
    compute_cost_per_lead: float = 0.02

    # Penalties (rare events)
    p_refund: float = 0.02
    p_reputation_hit: float = 0.01
    p_compliance_violation: float = 0.0001

    penalty_reputation_usd: float = 10000.0
    penalty_compliance_usd: float = 1_000_000.0

    # Pheromone dynamics (epoch-based)
    evaporation_rate: float = 0.03
    reinforce_alpha: float = 0.30
    min_weight: float = 0.05
    max_weight: float = 10.0

def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))

def normalize_nutrient(n: float, scale: float = 6000.0) -> float:
    # maps nutrient to ~[0,1]
    return 1 / (1 + math.exp(-n / scale))

def simulate_one_lead(params: SimParams, pher: Dict[Tuple[str,str], float]) -> dict:
    # Conversion map
    p_base = {
        ("awareness","interest"): params.p_awareness_to_interest,
        ("interest","discovery"): params.p_interest_to_discovery,
        ("discovery","starter"): params.p_discovery_to_starter,
        ("starter","professional"): params.p_starter_to_professional,
        ("professional","enterprise"): params.p_professional_to_enterprise,
    }

    current = "awareness"
    path = [current]
    compute_cost = params.compute_cost_per_lead
    revenue = 0.0
    direct_cost = 0.0
    penalty = 0.0

    for (a,b) in EDGES:
        if a != current:
            continue
        w = pher[(a,b)]
        effort = clamp(w, 0.2, 3.0)
        p_eff = clamp(p_base[(a,b)] * (0.80 + 0.20*effort), 0.0, 0.98)

        if random.random() <= p_eff:
            current = b
            path.append(current)
        else:
            break

    if current == "discovery":
        revenue += params.price_discovery
    elif current == "starter":
        revenue += params.price_starter
        direct_cost += params.cost_delivery_starter
    elif current == "professional":
        revenue += params.price_professional
        direct_cost += params.cost_delivery_professional
    elif current == "enterprise":
        revenue += params.price_enterprise
        direct_cost += params.cost_delivery_enterprise

    if revenue > 0 and random.random() < params.p_refund:
        penalty += revenue  # full refund

    if revenue > 0 and random.random() < params.p_reputation_hit:
        penalty += params.penalty_reputation_usd

    if random.random() < params.p_compliance_violation:
        penalty += params.penalty_compliance_usd

    nutrient = revenue - direct_cost - compute_cost - penalty

    return {
        "final_state": current,
        "path": "->".join(path),
        "path_edges": [(path[i], path[i+1]) for i in range(len(path)-1)],
        "revenue_usd": revenue,
        "direct_cost_usd": direct_cost,
        "compute_cost_usd": compute_cost,
        "penalty_usd": penalty,
        "nutrient": nutrient,
    }

def update_pheromones_epoch(pher: Dict[Tuple[str,str], float], edge_rewards: Dict[Tuple[str,str], float], params: SimParams) -> Dict[Tuple[str,str], float]:
    # Evaporate
    for e in list(pher.keys()):
        pher[e] = clamp(pher[e] * (1.0 - params.evaporation_rate), params.min_weight, params.max_weight)

    # Reinforce proportional to positive reward mass
    total = sum(max(0.0, r) for r in edge_rewards.values())
    if total <= 0:
        return pher

    for e, r in edge_rewards.items():
        if r <= 0:
            continue
        share = r / total
        pher[e] = clamp(pher[e] + params.reinforce_alpha * share * len(EDGES), params.min_weight, params.max_weight)

    return pher

def simulate(params: SimParams) -> Tuple[pd.DataFrame, pd.DataFrame, Dict[Tuple[str,str], float]]:
    random.seed(params.seed)

    pher: Dict[Tuple[str, str], float] = {e: 1.0 for e in EDGES}
    pher[("starter","professional")] = 0.5
    pher[("professional","enterprise")] = 0.3

    rows: List[dict] = []
    daily_rows: List[dict] = []

    leads_per_day = max(1, params.leads // params.days)

    for day in range(1, params.days + 1):
        edge_rewards: Dict[Tuple[str,str], float] = {e: 0.0 for e in EDGES}
        day_revenue = day_cost = day_penalty = day_nutrient = 0.0

        for _ in range(leads_per_day):
            r = simulate_one_lead(params, pher)
            n_norm = normalize_nutrient(r["nutrient"])
            # reward edges traversed weighted by nutrient (only positive contributes)
            for e in r["path_edges"]:
                edge_rewards[e] += max(0.0, n_norm)

            day_revenue += r["revenue_usd"]
            day_cost += (r["direct_cost_usd"] + r["compute_cost_usd"])
            day_penalty += r["penalty_usd"]
            day_nutrient += r["nutrient"]

            rows.append({k: v for k, v in r.items() if k not in ("path_edges",)})

        pher = update_pheromones_epoch(pher, edge_rewards, params)

        daily_rows.append({
            "day": day,
            "revenue_usd": day_revenue,
            "cost_usd": day_cost,
            "penalty_usd": day_penalty,
            "nutrient": day_nutrient,
            **{f"pher_{a}_{b}": pher[(a,b)] for (a,b) in EDGES}
        })

    df = pd.DataFrame(rows)
    df_daily = pd.DataFrame(daily_rows)
    return df, df_daily, pher

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--leads", type=int, default=3000)
    ap.add_argument("--days", type=int, default=30)
    ap.add_argument("--seed", type=int, default=7)
    args = ap.parse_args()

    params = SimParams(leads=args.leads, days=args.days, seed=args.seed)
    df, df_daily, pher = simulate(params)

    summary = df.groupby("final_state").agg(
        leads=("final_state","count"),
        revenue_usd=("revenue_usd","sum"),
        nutrient=("nutrient","sum"),
        avg_nutrient=("nutrient","mean")
    ).sort_values("leads", ascending=False)

    print("\n=== Funnel Outcome Summary ===")
    print(summary.to_string())

    print("\n=== Final Pheromone Weights (thickness) ===")
    for (a,b) in EDGES:
        print(f"{a} -> {b} : {pher[(a,b)]:.4f}")

    out_dir = os.path.dirname(os.path.abspath(__file__))
    df.to_csv(os.path.join(out_dir, "slimemold_sim_results.csv"), index=False)
    df_daily.to_csv(os.path.join(out_dir, "slimemold_sim_daily.csv"), index=False)
    summary.to_csv(os.path.join(out_dir, "slimemold_sim_summary.csv"))
    print(f"\nWrote: {out_dir}/slimemold_sim_results.csv, {out_dir}/slimemold_sim_daily.csv, {out_dir}/slimemold_sim_summary.csv")

if __name__ == "__main__":
    main()
