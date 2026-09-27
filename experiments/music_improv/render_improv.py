"""即興の回を音と図にする。同じ seed で「覚えて返すだけ」と「即興」を並べる。"""

import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

import improv as I
from music_field import MusicParams
from session import render, write_wav, write_midi

SEED = 2   # 6回のうち、ブレイク → 盛り上がり → B への回帰 → 離脱 → 終わり、の形がはっきり出た回 (選んだ回であることに注意)

for path in font_manager.findSystemFonts():
    if "NotoSansCJK-Regular" in path:
        font_manager.fontManager.addfont(path)
plt.rcParams["font.family"] = "Noto Sans CJK JP"

FAMILY = {1: "#555", 2: "#555", 4: "#2f6fd0", 8: "#2f6fd0", 16: "#2f6fd0",
          3: "#e0662f", 6: "#e0662f", 12: "#e0662f", 5: "#9b59b6", 7: "#9b59b6"}
NS = [1, 2, 3, 4, 5, 6, 7, 8, 12, 16]
ROW = {n: i for i, n in enumerate(NS)}

runs = {}
for name in ("memory", "improv"):
    f, events, notes = I.run(MusicParams(**I.CONDITIONS[name]), SEED)
    runs[name] = (f, events, notes, I.metrics(notes, f))
    total = I.N_BARS * I.BAR
    mix, _ = render(events, notes, total)
    write_wav(f"improv_{name}.wav", mix)
    write_midi(f"improv_{name}.mid", events, notes, MusicParams().bpm)

fig, axes = plt.subplots(3, 1, figsize=(15, 10), dpi=110, gridspec_kw={"height_ratios": [2.2, 2.2, 1.3]})
for ax, name, title in [(axes[0], "memory", "覚えて返すだけ (揺らぎなし)"),
                        (axes[1], "improv", "即興 (揺らぎ + ずれ + 割り込み + 自分を聴く + 疲れ + 恒常性)")]:
    f, events, notes, m = runs[name]
    ax.axvspan(0, I.A_BARS, color="#eef4ff")
    ax.axvspan(I.A_BARS, I.C0, color="#fff1e8")
    ax.axvspan(I.C0, I.N_BARS, color="#f3f3f3")
    for nt in notes:
        ax.scatter(nt["t"] / I.BAR, ROW[nt["n"]] + (0.18 if nt["voice"] >= 10 else -0.18),
                   s=3 + 20 * nt["vel"], color=FAMILY[nt["n"]], alpha=0.3 + 0.6 * nt["vel"], lw=0)
    for kind, t, n in f.events:
        if kind == "intrusion" and t >= I.C0 * I.BAR:
            ax.plot(t / I.BAR, ROW[n], marker="v", color="black", ms=5, alpha=0.6)
    ax.set_yticks(range(len(NS)), [f"n={n}" for n in NS], fontsize=8)
    ax.set_xlim(0, I.N_BARS)
    ax.set_ylim(-0.7, len(NS) - 0.3)
    ax.text(I.A_BARS / 2, len(NS) - 0.55, "A グルーヴ", ha="center", fontsize=9)
    ax.text((I.A_BARS + I.C0) / 2, len(NS) - 0.55, "B 3連", ha="center", fontsize=9)
    ax.text((I.C0 + I.N_BARS) / 2, len(NS) - 0.55, "C 入力なし (32小節)", ha="center", fontsize=9)
    ax.set_title(f"{title} — C で鳴った小節 {m['C_bars_with_sound']}/32、揃い方 {m['coherence']:.2f}、"
                 f"新しく出てきた声部 {m['new_voices'] or 'なし'}", fontsize=10)
axes[1].plot([], [], "v", color="black", label="割り込み (ふっと鳴らされた声部)")
axes[1].legend(loc="lower left", fontsize=8)

ax = axes[2]
xs = np.arange(I.C0, I.N_BARS) + 0.5
for name, col in (("memory", "#999"), ("improv", "#e0662f")):
    sim = [np.nan if v is None else v for v in runs[name][3]["sim_curve"]]
    ax.plot(xs, sim, color=col, lw=1.8, label=f"{'覚えて返すだけ' if name == 'memory' else '即興'}: B との似かた")
ax2 = ax.twinx()
ax2.bar(xs, runs["improv"][3]["notes_per_bar"], width=0.8, color="#e0662f", alpha=0.18, label="即興: 1小節の音数")
ax2.set_ylabel("音数", fontsize=9)
ax.set_xlim(0, I.N_BARS)
ax.set_ylim(0, 1)
ax.set_ylabel("B でよく鳴った形との重なり")
ax.set_xlabel("小節")
ax.legend(loc="upper left", fontsize=8)
ax2.legend(loc="upper right", fontsize=8)
ax.set_title("C の各小節が、B で覚えた形にどれだけ似ているか (1 = 同じ, 0 = 無関係)", fontsize=10)

fig.tight_layout()
fig.savefig("oblivionis_improv.png")
json.dump({k: v[3] for k, v in runs.items()}, open("improv_seed2.json", "w"), ensure_ascii=False, indent=1)
print({k: {kk: v[3][kk] for kk in ("C_bars_with_sound", "coherence", "bar_change_mean", "new_voices", "intrusions", "slips")} for k, v in runs.items()})
