import pandas as pd
import pytest

from portfolio_lab.data.base import StockData
from portfolio_lab.data.quality import REQUIRED, check_stock
from portfolio_lab.data.yahoo import normalize_currency
from portfolio_lab.universe import is_excluded_sector, load_universe

TODAY = pd.Timestamp("2026-10-01")


def good_stock() -> StockData:
    idx = pd.bdate_range("2020-01-01", "2026-10-01")
    px = pd.DataFrame({"Close": 100.0, "Dividends": 0.0}, index=idx)
    cols = [pd.Timestamp("2025-12-31"), pd.Timestamp("2024-12-31")]

    def stmt(rows):
        return pd.DataFrame(1.0, index=rows, columns=cols)

    return StockData(
        symbol="X", currency="USD", sector="Technology", country="United States",
        prices=px, income=stmt(REQUIRED["income"]), balance=stmt(REQUIRED["balance"]),
        cashflow=stmt(REQUIRED["cashflow"]),
    )


def test_pence_are_converted_to_pounds():
    assert normalize_currency("GBp") == ("GBP", 100.0)
    assert normalize_currency("USD") == ("USD", 1.0)
    assert normalize_currency(None) == (None, 1.0)


def test_good_stock_has_no_flags():
    assert check_stock(good_stock(), today=TODAY) == []


def test_missing_fundamental_row_is_flagged():
    s = good_stock()
    s.income = s.income.drop(index="Gross Profit")
    assert "missing Gross Profit" in check_stock(s, today=TODAY)


def test_stale_prices_are_flagged():
    s = good_stock()
    s.prices = s.prices.loc[:"2026-08-01"]
    assert any("stale" in f for f in check_stock(s, today=TODAY))


def test_price_jump_is_flagged():
    s = good_stock()
    s.prices.iloc[-5, s.prices.columns.get_loc("Close")] = 500.0
    assert "suspicious one-day price jump" in check_stock(s, today=TODAY)


def test_old_price_glitch_is_ignored():
    s = good_stock()
    s.prices.iloc[10, s.prices.columns.get_loc("Close")] = 500.0  # year 2020, outside window
    assert "suspicious one-day price jump" not in check_stock(s, today=TODAY)


def test_empty_stock_is_flagged_not_crashing():
    flags = check_stock(StockData(symbol="X", currency=""), today=TODAY)
    assert "no prices" in flags and "no currency" in flags


def test_financials_are_excluded():
    assert is_excluded_sector("Financial Services")
    assert not is_excluded_sector("Technology")


def test_universe_loads_without_duplicates():
    df = load_universe()
    assert {"symbol", "name"} <= set(df.columns)
    assert len(df) == df["symbol"].nunique() > 0


def test_duplicate_symbols_rejected(tmp_path):
    f = tmp_path / "u.csv"
    f.write_text("symbol,name\nA,a\nA,again\n")
    with pytest.raises(ValueError):
        load_universe(f)
