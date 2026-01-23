# Portfolio Cycle Risk Math Framework

## Overview

This framework enables portfolio-level cycle risk analysis through bucket aggregation, designed to answer:
- **"Portfolio is late/peaking because 38% of weight is in PEAKING signals"**
- **"Memory bucket is the source of transition risk"**
- **"Even if MU looks fine alone, the portfolio needs rotation"**

---

## 1. Core Objects

### A) PositionInput
Input data for each portfolio position:
- `ticker`: Stock symbol
- `market_value`: Dollar value of position
- `weight`: Position weight (market_value / total_portfolio_value)
- `bucket`: Industry bucket (Memory, Equipment, EDA, Analog, Foundry, Power, Speculative, Cash)
- `profile`: Stock profile type (memory, equipment, eda, analog)
- `story_tags`: Thematic exposures (e.g., ["AI_Compute", "Memory_Pricing"])

### B) StockCycleAnalysis
Cycle analysis results from indicator engine:
- `risk_total`: Total risk score (0-100)
- `opportunity_total`: Total opportunity score (0-100)
- `cycle_pressure`: risk - opportunity
- `phase`: Cycle phase (EARLY/MID/LATE/PEAKING/DOWNTURN)
- `transition_risk`: Stock-level transition risk (0-100)
- `critical_signals_fired`: List of critical indicators (e.g., ["RELATIVE_STRENGTH_VS_SOX", "GOOD_NEWS_EFFECTIVENESS"])
- `data_quality_ok`: Boolean flag

---

## 2. Bucket Aggregation

### A) Bucket-Level Weighted Pressure

For each bucket `b`:

```
P_b = Σ(w_i × p_i)
```

Where:
- `w_i` = portfolio weight of position i
- `p_i` = stock cycle_pressure (risk - opportunity)

**Interpretation**: How "hot" the bucket is, proportional to size.

**Example**:
- MU: 12% weight × 53 pressure = 6.36
- WDC: 8% weight × 43 pressure = 3.44
- STX: 8% weight × 50 pressure = 4.00
- **Memory bucket P_b = 13.8**

---

### B) Bucket Phase Distribution

Assign each phase a numeric score:
- EARLY = -10
- MID = 0
- LATE = +15
- PEAKING = +30
- DOWNTURN = +45

Calculate weighted phase score:

```
S_b = Σ(w_i × phase_score_i)
```

Convert `S_b` to bucket phase using thresholds:
- `S_b < -5` → EARLY
- `-5 ≤ S_b < 7.5` → MID
- `7.5 ≤ S_b < 22.5` → LATE
- `22.5 ≤ S_b < 37.5` → PEAKING
- `S_b ≥ 37.5` → DOWNTURN

**Example**:
- MU (PEAKING): 12% × 30 = 3.6
- WDC (LATE): 8% × 15 = 1.2
- STX (PEAKING): 8% × 30 = 2.4
- **Memory bucket S_b = 7.2 → LATE phase**

---

### C) Bucket Transition Risk

**Goal**: Bucket risk should spike when many holdings are peaking AND correlated.

**Formula**:

1. **Base bucket risk from pressure**:
   ```
   R_base_b = clip(2 × P_b, 0, 100)
   ```

2. **Critical signal breadth multiplier**:
   ```
   c_i = 1 if stock has critical signals, else 0
   B_b = Σ(w_i × c_i) / Σ(w_i)
   M_b = 1 + 0.8 × B_b
   ```

3. **Final bucket transition risk**:
   ```
   R_b = clip(R_base_b × M_b, 0, 100)
   ```

**Why**: A single stock peaking is manageable; a bucket peaking is portfolio-dangerous.

**Example (Memory bucket)**:
- Base risk: clip(2 × 13.8, 0, 100) = 27.6
- Critical breadth: (12% + 8% + 8%) / 28% = 100% (all have critical signals)
- Multiplier: 1 + 0.8 × 1.0 = 1.8
- **Transition risk: 27.6 × 1.8 = 49.7**

---

## 3. Portfolio Aggregation

### A) Portfolio Cycle Pressure

```
P_port = Σ(w_i × p_i)
```

Include all positions; cash has pressure = 0.

Map `P_port` to portfolio phase using same thresholds as bucket phase.

**Example**:
- Total weighted pressure across all positions
- If P_port = 8.5 → Portfolio phase = LATE

---

### B) Portfolio Concentration Risk (Bucket Sizing vs Limits)

For each bucket `b`:
- Actual weight: `W_b`
- Target max (policy): `L_b`
- Overage: `O_b = max(0, W_b - L_b)`

**Concentration risk score**:
```
R_conc = clip(200 × Σ(O_b), 0, 100)
```

**Interpretation**: If you're 10% overweight in risk buckets, this ramps fast.

**Example**:
- Memory: 28% actual, 18% limit → overage = 10%
- Equipment: 18% actual, 25% limit → overage = 0%
- **R_conc = clip(200 × 0.10, 0, 100) = 20**

---

### C) Portfolio Phase-Concentration Risk (Peaking Weight)

```
W_peak = sum of weights in PEAKING or DOWNTURN
R_phase = clip(250 × W_peak, 0, 100)
```

