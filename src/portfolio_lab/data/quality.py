"""Data-quality checks. A stock with any flag is skipped and reported."""

import pandas as pd

from portfolio_lab.data.base import StockData

# Rows the quality + value scores need, by statement.
REQUIRED = {
    "income": ["Net Income", "Total Revenue", "Gross Profit", "Operating Income"],
    "balance": ["Stockholders Equity", "Total Assets", "Total Debt"],
    "cashflow": ["Operating Cash Flow", "Free Cash Flow"],
}
MIN_PRICE_YEARS = 1.0
MAX_STALE_DAYS = 7
MAX_DAILY_MOVE = 0.5  # a >50% one-day move is more likely bad data than news
JUMP_CHECK_YEARS = 5  # old history has known glitches (e.g. Novo 2001-2010); we only use recent data


def check_stock(data: StockData, today: pd.Timestamp | None = None) -> list[str]:
    """Return a list of problems; empty means the stock is usable."""
    today = today or pd.Timestamp.today().normalize()
    flags: list[str] = []

    if not data.currency:
        flags.append("no currency")
    if not data.sector:
        flags.append("no sector")
    if not data.country:
        flags.append("no country")

    px = data.prices
    if px.empty:
        flags.append("no prices")
    else:
        if (px.index[-1] - px.index[0]).days / 365 < MIN_PRICE_YEARS:
            flags.append("less than 1 year of prices")
        if (today - px.index[-1]).days > MAX_STALE_DAYS:
            flags.append(f"prices stale (last {px.index[-1].date()})")
        if (px["Close"] <= 0).any():
            flags.append("non-positive price")
        recent = px.loc[px.index >= today - pd.DateOffset(years=JUMP_CHECK_YEARS), "Close"]
        if recent.pct_change().abs().max() > MAX_DAILY_MOVE:
            flags.append("suspicious one-day price jump")

    statements = {"income": data.income, "balance": data.balance, "cashflow": data.cashflow}
    for kind, rows in REQUIRED.items():
        df = statements[kind]
        for row in rows:
            if df is None or df.empty or row not in df.index or df.loc[row].notna().sum() == 0:
                flags.append(f"missing {row}")
    return flags


MAX_FX_DAILY_MOVE = 0.15  # real G10/Asia moves are far smaller; bigger means bad data


def check_fx(rates: pd.Series, today: pd.Timestamp | None = None) -> list[str]:
    """Problems with an FX series (NOK per unit of a currency); empty means usable."""
    today = today or pd.Timestamp.today().normalize()
    if rates.empty:
        return ["no FX rates"]
    flags: list[str] = []
    if (rates.index[-1] - rates.index[0]).days / 365 < MIN_PRICE_YEARS:
        flags.append("less than 1 year of FX history")
    if (today - rates.index[-1]).days > MAX_STALE_DAYS:
        flags.append(f"FX stale (last {rates.index[-1].date()})")
    if (rates <= 0).any():
        flags.append("non-positive FX rate")
    recent = rates.loc[rates.index >= today - pd.DateOffset(years=JUMP_CHECK_YEARS)]
    if recent.pct_change().abs().max() > MAX_FX_DAILY_MOVE:
        flags.append("suspicious one-day FX jump")
    return flags
