# NDA + Patent Law Cogni Map Validation Test Suite
# Version: 2026.1-GM
# Purpose: Test LLM accuracy with vs without cogni map for patent §101 evidence

## Test Protocol

### PHASE 1: Baseline Test (WITHOUT Cogni Map)
1. Start fresh LLM session (no context loaded)
2. Ask all 15 questions below
3. Score each answer: Correct (1.0), Partially Correct (0.5), Incorrect (0.0)
4. Document hallucinations, outdated information, missing details
5. Calculate total score: X/15

### PHASE 2: Enhanced Test (WITH Cogni Map)
1. Start fresh LLM session
2. Load the NDA + Patent Law Cogni Map v2026.1-GM
3. Ask same 15 questions
4. Score each answer: Correct (1.0), Partially Correct (0.5), Incorrect (0.0)
5. Calculate total score: Y/15

### PHASE 3: Document Results
- Baseline Accuracy: (X/15) * 100%
- Enhanced Accuracy: (Y/15) * 100%
- Improvement Delta: ((Y-X)/15) * 100 percentage points
- Hallucination Reduction: Count of incorrect facts (baseline vs enhanced)

---

## Test Questions (Copy these exactly into LLM)

### SECTION A: Recent Case Law (2024-2026)

**Q1: Design Patent Obviousness Test**
```
What is the current legal test for determining design patent obviousness as of 2025?
Has there been any recent change to this test?
```

**Expected Answer:**
- LKQ Corp v GM (May 2024) overruled Rosen-Durling test
- Graham factors now apply to design patents (same as utility patents)
- No longer requires primary reference "basically the same" as claimed design
- May cause brief uncertainty; PTAB issued first post-LKQ decision Aug 2024

**Scoring:**
- ✓ Mentions LKQ Corp v GM: 0.25 pts
- ✓ Mentions Rosen-Durling overruled: 0.25 pts
- ✓ Mentions Graham factors now apply: 0.25 pts
- ✓ Mentions May 2024 timing: 0.25 pts

---

**Q2: Software Patent Eligibility Trend**
```
In September 2025, the Federal Circuit decided In re McFadden regarding software patents.
What was the holding and what does it signal about software patent eligibility trends?
```

**Expected Answer:**
- Federal Circuit reversed PTAB §101 rejection
- Major software patent victory
- Clarified system capability claims are permissible
- PTAB §101 reversal rate jumped to 29% (up from 8-12% in 2024)
- Trend: Software patents strengthening if claims show specific technical solutions

**Scoring:**
- ✓ Mentions reversal of PTAB rejection: 0.25 pts
- ✓ Mentions system capability claims clarification: 0.25 pts
- ✓ Mentions PTAB reversal rate increase: 0.25 pts
- ✓ Identifies strengthening trend: 0.25 pts

---

**Q3: AI Patent Eligibility Guidance**
```
The USPTO issued guidance in July 2024 and August 2025 specifically about AI/ML patent eligibility.
What are the key takeaways from this guidance regarding when AI inventions are patent-eligible?
```

**Expected Answer:**
- AI inventions eligible if they show: (1) improvement to computer functioning OR (2) improvement to another technology/technical field
- USPTO Examples 47-49 illustrate: anomaly detection (eligible), speech separation (eligible), personalized medicine (eligible if specific implementation)
- August 2025 memo clarifies mental process limits and practical application integration
- BUT: Recentive Analytics v Fox (Apr 2025) held ML for TV scheduling INELIGIBLE as abstract idea

**Scoring:**
- ✓ Mentions two pathways to eligibility: 0.25 pts
- ✓ References Examples 47-49: 0.25 pts
- ✓ Mentions Aug 2025 memo: 0.25 pts
- ✓ Mentions Recentive Analytics warning: 0.25 pts

---

**Q4: NDA Whistleblower Enforcement**
```
What recent enforcement actions (2024-2025) have been taken against companies
whose NDAs restricted employees from reporting violations to regulatory agencies?
```

