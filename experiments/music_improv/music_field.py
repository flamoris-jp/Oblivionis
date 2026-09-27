"""
Oblivionis music — 聴いて、覚えて、鳴らす振動の場

各粒子は「リズム」と「音程」を同じ整数 n で持つ (Cowell の Rhythmicon と同じ対応):
    リズム: 1小節に n 回発火する        (n=4 → 4分音符, n=6 → 4分3連, n=8 → 8分)
    音程  : 基音 f0 の n 倍音             (n=2 → オクターブ, n=3 → 5度上, n=5 → 長3度 …)
つまり「倍音型」の干渉 (整数比) が、リズムではポリリズムに、音程では和音になる。

v0.5 の記憶の場との対応:
    Kuramoto 同期   → n:m 位相ロック (3拍と2拍が同じ小節の頭で揃う)
    共鳴による強化  → 入力の音の立ち上がりと自分の発火が重なると振幅 A が上がる
    ヘブ則          → 一緒に鳴って揃っている声部どうしの結合 K が育つ
    存在強度 S      → 外から響きをもらえないと下がり、S が低い声部は黙る (忘却)
"""

from __future__ import annotations

from dataclasses import dataclass
from math import gcd
import numpy as np


@dataclass
class MusicParams:
    bpm: float = 100.0
    f0: float = 55.0               # 基音 (A1)。粒子 n の音程は n·f0
    detune: float = 0.015          # 固有テンポのばらつき (これがあるので、同期しないとリズムがずれる)
    dt: float = 0.002

    entrain: float = 0.5           # 入力の立ち上がりが位相を 0 (発火点) へ引き寄せる強さ
    ear_width: float = 0.8         # どの高さの音にどれだけ反応するか (オクターブ単位の幅)。蝸牛の役
    sync_gain: float = 1.6         # 声部どうしの n:m 位相ロックの強さ

    A_decay: float = 0.35
    input_gain: float = 6.0        # 発火と立ち上がりが重なったときの振幅の増え方
    resonance_gain: float = 3.0    # ロックした相手からもらう振幅 (× S)
    inhibition: float = 0.12       # 全体抑制 (同時に鳴れる量に上限)

    hebb_rate: float = 2.0
    hebb_threshold: float = 0.2
    K_decay: float = 0.01
    K_max: float = 1.0

    S_init: float = 0.4
    S_growth: float = 1.0          # 外から響きをもらったときだけ育つ
    S_decay: float = 0.025         # 外から何も来ないと少しずつ減る
    S_silent: float = 0.08         # これ未満の声部は黙る

    core_gain: float = 0.0        # 核 (小節の頭の感覚) への引き込み。0 なら核なし
    core_entrain: float = 0.3     # 核が入力の立ち上がりに合わせる強さ

    gate: float = 0.25             # 振幅がこれ未満なら、発火しても音を出さない

    # --- 即興 (すべて 0 なら「覚えて返す」だけの版と同じ動き) ---
    phase_noise: float = 0.0       # 位相のゆらぎ (rad/√秒)。人間のタイミングの揺れ
    slip_rate: float = 0.0         # 鳴っている声部が、拍の位置ごとずれる頻度 (回/秒)
    intrusion_rate: float = 0.0    # ランダムな声部がふっと鳴り出す頻度 (回/秒)。v0.5 の日常語の割り込み
    intrusion_kick: float = 0.35   # 割り込みで与える振幅
    self_listen: float = 0.0       # 自分の出した音を入力として聴き直す強さ (0 = 聴かない)
    fatigue: float = 0.0           # 疲れ (馴化)。長く鳴り続けた声部ほど響きを受け取りにくくなる
    fatigue_tau: float = 8.0       # 疲れがたまる/抜ける時間 (秒)
    drive_target: float = 0.0      # 恒常性: 場全体の振幅の合計をこの値に保とうとする (0 = なし)。核の existence に当たる
    drive_tau: float = 4.0         # 恒常性が効く速さ (秒)