**Example**:
- MU (PEAKING): 12%
- STX (PEAKING): 8%
- **W_peak = 20%, R_phase = 50**

---

### D) Story Concentration Risk

Define story clusters (AI Compute, Memory Pricing, China/Export, etc.).

For each story `k`:
```
W_story,k = Σ(w_i for positions with story k)
R_story = clip(200 × max_k(W_story,k), 0, 100)
```

**Interpretation**: If 45% of portfolio relies on "AI Capex continues" → high risk even if charts look fine.

**Example**:
- AI_Compute: MU (12%) + TSM (12%) + MPWR (5%) = 29%
- Memory_Pricing: MU (12%) + WDC (8%) + STX (8%) = 28%
- **R_story = clip(200 × 0.29, 0, 100) = 58**

---

### E) Final Portfolio Transition Risk

**Weighted blend**:

```
R_trans = 0.35 × clip(2×P_port, 0, 100)
        + 0.25 × R_phase
        + 0.20 × R_conc
        + 0.20 × R_story
```

This yields a stable 0-100 "are we near a turning point" score.

**Example**:
- Pressure risk: 0.35 × 17 = 5.95
- Phase concentration: 0.25 × 50 = 12.5
- Bucket concentration: 0.20 × 20 = 4.0
- Story concentration: 0.20 × 58 = 11.6
- **R_trans = 34.05**

---

## 4. Portfolio Modes

Use transition risk + phase to determine positioning:

| Mode | Condition |
|------|-----------|
| **OFFENSE** | R_trans < 30 AND phase ≤ MID |
| **BALANCED** | 30 ≤ R_trans ≤ 60 |
| **DEFENSE** | R_trans > 60 OR phase = PEAKING/DOWNTURN |

**Example**: R_trans = 34, phase = LATE → **BALANCED mode**

---

## 5. Action Generation Rules

### A) Bucket Actions (Primary)

For any bucket with:
- `R_b > 70` OR bucket phase = PEAKING

**Action**:
- "Reduce bucket to limit L_b"
- "Rotate into earlier-phase buckets"

**Urgency**:
- HIGH: R_b > 80
- MEDIUM: 70 < R_b ≤ 80
- LOW: R_b ≤ 70 but overage > 5%

**Timeframe**:
- HIGH: 1-2 weeks
- MEDIUM: 2-4 weeks
- LOW: 4-8 weeks

---

### B) Position Actions (Secondary)

Within a flagged bucket:

1. **Rank positions** by (weight × cycle_pressure)
2. **Generate actions**:
   - **TRIM**: Top contributors (contribution > 3.0 or ≥2 critical signals)
     - Target: Reduce by 50%
   - **HOLD**: Mid-tier (contribution 1.5-3.0)
     - Target: Monitor, no change
   - **ADD**: Only if portfolio mode = OFFENSE and opportunity > 60
     - Target: Increase by 50%

**Priority**:
- 1: High-risk trims (critical signals)
- 2: Moderate trims
- 3: Holds
- 4: Adds (opportunities)

---

## 6. Example Bucket Report Output

```
Memory Bucket
==================================================
Weight: 28.0% (limit 18%) → ⚠️  over by 10.0%
Bucket Pressure: 13.8 (Very High)
Bucket Phase: LATE
Critical Breadth: 100% (High)
Bucket Risk: 50 (MODERATE)

Top Contributors:
  • MU: 12.0% × pressure 53.0 → 6.4 (PEAKING) 🔴 [RELATIVE_STRENGTH_VS_SOX, GOOD_NEWS_EFFECTIVENESS]
  • STX: 8.0% × pressure 50.0 → 4.0 (PEAKING) 🔴 [RELATIVE_STRENGTH_VS_SOX]
  • WDC: 8.0% × pressure 43.0 → 3.4 (LATE) 🔴 [FIRST_50DMA_FAILURE]

BUCKET ACTIONS
==================================================
1. 🟡 [MEDIUM] REDUCE Memory
   From 28.0% → 18.0% over 2-4 weeks
   Reason: Over limit by 10.0%; Critical signal breadth: 100%

POSITION ACTIONS
==================================================
TRIM Positions:
  • [1] MU: 12.0% → 6.0%
    Top risk contributor (6.4); Critical signals: RELATIVE_STRENGTH_VS_SOX, GOOD_NEWS_EFFECTIVENESS
  • [1] STX: 8.0% → 4.0%
    Top risk contributor (4.0); Critical signals: RELATIVE_STRENGTH_VS_SOX
  • [2] WDC: 8.0% → 5.6%
    Significant risk contributor (3.4)
```

---

## 7. Key Insights

This framework enables:

1. **Portfolio-first thinking**: "Even if MU looks fine alone, the portfolio needs rotation"
2. **Bucket-level risk**: "Memory bucket is the source of transition risk"
3. **Quantified exposure**: "38% of weight is in PEAKING signals"
4. **Actionable rotation**: "Reduce Memory from 28% → 18%, rotate to EDA/Equipment"
5. **Story correlation**: "45% exposed to AI Capex theme = single point of failure"

The math is **explainable**, **stable**, and **actionable** for real portfolio management.
