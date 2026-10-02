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
MIN_DIRECT_FX_ROWS = 250  # about a year; fewer means Yahoo has a stub, not a real series


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
        direct = _close_series(f"{currency}NOK=X")
        if direct is not None and len(direct) >= MIN_DIRECT_FX_ROWS:
            return direct
        # No usable direct pair (KRWNOK doesn't exist; HKDNOK returns one row): go through USD.
        usd_nok = _close_series("USDNOK=X")
        usd_ccy = _close_series(f"USD{currency}=X")
        if usd_nok is None or usd_ccy is None:
            raise ValueError(f"no FX rate available for {currency}->NOK")
        return cross_rate(usd_nok, usd_ccy)


def _close_series(symbol: str) -> pd.Series | None:
    hist = yf.Ticker(symbol).history(period="max")
    if hist.empty:
        return None
    s = hist["Close"].copy()
    s.index = s.index.tz_localize(None).normalize()
    return s


def cross_rate(usd_nok: pd.Series, usd_ccy: pd.Series) -> pd.Series:
    """NOK per 1 unit of ccy, from NOK-per-USD and ccy-per-USD."""
    return (usd_nok / usd_ccy).dropna()
