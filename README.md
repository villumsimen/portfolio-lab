# portfolio-lab

A **paper-trading learning platform**. No real money. It picks at most 8
large global stocks with a quality + value strategy, simulates the trades
(with realistic costs), and compares the result against global benchmarks.
The goal is to learn how investing works well enough to decide, one day,
whether to put real money on the table.

> Not financial advice. Paper results say little about real results, and
> short periods are mostly noise. The honest scoreboard is 2+ years against
> MSCI World.

## Design in one place

| Area | Choice |
|---|---|
| Universe | ~300-500 large global stocks, a file we maintain (`data/universe.csv`) |
| Strategy | Quality + value, scored relative to each stock's sector |
| Portfolio | Max 8 stocks, risk-based weights, max 3 per sector and 4 per country |
| Selling | Only when a stock falls out of the top ~15 (a buffer against churn) |
| Timing | Weekly trades, daily value and page refresh |
| Realism | Fees, FX cost, slippage, dividends in total return, all in NOK |
| Benchmarks | MSCI World (main), S&P 500, OSEBX |
| Data | Free (Yahoo) first, behind a layer so it can be swapped |
| Fundamentals delay | 6 months in backtests, to avoid peeking into the future |
| Bad data | Skip the stock and flag it in the report |
| Output | Static GitHub Pages site + short weekly email |
| Runs on | GitHub Actions |

Complexity is added over time as lessons: AI explanations, news flags, and
extra risk rules (stop-loss, drawdown halt, volatility targeting, regime
filter) each come later, one at a time, compared against the baseline.

## Phases

0. Setup (this)
1. Data layer and universe
2. Scoring
3. Portfolio and paper broker
4. Backtest (learning module, not proof)
5. Automation on GitHub Actions
6. Site and weekly email

## Learning material

- [`docs/glossary.md`](docs/glossary.md): every term defined in plain language
- [`docs/journal.md`](docs/journal.md): what happened and what we learned, week by week

## Repo rules

- Public repo. **Never commit secrets** (API keys, broker credentials, real holdings). Keys go in GitHub Secrets.
- Real money, when and if it comes, lives in a **separate private repo** that reads this project's output.
