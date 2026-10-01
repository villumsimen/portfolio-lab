"""The interface every data source implements.

The rest of the project only talks to `DataSource`, so swapping free
Yahoo data for a paid API later means writing one new class.
"""

from dataclasses import dataclass, field
from typing import Protocol

import pandas as pd


@dataclass
class StockData:
    """Everything we know about one stock, with prices in major currency units.

    `prices` has a 'Close' column (not adjusted for dividends) and a
    'Dividends' column. 'Close' is in `currency` (e.g. GBP, never pence).
    Statements are yearly, with one column per report date.
    """

    symbol: str
    currency: str
    financial_currency: str | None = None
    sector: str | None = None
    country: str | None = None
    prices: pd.DataFrame = field(default_factory=pd.DataFrame)
    income: pd.DataFrame = field(default_factory=pd.DataFrame)
    balance: pd.DataFrame = field(default_factory=pd.DataFrame)
    cashflow: pd.DataFrame = field(default_factory=pd.DataFrame)


class DataSource(Protocol):
    def stock(self, symbol: str) -> StockData: ...

    def fx_to_nok(self, currency: str) -> pd.Series:
        """Daily NOK per one unit of `currency` (a series indexed by date)."""
        ...
