from pairspread.PSpair import Pairs

from datetime import datetime
from dateutil.relativedelta import relativedelta
from typing import List, Tuple


class ProvePairs:
    """
        step 1) Find pairs
            - Correlation test.
                -> Historical return correlation to determine pairs
                -> Note: Use "PRICE SPREAD"
    """
    @staticmethod
    def _create_test_pairs(num:int) -> List:
        dt = datetime.now()
        test_dates = [dt - relativedelta(months=i) for i in range(num)]
        return test_dates

    @staticmethod
    def _drop_duplicate(t:[tuple]) -> [Tuple]:
        tmp = set()
        result = list()
        for pair in t:
            s0, s1 = pair
            if (s1, s0) not in tmp:
                tmp.add((s1, s0))
                tmp.add((s0, s1))

                result.append((s0, s1))
        return result

    def test_pairs(self, corr_month:int=12, corr_thres:float=0.70, corr_calc_dates:int=365) -> List:
        td = self._create_test_pairs(corr_month)
        # Test set
        test_first = True
        test_dict = dict()
        for ed in td:
            p = Pairs(end_date=ed)
            univ = p.mnt_universe()

            corr_pairs = p.create_pairs(
                p.get_hist_prc(univ, howmany=corr_calc_dates),
                thres=corr_thres,
                similar=True
            )
            if test_first is True:
                # test_first is True => set standard
                for k, v in corr_pairs.items():
                    for stk in v:
                        test_dict[(k, stk)] = 0
                test_first = False
                print(f"[ProvePairs] >>> compare month process completed. {ed}")
            else:
                # compare the result with test_first.
                # if (k, v) set is in keys, add 1
                # if (k, v): 12 <- This means that correlation above corr_thres:float
                # is achieved continuously throughout 12 months
                for k, v in corr_pairs.items():
                    for stk in v:
                        if (k, stk) in test_dict.keys():
                            test_dict[(k, stk)] += 1
                print(f"[ProvePairs] >>> test month process completed. {ed}")
        return self._drop_duplicate([k for k, v in test_dict.items() if v >= 6])


if __name__ == "__main__":
    pp = ProvePairs()
    s = pp.test_pairs()
