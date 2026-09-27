"""
セッション: 場に音楽を聴かせ、途中で入力を止めて、場が自分で何を鳴らすかを聴く。

  A  (1–12小節)  4つ打ち系のグルーヴ   キック 1・3拍 / スネア 2・4拍 / ハイハット 8分
  B  (13–24小節) 3連のポリリズム       キック・スネアはそのまま、ハイハットをやめてマリンバの4分3連
  C  (25–40小節) 入力なし              場だけが鳴る

音はすべてこのスクリプトの中で合成している (外部の音源・サンプルなし)。
"""

from __future__ import annotations

import json
import struct
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, lfilter

from music_field import MusicField, MusicParams

SR = 44100
P = MusicParams()
BAR = 60.0 / P.bpm * 4
SECTIONS = {"A": (0, 12), "B": (12, 24), "C": (24, 40)}
N_BARS = 40
HARMONICS = [1, 2, 3, 4, 5, 6, 7, 8, 12, 16] * 2        # 各 n に2声部 (少しずつテンポがずれている)

INSTR = {  # 名前: (耳に届く代表周波数, 強さ)
    "kick": (65.0, 1.0),
    "snare": (220.0, 0.8),
    "hat": (880.0, 0.45),
    "marimba": (330.0, 0.8),
}


def compose():
    events = []
    beat = BAR / 4
    for bar in range(N_BARS):
        t0 = bar * BAR
        if bar < 24:
            for b in (0, 2):
                events.append((t0 + b * beat, "kick"))
            for b in (1, 3):
                events.append((t0 + b * beat, "snare"))
        if bar < 12:
            for k in range(8):
                events.append((t0 + k * beat / 2, "hat"))
        elif bar < 24:
            for k in range(6):
                events.append((t0 + k * BAR / 6, "marimba"))
    return sorted(events)


def run(seed=0, params=None):
    field = MusicField(HARMONICS, params or P, seed=seed)
    events = compose()
    total = N_BARS * BAR
    steps = int(total / P.dt)
    ev_i = 0
    notes = []
    trace = {"t": [], "A": [], "S": [], "phi": []}
    for s in range(steps):
        t = s * P.dt
        onsets = []
        while ev_i < len(events) and events[ev_i][0] < t + P.dt:
            name = events[ev_i][1]
            freq, vel = INSTR[name]
            onsets.append((freq, vel))
            ev_i += 1
        fired = field.step(onsets)
        for i in fired:
            notes.append({"t": field.t, "voice": int(i), "n": int(field.n[i]),
                          "freq": float(field.pitch[i]), "vel": float(field.A[i])})
        if s % 25 == 0:
            trace["t"].append(field.t)
            trace["A"].append(field.A.copy())
            trace["S"].append(field.S.copy())
            trace["phi"].append(field.phi.copy())
    trace = {k: np.array(v) for k, v in trace.items()}
    return field, events, notes, trace


# ------------------------------------------------------------------
# 合成 (すべて自前)
# ------------------------------------------------------------------
def _env(n, attack, decay):
    t = np.arange(n) / SR
    return np.minimum(1, t / attack) * np.exp(-t / decay)


def voice_tone(freq, vel):
    """場の声: 倍音を少し含んだ減衰音 (低い音ほど長く鳴る)。"""
    dur = float(np.clip(1.2 * 220 / freq, 0.18, 1.4))
    n = int(dur * SR)
    t = np.arange(n) / SR
    wave = np.sin(2 * np.pi * freq * t) + 0.3 * np.sin(4 * np.pi * freq * t) * np.exp(-t / (dur / 4))
    return 0.22 * vel * wave * _env(n, 0.004, dur / 3)


