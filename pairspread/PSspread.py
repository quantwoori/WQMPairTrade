# Data
from dbm.DBmssql import MSSQL
from dbm.DBquant import PyQuantiwise
import pandas as pd

# Miscellaneous
from typing import Set
from datetime import datetime, timedelta


class Spread:
    """
        step 2) Find Hedge Ratios
            - OLS, TLS, Johansen Cointegration Test etc.
            - For this case we will use TLS
    """
    def __init__(self, stock1:str, stock2:str):
        # Constant
        print(f"[Hedge Calculation] {stock1} & {stock2}")
        self.STOCKA = stock1
        self.STOCKB = stock2
        self.DT = datetime.now()

        # Modules
        self.server =MSSQL.instance()
        self.qt = PyQuantiwise()

    def get_price(self, howmany:int, dfmt='%Y%m%d') -> pd.DataFrame:
        target_stocks = [self.STOCKA, self.STOCKB]

        # Date Info
        sd, ed = (
            (self.DT - timedelta(days=howmany)).strftime(dfmt),
            (self.DT - timedelta(days=1)).strftime(dfmt)
        )

        # Price
        ps = self.qt.stk_data_multi(
            stock_code_ls=target_stocks,
            start_date=sd,
            end_date=ed,
            item='수정주가'
        )
        ps.VAL = ps.VAL.astype('float32')
        ps.columns = ['date', 'id', 'prc']
        ps = ps.pivot_table(values='prc', index='date', columns='id')
        ps = ps.sort_index()
        return ps

    def get_spread(self, prc:pd.DataFrame) -> pd.DataFrame:
        p = prc.copy(deep=True)
        p['spread_AB_tmp'] = p[self.STOCKA] - p[self.STOCKB]
        p['spread_AB'] = (
                (
                        p['spread_AB_tmp'] - (p['spread_AB_tmp'].mean())
                ) / p['spread_AB_tmp'].std()
        )
        return p[prc.columns.tolist() + ['spread_AB']]

    @staticmethod
    def trade_signal_bt(spread_data:pd.DataFrame, buy_threshold:float=-1.0,
                        sell_threshold:float=1.0) -> (Set, Set):
        """
        Strictly for backtesting
        Spread Calc Now

        Case #1. StockA - StockB > 0
            - Stock B is undervalued
            - Sell Stock A, and Buy Stock B

        Case #2. StockA - StockB < 0
            - Buy Stock A and Sell Stock B

        Calculate it from Stock A's perspective

        :return (set if Case #2) (set if Case #1)
        """
        d = spread_data.copy(deep=True).shift(1)  # After Signal Buy Next Day
        d = d.reset_index().to_numpy()
        b, s = set(), set()
        for date, _, _, spread in d:
            if spread >= sell_threshold:
                # Case #1
                s.add(date)
            elif spread <= buy_threshold:
                # Case #2
                b.add(date)
        return b, s


if __name__ == '__main__':
    spd = Spread('086790', '105560')
    ps = spd.get_price(1000)
    pss = spd.get_spread(ps)
