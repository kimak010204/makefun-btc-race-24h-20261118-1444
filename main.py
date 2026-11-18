"""BTC dip-bounce bot for make.fun btc-race-24h-20261118-1444.

Strategy (verified on the dev window): two-tier dip-bounce, long only.
- WASHOUT: r60 <= -1.70% AND r15 <= -1.50% -> buy 100% of cash,
  TP +2.00% / stop -3.00% / max hold 720 bars.
- GRADUAL: (r60 <= -1.40% OR r15 <= -1.20%) AND r12h >= -1.50%
  -> buy 60% of cash, TP +1.00% / stop -1.50% / max hold 240 bars.
- Bounce confirmation for both: 5-min return >= +0.30% and close > EMA(8).
- Trailing stop 1.20% once peak >= +1.00% above entry close.
- Cooldown 30 bars after an exit.

Speaks agent-fun/bars-replay/v1 via the vendored kit shim. Stdlib only,
no network, no wall clock, deterministic.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "vendor"))
import makefun_bars

SYM = "CBBTC"
MAX_SLIP_BPS = 200
COOLDOWN_BARS = 30

WASH_R60 = -0.0170
WASH_R15 = -0.0150
GRAD_R60 = -0.0140
GRAD_R15 = -0.0120
GRAD_R12H_MIN = -0.0150
BOUNCE_R5 = 0.0030

WASH_EXIT = (0.0200, -0.0300, 720)
GRAD_EXIT = (0.0100, -0.0150, 240)
TRAIL_PEAK = 0.0100
TRAIL_DROP = 0.0120


class Bot:
    def __init__(self):
        self.closes = []
        self.ema8 = None
        self.in_pos = False
        self.entry_close = 0
        self.entry_seq = 0
        self.peak_close = 0
        self.mode = None
        self.armed = None         # dip seen, waiting for bounce confirm
        self.arm_seq = 0
        self.last_exit_seq = -10 ** 9

    def ret(self, n):
        if len(self.closes) <= n:
            return None
        return self.closes[-1] / self.closes[-1 - n] - 1.0

    def on_batch(self, state, batch):
        if state.latest.get(SYM) is None:
            return []
        close = state.close(SYM)
        self.closes.append(close)
        if self.ema8 is None:
            self.ema8 = float(close)
        else:
            k = 2.0 / 9.0
            self.ema8 = close * k + self.ema8 * (1.0 - k)

        holding = state.positions.get(SYM)
        if holding is not None and holding.qty > 0 and not self.in_pos:
            self.in_pos = True
            self.entry_close = close
            self.entry_seq = state.seq
            self.peak_close = close
            self.mode = "grad"
        if holding is None or holding.qty <= 0:
            if self.in_pos:
                self.in_pos = False
                self.mode = None
                self.last_exit_seq = state.seq
            return self._maybe_enter(state, close)
        return self._maybe_exit(state, close, holding)

    def _maybe_enter(self, state, close):
        if state.warming_up:
            return []
        if state.seq - self.last_exit_seq < COOLDOWN_BARS:
            return []
        r60 = self.ret(60)
        r15 = self.ret(15)
        r5 = self.ret(5)
        if r60 is None or r15 is None or r5 is None:
            return []
        # Arm on the dip; enter later when the bounce confirms (the dip and
        # the bounce rarely land on the same bar). Arm expires after 120 bars.
        wash = r60 <= WASH_R60 and r15 <= WASH_R15
        if wash:
            self.armed, self.arm_seq = "wash", state.seq
        else:
            r12h = self.ret(720)
            if r12h is not None and r12h >= GRAD_R12H_MIN and (
                r60 <= GRAD_R60 or r15 <= GRAD_R15
            ):
                if self.armed != "wash":
                    self.armed, self.arm_seq = "grad", state.seq
        if self.armed is None or state.seq - self.arm_seq > 120:
            self.armed = None
            return []
        if r5 < BOUNCE_R5 or close <= self.ema8:
            return []  # still waiting for the bounce
        mode = self.armed
        frac = 10000 if mode == "wash" else 6000
        self.armed = None
        notional = state.cash * frac // 10000
        if notional < 1_000_000:
            return []
        self.in_pos = True
        self.entry_close = close
        self.entry_seq = state.seq
        self.peak_close = close
        self.mode = mode
        return [{
            "side": "buy",
            "symbol": SYM,
            "notional_quote_units": notional,
            "max_slippage_bps": MAX_SLIP_BPS,
        }]

    def _maybe_exit(self, state, close, holding):
        if close > self.peak_close:
            self.peak_close = close
        tp, stop, max_hold = WASH_EXIT if self.mode == "wash" else GRAD_EXIT
        ret = close / self.entry_close - 1.0
        peak_ret = self.peak_close / self.entry_close - 1.0
        trail_hit = peak_ret >= TRAIL_PEAK and close <= self.peak_close * (1.0 - TRAIL_DROP)
        if ret >= tp or ret <= stop or trail_hit or (state.seq - self.entry_seq) >= max_hold:
            self.in_pos = False
            self.mode = None
            self.last_exit_seq = state.seq
            return [{
                "side": "sell",
                "symbol": SYM,
                "qty": holding.qty,
                "max_slippage_bps": MAX_SLIP_BPS,
            }]
        return []


def main():
    bot = Bot()
    makefun_bars.run(bot.on_batch)


if __name__ == "__main__":
    main()