def drum(name, rng):
    if name == "kick":
        n = int(0.35 * SR)
        t = np.arange(n) / SR
        f = 45 + 90 * np.exp(-t / 0.03)
        return 0.9 * np.sin(2 * np.pi * np.cumsum(f) / SR) * _env(n, 0.001, 0.12)
    if name == "snare":
        n = int(0.2 * SR)
        noise = rng.normal(0, 1, n)
        b, a = butter(2, [900 / (SR / 2), 6000 / (SR / 2)], "band")
        t = np.arange(n) / SR
        return 0.35 * lfilter(b, a, noise) * _env(n, 0.001, 0.05) + 0.2 * np.sin(2 * np.pi * 190 * t) * _env(n, 0.001, 0.04)
    if name == "hat":
        n = int(0.06 * SR)
        b, a = butter(2, 7000 / (SR / 2), "high")
        return 0.18 * lfilter(b, a, rng.normal(0, 1, n)) * _env(n, 0.0005, 0.015)
    if name == "marimba":
        n = int(0.4 * SR)
        t = np.arange(n) / SR
        f = 330.0
        return 0.35 * (np.sin(2 * np.pi * f * t) + 0.25 * np.sin(2 * np.pi * 4 * f * t) * np.exp(-t / 0.02)) * _env(n, 0.002, 0.12)
    raise ValueError(name)


def render(events, notes, total, include_input=True, include_field=True):
    rng = np.random.default_rng(7)
    out = np.zeros((int((total + 2) * SR), 2))
    if include_input:
        for t, name in events:
            x = drum(name, rng)
            i = int(t * SR)
            out[i:i + len(x), 0] += 0.9 * x
            out[i:i + len(x), 1] += 0.9 * x
    if include_field:
        for nt in notes:
            x = voice_tone(nt["freq"], nt["vel"])
            pan = 0.5 + 0.35 * np.sin(nt["voice"] * 2.1)   # 声部ごとに左右に散らす
            i = int(nt["t"] * SR)
            out[i:i + len(x), 0] += (1 - pan) * 1.4 * x
            out[i:i + len(x), 1] += pan * 1.4 * x
    peak = np.abs(out).max()
    out = out / max(peak, 1e-9) * 0.89
    return out, float(peak)


def write_wav(path, x):
    wavfile.write(path, SR, (x * 32767).astype(np.int16))


# ------------------------------------------------------------------
# MIDI (標準MIDIファイルを直接書く)
# ------------------------------------------------------------------
def _vlq(v):
    out = [v & 0x7F]
    v >>= 7
    while v:
        out.append((v & 0x7F) | 0x80)
        v >>= 7
    return bytes(reversed(out))


def write_midi(path, events, notes, bpm):
    tpq = 480
    sec_to_tick = tpq * bpm / 60.0

    def track(msgs):
        msgs = sorted(msgs, key=lambda m: m[0])
        data, last = b"", 0
        for tick, raw in msgs:
            data += _vlq(tick - last) + raw
            last = tick
        data += b"\x00\xff\x2f\x00"
        return b"MTrk" + struct.pack(">I", len(data)) + data

    tempo = int(60_000_000 / bpm)
    meta = [(0, b"\xff\x51\x03" + tempo.to_bytes(3, "big")), (0, b"\xff\x03\x06" + b"Tempo "[:6])]

    field_msgs = [(0, b"\xff\x03\x10Oblivionis field")]
    for nt in notes:
        midi = int(round(69 + 12 * np.log2(nt["freq"] / 440.0)))
        vel = int(np.clip(30 + 97 * nt["vel"], 1, 127))
        on = int(nt["t"] * sec_to_tick)
        dur = int(np.clip(1.2 * 220 / nt["freq"], 0.18, 1.4) * 0.5 * sec_to_tick)
        field_msgs.append((on, bytes([0x90, midi, vel])))
        field_msgs.append((on + dur, bytes([0x80, midi, 0])))

    gm = {"kick": 36, "snare": 38, "hat": 42, "marimba": None}
    drum_msgs = [(0, b"\xff\x03\x0bInput drums")]
    mar_msgs = [(0, b"\xff\x03\x0dInput marimba"), (0, bytes([0xC1, 12]))]
    for t, name in events:
        on = int(t * sec_to_tick)
        if gm[name] is not None:
            drum_msgs += [(on, bytes([0x99, gm[name], 100])), (on + 60, bytes([0x89, gm[name], 0]))]
        else:
            mar_msgs += [(on, bytes([0x91, 64, 100])), (on + 200, bytes([0x81, 64, 0]))]

    tracks = [track(meta), track(field_msgs), track(drum_msgs), track(mar_msgs)]
    header = b"MThd" + struct.pack(">IHHH", 6, 1, len(tracks), tpq)
    open(path, "wb").write(header + b"".join(tracks))


