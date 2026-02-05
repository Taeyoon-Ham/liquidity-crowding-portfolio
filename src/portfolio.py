# src/portfolio.py
import numpy as np
import pandas as pd

print("LOADED portfolio.py (base_weights + multipliers FINAL)")


def base_weights(sig: pd.DataFrame, vol: pd.DataFrame | None = None) -> pd.DataFrame:
    """
    Long-only base weights.
    - sig > 0만 사용 (이미 backtest에서 Long/Flat 처리해도 되고, 여기서도 안전하게 처리)
    - (선택) vol이 있으면 1/vol로 위험 조정
    - 월별 sum=1 정규화
    """
    w = sig.copy()
    w = w.fillna(0.0)
    w = w.where(w > 0, 0.0)

    if vol is not None:
        v = vol.replace(0, np.nan)
        invv = 1.0 / v
        invv = invv.replace([np.inf, -np.inf], np.nan).fillna(0.0)
        w = w * invv

    s = w.sum(axis=1)
    w = w.div(s.where(s > 1e-12, np.nan), axis=0).fillna(0.0)
    return w


def vol_multiplier(vol: pd.DataFrame, target_vol_annual: float = 0.10, vol_floor: float = 1e-4) -> pd.Series:
    """
    Vol targeting multiplier (portfolio-level).
    - asset vol 평균으로 proxy
    - m = target / current, clip으로 과도 레버리지 제한
    """
    v = vol.replace([np.inf, -np.inf], np.nan)
    v_level = v.mean(axis=1).clip(lower=vol_floor)
    m = (target_vol_annual / v_level).clip(lower=0.0, upper=1.5)
    return m.rename("m_vol")


def crowding_multiplier(crowd_z: pd.Series, beta: float = 0.7, cap: float = 3.0) -> pd.Series:
    """
    crowding z가 높을수록(동조화↑) 노출 감소.
    m = exp(-beta * clip(z, 0, cap))
    """
    z = crowd_z.replace([np.inf, -np.inf], np.nan).fillna(0.0)
    score = np.clip(z.values, 0.0, cap)
    m = np.exp(-beta * score)
    return pd.Series(m, index=z.index, name="m_crowd")


def liquidity_multiplier(liq_z: pd.Series, alpha: float = 0.6, cap: float = 3.0) -> pd.Series:
    """
    liquidity z가 높을수록(비유동성↑) 노출 감소.
    m = exp(-alpha * clip(z, 0, cap))
    """
    z = liq_z.replace([np.inf, -np.inf], np.nan).fillna(0.0)
    score = np.clip(z.values, 0.0, cap)
    m = np.exp(-alpha * score)
    return pd.Series(m, index=z.index, name="m_liq")
