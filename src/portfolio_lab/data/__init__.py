"""Data layer: one interface, swappable sources."""

from portfolio_lab.data.base import DataSource, StockData
from portfolio_lab.data.quality import check_stock

__all__ = ["DataSource", "StockData", "check_stock"]
