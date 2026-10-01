"""Free Yahoo Finance source (via yfinance), with an on-disk cache."""

import pickle
import time
from pathlib import Path

import pandas as pd
import yfinance as yf

from portfolio_lab.data.base import StockData

# Yahoo quotes some currencies in a minor unit. Map to (major unit, divisor).
# GBp = pence: a price of 2800 means 28.00 GBP. Forgetting this makes every
# UK stock look 100x too expensive.
MINOR_UNITS = {"GBp": ("GBP", 100.0), "GBX": ("GBP", 100.0), "ZAc": ("ZAR", 100.0), "ILA": ("ILS", 100.0)}

CACHE_DIR = Path(__file__).resolve().parents[3] / "data" / "cache"
CACHE_MAX_AGE_S = 20 * 3600  # refresh roughly daily


def normalize_currency(ccy: str | None) -> tuple[str | None, float]:
    """Return (major currency code, divisor to convert quoted prices to it)."""
    if ccy is None:
        return None, 1.0
    return MINOR_UNITS.get(ccy, (ccy, 1.0))


def _cached(key: str, fetch, max_age_s: float = CACHE_MAX_AGE_S):
    path = CACHE_DIR / f"{key.replace('/', '_')}.pkl"
    if path.exists() and time.time() - path.stat().st_mtime < max_age_s:
        return pickle.loads(path.read_bytes())
    value = fetch()
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    path.write_bytes(pickle.dumps(value))
    return value


class YahooSource:
    def stock(self, symbol: str) -> StockData:
        return _cached(f"stock_{symbol}", lambda: self._fetch_stock(symbol))

    def fx_to_nok(self, currency: str) -> pd.Series:
        if currency == "NOK":
            raise ValueError("NOK needs no conversion")
        return _cached(f"fx_{currency}", lambda: self._fetch_fx(currency))

    @staticmethod
    def _fetch_stock(symbol: str) -> StockData:
        t = yf.Ticker(symbol)
        info = t.info or {}
        hist = t.history(period="max", auto_adjust=False)
        quoted = info.get("currency")
        currency, divisor = normalize_currency(quoted)
        prices = pd.DataFrame()
        if not hist.empty:
            prices = hist[["Close", "Dividends"]].copy()
            prices.index = prices.index.tz_localize(None).normalize()
            prices["Close"] = prices["Close"] / divisor
            prices["Dividends"] = prices["Dividends"] / divisor
        fin_ccy, _ = normalize_currency(info.get("financialCurrency"))
        return StockData(
            symbol=symbol,
            currency=currency or "",
            financial_currency=fin_ccy,
            sector=info.get("sector"),
            country=info.get("country"),
            prices=prices,
            income=t.income_stmt,
            balance=t.balance_sheet,
            cashflow=t.cashflow,
        )

    @staticmethod
    def _fetch_fx(currency: str) -> pd.Series:
        hist = yf.Ticker(f"{currency}NOK=X").history(period="max")
        s = hist["Close"].copy()
        s.index = s.index.tz_localize(None).normalize()
        return s
