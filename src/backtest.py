# src/backtest.py
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from src.data import load_price_data, load_market_data
from src.signals import (
    momentum_signal,
    realized_vol,
    crowding_score_corr,
    liquidity_score_amihud,
)
from src.portfolio import (
    base_weights,
    vol_multiplier,
    crowding_multiplier,
    liquidity_multiplier,
)

print("### RUNNING backtest.py (Liquidity + Crowding + Drawdown FINAL) ###")


# =========================
# Utils
# =========================
def ensure_results_dir():
    os.makedirs("results", exist_ok=True)


def _safe_drawdown_ylim(dd_a: pd.Series, dd_b: pd.Series | None = None, pad: float = 0.05):
    mins = [dd_a.min()]
    if dd_b is not None:
        mins.append(dd_b.min())

    dd_min = float(np.nanmin(mins))
    if not np.isfinite(dd_min):
        dd_min = -0.01

    dd_min = min(dd_min, -1e-6)
    lower = dd_min - pad
    lower = max(lower, -1.0)
    upper = 0.0

    if lower >= upper:
        lower = -0.01
    return lower, upper


def performance_stats(daily_rets: pd.Series, ann: int = 252) -> dict:
    daily_rets = daily_rets.dropna()
    if len(daily_rets) < 5:
        return {"CAGR": np.nan, "Vol": np.nan, "Sharpe": np.nan, "MaxDD": np.nan}

    cum = (1 + daily_rets).cumprod()
    years = (cum.index[-1] - cum.index[0]).days / 365.25
    cagr = cum.iloc[-1] ** (1 / years) - 1 if years > 0 else np.nan

    vol = daily_rets.std() * np.sqrt(ann)
    sharpe = (daily_rets.mean() * ann) / vol if (vol is not None and vol > 0) else np.nan

    dd = cum / cum.cummax() - 1
    maxdd = float(dd.min())

    return {"CAGR": cagr, "Vol": vol, "Sharpe": sharpe, "MaxDD": maxdd}


