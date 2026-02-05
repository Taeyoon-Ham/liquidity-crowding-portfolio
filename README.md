# Liquidity & Crowding Portfolio Strategy

## Overview

This repository presents a systematic multi-asset portfolio strategy designed to dynamically adjust risk exposure based on **market structure conditions**, not just return forecasts.

Rather than relying on a single alpha signal, the strategy integrates:

- Momentum for directional exposure  
- Volatility for risk scaling  
- Crowding for diversification breakdown detection  
- Liquidity for market stress and deleveraging risk  

The primary goal is **drawdown control and robustness across regimes**, especially during periods when traditional signals fail due to crowded positioning or liquidity deterioration.

---

## Strategy Framework

### 1. Momentum Signal
- Cross-sectional momentum computed from monthly prices
- Long-only (long / flat) structure
- Provides base directional allocation across assets

### 2. Volatility Scaling
- Realized volatility estimated from historical monthly returns
- Portfolio exposure is reduced as volatility rises
- Prevents excessive risk-taking during unstable regimes

### 3. Crowding Overlay
- Market-level crowding measured using rolling cross-asset correlation
- High correlation indicates crowded positioning and reduced diversification
- Exposure is scaled down when correlation regimes worsen

### 4. Liquidity Overlay
- Liquidity estimated using an Amihud-style illiquidity proxy
- Designed to reduce exposure during liquidity stress
- Targets crash risk and forced deleveraging scenarios

### 5. Cash Allocation (BIL)
- Residual weight is allocated to a short-term Treasury ETF (BIL)
- Cash is treated as an explicit portfolio component
- Full fallback to cash when signals are invalid or unavailable

---

## Portfolio Construction

- Signals and overlays are computed at a **monthly frequency**
- Portfolio weights are forward-filled to daily frequency for performance evaluation
- No leverage or short-selling is assumed
- Gross exposure is capped at 100%

---

## Backtest Summary (2005–2026)

| Metric | Strategy | SPY Buy & Hold |
|------|---------|----------------|
| CAGR | ~11–12% | ~10% |
| Volatility | ~11% | ~20% |
| Sharpe Ratio | ~1.0 | ~0.6 |
| Maximum Drawdown | ~-20% | ~-55% |

The strategy sacrifices some upside participation in exchange for **significantly improved drawdown and risk-adjusted performance**.

---
## Project Structure

```text
liquidity-crowding-portfolio/
├── src/
│   ├── data.py        # Data loading utilities
│   ├── signals.py     # Momentum, volatility, crowding, liquidity signals
│   ├── portfolio.py  # Weight construction and risk multipliers
│   └── backtest.py   # End-to-end backtest execution
├── results/           # Backtest outputs (returns, curves, drawdowns)
├── report.md          # Extended analysis notes
└── README.md


