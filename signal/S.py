from dbm.DBmssql import MSSQL
from pairspread.PSprove import ProvePairs
from pairspread.PSspread import Spread

import pandas as pd

from datetime import datetime
from typing import List


class DailyPairs:
    signal_name = "pt_v1_{}_{}"

    def __init__(self, desig:(tuple)=None):
        # Class local modules
        self.server = MSSQL.instance()
        self.server.login(id='wsol1', pw='wsol1')

        if desig is None:
            p = ProvePairs()
            self.approve = p.test_pairs()
        else:
            self.approve = desig
        self.DT = datetime.now()

    def gen_signals(self, insertion:bool=False):
        for stock_pairs in self.approve:
            s1, s2 = stock_pairs

            # Get Spread
            spd = Spread(s1, s2)
            ps = spd.get_price(600)
            ps = spd.get_spread(ps)
            signal, signal_strn = self.__gen_signals(spread_data=ps)

            if signal == 1:
                # Buy s1, Sell s2
                row = [
                    (
                        self.DT.strftime("%Y-%m-%d"),
                        signal_strn,
                        "spread_buy",
                        s1,
                        self.signal_name.format(s1, s2)),
                    (
                        self.DT.strftime('%Y-%m-%d'),
                        signal_strn, "spread_sell",
                        s2,
                        self.signal_name.format(s1, s2)
                    )
                ]
            elif signal == -1:
                # Buy s2, Sell s1
                row = [
                    (
                        self.DT.strftime('%Y-%m-%d'),
                        signal_strn,
                        "spread_buy",
                        s2,
                        self.signal_name.format(s1, s2)
                    ),
                    (
                        self.DT.strftime('%Y-%m-%d'),
                        signal_strn,
                        "spread_sell",
                        s1,
                        self.signal_name.format(s1, s2)
                    )
                ]
            else:
                # No Signal
                row = list()

            if insertion:
                self.ins_signal(row)

    def ins_signal(self, row:[tuple]):
        if len(row) != 0:
            print(row)
            c = ["date", "sigstren", "sig", "stk", "sigtyp"]
            self.server.insert_row(
                database="WSOL",
                schema='dbo',
                table_name='sig',
                col_=c,
                rows_=row
            )

    @staticmethod
    def __gen_signals(spread_data:pd.DataFrame, buy_threshold:float=-1.0,
                      sell_threshold:float=1.0) -> (int, int):
        # Spread calculated by last day's closing price
        # spread * (10 ** 5) and round, int
        # ^^^^^^^^^^^^^^^^^^
        # to match BIGINT on sig table on Database
        today = spread_data.to_numpy()[-1]
        _, __, spread = today
        if spread <= buy_threshold:
            return 1, int(round(spread * (10 ** 5), 0))
        elif spread >= sell_threshold:
            return -1, int(round(spread * (10 ** 5), 0))
        else:
            return 0, int(round(spread * (10 ** 5), 0))


if __name__ == "__main__":
    daily = DailyPairs()
    daily.gen_signals(True)
