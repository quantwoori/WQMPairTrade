from pairspread.PSprove import ProvePairs
from pairspread.PSspread import Spread


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
    spd = Spread(s1, s2)
    ps = spd.get_price(365)
    break