from dataclasses import dataclass, field
from typing import List
import math


# -----------------------------
# Particle
# -----------------------------
@dataclass
class Particle:
    value: str
    polarity: int

    base_strength: float
    wave_strength: float

    distance: float
    angle: float

    amplitude: float
    frequency: float
    phase: float

    decay: float = 0.97
    active: bool = True

    def step(self):
        if not self.active:
            return

        # 位相進行
        self.phase += self.frequency

        # 振動
        osc = 1 + self.amplitude * math.sin(self.phase)
        self.wave_strength = self.base_strength * osc

        # 減衰
        self.base_strength *= self.decay

        if self.base_strength < 0.05:
            self.active = False


# -----------------------------
# Core
# -----------------------------
@dataclass
class Core:
    existence: float = 1.0
    stability: float = 0.0


# -----------------------------
# System
# -----------------------------
@dataclass
class OblivionisV03:
    core: Core = field(default_factory=Core)
    particles: List[Particle] = field(default_factory=list)

    def inject(self, value, polarity):
        self.particles.append(
            Particle(
                value=value,
                polarity=1 if polarity >= 0 else -1,
                base_strength=1.0,
                wave_strength=1.0,
                distance=1.0,
                angle=0.0,
                amplitude=0.4,
                frequency=0.2,
                phase=0.0,
            )
        )

    # -----------------------------
    # 干渉計算（v0.3の核心）
    # -----------------------------
    def interaction(self, p1: Particle, p2: Particle):
        phase_diff = p1.phase - p2.phase

        # 距離減衰
        dist = abs(p1.distance - p2.distance)
        distance_factor = 1 / (1 + dist)

        # 干渉
        return (
            p1.wave_strength
            * p2.wave_strength
            * math.cos(phase_diff)
            * distance_factor
        )

    # -----------------------------
    # 更新
    # -----------------------------
    def step(self):
        # 粒子更新
        for p in self.particles:
            p.step()

        self.particles = [p for p in self.particles if p.active]

        # -----------------------------
        # 粒子同士の干渉
        # -----------------------------
        influences = [0.0 for _ in self.particles]

        for i in range(len(self.particles)):
            for j in range(i + 1, len(self.particles)):
                p1 = self.particles[i]
                p2 = self.particles[j]

                inter = self.interaction(p1, p2)

                # 相互に影響
                influences[i] += inter
                influences[j] += inter

        # -----------------------------
        # 粒子の移動（クラスター形成）
        # -----------------------------
        for i, p in enumerate(self.particles):
            drift = influences[i] * 0.02

            if drift > 0:
                p.distance -= drift  # 引き寄せ
            else:
                p.distance -= drift  # 反発（逆符号）

            if p.distance < 0.2:
                p.distance = 0.2

        # -----------------------------
        # 核への影響
        # -----------------------------
        retain = 0
        fade = 0

        for p in self.particles:
            influence = p.wave_strength / (1 + p.distance)

            if p.polarity > 0:
                retain += influence
            else:
                fade += influence

        self.core.stability = retain - fade
        self.core.existence += self.core.stability * 0.01

        if self.core.existence < 0:
            self.core.existence = 0

    def debug(self):
        return [
            {
                "value": p.value,
                "strength": round(p.wave_strength, 3),
                "distance": round(p.distance, 3),
                "phase": round(p.phase, 3),
            }
            for p in self.particles
        ]
