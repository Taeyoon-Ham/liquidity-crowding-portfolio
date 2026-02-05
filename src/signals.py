# src/signals.py
import numpy as np
import pandas as pd

print("LOADED signals.py (momentum + realized_vol + crowding + liquidity)")


def momentum_signal(
    prices_m: pd.DataFrame,
    long: int = 12,
    short: int = 6,
    z_window: int = 36,
) -> pd.DataFrame:
    # risk-only
    prices_m = prices_m.drop(columns=["BIL"], errors="ignore")

    mom_long = prices_m.pct_change(long)
    mom_short = prices_m.pct_change(short)
    raw = mom_long - mom_short

    mu = raw.rolling(z_window).mean()
    sigma = raw.rolling(z_window).std()
    z = (raw - mu) / sigma
    return z


def realized_vol(prices_m: pd.DataFrame, window: int = 6) -> pd.DataFrame:
    # risk-only
    prices_m = prices_m.drop(columns=["BIL"], errors="ignore")

    r = prices_m.pct_change()
    vol = r.rolling(window).std()
    return vol


def crowding_score_corr(
    prices_m: pd.DataFrame,
    window: int = 6,
    z_window: int = 36,
) -> pd.Series:
    """
    Portfolio-level crowding proxy:
    - rolling mean pairwise correlation of risk-asset returns
    - then z-score
    """
    prices_m = prices_m.drop(columns=["BIL"], errors="ignore")
    r = prices_m.pct_change()

    idx = r.index
    out = pd.Series(np.nan, index=idx, name="crowding_level")

    for i in range(len(idx)):
        if i < window:
            continue
        w = r.iloc[i - window + 1 : i + 1].dropna(how="any")
        if w.shape[0] < 2 or w.shape[1] < 2:
            continue

        c = w.corr()
        iu = np.triu_indices_from(c.values, k=1)
        vals = c.values[iu]
        out.iloc[i] = float(np.nanmean(vals))

    # z-score (crowding 높을수록 위험)
    mu = out.rolling(z_window).mean()
    sigma = out.rolling(z_window).std()
    z = (out - mu) / sigma
    return z.rename("crowding_z")



def liquidity_score_amihud(
    prices_d: pd.DataFrame,
    dollar_vol_d: pd.DataFrame,
    z_window: int = 36,
) -> pd.Series:
    """
    Portfolio-level liquidity(illiquidity) proxy:
    Amihud-style: |r_d| / DollarVolume_d

    Steps:
    1) daily illiq per asset
    2) monthly mean
    3) cross-asset mean -> portfolio-level series
    4) rolling z-score
    """
    prices_d = prices_d.drop(columns=["BIL"], errors="ignore")
    dollar_vol_d = dollar_vol_d.drop(columns=["BIL"], errors="ignore")

    r_d = prices_d.pct_change()
    illiq_d = (r_d.abs() / dollar_vol_d).replace([np.inf, -np.inf], np.nan)

    illiq_m = illiq_d.resample("ME").mean()
    liq_level = illiq_m.mean(axis=1)  # portfolio-level

    mu = liq_level.rolling(z_window).mean()
    sigma = liq_level.rolling(z_window).std()
    z = (liq_level - mu) / sigma

    return z.rename("liquidity_z")