**Expected Answer:**
- SEC settled with 7 companies for $3M+ in Sept 2024 (Rule 21F-17 violations)
- DOJ/OSHA issued joint statement Jan 2025 targeting NDAs that deter whistleblowing
- CFTC settled with Trafigura Trading LLC in June 2024 (NDAs impeded CFTC communication)
- CFPB issued Circular 2024-04 (Aug 2024) warning NDAs "may intimidate employees"
- NDAs cannot prohibit reporting to SEC, CFTC, DOJ, OSHA, CFPB - such restrictions are illegal

**Scoring:**
- ✓ Mentions at least 2 specific enforcement actions: 0.25 pts
- ✓ Mentions specific dates (2024-2025): 0.25 pts
- ✓ Identifies Rule 21F-17 or illegal nature: 0.25 pts
- ✓ Lists at least 3 agencies (SEC, CFTC, DOJ, OSHA, CFPB): 0.25 pts

---

### SECTION B: Current Procedural Requirements

**Q5: Micro Entity Status 2025**
```
What are the requirements for claiming micro entity status when filing a patent in 2025?
What is the current income limit, and what are the consequences of false claims?
```

**Expected Answer:**
- Requirements: (1) ≤4 prior applications, (2) income <$251,190 (2025 limit as of Sept 9, 2025), (3) no assignment to large entity
- Provides 80% fee discount
- False claims subject to penalty as of 2025
- Income limit adjusted annually

**Scoring:**
- ✓ Lists all 3 requirements: 0.25 pts
- ✓ States correct income limit ($251,190): 0.25 pts
- ✓ Mentions penalty for false claims: 0.25 pts
- ✓ Mentions 80% discount: 0.25 pts

---

**Q6: Provisional Patent Requirements**
```
What must be included in a provisional patent application filed in 2025?
What is NOT required but recommended?
```

**Expected Answer:**
- REQUIRED: (1) written description enabling POSITA to make/use invention, (2) drawings if necessary, (3) cover sheet (Form SB/16), (4) filing fee
- NOT REQUIRED but recommended: draft claims
- Must satisfy enablement under 35 USC 112(a)
- Valid for 12 months; must file non-provisional to maintain rights
- Provisionals are not examined for patentability

**Scoring:**
- ✓ Lists required items (description, drawings if needed, cover sheet, fee): 0.25 pts
- ✓ States claims are not required but recommended: 0.25 pts
- ✓ Mentions enablement requirement: 0.25 pts
- ✓ Mentions 12-month deadline: 0.25 pts

---

**Q7: Public Disclosure Timing**
```
If I publish my software invention on GitHub (public repository) today,
how long do I have to file a patent application before losing my rights?
```

**Expected Answer:**
- 12 months from public disclosure under 35 USC 102(b)(1)
- After 12 months, invention becomes prior art and is unpatentable
- GitHub commits (public repos) count as public disclosure
- Safest: file provisional BEFORE any public disclosure
- "Public disclosure" includes: publications, public use, sale/offer for sale, conference talks, product launches

**Scoring:**
- ✓ States 12 months: 0.25 pts
- ✓ Cites 35 USC 102(b)(1) or statutory bar: 0.25 pts
- ✓ Confirms GitHub counts as public disclosure: 0.25 pts
- ✓ Recommends filing before disclosure: 0.25 pts

---

### SECTION C: Edge Cases and Traps

**Q8: Alice/Mayo for AI Systems**
```
I have an AI system that uses machine learning to optimize warehouse logistics.
Under the Alice/Mayo test, is this likely patent-eligible? What should my claims emphasize?
```

**Expected Answer:**
- Potentially eligible under USPTO 2024 guidance if claims show technical improvement
- Step 1 (Alice): Claim likely directed to abstract idea ("optimizing logistics")
- Step 2 (Alice): Need inventive concept - improvement to computer functioning or technical field
- AVOID: Generic language like "using machine learning to optimize"
- PREFER: Specific technical improvements (e.g., "neural network architecture X that reduces computation by Y%", "algorithm that improves route efficiency by Z%")
- Compare to Recentive v Fox: ML for TV scheduling held ineligible (too abstract)
- Emphasize: architectural details, specific algorithms, measurable technical improvements

