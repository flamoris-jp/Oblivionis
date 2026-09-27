"""
即興の実験: 入力を止めたあと、場は「覚えたものを返す」だけか、「崩して返す」か。

  A  (1–8小節)   グルーヴ
  B  (9–16小節)  3連のポリリズム
  C  (17–48小節) 入力なし (32小節 ≈ 77秒)

条件
  memory    : 揺らぎなし (前回の版)
  fluct     : 揺らぎ + ずれ + 割り込み
  improv    : 上に加えて、自分の音を聴き直す + 疲れ (馴化) + 恒常性 (鳴りたい量を保つ)
  random    : 比較用。improv の C の音を、数と声部はそのまま小節内のランダムな位置に置き直したもの
"""

from __future__ import annotations

import json
import sys
import numpy as np

from music_field import MusicField, MusicParams
from session import HARMONICS, INSTR, render, write_wav, write_midi

P0 = MusicParams()
BAR = 60.0 / P0.bpm * 4
A_BARS, B_BARS, C_BARS = 8, 8, 32
N_BARS = A_BARS + B_BARS + C_BARS
C0 = A_BARS + B_BARS
END_BARS = 6
SLOTS = 48                          # 1小節 = 48 (16分 = 3, 3連8分 = 4 で割り切れる)

CONDITIONS = {
    "memory": {},
    "fluct": dict(phase_noise=0.08, slip_rate=0.12, intrusion_rate=0.35),
    "improv": dict(phase_noise=0.08, slip_rate=0.12, intrusion_rate=0.35,
                   self_listen=0.12, fatigue=0.6, drive_target=3.5),
}


def compose():
    ev, beat = [], BAR / 4
    for bar in range(C0):
        t0 = bar * BAR
        ev += [(t0 + b * beat, "kick") for b in (0, 2)] + [(t0 + b * beat, "snare") for b in (1, 3)]
        if bar < A_BARS:
            ev += [(t0 + k * beat / 2, "hat") for k in range(8)]
        else:
            ev += [(t0 + k * BAR / 6, "marimba") for k in range(6)]
    return sorted(ev)


def run(params: MusicParams, seed: int):
    field = MusicField(HARMONICS, params, seed=seed)
    events = compose()
    ev_i, notes = 0, []
    for s in range(int(N_BARS * BAR / params.dt)):
        t = s * params.dt
        on = []
        while ev_i < len(events) and events[ev_i][0] < t + params.dt:
            on.append(INSTR[events[ev_i][1]])
            ev_i += 1
        if params.drive_target > 0 and t >= (N_BARS - END_BARS) * BAR:     # 終わりの数小節で、鳴りたい気持ちを下げていく
            field.target = params.drive_target * max(0.0, (N_BARS * BAR - t) / (END_BARS * BAR) - 0.15)
        for i in field.step(on):
            notes.append({"t": field.t, "voice": int(i), "n": int(field.n[i]),
                          "freq": float(field.pitch[i]), "vel": float(field.A[i])})
    return field, events, notes


