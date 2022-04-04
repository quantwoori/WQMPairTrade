# Data
from dbm.DBmssql import MSSQL
from dbm.DBquant import PyQuantiwise

# Statistics model


# Miscellaneous
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

    def get_price(self, howmany:int, dfmt='%Y%m%d'):
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
        ps['spread_AB'] = ps[self.STOCKA] - ps[self.STOCKB]
        return ps


if __name__ == '__main__':
    spd = Spread('032350', '114090')
    ps = spd.get_price(365)