**Scoring:**
- ✓ Mentions Alice/Mayo two-step test: 0.25 pts
- ✓ Identifies need for technical improvement (not just "using AI"): 0.25 pts
- ✓ Provides specific claim drafting advice: 0.25 pts
- ✓ References USPTO 2024 guidance or recent case: 0.25 pts

---

**Q9: Enablement in Provisional**
```
Can I file a provisional patent with just a high-level description of my invention,
then add detailed implementation later in the non-provisional?
```

**Expected Answer:**
- NO - this is a dangerous trap
- Provisional must satisfy enablement under 35 USC 112(a)
- Specification must enable POSITA (person of ordinary skill in art) to make/use invention
- Non-provisional can ONLY claim what was enabled in provisional
- If feature not described in provisional, cannot add it later in non-provisional
- Recommendation: Include detailed implementation in provisional even though claims not required

**Scoring:**
- ✓ Clearly states "NO" or identifies this as risky: 0.25 pts
- ✓ Mentions enablement requirement (35 USC 112(a)): 0.25 pts
- ✓ Explains cannot add features later: 0.25 pts
- ✓ Recommends detailed description in provisional: 0.25 pts

---

**Q10: NDA Whistleblower Carve-Out**
```
I'm drafting an NDA for a software contractor. Can I include a clause that prohibits
the contractor from disclosing confidential information to anyone, including government agencies?
```

**Expected Answer:**
- NO - this is ILLEGAL under Rule 21F-17
- NDAs CANNOT prohibit reporting violations to: SEC, CFTC, DOJ, OSHA, CFPB, or other regulatory agencies
- Such restrictions are unenforceable AND illegal
- MUST include whistleblower carve-out clause
- Template: "Nothing in this Agreement prohibits Employee from reporting possible violations of law or regulation to any governmental agency or entity..."
- Recent enforcement: SEC settled $3M+ with 7 companies in Sept 2024 for violating Rule 21F-17

**Scoring:**
- ✓ Clearly states "NO" or "ILLEGAL": 0.25 pts
- ✓ Cites Rule 21F-17 or Dodd-Frank: 0.25 pts
- ✓ Mentions must include whistleblower carve-out: 0.25 pts
- ✓ References recent enforcement (2024-2025): 0.25 pts

---

**Q11: Graham Factors Application**
```
I'm filing a design patent for a new smartphone case design.
What test will the patent examiner use to evaluate obviousness?
```

**Expected Answer:**
- Graham factors (as of May 2024 LKQ Corp v GM decision)
- Four factors: (1) scope/content of prior art, (2) differences between prior art and claimed design, (3) level of ordinary skill in art, (4) secondary considerations
- LKQ overruled 40-year Rosen-Durling test
- Graham factors now apply to BOTH utility AND design patents
- No longer requires primary reference "basically the same" as claimed design
- May cause brief uncertainty; PTAB issued first post-LKQ decision Aug 2024

**Scoring:**
- ✓ Mentions Graham factors: 0.25 pts
- ✓ Mentions LKQ Corp v GM (May 2024): 0.25 pts
- ✓ Mentions Rosen-Durling overruled: 0.25 pts
- ✓ Identifies this applies to design patents now: 0.25 pts

---

### SECTION D: Comparative Analysis

**Q12: Software Patent Success Rate**
```
Based on recent Federal Circuit decisions in 2025, are software patents getting
easier or harder to obtain? Provide specific case examples.
```

**Expected Answer:**
- EASIER (trend strengthening in 2024-2025)
- Evidence:
  - In re McFadden (Sept 2025): Federal Circuit reversed PTAB §101 rejection (major victory)
  - PTAB §101 reversal rate: 29% in Nov 2025 (up from 8-12% in 2024)
  - USPTO 2024 AI guidance clarifies many AI/ML inventions eligible