# ------------------------------------------------------------------
# 指標
# ------------------------------------------------------------------
def bar_patterns(notes, b0, b1):
    """小節ごとの「どの声部が、小節内のどの位置で鳴ったか」の集合。"""
    pats = [set() for _ in range(b1 - b0)]
    for nt in notes:
        b = int(nt["t"] // BAR)
        if b0 <= b < b1:
            slot = int(round((nt["t"] % BAR) / BAR * SLOTS)) % SLOTS
            pats[b - b0].add((nt["n"], slot))
    return pats


def _jac(a, b):
    if not a and not b:
        return float("nan")
    return len(a & b) / len(a | b)


def jaccard(a, b, max_shift=4):
    """小節全体を ±max_shift スロット (1スロット = 50ms) までずらして一番重なるときの Jaccard。
    入力が止まるとテンポが少しずつずれるので、ずれを許して「形」を比べる。"""
    if not a and not b:
        return float("nan")
    best = 0.0
    for sh in range(-max_shift, max_shift + 1):
        a2 = {(n, (sl + sh) % SLOTS) for n, sl in a}
        best = max(best, _jac(a2, b))
    return best


def grid_ok(t):
    pos = (t % BAR) / BAR
    d16 = abs(pos * 16 - round(pos * 16)) / 16 * BAR
    d12 = abs(pos * 12 - round(pos * 12)) / 12 * BAR
    return min(d16, d12) < 0.015      # ±15ms (ランダムに置いた場合でも約3割は入る)


def coherence(c_notes):
    """小節ごとに格子を ±75ms までずらしてよいとして、音がどれだけ共通の格子 (16分 ∪ 3連8分) に乗っているか。
    入力が止まると場のテンポは少しずつずれていくので、元のクリックではなく「お互いに揃っているか」を見る。"""
    by_bar = {}
    for n in c_notes:
        by_bar.setdefault(int(n["t"] // BAR), []).append(n["t"] % BAR)
    hits = total = 0
    for pos in by_bar.values():
        pos = np.array(pos)
        best = 0
        for off in np.arange(-0.075, 0.0751, 0.002):
            q = ((pos - off) % BAR) / BAR
            d16 = np.abs(q * 16 - np.round(q * 16)) / 16 * BAR
            d12 = np.abs(q * 12 - np.round(q * 12)) / 12 * BAR
            best = max(best, int(np.sum(np.minimum(d16, d12) < 0.015)))
        hits += best
        total += len(pos)
    return hits / total if total else float("nan")


def metrics(notes, field=None):
    ref_bars = bar_patterns(notes, C0 - 4, C0)                    # B の最後の4小節
    counts = {}
    for pset in ref_bars:
        for x in pset:
            counts[x] = counts.get(x, 0) + 1
    ref = {x for x, c in counts.items() if c >= 2}                # B でよく鳴っていた形
    c_bars = bar_patterns(notes, C0, N_BARS)
    sim_to_B = [jaccard(p, ref) for p in c_bars]
    change = [1 - jaccard(c_bars[k], c_bars[k - 1]) for k in range(1, len(c_bars))]
    c_notes = [n for n in notes if n["t"] >= C0 * BAR]
    b_voices = {n["n"] for n in notes if (C0 - 4) * BAR <= n["t"] < C0 * BAR}
    new_voice_notes = [n for n in c_notes if n["n"] not in b_voices]
    alive_bars = [k for k, p in enumerate(c_bars) if len(p) > 0]
    out = {
        "C_notes": len(c_notes),
        "C_bars_with_sound": len(alive_bars),
        "last_sound_bar_in_C": (max(alive_bars) + 1) if alive_bars else 0,
        "sim_to_B_first8": float(np.nanmean(sim_to_B[:8])),
        "sim_to_B_last8_of_sound": float(np.nanmean([sim_to_B[k] for k in alive_bars[-8:]])) if alive_bars else float("nan"),
        "bar_change_mean": float(np.nanmean([change[k - 1] for k in alive_bars if k >= 1])) if len(alive_bars) > 1 else float("nan"),
        "on_grid": float(np.mean([grid_ok(n["t"]) for n in c_notes])) if c_notes else float("nan"),
        "coherence": coherence(c_notes),
        "new_voice_notes": len(new_voice_notes),
        "new_voices": sorted({n["n"] for n in new_voice_notes}),
        "sim_curve": [None if np.isnan(x) else round(float(x), 3) for x in sim_to_B],
        "notes_per_bar": [len([n for n in c_notes if int(n["t"] // BAR) == C0 + k]) for k in range(C_BARS)],
    }
    if field is not None:
        out["intrusions"] = sum(1 for e in field.events if e[0] == "intrusion" and e[1] >= C0 * BAR)
        out["slips"] = sum(1 for e in field.events if e[0] == "slip" and e[1] >= C0 * BAR)
    return out


def randomized(notes, seed):
    rng = np.random.default_rng(seed)
    out = []
    for n in notes:
        if n["t"] >= C0 * BAR:
            b = int(n["t"] // BAR)
            n = dict(n, t=b * BAR + rng.uniform(0, BAR))
        out.append(n)
    return sorted(out, key=lambda x: x["t"])


def evaluate(seeds=range(6), conditions=CONDITIONS):
    table = {}
    for name, kw in conditions.items():
        rows = []
        for seed in seeds:
            f, ev, notes = run(MusicParams(**kw), seed)
            rows.append(metrics(notes, f))
            if name == "improv":
                table.setdefault("random", []).append(metrics(randomized(notes, seed)))
        table[name] = rows
    return table


def summarize(table):
    keys = ["C_bars_with_sound", "sim_to_B_first8", "sim_to_B_last8_of_sound", "bar_change_mean",
            "on_grid", "coherence", "new_voice_notes"]
    summ = {}
    for name, rows in table.items():
        summ[name] = {k: round(float(np.nanmean([r[k] for r in rows])), 3) for k in keys}
    return summ


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "quick":
        extra = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
        conds = {"memory": {}, "try": {**CONDITIONS["improv"], **extra}}
        t = evaluate(range(3), conds)
        for k, v in summarize(t).items():
            print(k, v)
        for r in t["try"]:
            print(" try", r["notes_per_bar"], r["new_voices"], r.get("intrusions"), r.get("slips"))
        sys.exit()
    table = evaluate()
    summ = summarize(table)
    json.dump({"conditions": CONDITIONS, "summary": summ, "rows": table}, open("improv_results.json", "w"),
              ensure_ascii=False, indent=1)
    for k, v in summ.items():
        print(k, v)