# ------------------------------------------------------------------
# 分析
# ------------------------------------------------------------------
def analyze(field, events, notes, trace):
    res = {}
    grid = BAR / 12                                  # 3連と16分の両方を含む細かい格子 (1小節=12分割 → 16分は含まない)
    for sec, (b0, b1) in SECTIONS.items():
        t0, t1 = b0 * BAR, b1 * BAR
        sn = [n for n in notes if t0 <= n["t"] < t1]
        by_n = {}
        for n in sn:
            by_n[n["n"]] = by_n.get(n["n"], 0) + 1
        # 小節の頭からの位置を 1/48 小節単位で見て、4分・8分・3連のどの格子に近いか
        pos = np.array([((n["t"] % BAR) / BAR) for n in sn])
        def on_grid(div):
            if len(pos) == 0:
                return float("nan")
            d = np.abs(pos * div - np.round(pos * div)) / div * BAR
            return float(np.mean(d < 0.03))
        # 声部の種類ごとに、本来の格子からのずれ (ms)
        def err_ms(ns, div):
            ts = np.array([n["t"] for n in sn if n["n"] in ns])
            if len(ts) == 0:
                return None
            pos = (ts % BAR) / BAR
            d = np.abs(pos * div - np.round(pos * div)) / div * BAR * 1000
            return {"count": int(len(ts)), "median_ms": round(float(np.median(d)), 1),
                    "within_30ms": round(float(np.mean(d < 30)), 3)}
        res[sec] = {
            "notes": len(sn),
            "notes_per_bar": round(len(sn) / (b1 - b0), 1),
            "voices_by_n": dict(sorted(by_n.items())),
            "on_16th_grid": round(on_grid(16), 3),
            "on_triplet_grid": round(on_grid(12), 3),
            "straight_voices_vs_16th": err_ms({1, 2, 4, 8, 16}, 16),
            "triplet_voices_vs_triplet": err_ms({3, 6, 12}, 12),
        }
    # 入力をやめたあと、どれくらい鳴り続けたか
    tc = SECTIONS["C"][0] * BAR
    later = [n for n in notes if n["t"] >= tc]
    for k in range(SECTIONS["C"][0], N_BARS, 4):
        cnt = sum(1 for n in later if k * BAR <= n["t"] < (k + 4) * BAR)
        res.setdefault("C_notes_per_4bars", []).append(cnt)
    res["last_note_bar"] = round(max(n["t"] for n in notes) / BAR, 2) if notes else None
    res["silenced_voices_end"] = sorted({int(field.n[i]) for i in range(field.N) if field.S[i] < field.p.S_silent})
    res["S_end_by_n"] = {int(k): round(float(field.S[field.n == k].mean()), 3) for k in sorted(set(field.n.tolist()))}
    Kn = {}
    for i in range(field.N):
        for j in range(i + 1, field.N):
            key = f"{min(field.n[i], field.n[j])}:{max(field.n[i], field.n[j])}"
            Kn.setdefault(key, []).append(field.K[i, j])
    res["K_end_top"] = sorted(((k, round(float(np.max(v)), 3)) for k, v in Kn.items()), key=lambda x: -x[1])[:10]
    return res


if __name__ == "__main__":
    field, events, notes, trace = run(seed=0)
    total = N_BARS * BAR
    mix, peak = render(events, notes, total)
    write_wav("oblivionis_music_session.wav", mix)
    solo, _ = render(events, notes, total, include_input=False)
    write_wav("oblivionis_music_field_only.wav", solo)
    write_midi("oblivionis_music_session.mid", events, notes, P.bpm)
    res = analyze(field, events, notes, trace)
    res["raw_peak_before_normalize"] = round(peak, 3)
    np.savez_compressed("trace.npz", **trace, n=field.n, K=field.K)
    json.dump({"notes": notes, "events": events}, open("notes.json", "w"))
    json.dump(res, open("music_results.json", "w"), ensure_ascii=False, indent=1)
    print(json.dumps(res, ensure_ascii=False, indent=1))
