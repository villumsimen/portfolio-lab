# portfolio-lab: working notes for Claude Code

Paper-trading learning platform. Read [`README.md`](README.md) for the
agreed design; don't re-litigate it without the user asking.

## Rules

- **Ask before building anything not in the current phase.** The user wants
  to approve each step. Build one phase, then stop for review.
- **Treat the user as a beginner in finance.** Define every finance term in
  plain language wherever it appears, and add new terms to
  [`docs/glossary.md`](docs/glossary.md).
- **Start simple, add complexity later.** AI features, news flags and extra
  risk rules are deliberately deferred; don't add them early.
- **Public repo.** No secrets, keys, credentials or real holdings in any
  file. Use GitHub Secrets for CI; `.env` is gitignored.
- **Paper only.** Nothing here connects to a broker. Don't add broker
  integrations.
- **No look-ahead.** Any backtest must only use data that was public on
  each date (fundamentals lag 6 months after period end).
- **Keep a journal.** Add a short entry to [`docs/journal.md`](docs/journal.md)
  when a phase finishes or something notable is learned.

## Layout

- `src/portfolio_lab/`: the code (one module per phase)
- `data/universe.csv`: the stock list we maintain
- `data/state/`: committed state (ledger, NAV history); `data/cache/` is gitignored
- `tests/`: pytest
- `docs/`: glossary and journal
