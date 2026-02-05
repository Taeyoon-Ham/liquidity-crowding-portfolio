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
Liquidity & Crowding 포트폴리오 전략
프로젝트 개요

본 프로젝트는 단순한 수익 예측 기반 전략이 아니라,
시장 구조 변화에 대응하는 리스크 관리 중심 포트폴리오 전략입니다.

모멘텀 신호만으로는 설명되지 않는 다음과 같은 환경 변화를 고려합니다.

시장 군집화 (Crowding)

유동성 악화 (Liquidity Stress)

변동성 급등

이러한 구조적 리스크를 정량적으로 측정하고,
시장 상황에 따라 포트폴리오의 위험 노출을 동적으로 조절하도록 설계되었습니다.

전략 구성 요소
1. 모멘텀 신호 (Momentum Signal)

월별 가격 데이터를 이용한 횡단면 모멘텀

롱 온리 (Long / Flat) 구조

기본적인 자산 선택 및 비중 결정 역할

2. 변동성 스케일링 (Volatility Scaling)

과거 월별 수익률 기반 실현 변동성 사용

변동성 상승 시 전체 포트폴리오 노출 축소

불안정한 국면에서의 과도한 리스크 방지

3. 크라우딩 오버레이 (Crowding Overlay)

자산 간 상관계수 기반 시장 군집도 측정

상관관계 상승을 포지션 혼잡도 증가로 해석

분산 효과 붕괴 시 포트폴리오 익스포저 축소

4. 유동성 오버레이 (Liquidity Overlay)

Amihud 방식의 비유동성 지표 활용

유동성 악화 구간에서 리스크 노출 감소

급락 및 강제 청산 리스크 완화 목적

5. 현금(BIL) 비중 관리

잔여 비중은 단기 국채 ETF(BIL)에 배분

현금을 명시적 자산으로 취급

신호 이상 시 전액 현금 대피(Fallback) 구조 포함

포트폴리오 구성 방식

모든 신호 및 오버레이는 월별로 계산

일별 수익률 평가를 위해 가중치는 일 단위로 확장

레버리지 및 숏 포지션 미사용

총 익스포저는 항상 100% 이내로 제한

백테스트 요약 (2005–2026)

연평균 수익률(CAGR): 약 11–12%

연간 변동성: 약 11%

샤프 비율: 약 1.0

최대 낙폭(Max Drawdown): 약 -20%

동기간 SPY 단순 보유 대비
낮은 변동성과 현저히 개선된 드로우다운을 기록하였습니다.

본 전략은 수익 극대화보다는
리스크 조정 성과 및 하방 방어력 개선을 목표로 합니다.

프로젝트 구조

liquidity-crowding-portfolio/
├── src/
│ ├── data.py : 데이터 로딩
│ ├── signals.py : 모멘텀, 변동성, 크라우딩, 유동성 신호
│ ├── portfolio.py : 포트폴리오 가중치 및 리스크 오버레이
│ └── backtest.py : 백테스트 실행
├── results/ : 백테스트 결과
├── report.md : 추가 분석 및 메모
└── README.md

프로젝트 의도

실제 금융시장에서 전략이 실패하는 원인은
알파 신호의 부재보다는 과도한 포지션 군집과 유동성 붕괴인 경우가 많습니다.

본 프로젝트는 이러한 구조적 리스크를
정량적으로 측정하고 포트폴리오에 반영하려는 시도입니다.

활용 목적

퀀트 리서치 / 자산배분 포지션 포트폴리오 제출

시장 구조 기반 리스크 관리 전략 예시

멀티 팩터 오버레이 설계 사례

✅ 사용 방법

README.md 열기

기존 한국어 코드블록(markdown … ) 전부 삭제

위 내용 그대로 붙여넣기

저장 후 GitHub 새로고침
