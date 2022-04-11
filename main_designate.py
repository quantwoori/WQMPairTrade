from pairspread.PSspread import Spread


# Calculate Spread from current spread pairs
# spread pairs are designated

designate = (
    ("138930", "086790"),
    ("024110", "105560")
)

for stock_pairs in designate:
    s1, s2 = stock_pairs
    # Get Spread
    spd = Spread(s1, s2)
    ps = spd.get_price(600)
    ps = spd.get_spread(ps)