class MusicField:
    def __init__(self, harmonics, p: MusicParams | None = None, seed: int = 0):
        self.p = p or MusicParams()
        rng = np.random.default_rng(seed)
        self.rng = np.random.default_rng(seed + 1000)   # 即興用 (初期配置とは別の乱数)
        self.heard_self = []                              # 直前に自分が鳴らした音 (次の step で聴く)
        self.events = []                                  # 割り込み・ずれの記録
        self.F = np.zeros(len(harmonics))                 # 疲れ
        self.drive = 1.0                                  # 恒常性で上下する全体のゲイン
        self.target = self.p.drive_target                 # 外から変えられる (曲の終わりに下げる、など)
        self.n = np.array(harmonics, dtype=int)
        self.N = len(self.n)
        bar_hz = self.p.bpm / 60.0 / 4.0
        self.omega = 2 * np.pi * bar_hz * self.n * (1 + rng.normal(0, self.p.detune, self.N))
        self.pitch = self.p.f0 * self.n
        self.phi = rng.uniform(0, 2 * np.pi, self.N)
        self.A = np.zeros(self.N)
        self.S = np.full(self.N, self.p.S_init)
        self.K = np.zeros((self.N, self.N))
        self.t = 0.0
        # 核: 音は出さず、1小節に1回まわる「1拍目の感覚」。v0.3 の Core に当たる
        self.core_phi = 0.0
        self.core_omega = 2 * np.pi * bar_hz

        # n:m ロック用の既約比 (p_ij, q_ij)。χij = q·φi − p·φj を 0 に保とうとする
        P = np.zeros((self.N, self.N), dtype=int)
        Q = np.zeros((self.N, self.N), dtype=int)
        for i in range(self.N):
            for j in range(self.N):
                g = gcd(int(self.n[i]), int(self.n[j]))
                P[i, j], Q[i, j] = self.n[i] // g, self.n[j] // g
        self.P, self.Q = P, Q

    def ear(self, freq: float) -> np.ndarray:
        """周波数 freq の音に、各粒子がどれだけ反応するか (0..1)。"""
        octaves = np.log2(self.pitch / freq)
        return np.exp(-0.5 * (octaves / self.p.ear_width) ** 2)

    def step(self, onsets):
        """onsets: この dt の間に鳴った入力音 [(freq, velocity), ...]。発火した粒子の index を返す。"""
        p, dt = self.p, self.p.dt
        external = [(f, v, -1) for f, v in onsets]
        own = self.heard_self              # 自分の音: (freq, velocity, 鳴らした声部)
        self.heard_self = []

        # χij = q·φi − p·φj  (0 なら i と j は小節の頭で揃っている)
        chi = self.Q * self.phi[:, None] - self.P * self.phi[None, :]
        lock = np.cos(chi)
        KA = self.K * self.A[None, :]

        # 位相: 固有テンポ + 相手とのロック
        dphi = self.omega - p.sync_gain * (KA * np.sin(chi)).sum(axis=1)
        # 核との 1:n ロック (χ = φi − n·φcore は解が1つだけ → 小節の頭に正しく揃う)
        dphi -= p.core_gain * self.n * np.sin(self.phi - self.n * self.core_phi)   # 速い声部ほど強く (テンポのずれは n に比例するので)

        # 振幅: 減衰 + ロックした相手からの共鳴 (存在強度 S に比例) − 全体抑制
        res = (KA * np.clip(lock, 0, None)).sum(axis=1) / (1.0 + self.K.sum(axis=1))
        fresh = 1.0 - p.fatigue * self.F                  # 疲れていない度合い
        dA = (-p.A_decay * self.A + p.resonance_gain * self.drive * self.S * fresh * res * (1 - self.A)
              - p.inhibition * self.A * self.A.sum())
        dS = -p.S_decay * self.S

        phi = self.phi + dt * dphi
        A = self.A + dt * dA

        # 入力音: 位相を発火点へ引き寄せ、発火点の近くにいた粒子は振幅と存在強度をもらう
        # 自分の音も (弱めて) 同じ耳で聴く。ただし鳴らした本人は自分の音では育たない
        for freq, vel, src in external + own:
            heard = vel * self.ear(freq)
            if src >= 0:
                heard = heard * p.self_listen
                heard[src] = 0.0
            near = ((1 + np.cos(phi)) / 2) ** 6          # 発火点 (位相 0) の近くほど 1
            phi = phi - p.entrain * heard * np.sin(phi)
            A = A + p.input_gain * dt * heard * near * (1 - A) * 20 * (1.0 - p.fatigue * self.F)
            dS = dS + p.S_growth * heard * near * (1 - self.S) * 20

        # 揺らぎ: 位相の小さなゆれ
        if p.phase_noise > 0:
            phi = phi + p.phase_noise * np.sqrt(dt) * self.rng.normal(0, 1, self.N)
        # ずれ: 鳴っている声部が、ときどき拍の位置ごと (1/4 か 1/2 周) ずれる → シンコペーション
        if p.slip_rate > 0 and self.rng.random() < p.slip_rate * dt:
            active = np.where(self.A >= p.gate)[0]
            if len(active):
                i = int(self.rng.choice(active))
                # 16分か3連8分の格子に乗ったままになる位置へだけずらす (時間で m/16 か m/12 小節)
                n_i = int(self.n[i])
                cands = sorted({round((2 * np.pi * n_i * m / D) % (2 * np.pi), 6)
                                for D in (16, 12) for m in range(1, D)} - {0.0, round(2 * np.pi, 6)})
                if cands:
                    phi[i] += float(self.rng.choice(cands))
                self.events.append(("slip", self.t, int(self.n[i])))
        # 割り込み: ランダムな声部がふっと鳴り出す。周りと共鳴すれば育ち、しなければ消える
        if p.intrusion_rate > 0 and self.rng.random() < p.intrusion_rate * dt:
            i = int(self.rng.integers(self.N))
            A[i] = min(1.0, A[i] + p.intrusion_kick)
            # いま一番強く鳴っている声部とロックした位置から入る (でたらめな位置では入らない)
            j = int(np.argmax(np.where(np.arange(self.N) == i, -1, self.A)))
            if self.A[j] >= p.gate:
                k = int(self.rng.integers(self.Q[i, j]))
                phi[i] = (self.P[i, j] * phi[j] + 2 * np.pi * k) / self.Q[i, j]
            self.events.append(("intrusion", self.t, int(self.n[i])))

        a = np.clip(self.A - p.hebb_threshold, 0, None)
        dK = p.hebb_rate * np.outer(a, a) * lock * (p.K_max - self.K) - p.K_decay * self.K

        core = self.core_phi + dt * self.core_omega
        for freq, vel in onsets:
            core -= p.core_entrain * vel * np.sin(core)

        fired = np.where(phi >= 2 * np.pi)[0]
        self.core_phi = float(np.mod(core, 2 * np.pi))
        self.phi = np.mod(phi, 2 * np.pi)
        self.A = np.clip(A, 0, 1)
        self.S = np.clip(self.S + dt * dS, 0, 1)
        if p.fatigue > 0:
            self.F += dt * (self.A - self.F) / p.fatigue_tau
        if p.drive_target > 0:
            self.drive = float(np.clip(self.drive + dt * (self.target - self.A.sum()) / (p.drive_tau * max(self.target, 0.5)), 0.2, 4.0))
        self.K = np.clip(self.K + dt * dK, 0, p.K_max)
        np.fill_diagonal(self.K, 0)
        self.t += dt

        audible = [i for i in fired if self.A[i] >= p.gate and self.S[i] >= p.S_silent]
        if p.self_listen > 0:
            self.heard_self = [(float(self.pitch[i]), float(self.A[i]), int(i)) for i in audible]
        return audible
