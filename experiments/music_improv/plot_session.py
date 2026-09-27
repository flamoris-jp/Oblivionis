"""セッションの可視化: 誰がいつ鳴ったか (ピアノロール) と、声部ごとの存在強度。"""

import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

from session import BAR, SECTIONS, N_BARS

for path in font_manager.findSystemFonts():
    if "NotoSansCJK-Regular" in path:
        font_manager.fontManager.addfont(path)
plt.rcParams["font.family"] = "Noto Sans CJK JP"

data = json.load(open("notes.json"))
notes, events = data["notes"], data["events"]
tr = np.load("trace.npz")
res = json.load(open("music_results.json"))

RHYTHM = {1: "全音符", 2: "2分", 3: "2分3連", 4: "4分", 5: "5連", 6: "4分3連", 7: "7連",
          8: "8分", 12: "8分3連", 16: "16分"}
NOTE = {1: "A1", 2: "A2", 3: "E3", 4: "A3", 5: "C#4", 6: "E4", 7: "G4-", 8: "A4", 12: "E5", 16: "A5"}
FAMILY = {1: "#555", 2: "#555", 4: "#2f6fd0", 8: "#2f6fd0", 16: "#2f6fd0",
          3: "#e0662f", 6: "#e0662f", 12: "#e0662f", 5: "#9b59b6", 7: "#9b59b6"}
SEC_COL = {"A": "#eef4ff", "B": "#fff1e8", "C": "#f3f3f3"}
SEC_NAME = {"A": "A: グルーヴを聴く", "B": "B: 3連を聴く", "C": "C: 入力なし — 場だけが鳴る"}

ns = sorted({1, 2, 3, 4, 5, 6, 7, 8, 12, 16})
row = {n: i for i, n in enumerate(ns)}

fig = plt.figure(figsize=(15, 10.5), dpi=110)
gs = fig.add_gridspec(3, 2, height_ratios=[3.2, 1.3, 2.0], hspace=0.45, wspace=0.12)

# (1) 全体のピアノロール
ax = fig.add_subplot(gs[0, :])
for s, (b0, b1) in SECTIONS.items():
    ax.axvspan(b0, b1, color=SEC_COL[s], zorder=0)
    ax.text((b0 + b1) / 2, len(ns) + 0.9, SEC_NAME[s], ha="center", fontsize=10)
for t, name in events:
    y = {"kick": -3.1, "snare": -2.5, "hat": -1.9, "marimba": -1.3}[name]
    ax.plot(t / BAR, y, "|", color="#333" if name != "marimba" else "#e0662f", ms=5, mew=1)
for nt in notes:
    ax.scatter(nt["t"] / BAR, row[nt["n"]] + (0.18 if nt["voice"] >= 10 else -0.18),
               s=4 + 26 * nt["vel"], color=FAMILY[nt["n"]], alpha=0.35 + 0.6 * nt["vel"], lw=0)
ax.set_yticks([row[n] for n in ns] + [-3.1, -2.5, -1.9, -1.3],
              [f"n={n}  {RHYTHM[n]} / {NOTE[n]}" for n in ns] + ["入力: キック", "スネア", "ハイハット", "マリンバ3連"], fontsize=8)
ax.set_ylim(-3.6, len(ns) + 1.5)
ax.set_xlim(0, N_BARS)
ax.set_xlabel("小節")
ax.set_title("Oblivionis music — 場の各声部がいつ鳴ったか (点の大きさ = 強さ)。紫の 5連・7連 は入力に一度も含まれない", fontsize=11)

# (2) 拡大: B と C の2小節ずつ
for k, (b, label) in enumerate([(20, "B の中 (20–22小節) — 入力と一緒に"), (27, "C の中 (27–29小節) — 入力なしで、覚えた 2:3 を鳴らし続ける")]):
    ax2 = fig.add_subplot(gs[1, k])
    for x in np.arange(b, b + 2.001, 0.25):
        ax2.axvline(x, color="#2f6fd0", lw=0.5, alpha=0.35)
    for x in np.arange(b, b + 2.001, 1 / 6):
        ax2.axvline(x, color="#e0662f", lw=0.5, alpha=0.35, ls=":")
    for nt in notes:
        if b <= nt["t"] / BAR < b + 2:
            ax2.scatter(nt["t"] / BAR, row[nt["n"]], s=10 + 50 * nt["vel"], color=FAMILY[nt["n"]], lw=0)
    for t, name in events:
        if b <= t / BAR < b + 2:
            ax2.plot(t / BAR, -1, "|", color="#333" if name != "marimba" else "#e0662f", ms=8, mew=1.2)
    ax2.set_xlim(b, b + 2)
    ax2.set_ylim(-1.6, len(ns))
    ax2.set_yticks([row[n] for n in ns if n in (2, 4, 6, 8, 12)] + [-1], [f"n={n}" for n in (2, 4, 6, 8, 12)] + ["入力"], fontsize=8)
    ax2.set_title(label + "\n青線 = 4分の格子 / 橙点線 = 3連の格子", fontsize=9)

# (3) 存在強度 S
ax3 = fig.add_subplot(gs[2, :])
t = tr["t"] / BAR
S, n_of = tr["S"], tr["n"]
for s, (b0, b1) in SECTIONS.items():
    ax3.axvspan(b0, b1, color=SEC_COL[s], zorder=0)
for n in ns:
    m = S[:, n_of == n].mean(axis=1)
    ax3.plot(t, m, color=FAMILY[n], lw=1.6 if n in (4, 6, 8, 12, 16) else 1.0,
             ls="-" if n not in (5, 7) else "--", label=f"n={n}")
ax3.axhline(0.08, color="#999", ls=":", lw=1)
ax3.text(N_BARS - 0.2, 0.09, "黙る閾値", ha="right", fontsize=8, color="#777")
ax3.set_xlim(0, N_BARS)
ax3.set_ylim(0, None)
ax3.set_xlabel("小節")
ax3.set_ylabel("存在強度 S")
ax3.legend(ncol=10, fontsize=8, loc="upper left")
ax3.set_title("存在強度: 外から響きをもらった声部だけが育つ (4分・8分は A、3連は B で)。5連・7連・16分は育たない。C では誰も外から響きをもらえないので、全員ゆっくり下がっていく", fontsize=10)

fig.savefig("oblivionis_music_session.png", bbox_inches="tight")
print("ok")