# =========================
# Main
# =========================
def run_backtest():
    ensure_results_dir()

    # -------------------------
    # 1) Load data
    # -------------------------
    prices = load_price_data(start="2005-01-01").sort_index()
    prices.index = pd.to_datetime(prices.index)

    prices_m = prices.ffill().resample("ME").last()

    # market data for liquidity (daily)
    prices_d, dollar_vol_d = load_market_data(start="2005-01-01")
    prices_d = prices_d.sort_index()
    dollar_vol_d = dollar_vol_d.sort_index()

    print("\n=== Monthly data check ===")
    print("prices_m range:", prices_m.index.min(), "->", prices_m.index.max(), "len:", len(prices_m))
    print(prices_m.tail())

    # BIL must exist for cash bucket
    if "BIL" not in prices_m.columns:
        raise KeyError("BIL이 prices에 없습니다. src/data.py tickers에 'BIL'을 추가하세요.")

    # -------------------------
    # 2) Signals
    # -------------------------
    sig = momentum_signal(prices_m).fillna(0.0)
    sig = sig.where(sig > 0, 0.0)  # Long/Flat

    vol = realized_vol(prices_m)                      # DataFrame (per-asset, monthly)
    crowd_z = crowding_score_corr(prices_m)           # Series (monthly)
    liq_z = liquidity_score_amihud(prices_d, dollar_vol_d)  # Series (monthly)

    print("\n=== NaN diagnostics ===")
    print("sig NaN ratio:", float(sig.isna().mean().mean()))
    print("vol NaN ratio:", float(vol.isna().mean().mean()))
    print("crowd_z NaN ratio:", float(crowd_z.isna().mean()))
    print("liq_z NaN ratio:", float(liq_z.isna().mean()))

    # -------------------------
    # 3) Base weights + overlays
    # -------------------------
    w_base = base_weights(sig, vol)  # should return weights for risk assets (may include BIL if you coded so)

    # Multipliers
    m_vol = vol_multiplier(vol)                 # Series aligned to months
    m_crowd = crowding_multiplier(crowd_z)      # Series
    m_liq = liquidity_multiplier(liq_z)         # Series

    # Align indexes
    m_vol = m_vol.reindex(w_base.index).fillna(1.0)
    m_crowd = m_crowd.reindex(w_base.index).fillna(1.0)
    m_liq = m_liq.reindex(w_base.index).fillna(1.0)

    # IMPORTANT:
    # - 여기서 clip(0,1)로 강제하면 vol targeting(>1) 효과를 죽일 수 있음
    # - cash bucket이 최종 총합을 1로 맞춰주므로 m_total은 "그대로" 두는 게 정석
    m_total = (m_vol * m_crowd * m_liq)

    print("\n=== Overlay check ===")
    print("m_vol  stats (min/mean/max):", float(m_vol.min()), float(m_vol.mean()), float(m_vol.max()))
    print("m_crowd stats (min/mean/max):", float(m_crowd.min()), float(m_crowd.mean()), float(m_crowd.max()))
    print("m_liq  stats (min/mean/max):", float(m_liq.min()), float(m_liq.mean()), float(m_liq.max()))
    print("m_total stats (min/mean/max):", float(m_total.min()), float(m_total.mean()), float(m_total.max()))

    # Apply overlay to base weights (risk assets)
    w_m = w_base.mul(m_total, axis=0)

    # Ensure BIL column exists (we will fill leftover into BIL)
    if "BIL" not in w_m.columns:
        w_m["BIL"] = 0.0

    # 위험자산 컬럼 (BIL 제외)
    risk_cols = [c for c in w_m.columns if c != "BIL"]

    # -------------------------
    # 3.5) CASH BUCKET + (optional) BIL cap
    # -------------------------
    # (A) 위험자산 비중은 음수가 나오면 0으로 컷 (Long/Flat 유지)
    #     base_weights가 이미 Long/Flat이면 필요 없지만, 안전하게 한 번 더
    w_m[risk_cols] = w_m[risk_cols].clip(lower=0.0)

    # (B) 위험자산 합이 1을 넘으면 비례 축소해서 1로 맞춤
    risk_sum = w_m[risk_cols].sum(axis=1)
    scale = (1.0 / risk_sum).where(risk_sum > 1.0, 1.0)
    w_m[risk_cols] = w_m[risk_cols].mul(scale, axis=0)

    # (C) 남는 비중은 BIL로
    risk_sum2 = w_m[risk_cols].sum(axis=1)
    w_m["BIL"] = (1.0 - risk_sum2).clip(lower=0.0, upper=1.0)

    # (D) OPTIONAL: BIL cap 40%
    #     - 현금을 너무 많이 들고 있어 수익이 눌리는 경우 참여율 하한을 둠
    BIL_CAP = 0.40  # 필요 없으면 None으로 바꾸거나 아래 블록을 주석 처리
    if BIL_CAP is not None:
        # BIL이 cap을 초과한 달의 "초과분"을 위험자산으로 재분배
        excess = (w_m["BIL"] - BIL_CAP).clip(lower=0.0)
        w_m["BIL"] = w_m["BIL"].clip(upper=BIL_CAP)

        # 위험자산 비중 비례로 초과분 재배분
        denom = w_m[risk_cols].sum(axis=1).replace(0.0, np.nan)
        add = excess.div(denom, axis=0).replace([np.inf, -np.inf], np.nan).fillna(0.0)
        w_m[risk_cols] = w_m[risk_cols].mul(1.0 + add, axis=0)

        # 다시 합 1 넘으면 축소 후 leftover를 BIL로
        risk_sum3 = w_m[risk_cols].sum(axis=1)
        scale2 = (1.0 / risk_sum3).where(risk_sum3 > 1.0, 1.0)
        w_m[risk_cols] = w_m[risk_cols].mul(scale2, axis=0)
        w_m["BIL"] = (1.0 - w_m[risk_cols].sum(axis=1)).clip(lower=0.0, upper=1.0)

    # -------------------------
    # 4) Fallback: if vol is fully NaN month -> go to BIL (cash)
    # -------------------------
    invalid_mask = vol.isna().all(axis=1)
    fallback_ratio = float(invalid_mask.mean())
    print("\n=== Fallback check ===")
    print("fallback months ratio:", fallback_ratio)
    print("fallback months count:", int(invalid_mask.sum()), "/", int(len(invalid_mask)))

    if invalid_mask.any():
        w_m.loc[invalid_mask, risk_cols] = 0.0
        w_m.loc[invalid_mask, "BIL"] = 1.0

    # 마지막 안전장치: 총합 1
    total_sum = w_m.sum(axis=1)
    w_m = w_m.div(total_sum.where(total_sum > 1e-12, 1.0), axis=0)

    # -------------------------
    # 5) Daily expansion & returns
    # -------------------------
    daily_rets = prices.pct_change().dropna()
    w_d = w_m.reindex(daily_rets.index, method="ffill").fillna(0.0)

    print("\n=== Weight sanity check ===")
    print("mean gross exposure:", float(w_d.sum(axis=1).mean()))
    print("nonzero days ratio :", float((w_d.sum(axis=1) > 1e-6).mean()))
    print("BIL days ratio     :", float((w_d["BIL"] > 1e-9).mean()))
    print("w_m tail:\n", w_m.tail())

    port_rets = (w_d.shift(1) * daily_rets).sum(axis=1).dropna()

    if "SPY" not in prices.columns:
        raise KeyError("prices 데이터에 'SPY' 컬럼이 없습니다. 벤치마크 비교를 위해 필요합니다.")
    spy_rets = prices["SPY"].pct_change().dropna()

    common_idx = port_rets.index.intersection(spy_rets.index)
    strat_rets = port_rets.loc[common_idx]
    spy_rets = spy_rets.loc[common_idx]

    strat_cum = (1 + strat_rets).cumprod()
    spy_cum = (1 + spy_rets).cumprod()

    strat_dd = strat_cum / strat_cum.cummax() - 1
    spy_dd = spy_cum / spy_cum.cummax() - 1

    # -------------------------
    # 6) Stats
    # -------------------------
    s_stats = performance_stats(strat_rets)
    b_stats = performance_stats(spy_rets)

    print("\n=== Performance Summary (Strategy) ===")
    print(f"CAGR   : {s_stats['CAGR']:.2%}")
    print(f"Vol    : {s_stats['Vol']:.2%}")
    print(f"Sharpe : {s_stats['Sharpe']:.2f}")
    print(f"MaxDD  : {s_stats['MaxDD']:.2%}")

    print("\n=== Performance Summary (SPY Buy&Hold) ===")
    print(f"CAGR   : {b_stats['CAGR']:.2%}")
    print(f"Vol    : {b_stats['Vol']:.2%}")
    print(f"Sharpe : {b_stats['Sharpe']:.2f}")
    print(f"MaxDD  : {b_stats['MaxDD']:.2%}")

    # -------------------------
    # 7) Save outputs
    # -------------------------
    strat_rets.to_csv("results/strategy_daily_returns.csv")
    spy_rets.to_csv("results/spy_daily_returns.csv")
    strat_cum.to_csv("results/strategy_cum_curve.csv")
    spy_cum.to_csv("results/spy_cum_curve.csv")
    strat_dd.to_csv("results/strategy_drawdown.csv")
    spy_dd.to_csv("results/spy_drawdown.csv")
    w_m.to_csv("results/weights_monthly.csv")

    # -------------------------
    # 8) Plots
    # -------------------------
    plt.figure(figsize=(10, 4))
    plt.plot(strat_cum, label="Strategy")
    plt.plot(spy_cum, label="SPY")
    plt.yscale("log")
    plt.title("Cumulative Performance (log scale)")
    plt.grid(True)
    plt.legend()
    plt.margins(x=0.01, y=0.05)
    plt.tight_layout()
    plt.savefig("results/portfolio_curve.png", dpi=150)
    plt.show()

    plt.figure(figsize=(10, 4))
    plt.plot(strat_dd, label="Strategy DD")
    plt.plot(spy_dd, label="SPY DD")
    plt.axhline(0, linewidth=1)
    plt.title("Drawdown Comparison")
    plt.grid(True)
    plt.legend()

    y0, y1 = _safe_drawdown_ylim(strat_dd, spy_dd, pad=0.05)
    plt.ylim(y0, y1)
    plt.margins(x=0.01, y=0.02)
    plt.tight_layout()
    plt.savefig("results/drawdown_compare.png", dpi=150)
    plt.show()


if __name__ == "__main__":
    run_backtest()


