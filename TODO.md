# TODO: Critical Path to Production

**Status:** Repo has 70% documentation, 30% working code. Need to flip that ratio.

---

## 🔴 Critical (Blocks Production)

### 1. Connect UMC Server to PostgreSQL
**Current:** Uses in-memory dict (data lost on restart)
**Need:** Actual PostgreSQL connection

**Tasks:**
- [ ] Add SQLAlchemy models for `notes`, `state_updates`, `audit_log`
- [ ] Connect to `DATABASE_URL` from environment
- [ ] Update all endpoints to use database instead of dict
- [ ] Test data persistence after restart
- [ ] Add database migration runner

**Files to modify:**
- `middleware/umc_memory_server.py` (lines 43-46: replace dicts with DB)

**Time estimate:** 4-6 hours

---

### 2. Write Tests (Currently 0 Tests for Python Code)
**Current:** 0 tests for Python code (only n8n-mcp has tests)
**Need:** >80% coverage minimum

**Tasks:**
- [ ] Implement tests in `tests/test_umc_server.py` (16 tests marked TODO)
- [ ] Implement tests in `tests/test_genesis_void.py` (15 tests marked TODO)
- [ ] Add `pytest.ini` configuration
- [ ] Add test fixtures for mock data
- [ ] Set up CI/CD to run tests on commit

**Files:**
- `tests/test_umc_server.py` - 16 test stubs need implementation
- `tests/test_genesis_void.py` - 15 test stubs need implementation

**Time estimate:** 12-16 hours

---

### 3. Create Genesis REST API Wrapper
**Current:** Genesis void is standalone Python module
**Need:** REST API so n8n can call it

**Tasks:**
- [ ] Create `genesis_api.py` with FastAPI routes:
  - `POST /genesis/discover` - Run Monte Carlo exploration
  - `POST /genesis/allocate` - Allocate resources to voids
  - `POST /genesis/detect` - Detect emergence signals
  - `POST /genesis/converge` - Learn routing rules
  - `GET /genesis/voids` - List active voids
  - `GET /genesis/rules` - List learned routing rules
- [ ] Connect to PostgreSQL (store voids, rules, signals)
- [ ] Add to Docker Compose
- [ ] Create OpenAPI spec for n8n integration

**New file:** `genesis_api.py` (~400 lines)

**Time estimate:** 8-10 hours

---

### 4. Create n8n ↔ Genesis Connector Workflow
**Current:** No actual n8n workflow uses Genesis
**Need:** Working n8n workflow that calls Genesis API

**Tasks:**
- [ ] Create `workflows/genesis-discovery-daily.json` (actual n8n workflow)
- [ ] Create `workflows/genesis-exploitation-hourly.json`
- [ ] Create `workflows/genesis-emergence-weekly.json`
- [ ] Create `workflows/genesis-meta-learning-weekly.json`
- [ ] Test workflows in running n8n instance
- [ ] Document workflow import process

**Files:**
- 4 new workflow JSON files (not just markdown blueprints)

**Time estimate:** 6-8 hours

---

## 🟡 High Priority (Production Readiness)

### 5. Fix Docker Compose to Actually Run
**Current:** `docker-compose.yml` exists but not tested
**Need:** Verified working full stack

**Tasks:**
- [ ] Test `docker-compose up` works
- [ ] Verify PostgreSQL initializes with migrations
- [ ] Verify UMC server connects to database
- [ ] Verify n8n can connect to UMC server
- [ ] Add healthchecks for all services
- [ ] Document startup order and dependencies

**Time estimate:** 4 hours

---

### 6. Validate Genesis Claims with Real Data
**Current:** Simulation showed 68% WORSE performance
**Need:** Proof it actually works

**Tasks:**
- [ ] Run 180-day simulation (not just 90 days)
- [ ] Verify routing rules actually get learned (not 0)
- [ ] Test with real data (not synthetic)
- [ ] Measure actual performance vs naive approach
- [ ] Update claims in documentation based on results

**Time estimate:** 40-60 hours (2-3 weeks)

