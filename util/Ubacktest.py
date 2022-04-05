from dbm.DBquant import PyQuantiwise

import pandas as pd

from datetime import datetime, timedelta


class RatioBackTest:
    def __init__(self, stock1:str, stock2:str, initial:(float, float), initial_money:int, test_dates:int):
        assert initial[0] <= 1
        assert initial[1] <= 1
        assert sum(initial) == 1
        # CLASS MODULES
        self.qt = PyQuantiwise()

        # IMMUTABLE CONSTANT
        self.STK1, self.STK2 = stock1, stock2

        self.ENDDATE = datetime.now() - timedelta(days=1)
        self.STARTDATE = datetime.now() - timedelta(days=test_dates)
        self.PRCDATA = self.get_price()

        self.ACCOUNT = initial_money
        self.RSTK1, self.RSTK2 = initial

    def get_price(self, dfmt='%Y%m%d') -> pd.DataFrame:
        r = self.qt.stk_data_multi(
            stock_code_ls=[self.STK1, self.STK2],
            start_date=self.STARTDATE.strftime(dfmt),
            end_date=self.ENDDATE.strftime(dfmt),
            item='수정주가'
        )
        r.VAL = r.VAL.astype('float32')
        r.columns = ['date', 'id', 'prc']
        r = r.pivot_table(values='prc', index='date', columns='id')
        r = r.sort_index()
        return r

    def comp_portfolio(self):
        rtn = self.PRCDATA.pct_change().dropna().reset_index()

        result = list()
        for date, rtn0, rtn1 in rtn.to_numpy():
            result.append(
                (date, rtn0 * self.RSTK1, rtn1 * self.RSTK2)
            )
        result = pd.DataFrame(result, columns=['date'] + list(self.PRCDATA.columns))
        return result.set_index('date')

    def test_portfolio(self, buy_stk0_dates, sell_stk0_dates):
        bd = set(buy_stk0_dates)
        sd = set(sell_stk0_dates)

        rtn = self.PRCDATA.pct_change().dropna().reset_index()

        result = list()
        for date, rtn0, rtn1 in rtn.to_numpy():
            cond_buy = date in bd
            cond_sell = date in sd
            cond_norm = (date not in bd) and (date not in sd)

            if cond_norm:
                result.append(
                    (date, rtn0 * self.RSTK1, rtn1 * self.RSTK2)
                )
            if cond_buy:
                # Stock0 is undervalued
                # Buy Stock0 and Sell Stock1
                result.append(
                    (date, rtn0 * 1, rtn1 * 0)
                )
            if cond_sell:
                # Stock0 is overpriced
                # Sell Stock0 and Buy Stock1
                result.append(
                    (date, rtn0 * 0, rtn1 * 1)
                )
        result = pd.DataFrame(result, columns=['date'] + list(self.PRCDATA.columns))
        return result.set_index('date')


if __name__ == "__main__":
    s0, s1 = '086790', '105560'
    backtest = RatioBackTest(
        stock1=s0,
        stock2=s1,
        initial=(0.5, 0.5),
        initial_money=10**8,
        test_dates=730
    )
    cp = backtest.comp_portfolio()