from dataclasses import dataclass

import pandas as pd


@dataclass
class BacktestResult:
    average_1d_return: float
    average_5d_return: float
    average_20d_return: float


class EventBacktester:
    def run(self, df: pd.DataFrame) -> BacktestResult:
        if df.empty:
            return BacktestResult(0.0, 0.0, 0.0)
        return BacktestResult(
            average_1d_return=round(df['ret_1d'].mean(), 4),
            average_5d_return=round(df['ret_5d'].mean(), 4),
            average_20d_return=round(df['ret_20d'].mean(), 4),
        )
