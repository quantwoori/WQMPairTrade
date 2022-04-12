from pairspread.PSprove import ProvePairs
from pairspread.PSspread import Spread
from util.Ubacktest import RatioBackTest

import pandas as pd
import matplotlib.pyplot as plt

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
    backtest = RatioBackTest(
        stock1=s1,
        stock2=s2,
        initial=(0.5, 0.5),
        initial_money=10**8,
        test_dates=730
    )
    cp = backtest.comp_portfolio()
    tp = backtest.test_portfolio(
        buy_stk0_dates=bsig,
        sell_stk0_dates=ssig
    )

    # Step 3) without losscut
    spread = pd.DataFrame()
    spread['comparison'] = cp.cumsum().sum(axis=1)
    spread['test'] = tp.cumsum().sum(axis=1)

    # Step 3 - 1) plotting
    spread.plot()
    plt.title(f"{s1} & {s2} Pair Trade")
    plt.savefig(f"C:/Users/wooriam/PycharmProjects/WQMPairTrade/report/{s1}_{s2}_pt.png")
    plt.close()