---

### 7. Create Monitoring Dashboard
**Current:** No visibility into Genesis performance
**Need:** Grafana dashboard with metrics

**Tasks:**
- [ ] Add Prometheus metrics to UMC server
- [ ] Add Prometheus metrics to Genesis API
- [ ] Create Grafana dashboard:
  - Active voids count
  - Void energy distribution
  - Resource allocation (exploration vs exploitation)
  - Variant promotion events
  - Routing rules learned
  - Performance vs baseline
- [ ] Add alerting for critical thresholds

**Time estimate:** 8 hours

---

## 🟢 Medium Priority (Nice to Have)

### 8. Clean Up Duplicate Simulation Files
**Current:** 5 simulation files doing similar things
**Need:** One canonical simulation

**Tasks:**
- [ ] Keep `slimemold_genesis_integrated_simulation.py` as canonical
- [ ] Archive old simulation variants to `archive/`
- [ ] Document what each simulation was testing
- [ ] Remove duplicate CSV output files

**Time estimate:** 2 hours

---

### 9. Align Documentation with Reality
**Current:** Documentation makes claims code doesn't support
**Need:** Honest documentation

**Tasks:**
- [ ] Update README.md to link to README-HONEST.md
- [ ] Remove "Production-ready" claims until actually validated
- [ ] Add "Status: Experimental" badges to unproven features
- [ ] Move aspirational content to ROADMAP.md
- [ ] Add "What Actually Works" section to all docs

**Time estimate:** 4 hours

---

### 10. Add CLI Tools
**Current:** No easy way to run things
**Need:** Simple CLI commands

**Tasks:**
- [ ] `umc-server start` - Run UMC server
- [ ] `umc-server migrate` - Run database migrations
- [ ] `genesis discover` - Run discovery phase
- [ ] `genesis status` - Show active voids, rules, signals
- [ ] Add to `setup.py` entry_points

**Time estimate:** 4 hours

---

## ⚪ Low Priority (Future)

### 11. Add More Void Space Types
**Current:** Only parameter and topology voids implemented
**Need:** Code, memory, network voids

**Tasks:**
- [ ] Implement code space exploration
- [ ] Implement memory space exploration
- [ ] Implement network space exploration
- [ ] Test cross-space patterns

**Time estimate:** 20 hours

---

### 12. Import 2,169 Cogni Maps
**Current:** Not integrated with organism
**Need:** Full Cogni Map library in database

**Tasks:**
- [ ] Export Cogni Maps to CSV
- [ ] Create import script
- [ ] Load into `organism_cogni_map_library` table
- [ ] Link to variant breeding system

**Time estimate:** 6 hours

---

## Summary: Time to Production

**Critical path (items 1-4):** 30-40 hours = 1 week (focused work)
**High priority (items 5-7):** 52-72 hours = 2 weeks
**Medium priority (items 8-10):** 10 hours = 2 days

**Total to MVP:** ~4 weeks of focused engineering

---

## Current Blockers

1. **No database connection** - UMC server loses data on restart
2. **No tests** - Can't validate anything works correctly
3. **No Genesis API** - n8n can't call Genesis void
4. **No integration** - All components work standalone, not together
5. **No validation** - Simulation results are concerning (68% worse)

**Recommendation:** Focus on items 1-4 (Critical path) before writing more documentation.

---

## Definition of Done

**v1.0.0 Production Ready means:**
- ✅ UMC server connected to PostgreSQL (data persists)
- ✅ Tests >80% coverage (currently 0%)
- ✅ Genesis API with REST endpoints (n8n can call it)
- ✅ At least 1 working n8n workflow using Genesis
- ✅ Docker Compose runs full stack
- ✅ Genesis void validated on real data (not simulation)
- ✅ Routing rules actually get learned (not 0)
- ✅ Documentation matches reality

**Current status:** 2 out of 8 complete (25%)

---

**Last updated:** 2026-01-14
**Reviewed by:** Senior Engineer (brutally honest assessment)
