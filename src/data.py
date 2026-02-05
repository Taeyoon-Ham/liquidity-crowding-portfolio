# src/data.py
import pandas as pd
import yfinance as yf


def load_market_data(
    start: str = "2005-01-01",
    tickers: list[str] | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Returns:
      prices: daily close-like price (Adj Close if available else Close), columns=tickers
      dollar_vol: daily dollar volume proxy = Close * Volume, columns=tickers
    """
    if tickers is None:
        tickers = ["SPY", "QQQ", "GLD", "TLT", "BIL"]

    raw = yf.download(
        tickers=tickers,
        start=start,
        auto_adjust=False,
        group_by="column",
        progress=False,
        threads=True,
    )

    if raw is None or raw.empty:
        raise RuntimeError("yfinance download returned empty data.")

    # ---- prices ----
    if isinstance(raw.columns, pd.MultiIndex):
        lvl0 = raw.columns.get_level_values(0)
        if "Adj Close" in lvl0:
            prices = raw["Adj Close"].copy()
        elif "Close" in lvl0:
            prices = raw["Close"].copy()
        else:
            raise KeyError(f"Neither 'Adj Close' nor 'Close' in downloaded data. level0={sorted(set(lvl0))}")
    else:
        cols = set(raw.columns.astype(str))
        if "Adj Close" in cols:
            prices = raw["Adj Close"].copy()
        elif "Close" in cols:
            prices = raw["Close"].copy()
        else:
            raise KeyError(f"Neither 'Adj Close' nor 'Close' in downloaded data. cols={list(raw.columns)}")

    if isinstance(prices, pd.Series):
        prices = prices.to_frame()
    prices.columns = [str(c) for c in prices.columns]
    prices = prices.sort_index()
    prices.index = pd.to_datetime(prices.index)

    # ---- dollar volume proxy = Close * Volume ----
    # (Adj Close는 분배/분할 반영이라 Volume과 곱하면 의미가 흔들릴 수 있어 Close 사용)
    if isinstance(raw.columns, pd.MultiIndex):
        lvl0 = raw.columns.get_level_values(0)
        if "Close" in lvl0 and "Volume" in lvl0:
            close = raw["Close"].copy()
            vol = raw["Volume"].copy()
        else:
            # Volume이 없으면 유동성 점수를 만들 수 없음
            raise KeyError(f"Need both 'Close' and 'Volume' for liquidity score. level0={sorted(set(lvl0))}")
    else:
        cols = set(raw.columns.astype(str))
        if "Close" in cols and "Volume" in cols:
            close = raw["Close"].copy()
            vol = raw["Volume"].copy()
        else:
            raise KeyError(f"Need both 'Close' and 'Volume' for liquidity score. cols={list(raw.columns)}")

    if isinstance(close, pd.Series):
        close = close.to_frame()
    if isinstance(vol, pd.Series):
        vol = vol.to_frame()

    close.columns = [str(c) for c in close.columns]
    vol.columns = [str(c) for c in vol.columns]

    close = close.sort_index()
    vol = vol.sort_index()
    close.index = pd.to_datetime(close.index)
    vol.index = pd.to_datetime(vol.index)

    dollar_vol = (close * vol).replace([0, float("inf"), float("-inf")], pd.NA)

    # 최소 sanity
    if prices.dropna(how="all").empty:
        raise RuntimeError("prices is all-NaN.")
    if dollar_vol.dropna(how="all").empty:
        raise RuntimeError("dollar_vol is all-NaN (liquidity score requires Volume).")

    return prices, dollar_vol


# Backward compatibility: 기존 코드가 load_price_data만 쓰는 경우를 위해 유지
def load_price_data(start: str = "2005-01-01") -> pd.DataFrame:
    prices, _ = load_market_data(start=start)
    return prices




