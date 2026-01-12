-- ============================================================================
-- Slime Mold Business Organism v0.1.2 - Evolutionary Cognitive Architecture
-- ============================================================================
--
-- PURPOSE: Extends v0.1.1 with evolutionary breeding of Cogni Map variants
--
-- KEY ADDITIONS:
-- - organism_cogni_map_library: Registry of all cogni maps (2169+ maps)
-- - organism_variant_lineage: Tracks generations, parents, mutations
-- - Enhanced tendrils table: Links to cogni_map_id, tracks genetic lineage
-- - Shadow mode deployment: Test variants before promoting to production
-- - Breeding functions: Crossover, mutation, selection pressure
--
-- EVOLUTIONARY LOOP:
-- 1. Identify top performers (nutrient > threshold)
-- 2. Breed new variants (crossover + mutation)
-- 3. Deploy offspring in shadow mode
-- 4. Track nutrient per variant
-- 5. Retire poor performers (bottom 20% after min sample size)
-- 6. Promote winners to production
--
-- ============================================================================

-- ============================================================================
-- 1. COGNI MAP LIBRARY (Pattern Genome)
-- ============================================================================

CREATE TABLE IF NOT EXISTS organism_cogni_map_library (
  id BIGSERIAL PRIMARY KEY,

  -- Identification
  map_id TEXT NOT NULL UNIQUE, -- e.g. "GM:invoice-chase-agent-mvp-v1.2.0-HIGGS"
  map_name TEXT NOT NULL,
  version TEXT NOT NULL,
  category TEXT, -- e.g. "revenue_operations", "customer_service", "marketing"

  -- Cogni Map Content
  map_json JSONB NOT NULL, -- Full cogni map structure
  map_hash TEXT NOT NULL, -- SHA-256 hash for deduplication

  -- Provenance
  source TEXT, -- "apple_notes", "manual_upload", "evolved"
  imported_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  created_by TEXT, -- user or "slime_mold_organism"

  -- Evolution Metadata
  is_variant BOOLEAN DEFAULT FALSE,
  parent_map_ids TEXT[], -- If evolved, which maps were parents
  generation INT DEFAULT 0, -- 0 = original, 1+ = evolved
  mutations JSONB, -- Record of what was changed

  -- Performance (aggregated from tendrils that use this map)
  total_deployments INT DEFAULT 0,
  avg_nutrient_usd NUMERIC(12,2),
  best_nutrient_usd NUMERIC(12,2),
  worst_nutrient_usd NUMERIC(12,2),

  -- Lifecycle
  status TEXT DEFAULT 'active', -- 'active', 'retired', 'shadow'
  retired_at TIMESTAMPTZ,
  retirement_reason TEXT,

  -- Indexes
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_cogni_map_library_map_id ON organism_cogni_map_library(map_id);
CREATE INDEX idx_cogni_map_library_category ON organism_cogni_map_library(category);
CREATE INDEX idx_cogni_map_library_status ON organism_cogni_map_library(status);
CREATE INDEX idx_cogni_map_library_generation ON organism_cogni_map_library(generation);
CREATE INDEX idx_cogni_map_library_parent_maps ON organism_cogni_map_library USING GIN(parent_map_ids);

COMMENT ON TABLE organism_cogni_map_library IS 'Registry of all cogni maps - the pattern genome for business operations';
COMMENT ON COLUMN organism_cogni_map_library.map_json IS 'Full cogni map JSON structure with nodes, edges, epistemic tags';
COMMENT ON COLUMN organism_cogni_map_library.mutations IS 'JSONB array of mutations applied: [{op: "adjust_threshold", path: "$.rules.high_value", old: 10000, new: 5000}]';


-- ============================================================================
-- 2. VARIANT LINEAGE (Evolution Tree)
-- ============================================================================

CREATE TABLE IF NOT EXISTS organism_variant_lineage (
  id BIGSERIAL PRIMARY KEY,

  -- Variant Identity
  variant_id TEXT NOT NULL, -- Unique ID for this variant instance
  cogni_map_id TEXT NOT NULL REFERENCES organism_cogni_map_library(map_id),
  tendril_key TEXT NOT NULL, -- Which tendril deployed this variant

  -- Genetics
  generation INT NOT NULL DEFAULT 0,
  parent_variant_ids TEXT[], -- Parent variant IDs (1-2 for crossover)
  parent_map_ids TEXT[], -- Parent cogni map IDs
  breeding_method TEXT, -- 'clone', 'mutation', 'crossover', 'novel'
  mutations JSONB, -- Specific mutations in this variant

  -- Deployment
  deployed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  deployment_mode TEXT NOT NULL DEFAULT 'shadow', -- 'shadow', 'canary', 'production'
  promoted_at TIMESTAMPTZ, -- When promoted from shadow to production
  retired_at TIMESTAMPTZ,

  -- Performance Metrics
  sample_size INT DEFAULT 0, -- Number of outcomes observed
  lifetime_nutrient_usd NUMERIC(12,2) DEFAULT 0,
  lifetime_revenue_usd NUMERIC(12,2) DEFAULT 0,
  lifetime_cost_usd NUMERIC(12,2) DEFAULT 0,
  lifetime_penalty_usd NUMERIC(12,2) DEFAULT 0,

  -- Statistical Confidence
  nutrient_mean NUMERIC(12,2),
  nutrient_stddev NUMERIC(12,2),
  confidence_level NUMERIC(5,2), -- 0-100

  -- Selection Pressure
  fitness_score NUMERIC(12,4), -- Computed: nutrient_mean / (1 + nutrient_stddev)
  survival_status TEXT DEFAULT 'active', -- 'active', 'promoted', 'retired', 'pruned'
  pruned_reason TEXT,

  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_variant_lineage_variant_id ON organism_variant_lineage(variant_id);
CREATE INDEX idx_variant_lineage_cogni_map_id ON organism_variant_lineage(cogni_map_id);
CREATE INDEX idx_variant_lineage_tendril_key ON organism_variant_lineage(tendril_key);
CREATE INDEX idx_variant_lineage_generation ON organism_variant_lineage(generation);
CREATE INDEX idx_variant_lineage_survival_status ON organism_variant_lineage(survival_status);
CREATE INDEX idx_variant_lineage_fitness_score ON organism_variant_lineage(fitness_score DESC);

COMMENT ON TABLE organism_variant_lineage IS 'Tracks evolutionary lineage of cogni map variants - the family tree';
COMMENT ON COLUMN organism_variant_lineage.fitness_score IS 'Mean nutrient divided by (1 + stddev) - rewards consistent high performers';
COMMENT ON COLUMN organism_variant_lineage.deployment_mode IS 'shadow = testing, canary = partial rollout, production = full deployment';


-- ============================================================================
-- 3. ENHANCED TENDRILS TABLE (Add Cognitive Architecture Columns)
-- ============================================================================

-- Add new columns to existing tendrils table
ALTER TABLE tendrils ADD COLUMN IF NOT EXISTS cogni_map_id TEXT REFERENCES organism_cogni_map_library(map_id);
ALTER TABLE tendrils ADD COLUMN IF NOT EXISTS current_variant_id TEXT;
ALTER TABLE tendrils ADD COLUMN IF NOT EXISTS parent_map_ids TEXT[];
ALTER TABLE tendrils ADD COLUMN IF NOT EXISTS mutations JSONB;
ALTER TABLE tendrils ADD COLUMN IF NOT EXISTS generation INT DEFAULT 0;
ALTER TABLE tendrils ADD COLUMN IF NOT EXISTS evolutionary_mode BOOLEAN DEFAULT FALSE;

CREATE INDEX IF NOT EXISTS idx_tendrils_cogni_map_id ON tendrils(cogni_map_id);
CREATE INDEX IF NOT EXISTS idx_tendrils_evolutionary_mode ON tendrils(evolutionary_mode) WHERE evolutionary_mode = TRUE;

COMMENT ON COLUMN tendrils.cogni_map_id IS 'Which cogni map defines this tendrils business logic';
COMMENT ON COLUMN tendrils.current_variant_id IS 'Currently deployed variant (if in evolutionary mode)';
COMMENT ON COLUMN tendrils.evolutionary_mode IS 'TRUE = organism actively breeds variants for this tendril';


-- ============================================================================
-- 4. SHADOW MODE DEPLOYMENT TRACKING
-- ============================================================================

CREATE TABLE IF NOT EXISTS organism_shadow_deployments (
  id BIGSERIAL PRIMARY KEY,

  -- Deployment Identity
  deployment_id TEXT NOT NULL UNIQUE,
  variant_id TEXT NOT NULL,
  cogni_map_id TEXT NOT NULL REFERENCES organism_cogni_map_library(map_id),
  tendril_key TEXT NOT NULL,

  -- Shadow Configuration
  shadow_mode TEXT NOT NULL DEFAULT 'observe', -- 'observe', 'dry_run', 'percentage_rollout'
  traffic_percentage NUMERIC(5,2), -- If percentage_rollout, what % gets this variant

  -- Experimental Design
  control_variant_id TEXT, -- Baseline variant for comparison
  hypothesis TEXT, -- What we're testing
  success_criteria JSONB, -- {"min_sample_size": 100, "min_nutrient_improvement": 500}

  -- Execution Window
  started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  planned_end_at TIMESTAMPTZ,
  actual_end_at TIMESTAMPTZ,

  -- Results
  sample_size INT DEFAULT 0,
  nutrient_observed NUMERIC(12,2) DEFAULT 0,
  control_nutrient NUMERIC(12,2), -- Nutrient of control during same period
  lift_vs_control NUMERIC(12,2), -- Percentage improvement

  -- Decision
  conclusion TEXT, -- 'promote', 'iterate', 'retire', 'inconclusive'
  decided_at TIMESTAMPTZ,
  decided_by TEXT, -- 'organism_auto', 'human_override'
  decision_notes TEXT,

  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_shadow_deployments_deployment_id ON organism_shadow_deployments(deployment_id);
CREATE INDEX idx_shadow_deployments_variant_id ON organism_shadow_deployments(variant_id);
CREATE INDEX idx_shadow_deployments_tendril_key ON organism_shadow_deployments(tendril_key);
CREATE INDEX idx_shadow_deployments_started_at ON organism_shadow_deployments(started_at);

COMMENT ON TABLE organism_shadow_deployments IS 'Tracks A/B experiments and shadow mode testing of variants';


-- ============================================================================
-- 5. BREEDING CONFIGURATION
-- ============================================================================

CREATE TABLE IF NOT EXISTS organism_breeding_config (
  id BIGSERIAL PRIMARY KEY,
  tenant_id TEXT NOT NULL DEFAULT 'default',

  -- Selection Pressure
  min_sample_size_for_selection INT DEFAULT 100, -- Need 100+ outcomes before evaluating
  top_performer_percentile NUMERIC(5,2) DEFAULT 20.0, -- Top 20% are candidates for breeding
  prune_percentile NUMERIC(5,2) DEFAULT 20.0, -- Bottom 20% get pruned

  -- Breeding Rates
  mutation_rate NUMERIC(5,2) DEFAULT 15.0, -- 15% chance of mutation per breeding
  crossover_rate NUMERIC(5,2) DEFAULT 60.0, -- 60% chance of crossover breeding
  novel_variant_rate NUMERIC(5,2) DEFAULT 5.0, -- 5% chance of completely novel variant

  -- Population Control
  max_variants_per_tendril INT DEFAULT 10, -- Max concurrent variants per tendril
  max_generations INT DEFAULT 50, -- Stop evolving after 50 generations

  -- Promotion Thresholds
  promotion_confidence_threshold NUMERIC(5,2) DEFAULT 95.0, -- 95% confidence required
  promotion_min_lift_pct NUMERIC(5,2) DEFAULT 10.0, -- Must be 10%+ better than control

  -- Mutation Parameters
  mutation_ops JSONB DEFAULT '["adjust_threshold", "change_timing", "swap_channel", "adjust_priority"]'::jsonb,
  mutation_magnitude_pct NUMERIC(5,2) DEFAULT 20.0, -- Mutations adjust by ±20%

  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Insert default config
INSERT INTO organism_breeding_config (tenant_id) VALUES ('default')
ON CONFLICT DO NOTHING;

COMMENT ON TABLE organism_breeding_config IS 'Configuration parameters for evolutionary breeding algorithm';


-- ============================================================================
-- 6. HELPER FUNCTIONS
-- ============================================================================

-- Function: Compute fitness score for a variant
CREATE OR REPLACE FUNCTION compute_variant_fitness(
  p_variant_id TEXT
) RETURNS NUMERIC AS $$
DECLARE
  v_nutrient_mean NUMERIC;
  v_nutrient_stddev NUMERIC;
  v_fitness NUMERIC;
BEGIN
  SELECT
    AVG(nutrient_usd),
    STDDEV(nutrient_usd)
  INTO v_nutrient_mean, v_nutrient_stddev
  FROM organism_events
  WHERE meta_json->>'variant_id' = p_variant_id;

  -- Fitness = mean / (1 + stddev)
  -- Rewards high mean AND low variance (consistency)
  v_fitness := v_nutrient_mean / (1 + COALESCE(v_nutrient_stddev, 0));

  RETURN v_fitness;
END;
$$ LANGUAGE plpgsql;


-- Function: Select top performers for breeding
CREATE OR REPLACE FUNCTION select_top_performers(
  p_tendril_key TEXT,
  p_top_percentile NUMERIC DEFAULT 20.0,
  p_min_sample_size INT DEFAULT 100
) RETURNS TABLE(variant_id TEXT, fitness_score NUMERIC, sample_size INT) AS $$
BEGIN
  RETURN QUERY
  SELECT
    vl.variant_id,
    vl.fitness_score,
    vl.sample_size
  FROM organism_variant_lineage vl
  WHERE vl.tendril_key = p_tendril_key
    AND vl.survival_status = 'active'
    AND vl.sample_size >= p_min_sample_size
  ORDER BY vl.fitness_score DESC
  LIMIT (
    SELECT CEIL(COUNT(*) * p_top_percentile / 100.0)::INT
    FROM organism_variant_lineage
    WHERE tendril_key = p_tendril_key
      AND survival_status = 'active'
      AND sample_size >= p_min_sample_size
  );
END;
$$ LANGUAGE plpgsql;


-- Function: Prune poor performers
CREATE OR REPLACE FUNCTION prune_poor_performers(
  p_tendril_key TEXT,
  p_bottom_percentile NUMERIC DEFAULT 20.0,
  p_min_sample_size INT DEFAULT 100
) RETURNS INT AS $$
DECLARE
  v_pruned_count INT := 0;
BEGIN
  WITH ranked AS (
    SELECT
      variant_id,
      fitness_score,
      PERCENT_RANK() OVER (ORDER BY fitness_score DESC) as percentile_rank
    FROM organism_variant_lineage
    WHERE tendril_key = p_tendril_key
      AND survival_status = 'active'
      AND sample_size >= p_min_sample_size
  ),
  to_prune AS (
    SELECT variant_id
    FROM ranked
    WHERE percentile_rank >= (1.0 - p_bottom_percentile / 100.0)
  )
  UPDATE organism_variant_lineage
  SET
    survival_status = 'pruned',
    pruned_reason = 'low_fitness_score',
    updated_at = NOW()
  WHERE variant_id IN (SELECT variant_id FROM to_prune)
  RETURNING 1 INTO v_pruned_count;

  GET DIAGNOSTICS v_pruned_count = ROW_COUNT;
  RETURN v_pruned_count;
END;
$$ LANGUAGE plpgsql;


-- ============================================================================
-- 7. VIEWS FOR MONITORING
-- ============================================================================

-- View: Current variant performance dashboard
CREATE OR REPLACE VIEW v_variant_performance_dashboard AS
SELECT
  vl.variant_id,
  vl.cogni_map_id,
  vl.tendril_key,
  vl.generation,
  vl.deployment_mode,
  vl.sample_size,
  vl.lifetime_nutrient_usd,
  vl.nutrient_mean,
  vl.nutrient_stddev,
  vl.fitness_score,
  vl.survival_status,
  vl.deployed_at,
  vl.promoted_at,
  EXTRACT(EPOCH FROM (NOW() - vl.deployed_at)) / 3600 AS hours_deployed,
  cm.map_name,
  cm.version AS map_version,
  cm.category
FROM organism_variant_lineage vl
JOIN organism_cogni_map_library cm ON vl.cogni_map_id = cm.map_id
WHERE vl.survival_status IN ('active', 'promoted')
ORDER BY vl.fitness_score DESC;

COMMENT ON VIEW v_variant_performance_dashboard IS 'Real-time dashboard of active variant performance';


-- View: Evolutionary lineage tree
CREATE OR REPLACE VIEW v_evolutionary_lineage_tree AS
WITH RECURSIVE lineage AS (
  -- Base case: original variants (generation 0)
  SELECT
    variant_id,
    cogni_map_id,
    generation,
    parent_variant_ids,
    ARRAY[variant_id] AS ancestry_path,
    fitness_score,
    survival_status
  FROM organism_variant_lineage
  WHERE generation = 0

  UNION ALL

  -- Recursive case: descendants
  SELECT
    child.variant_id,
    child.cogni_map_id,
    child.generation,
    child.parent_variant_ids,
    parent.ancestry_path || child.variant_id,
    child.fitness_score,
    child.survival_status
  FROM organism_variant_lineage child
  JOIN lineage parent ON parent.variant_id = ANY(child.parent_variant_ids)
)
SELECT * FROM lineage;

COMMENT ON VIEW v_evolutionary_lineage_tree IS 'Recursive ancestry tree showing variant evolution paths';


-- ============================================================================
-- 8. MIGRATION VALIDATION
-- ============================================================================

-- Verify all tables exist
DO $$
DECLARE
  v_missing_tables TEXT[];
BEGIN
  SELECT ARRAY_AGG(table_name)
  INTO v_missing_tables
  FROM (VALUES
    ('organism_cogni_map_library'),
    ('organism_variant_lineage'),
    ('organism_shadow_deployments'),
    ('organism_breeding_config')
  ) AS expected(table_name)
  WHERE NOT EXISTS (
    SELECT 1 FROM information_schema.tables
    WHERE table_schema = 'public'
      AND table_name = expected.table_name
  );

  IF v_missing_tables IS NOT NULL THEN
    RAISE EXCEPTION 'Migration incomplete. Missing tables: %', v_missing_tables;
  ELSE
    RAISE NOTICE '✅ All evolutionary architecture tables created successfully';
  END IF;
END $$;


-- ============================================================================
-- COMPLETE
-- ============================================================================
--
-- Next steps:
-- 1. Run this migration: psql -f slimemold_v0.1.2_evolutionary_architecture.sql
-- 2. Import your 2169 cogni maps into organism_cogni_map_library
-- 3. Deploy n8n evolutionary breeding workflows
-- 4. Enable evolutionary_mode on selected tendrils
-- 5. Watch the organism evolve optimal business strategies
--
-- ============================================================================