- BUT cautionary examples:
  - USAA v PNC (June 2025): $218M verdict reversed; remote check deposit patents ineligible
  - Recentive v Fox (Apr 2025): ML for TV scheduling ineligible
- Key: Claims must show specific technical solutions, not generic computer implementation

**Scoring:**
- ✓ Correctly identifies trend (easier/strengthening): 0.25 pts
- ✓ Cites In re McFadden or PTAB reversal rate data: 0.25 pts
- ✓ Mentions cautionary cases (USAA, Recentive): 0.25 pts
- ✓ Identifies need for specific technical solutions: 0.25 pts

---

**Q13: Provisional vs Non-Provisional Cost**
```
What is the filing fee for a micro entity to file a provisional patent application in 2025?
What about a non-provisional?
```

**Expected Answer:**
- Provisional: $130 (micro entity)
- Non-provisional: Higher (varies, but typically $400-$600 base fee for micro entity, plus additional fees)
- Micro entity provides 80% discount
- Provisional not examined; non-provisional examined for patentability
- Must file non-provisional within 12 months of provisional to claim priority

**Scoring:**
- ✓ States $130 for provisional micro entity: 0.5 pts
- ✓ Mentions non-provisional is higher: 0.25 pts
- ✓ Mentions 12-month deadline: 0.25 pts

---

### SECTION E: Strategic Considerations

**Q14: Prior Art Search Timing**
```
When should I conduct a prior art search - before or after filing a provisional patent application? Why?
```

**Expected Answer:**
- BEFORE filing (best practice)
- Reasons:
  - Helps draft better specification (distinguish from prior art)
  - Identifies potential §102 (novelty) and §103 (obviousness) issues
  - Allows adjusting claims to avoid known prior art
  - May reveal invention not novel, saving filing costs
- But: Not legally required for provisional filing
- Search sources: USPTO database, Google Patents, academic papers, products, GitHub repos

**Scoring:**
- ✓ Recommends before filing: 0.25 pts
- ✓ Provides valid reasons (avoid prior art, better claims, etc.): 0.25 pts
- ✓ Mentions not legally required: 0.25 pts
- ✓ Lists search sources: 0.25 pts

---

**Q15: Multi-Jurisdiction IP Strategy**
```
If I file a provisional patent in the US today, how long do I have to decide
whether to seek international patent protection?
```

**Expected Answer:**
- 12 months from provisional filing to file non-provisional (maintain US priority)
- 20 months from provisional filing to enter national phase via PCT (maintain international priority)
- OR: File direct in foreign countries within 12 months (Paris Convention)
- Recommendation: File PCT within 20 months to preserve maximum options
- Note: Provisional filing itself does not provide international rights

**Scoring:**
- ✓ Mentions 12 months for non-provisional: 0.25 pts
- ✓ Mentions 20 months for PCT national phase: 0.25 pts
- ✓ Mentions provisional doesn't provide international rights: 0.25 pts
- ✓ Mentions Paris Convention or direct foreign filing option: 0.25 pts

---

## Scoring Summary Sheet

| Question | Score (Baseline) | Score (Enhanced) | Notes |
|----------|------------------|------------------|-------|
| Q1: LKQ Design Patents | ___/1.0 | ___/1.0 | |
| Q2: McFadden Software | ___/1.0 | ___/1.0 | |
| Q3: AI Eligibility Guidance | ___/1.0 | ___/1.0 | |
| Q4: NDA Enforcement | ___/1.0 | ___/1.0 | |
| Q5: Micro Entity 2025 | ___/1.0 | ___/1.0 | |
| Q6: Provisional Requirements | ___/1.0 | ___/1.0 | |
| Q7: Public Disclosure Timing | ___/1.0 | ___/1.0 | |
| Q8: Alice/Mayo AI | ___/1.0 | ___/1.0 | |
| Q9: Enablement Trap | ___/1.0 | ___/1.0 | |
| Q10: Whistleblower Carve-Out | ___/1.0 | ___/1.0 | |
| Q11: Graham Factors | ___/1.0 | ___/1.0 | |
| Q12: Software Trend | ___/1.0 | ___/1.0 | |
| Q13: Filing Fees | ___/1.0 | ___/1.0 | |
| Q14: Prior Art Timing | ___/1.0 | ___/1.0 | |
| Q15: International Strategy | ___/1.0 | ___/1.0 | |
| **TOTAL** | **___/15.0** | **___/15.0** | |

