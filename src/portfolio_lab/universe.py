"""The stock universe: a CSV we maintain by hand.

Only symbol and name live in the file. Sector, country and currency come
from the data source, so there is one place to keep them correct.
Banks and insurers are excluded in v1: Yahoo doesn't report gross profit,
operating income or EBITDA for them, so our quality scores don't apply.
Scoring financials separately is a planned later lesson.
"""

from pathlib import Path

import pandas as pd

UNIVERSE_PATH = Path(__file__).resolve().parents[2] / "data" / "universe.csv"
EXCLUDED_SECTORS = {"Financial Services"}


def load_universe(path: Path = UNIVERSE_PATH) -> pd.DataFrame:
    df = pd.read_csv(path, comment="#", skipinitialspace=True)
    if df["symbol"].duplicated().any():
        dupes = df.loc[df["symbol"].duplicated(), "symbol"].tolist()
        raise ValueError(f"duplicate symbols in universe: {dupes}")
    return df


def is_excluded_sector(sector: str | None) -> bool:
    return sector in EXCLUDED_SECTORS
