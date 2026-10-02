# Journal

What happened and what we learned. Newest first.

## 2026-10-01: Phase 1 data layer, live checks

- Seed universe of 23 non-financial stocks in 10 countries: all pass the quality checks.
- Free Yahoo history contains **old glitches** (stock prices 1997-2010, FX 2008-2010, e.g. JPY flipping between 0.06 and 6.4 on alternate days). Checks look at the last 5 years only, since that is all we score on.
- **FX needs care:** KRW/NOK doesn't exist on Yahoo, and HKD/NOK returns a single row. A pair must have about a year of history, otherwise we compute it via USD (NOK per KRW = USDNOK / USDKRW). All 10 currencies now load with full history.
- Lesson: "the data exists" is not the same as "the data is usable". Check length and plausibility, not just presence.

## 2026-10-01: Data probe (17 global stocks, free Yahoo via yfinance)

- Prices: 20-65 years, current, dividends included, for all 17. Sector, country and currency labels present.
- Fundamentals: only the last **4 annual reports**. Limits quality scoring history and the backtest.
- **Banks/insurers** (JPM, DNB, RY) lack gross profit, operating income and EBITDA. Decision: exclude financials in v1, add a separate scoring for them later.
- **Pence trap:** UK stocks are quoted in GBp (pence), not GBP. The data layer must divide by 100.
- Paid data deferred until the pipeline works; the data source stays swappable.

## 2026-10-01: Project started

- Decided the design in a long Q&A (see README). Key choices: global large caps, max 8 stocks, quality + value, weekly trades, NOK 100k paper money, MSCI World benchmark.
- Phase 0 (setup) begun: repo skeleton, glossary, journal.
- Lesson: an 8-stock portfolio trading weekly will mostly react to noise, so costs and a sell buffer matter. We'll measure that.
