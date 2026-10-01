"""Phase 1 probe: how good is free Yahoo data for a spread of global stocks?

Checks, per ticker: price history length, FX, and whether the fundamentals
we need for quality + value scoring are available (and how far back).
Prints a table; changes nothing. Run: .venv/bin/python scripts/probe_data.py
"""

import warnings

import pandas as pd
import yfinance as yf

warnings.filterwarnings("ignore")

# A deliberate mix: US, Europe, Nordics, Asia, plus banks/insurers, whose
# statements look different from normal companies.
TICKERS = {
    "AAPL": "US tech",
    "JNJ": "US health",
    "JPM": "US bank",
    "XOM": "US energy",
    "NESN.SW": "Swiss food",
    "ASML.AS": "Dutch semis",
    "SAP.DE": "German software",
    "SHEL.L": "UK energy",
    "NOVO-B.CO": "Danish pharma",
    "EQNR.OL": "Norway energy",
    "DNB.OL": "Norway bank",
    "7203.T": "Japan autos",
    "9984.T": "Japan holding",
    "005930.KS": "Korea electronics",
    "0700.HK": "HK internet",
    "RY.TO": "Canada bank",
    "BHP.AX": "Australia mining",
}

# Fundamentals the scoring needs, mapped to Yahoo row names.
NEEDED = {
    "income": ["Net Income", "Total Revenue", "Gross Profit", "Operating Income", "EBITDA"],
    "balance": ["Stockholders Equity", "Total Assets", "Total Debt"],
    "cashflow": ["Operating Cash Flow", "Free Cash Flow"],
}


def years_of(df: pd.DataFrame, row: str) -> int:
    if df is None or df.empty or row not in df.index:
        return 0
    return int(df.loc[row].notna().sum())


def probe(symbol: str) -> dict:
    t = yf.Ticker(symbol)
    out = {"symbol": symbol}
    try:
        hist = t.history(period="max", auto_adjust=False)
        out["px_years"] = round(len(hist) / 252, 1)
        out["px_last"] = None if hist.empty else hist.index[-1].strftime("%Y-%m-%d")
        out["divs"] = int((hist.get("Dividends", pd.Series(dtype=float)) > 0).sum()) if not hist.empty else 0
    except Exception as e:  # noqa: BLE001
        out["px_error"] = str(e)[:40]
    try:
        info = t.info
        out["ccy"] = info.get("currency")
        out["sector"] = info.get("sector")
        out["country"] = info.get("country")
    except Exception as e:  # noqa: BLE001
        out["info_error"] = str(e)[:40]
    try:
        stmts = {
            "income": t.income_stmt,
            "balance": t.balance_sheet,
            "cashflow": t.cashflow,
        }
        missing, depth = [], []
        for kind, rows in NEEDED.items():
            for row in rows:
                n = years_of(stmts[kind], row)
                depth.append(n)
                if n == 0:
                    missing.append(row)
        out["fund_years_min"] = min(depth) if depth else 0
        out["fund_years_max"] = max(depth) if depth else 0
        out["missing"] = ", ".join(missing) or "-"
    except Exception as e:  # noqa: BLE001
        out["fund_error"] = str(e)[:40]
    return out


if __name__ == "__main__":
    rows = []
    for sym, label in TICKERS.items():
        r = probe(sym)
        r["label"] = label
        rows.append(r)
        print(f"done {sym}", flush=True)
    df = pd.DataFrame(rows)
    cols = [c for c in ["symbol", "label", "ccy", "sector", "country", "px_years", "px_last",
                        "divs", "fund_years_min", "fund_years_max", "missing"] if c in df.columns]
    with pd.option_context("display.width", 250, "display.max_columns", None,
                           "display.max_colwidth", 60):
        print(df[cols].to_string(index=False))
    err_cols = [c for c in df.columns if c.endswith("_error")]
    if err_cols:
        print("\nERRORS:\n", df[["symbol", *err_cols]].dropna(how="all", subset=err_cols).to_string(index=False))
