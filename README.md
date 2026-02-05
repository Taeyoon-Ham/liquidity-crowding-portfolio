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
liquidity-crowding-portfolio/
├── src/
│ ├── data.py # Data loading utilities
│ ├── signals.py # Momentum, volatility, crowding, liquidity signals
│ ├── portfolio.py # Weight construction and risk multipliers
│ └── backtest.py # End-to-end backtest execution
├── results/ # Backtest outputs (returns, curves, drawdowns)
├── report.md # Extended analysis notes
└── README.md




---

README (한국어)
---

# 유동성 & 크라우딩 기반 포트폴리오 전략  
(Liquidity & Crowding Portfolio Strategy)

## 개요

본 리포지토리는 단일 알파 시그널에 의존하지 않고,  
**시장 구조(Market Structure)** 변화에 따라 위험 노출을 동적으로 조정하는  
시스템 트레이딩 기반 멀티자산 포트폴리오 전략을 제시합니다.

본 전략은 수익 예측 자체보다 다음과 같은 **리스크 환경 요인**을 핵심 입력값으로 사용합니다.

- 모멘텀: 자산의 방향성 판단  
- 변동성: 리스크 규모 조절  
- 크라우딩: 분산 효과 붕괴 감지  
- 유동성: 시장 스트레스 및 디레버리징 위험 관리  

전략의 핵심 목표는 **수익 극대화가 아닌**,  
급락 구간에서의 **낙폭 관리(drawdown control)** 와  
시장 국면 전반에서의 **견고한 리스크 조정 성과**입니다.

---

## 전략 프레임워크

### 1. 모멘텀 시그널
- 월별 가격 데이터를 기반으로 횡단면 모멘텀 산출
- 롱 온리(Long / Flat) 구조
- 자산별 기본 방향성 결정 역할 수행

### 2. 변동성 스케일링
- 과거 월별 수익률을 이용해 실현 변동성 추정
- 변동성 상승 시 포트폴리오 총 익스포저 자동 축소
- 불안정한 시장 국면에서의 과도한 리스크 노출 방지

### 3. 크라우딩 오버레이
- 자산 간 롤링 상관계수를 활용해 시장 크라우딩 수준 측정
- 높은 상관계수는 포지션 집중 및 분산 효과 약화를 의미
- 크라우딩이 심화될수록 포트폴리오 익스포저 감소

### 4. 유동성 오버레이
- Amihud 방식 기반 비유동성 지표를 활용한 유동성 측정
- 유동성 악화 국면에서 노출 축소
- 급락 및 강제 디레버리징 리스크 대응 목적

### 5. 현금 자산 (BIL)
- 잔여 비중은 단기 국채 ETF(BIL)에 배분
- 현금을 명시적 포트폴리오 구성 자산으로 취급
- 시그널이 유효하지 않거나 리스크 환경이 극단적일 경우 전액 현금 전환

---

## 포트폴리오 구성 방식

- 모든 시그널 및 오버레이는 **월 단위 빈도**로 계산
- 산출된 포트폴리오 비중은 일별 수익률 계산을 위해 forward-fill 방식으로 적용
- 레버리지 및 공매도는 가정하지 않음
- 포트폴리오 총 익스포저는 최대 100%로 제한

---

## 백테스트 요약 (2005–2026)

| 지표 | 본 전략 | SPY 단순 보유 |
|------|--------|---------------|
| 연평균 수익률 (CAGR) | 약 11–12% | 약 10% |
| 변동성 | 약 11% | 약 20% |
| 샤프 비율 | 약 1.0 | 약 0.6 |
| 최대 낙폭 (MDD) | 약 -20% | 약 -55% |

본 전략은 상승장에서의 일부 수익을 포기하는 대신,  
**하락장에서의 손실을 크게 제한**하며  
장기적으로 더 안정적인 리스크 조정 성과를 목표로 합니다.

---

## 프로젝트 구조

liquidity-crowding-portfolio/
├── src/
│   ├── data.py        # 데이터 로딩 유틸리티
│   ├── signals.py     # 모멘텀, 변동성, 크라우딩, 유동성 시그널
│   ├── portfolio.py  # 포트폴리오 비중 산출 및 리스크 조정
│   └── backtest.py   # 전체 백테스트 실행
├── results/           # 백테스트 결과 (수익률, 누적 곡선, 낙폭)
├── report.md          # 확장 분석 노트
└── README.md
