"""Load every universe stock, run quality checks, print who passes.

Run: .venv/bin/python scripts/check_universe.py
"""

from portfolio_lab.data.quality import check_stock
from portfolio_lab.data.yahoo import YahooSource
from portfolio_lab.universe import is_excluded_sector, load_universe

source = YahooSource()
ok, skipped, excluded = [], [], []
for row in load_universe().itertuples():
    try:
        data = source.stock(row.symbol)
    except Exception as e:  # noqa: BLE001
        skipped.append((row.symbol, [f"fetch failed: {str(e)[:50]}"]))
        continue
    if is_excluded_sector(data.sector):
        excluded.append((row.symbol, data.sector))
        continue
    flags = check_stock(data)
    (skipped.append((row.symbol, flags)) if flags else ok.append((row.symbol, data)))
    print(f"checked {row.symbol}", flush=True)

print(f"\nUSABLE ({len(ok)}):")
for sym, d in ok:
    print(f"  {sym:<10} {d.currency:<4} {d.sector:<24} {d.country:<16} last close {d.prices['Close'].iloc[-1]:,.2f}")
print(f"\nEXCLUDED financials ({len(excluded)}): {[s for s, _ in excluded]}")
print(f"\nSKIPPED ({len(skipped)}):")
for sym, flags in skipped:
    print(f"  {sym:<10} {'; '.join(flags)}")
