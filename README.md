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
```

# Liquidity & Crowding 기반 포트폴리오 전략

## 개요

본 리포지토리는 단순한 수익률 예측이 아니라,  
**시장 구조(Market Structure) 조건에 기반하여 포트폴리오의 위험 노출을 동적으로 조정하는 시스템 기반 멀티자산 전략**을 제시합니다.

단일 알파 시그널에 의존하지 않고, 다음 요소들을 통합합니다.

- **모멘텀**: 방향성 익스포저 결정  
- **변동성**: 리스크 스케일링 (위험 조절)  
- **크라우딩**: 분산 효과 붕괴 감지  
- **유동성**: 시장 스트레스 및 디레버리징 위험 대응  

본 전략의 핵심 목표는,  
특히 **포지션 쏠림(크라우딩)** 이나 **유동성 악화**로 인해 기존 시그널이 실패하는 구간에서  
**낙폭(drawdown) 관리와 국면(regime) 전반의 견고함**을 확보하는 것입니다.

---

## 전략 프레임워크

### 1. 모멘텀 시그널
- 월별 가격 데이터를 기반으로 횡단면 모멘텀 산출
- 롱 온리(Long / Flat) 구조
- 자산별 기본 방향성 배분(베이스 익스포저) 제공

### 2. 변동성 스케일링
- 과거 월별 수익률을 이용한 실현 변동성 추정
- 변동성 상승 시 포트폴리오 익스포저 축소
- 불안정 국면에서 과도한 리스크 노출 방지

### 3. 크라우딩 오버레이
- 자산 간 롤링 상관계수를 사용해 시장 수준의 크라우딩 측정
- 상관계수 상승은 포지션 쏠림 및 분산 효과 약화를 의미
- 상관 구조가 악화되는 국면에서 익스포저 축소

### 4. 유동성 오버레이
- Amihud 방식의 비유동성(illiquidity) 프록시를 활용한 유동성 수준 추정
- 유동성 스트레스 구간에서 익스포저 축소
- 급락 리스크 및 강제 디레버리징 시나리오 대응

### 5. 현금 배분 (BIL)
- 잔여 비중은 단기 국채 ETF(BIL)에 배분
- 현금을 명시적인 포트폴리오 구성 요소로 취급
- 시그널이 유효하지 않을 경우 전액 현금으로 폴백(fallback)

---

## 포트폴리오 구성 방식

- 시그널 및 오버레이는 **월 단위 빈도**로 계산
- 성과 평가를 위해 비중은 **일 단위로 forward-fill**
- 레버리지 및 공매도 미사용
- 총 익스포저는 **100%로 제한**

---

## 백테스트 요약 (2005–2026)

| 지표 | 본 전략 | SPY 단순 보유 |
|---|---|---|
| 연평균 수익률 (CAGR) | 약 11–12% | 약 10% |
| 변동성 | 약 11% | 약 20% |
| 샤프 비율 | 약 1.0 | 약 0.6 |
| 최대 낙폭 (MDD) | 약 -20% | 약 -55% |

본 전략은 상승장에서의 일부 수익 참여를 희생하는 대신,  
**낙폭과 리스크 조정 성과를 유의미하게 개선하는 것**을 목표로 합니다.

---

## 프로젝트 구조

liquidity-crowding-portfolio/
├── src/
│   ├── data.py        # Data loading utilities
│   ├── signals.py     # Momentum, volatility, crowding, liquidity signals
│   ├── portfolio.py  # Weight construction and risk multipliers
│   └── backtest.py   # End-to-end backtest execution
├── results/           # Backtest outputs (returns, curves, drawdowns)
├── report.md          # Extended analysis notes
└── README.md


## 프로젝트 의도

실제 금융시장에서 전략이 실패하는 주요 원인은  
알파 시그널의 부재보다 **과도한 포지션 쏠림과 유동성 붕괴**인 경우가 많습니다.

본 프로젝트는 이러한 구조적 리스크를  
정량적으로 포트폴리오에 반영하려는 시도입니다.

---

## 활용 목적

- 퀀트 리서치 / 자산배분 / 리스크 관리 포지션 포트폴리오 제출
- 시장 구조 기반 리스크 관리 전략 사례
- 멀티 팩터 오버레이 설계 예시
