from pairspread.PSprove import ProvePairs
import pandas as pd

pp = ProvePairs()
s = pp.test_pairs(corr_thres=0.8, corr_calc_dates=30, corr_count=11)
s = pd.DataFrame(s)
print(s)