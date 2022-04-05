import numpy as np

from dbm.DBmssql import MSSQL
from dbm.DBquant import PyQuantiwise

import pandas as pd
import numpy as np
from statsmodels.tsa.stattools import coint

from datetime import datetime, timedelta
from typing import Iterable, Dict


class Pairs:
    def __init__(self, end_date:datetime, target_index:str='ks200'):
        self.server = MSSQL.instance()
        self.qt = PyQuantiwise()
        self.dt = end_date
        self.universe = self.mnt_universe(tgt=target_index)

    def mnt_universe(self, tgt:str='ks200'):
        col = ['stk_no']
        cnd = [
            f'year = {self.dt.year}',
            f'chg_no = {self.dt.month}',
            f"ind_ = '{tgt}'"
        ]
        cnd = ' and '.join(cnd)
        q = self.server.select_db(
            database="WSOL",
            schema="dbo",
            table='indcomp',
            column=col,
            condition=cnd
        )
        return list(sum(q, ()))

    def get_hist_prc(self, stks:Iterable, howmany:int, dfmt='%Y%m%d'):
        p = self.qt.stk_data_multi(
            stock_code_ls=stks,
            start_date=(self.dt - timedelta(days=howmany)).strftime(dfmt),
            end_date=(self.dt - timedelta(days=1)).strftime(dfmt),
            item='수정주가'
        )
        p.VAL = p.VAL.astype('float32')
        p.columns = ['date', 'id', 'prc']
        p = p.pivot_table(index='date', columns='id')
        return p

    def create_pairs_coint(self, prc:pd.DataFrame, thres:float) -> Dict:
        # Prep Data
        d = prc.dropna(axis=1)
        n = d.shape[1]
        k = d.keys()

        # Result containers
        score_matrix, pval_matrix = (
            np.zeros((n, n)),
            np.zeros((n, n))
        )
        res = dict()

        for i in range(n):
            for j in range(i + 1, n):
                s0, s1 = d[k[i]], d[k[j]]
                result = coint(s0, s1)

                score_matrix[i, j] = result[0]
                pval_matrix[i, j] = result[1]

                if result[1] < thres:
                    if k[i][1] not in res.keys():
                        res[k[i][1]] = [k[j][1]]
                    else:
                        res[k[i][1]].append(k[j][1])
        return res

    def create_pairs_corr(self, prc:pd.DataFrame, thres:float, similar:bool=True) -> Dict:
        # d = prc.dropna(axis=1).pct_change().dropna().corr()
        # Delete Stocks with short periods
        d = prc.dropna(axis=1)
        d = d.pct_change().dropna()
        crr = d.corr()
        if similar is True:
            return self._find_highcorr(crr, thres)
        else:
            return self._find_lowcorr(crr, thres)

    @staticmethod
    def _find_lowcorr(correlation:pd.DataFrame, thres:float) -> Dict:
        result = dict()
        for c in correlation.columns:
            _, stk = c

            # Sort low correlation
            low = correlation[c].loc[correlation[c] <= thres]
            temp = list()
            for l in low.index:
                _, low_stk = l
                if stk != low_stk:
                    temp.append(low_stk)

            if (len(temp) > 0) and (stk not in result.keys()):
                result[stk] = temp

        return result

    @staticmethod
    def _find_highcorr(correlation:pd.DataFrame, thres:float) -> Dict:
        result = dict()
        for c in correlation.columns:
            _, stk = c

            # Sort high correlation
            high = correlation[c].loc[correlation[c] >= thres]
            temp = list()
            for h in high.index:
                _, high_stk = h
                if stk != high_stk:
                    temp.append(high_stk)

            # Dictionary
            if (len(temp) > 0) and (stk not in result.keys()):
                result[stk] = temp

        return result