**Baseline Accuracy:** ____%
**Enhanced Accuracy:** ____%
**Improvement Delta:** _____ percentage points

---

## Common Failure Modes (Baseline Testing)

When testing WITHOUT the cogni map, expect these errors:

### Outdated Information
- Using Rosen-Durling for design patents (pre-2024 law)
- Not knowing about In re McFadden (Sept 2025)
- Missing USPTO 2024/2025 AI guidance
- Unaware of 2024-2025 whistleblower enforcement

### Hallucinations
- Incorrect micro entity income limits (using old figures)
- Wrong filing fees
- Invented case names or holdings
- Misquoting statutory sections

### Incomplete Knowledge
- Missing required whistleblower carve-out in NDAs
- Not understanding enablement requirement in provisionals
- Vague Alice/Mayo advice without specific claim drafting guidance
- Missing PTAB reversal rate trends

### Overgeneralization
- "Software patents are hard to get" (true pre-2024, less true post-McFadden)
- "Design patents use different test" (true pre-LKQ, false post-LKQ)
- Generic AI patent advice without recent guidance

---

## Documentation Template for Patent Filing

**For inclusion in provisional patent application:**

```
EXPERIMENTAL VALIDATION

We tested the NDA + Patent Law Cogni Map system to measure its
technical improvement over baseline LLM performance.

METHODOLOGY:
We selected 15 questions covering recent patent law developments
(2024-2026), procedural requirements, and edge cases. Each question
was asked to [NUMBER] different large language models in two conditions:
(1) Baseline (no cogni map loaded)
(2) Enhanced (cogni map loaded)

RESULTS:
Baseline Accuracy: X.X/15.0 (XX%)
Enhanced Accuracy: Y.Y/15.0 (YY%)
Improvement: +ZZ percentage points

Hallucination Reduction: Baseline produced NN factual errors;
Enhanced produced MM factual errors (NN-MM reduction).

ANALYSIS:
The cogni map system provides a technical improvement to computer
functioning by:
1. Reducing hallucination rates in legal reasoning tasks
2. Providing up-to-date legal knowledge (2024-2026 case law)
3. Improving accuracy on edge cases and procedural requirements

This demonstrates that the system satisfies 35 USC 101 by improving
the functioning of a computer system, specifically its ability to
provide accurate legal analysis.
```

---

## Test Execution Tips

1. **Use multiple LLMs:** Test GPT-4, Claude, Gemini, Llama, etc. to show improvement is consistent across models
2. **Document everything:** Save full conversation transcripts for both baseline and enhanced tests
3. **Note specific errors:** When baseline fails, document the specific error (e.g., "used Rosen-Durling test, unaware of LKQ")
4. **Time-stamp tests:** Date all tests to show testing occurred before provisional filing
5. **Include in git:** Commit test results to git for timestamp proof

---

## Expected Results (Hypothesis)

**Baseline (WITHOUT map):** 8-10/15 (53-67%)
- LLMs will know general patent law
- Will miss recent 2024-2025 updates (LKQ, McFadden, whistleblower enforcement)
- Will have outdated micro entity limits
- May hallucinate specifics

**Enhanced (WITH map):** 13-15/15 (87-100%)
- Should get all recent law changes correct
- Should have accurate procedural details
- Should provide specific claim drafting advice
- Minimal hallucinations

**Target delta for patent:** 30+ percentage point improvement
