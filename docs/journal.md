# Journal

What happened and what we learned. Newest first.

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
