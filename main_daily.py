from pairspread.PSprove import ProvePairs
from pairspread.PSspread import Spread

from datetime import datetime, timedelta

"""
Starting Pair Trade

    step 1) Find pairs
        - Correlation test.
            -> Historical return correlation to determine pairs
            -> Note: Use "PRICE SPREAD"
    step 2) Find Hedge Ratios
        - OLS, TLS, Johansen Cointegration Test etc.
        - For this case we will use TLS
    step 3)
        - Rules for Entry, Exit, and Loss Cut

"""

# Step 1) Get Pairs
p = ProvePairs()
approve = p.test_pairs()

# Step 2) Find Hedge Ratios
for stock_pairs in approve:
    s1, s2 = stock_pairs
    # Get Spread
    spd = Spread(s1, s2)
    ps = spd.get_price(600)
    ps = spd.get_spread(ps)

    # Trade Signals
    bsig, ssig = spd.trade_signal_bt(ps)
    td = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')
    if td in bsig:
        print("=========Trade Signal=========")
        print(f">> Date {td} in bsig")
        print(f">> Buy {s1}")
        print(f">> Sell {s2}")
        print("==============================")
    elif td in ssig:
        print("=========Trade Signal=========")
        print(f">> Date {td} in ssig")
        print(f">> Sell {s1}")
        print(f">> Buy {s2}")
        print("==============================")
    else:
        print("Nah")

