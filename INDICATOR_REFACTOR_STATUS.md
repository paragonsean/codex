# Semiconductor Indicator Refactoring Status

## Objective
Refactor all existing indicators to use standardized `IndicatorResult` schema for clean architecture and generic report generation.

## Completed Infrastructure

### ✅ Created Files
1. **`features/indicator_result.py`** - Standardized schema
   - `IndicatorResult` dataclass with metadata, evidence, rules, scoring
   - `IndicatorCategory`, `IndicatorTimeframe`, `IndicatorDirection` enums
   - `IndicatorRule` for individual rule tracking
   - `DriverSelector` for automatic top driver selection
   - `format_driver_summary()` for human-readable output

2. **`features/relative_strength.py`** - RS vs SOX analyzer
   - Normalizes stock and SOX series
   - Calculates RS ratio slopes (20D, 60D)
   - Rules: RS_LEADERSHIP_LOSS, RS_DISTRIBUTION_WARNING, RS_BREAKDOWN, RS_RECOVERY, RS_STRONG
   - Returns standardized `IndicatorResult`

3. **`features/news_effectiveness.py`** - Good news effectiveness analyzer
   - Already built, needs `IndicatorResult` wrapper

## Current Issue
The file `features/semiconductor_indicators.py` has syntax errors from incomplete refactoring attempt.

## Solution: Clean Slate Approach

Instead of trying to fix the corrupted file, we should:

1. **Keep the working Phase 1 indicators** (ATR, MA extension, vol regime) as-is for now
2. **Create new indicator modules** using the standardized schema
3. **Gradually migrate** to the new architecture without breaking the working system

## Recommended Next Steps

### Option A: Minimal Integration (Fast)
- Keep existing `semiconductor_indicators.py` working as-is
- Add RS vs SOX as a new standalone indicator
- Test with MU to show RS analysis working alongside existing indicators
- Reports show both old and new format temporarily

### Option B: Complete Refactor (Clean but slower)
- Restore `semiconductor_indicators.py` from backup/git
- Carefully refactor one indicator at a time
- Test after each refactor
- Full migration to `IndicatorResult` schema

### Option C: Hybrid Approach (Recommended)
- Fix syntax errors in `semiconductor_indicators.py` to restore working state
- Keep existing indicators returning Dict for now
- Add wrapper functions that convert Dict → IndicatorResult
- New indicators (RS, OBV, etc.) use IndicatorResult natively
- Gradually migrate old indicators over time

## Current Working Features (Before Refactor)
- 10 indicators operational:
  1. RSI Sustained Overbought (weekly)
  2. Exhaustion Near 20D High
  3. RSI Divergence
  4. ROC Compression
  5. RSI 55-70 Zone
  6. Trend Persistence
  7. First 50DMA Failure
  8. ATR Expansion
  9. MA Extension
  10. Volatility Regime

- All integrated into `analyze_semiconductor_cycle_risk()`
- All displayed in HTML and Markdown reports
- Tested with MU showing CRITICAL risk (75 points)

## What User Wants
User selected **Option 2**: Refactor existing indicators to use IndicatorResult schema first, establishing clean architecture before adding more indicators.

## Immediate Action Needed
Fix the syntax errors in `semiconductor_indicators.py` to restore working state, then proceed with careful, incremental refactoring.
