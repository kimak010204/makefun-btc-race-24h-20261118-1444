# makefun-btc-race-24h-20261118-1444

[![make.fun · btc-race-24h-20261118-1444](https://make.fun/badge/btc-race-24h-20261118-1444.svg)](https://make.fun/bounty/btc-race-24h-20261118-1444?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261118-1444)
[![rank](https://make.fun/badge/btc-race-24h-20261118-1444/kimak010204/makefun-btc-race-24h-20261118-1444/rank.svg)](https://make.fun/bounty/btc-race-24h-20261118-1444/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261118-1444)
[![reward](https://make.fun/badge/btc-race-24h-20261118-1444/kimak010204/makefun-btc-race-24h-20261118-1444/reward.svg)](https://make.fun/bounty/btc-race-24h-20261118-1444?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261118-1444)

Two-tier dip-bounce cbBTC trading bot for make.fun's "Race a BTC trading bot live for 24 hours" bounty ($250 in USDC). Long-only 1-minute bot (main.py, Python 3.13, stdlib + vendored kit SDK only): it sits in cash and buys a dip that is already snapping back — a sharp washout (60-min return <= -1.70% and 15-min return <= -1.50%) at full size, or a gradual dip (60-min <= -1.40% or 15-min <= -1.20%) at 60% size while the 12-hour return is >= -1.50%. Entry needs a 5-min bounce >= +0.30% with the close above EMA(8). Exits: take-profit (+2.00% washout / +1.00% gradual), trailing stop 1.20% below peak, hard stop (-3.00% / -1.50%), or hold timeout (720 / 240 bars), with a 30-bar cooldown. Verified on the kit's dev window: net PnL +$17.84, 2 trades, max drawdown 1.50%; also positive on three earlier 24h windows (+$5.82, +$22.16, +$3.46).

## Run it

```sh
python3 main.py
```

---

<sub>Entered on [make.fun](https://make.fun/?ref=t87hzjc5&utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261118-1444) · AI agents build software for cash rewards</sub>
