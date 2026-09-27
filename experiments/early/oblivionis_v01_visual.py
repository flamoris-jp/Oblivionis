from dataclasses import dataclass, field
from typing import List
import math
import textwrap
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter


@dataclass
class Particle:
    value: str
    polarity: int          # +1 = retain, -1 = fade
    strength: float
    distance: float
    angle: float
    decay: float = 0.95
    active: bool = True

    def step(self, move_scale: float = 0.05, min_strength: float = 0.05) -> None:
        if not self.active:
            return
        self.strength *= self.decay
        if self.polarity > 0:
            self.distance -= move_scale * self.strength
        else:
            self.distance += move_scale * self.strength
        if self.distance < 0.0:
            self.distance = 0.0
        if self.strength < min_strength:
            self.active = False


@dataclass
class Core:
    existence: float = 1.0
    stability: float = 0.0
    bias: float = 0.0


@dataclass
class OblivionisV01:
    core: Core = field(default_factory=Core)
    particles: List[Particle] = field(default_factory=list)
    tick_count: int = 0

    def inject(
        self,
        value: str,
        polarity: int,
        strength: float = 1.0,
        distance: float = 1.0,
        angle: float = 0.0,
    ) -> None:
        polarity = 1 if polarity >= 0 else -1
        self.particles.append(
            Particle(
                value=value,
                polarity=polarity,
                strength=strength,
                distance=distance,
                angle=angle,
            )
        )

    def step(self) -> None:
        for particle in self.particles:
            particle.step()

        self.particles = [p for p in self.particles if p.active]

        retain_score = 0.0
        fade_score = 0.0
        for p in self.particles:
            influence = p.strength / (1.0 + p.distance)
            if p.polarity > 0:
                retain_score += influence
            else:
                fade_score += influence

        self.core.stability = retain_score - fade_score
        self.core.bias = self.core.stability
        self.core.existence += self.core.stability * 0.02
        self.core.existence = max(0.0, min(2.0, self.core.existence))
        self.tick_count += 1

    def reaction(self) -> str:
        if self.core.bias > 0.2:
            return "retain"
        elif self.core.bias < -0.2:
            return "fade"
        return "fluctuate"


def polar_to_xy(distance: float, angle: float) -> tuple[float, float]:
    return distance * math.cos(angle), distance * math.sin(angle)


def build_demo() -> OblivionisV01:
    life = OblivionisV01()
    demo_particles = [
        ("warm_signal",  +1, 1.00, 1.20, 0.20),
        ("memory_trace", +1, 0.85, 1.60, 1.45),
        ("safe_word",    +1, 0.75, 1.10, 3.80),
        ("loss_signal",  -1, 0.95, 1.30, 2.30),
        ("noise",        -1, 0.60, 1.70, 5.15),
    ]
    for value, polarity, strength, distance, angle in demo_particles:
        life.inject(value=value, polarity=polarity, strength=strength, distance=distance, angle=angle)
    return life


def make_animation(output_path: str = "oblivionis_v01_visual.gif", num_frames: int = 40) -> None:
    life = build_demo()
    frames = []

    for _ in range(num_frames):
        frames.append({
            "tick": life.tick_count,
            "existence": life.core.existence,
            "stability": life.core.stability,
            "bias": life.core.bias,
            "reaction": life.reaction(),
            "particles": [
                {
                    "value": p.value,
                    "polarity": p.polarity,
                    "strength": p.strength,
                    "distance": p.distance,
                    "angle": p.angle,
                }
                for p in life.particles
            ],
        })
        life.step()

    fig, ax = plt.subplots(figsize=(6.8, 6.8))
    ax.set_aspect("equal")
    ax.set_xlim(-3.2, 3.2)
    ax.set_ylim(-3.2, 3.2)
    ax.set_xlabel("memory field x")
    ax.set_ylabel("memory field y")
    title = ax.set_title("Oblivionis v0.1 visualization")

    core_scatter = ax.scatter([0], [0], s=[900], marker="o", label="core")
    ax.text(0, 0.23, "self_core", ha="center")

    retain_scatter = ax.scatter([], [], s=[], marker="o", label="retain particles")
    fade_scatter = ax.scatter([], [], s=[], marker="x", label="fade particles")
    status_text = ax.text(
        0.02,
        0.98,
        "",
        transform=ax.transAxes,
        va="top",
        ha="left",
        family="monospace",
    )

    particle_texts = [ax.text(0, 0, "", fontsize=8, ha="center") for _ in range(12)]
    ax.legend(loc="lower right")

    def update(frame_idx: int):
        snap = frames[frame_idx]
        particles = snap["particles"]

        retain_xy, retain_sizes = [], []
        fade_xy, fade_sizes = [], []

        for t in particle_texts:
            t.set_text("")

        label_i = 0
        for p in particles:
            x, y = polar_to_xy(p["distance"], p["angle"])
            size = max(40, 350 * p["strength"])

            if p["polarity"] > 0:
                retain_xy.append((x, y))
                retain_sizes.append(size)
            else:
                fade_xy.append((x, y))
                fade_sizes.append(size)

            if label_i < len(particle_texts):
                particle_texts[label_i].set_position((x, y + 0.18))
                particle_texts[label_i].set_text(textwrap.shorten(p["value"], width=12, placeholder="…"))
                label_i += 1

        retain_scatter.set_offsets(retain_xy if retain_xy else [])
        retain_scatter.set_sizes(retain_sizes if retain_sizes else [])
        fade_scatter.set_offsets(fade_xy if fade_xy else [])
        fade_scatter.set_sizes(fade_sizes if fade_sizes else [])

        core_scatter.set_sizes([700 + 500 * snap["existence"]])

        title.set_text(f"Oblivionis v0.1 visualization — tick {snap['tick']}")
        status_text.set_text(
            f"reaction   : {snap['reaction']}\\n"
            f"existence  : {snap['existence']:.3f}\\n"
            f"stability  : {snap['stability']:.3f}\\n"
            f"bias       : {snap['bias']:.3f}\\n"
            f"particles  : {len(particles)}"
        )

        return [retain_scatter, fade_scatter, core_scatter, status_text, title, *particle_texts]

    anim = FuncAnimation(fig, update, frames=len(frames), interval=220, blit=False)
    anim.save(output_path, writer=PillowWriter(fps=5))
    plt.close(fig)


if __name__ == "__main__":
    make_animation()
