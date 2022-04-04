from pairspread.PSpair import Pairs

from datetime import datetime

end_date = datetime.now()
p = Pairs(end_date)
r = p.create_pairs(
    p.get_hist_prc(p.mnt_universe(),
                   howmany=30),
    thres=0.8,
    similar=True
)
