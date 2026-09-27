from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Particle:
    value: str
    polarity: int          # +1 = retain, -1 = fade
    strength: float
    distance: float
    decay: float = 0.95
    active: bool = True

    def step(self, move_scale: float = 0.05, min_strength: float = 0.05) -> None:
        if not self.active:
            return

        # 強度減衰
        self.strength *= self.decay

        # 核との距離変化
        if self.polarity > 0:
            self.distance -= move_scale * self.strength
        else:
            self.distance += move_scale * self.strength

        # 距離の下限
        if self.distance < 0.0:
            self.distance = 0.0

        # 閾値以下で消滅
        if self.strength < min_strength:
            self.active = False


@dataclass
class Core:
    existence: float = 1.0
    stability: float = 0.0
    bias: float = 0.0   # +なら retain 側、-なら fade 側


@dataclass
class OblivionisV01:
    core: Core = field(default_factory=Core)
    particles: List[Particle] = field(default_factory=list)
    tick_count: int = 0

    def inject(self, value: str, polarity: int, strength: float = 1.0, distance: float = 1.0) -> None:
        polarity = 1 if polarity >= 0 else -1
        self.particles.append(
            Particle(
                value=value,
                polarity=polarity,
                strength=strength,
                distance=distance,
            )
        )

    def step(self) -> None:
        # 素子更新
        for particle in self.particles:
            particle.step()

        # 非アクティブ除去
        self.particles = [p for p in self.particles if p.active]

        # 核状態再計算
        retain_score = 0.0
        fade_score = 0.0

        for p in self.particles:
            # 近い・強いほど寄与が強い
            influence = p.strength / (1.0 + p.distance)

            if p.polarity > 0:
                retain_score += influence
            else:
                fade_score += influence

        self.core.stability = retain_score - fade_score
        self.core.bias = self.core.stability

        # 存在強度も少し変化させる
        self.core.existence += self.core.stability * 0.02

        # 範囲制限
        if self.core.existence < 0.0:
            self.core.existence = 0.0
        if self.core.existence > 2.0:
            self.core.existence = 2.0

        self.tick_count += 1

    def read_state(self) -> dict:
        retain_count = sum(1 for p in self.particles if p.polarity > 0)
        fade_count = sum(1 for p in self.particles if p.polarity < 0)

        if self.core.bias > 0.2:
            reaction = "retain"
        elif self.core.bias < -0.2:
            reaction = "fade"
        else:
            reaction = "fluctuate"

        return {
            "tick": self.tick_count,
            "existence": round(self.core.existence, 4),
            "stability": round(self.core.stability, 4),
            "bias": round(self.core.bias, 4),
            "reaction": reaction,
            "particle_count": len(self.particles),
            "retain_count": retain_count,
            "fade_count": fade_count,
        }

    def debug_particles(self) -> List[dict]:
        rows = []
        for i, p in enumerate(self.particles):
            rows.append({
                "index": i,
                "value": p.value,
                "polarity": "retain" if p.polarity > 0 else "fade",
                "strength": round(p.strength, 4),
                "distance": round(p.distance, 4),
                "active": p.active,
            })
        return rows


def demo() -> None:
    life = OblivionisV01()

    # 入力注入
    life.inject("warm_signal", polarity=+1, strength=1.0, distance=1.0)
    life.inject("loss_signal", polarity=-1, strength=0.8, distance=1.2)

    for _ in range(10):
        life.step()
        print(life.read_state())
        print(life.debug_particles())
        print("-" * 40)


if __name__ == "__main__":
    demo()
