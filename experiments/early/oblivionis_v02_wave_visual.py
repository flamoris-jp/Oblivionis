from dataclasses import dataclass, field
from typing import List
import math
import textwrap
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter


@dataclass
class Particle:
    value: str
    polarity: int
    base_strength: float
    distance: float
    angle: float
    amplitude: float
    frequency: float
    phase: float
    decay: float = 0.97
    angular_velocity: float = 0.035
    active: bool = True
    wave_strength: float = 0.0

    def step(self, move_scale: float = 0.04, min_strength: float = 0.05) -> None:
        if not self.active:
            return

        self.phase += self.frequency
        self.angle += self.angular_velocity

        osc = 1.0 + self.amplitude * math.sin(self.phase)
        self.wave_strength = max(0.0, self.base_strength * osc)

        self.base_strength *= self.decay

        drift = move_scale * self.wave_strength
        ripple = 0.02 * math.sin(self.phase * 0.8)

        if self.polarity > 0:
            self.distance -= drift
            self.distance += ripple
        else:
            self.distance += drift
            self.distance += ripple

        if self.distance < 0.15:
            self.distance = 0.15

        if self.base_strength < min_strength:
            self.active = False


@dataclass
class Core:
    existence: float = 1.0
    stability: float = 0.0
    bias: float = 0.0
    pulse_phase: float = 0.0


@dataclass
class OblivionisV02:
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
        amplitude: float = 0.35,
        frequency: float = 0.22,
        phase: float = 0.0,
    ) -> None:
        polarity = 1 if polarity >= 0 else -1
        self.particles.append(
            Particle(
                value=value,
                polarity=polarity,
                base_strength=strength,
                distance=distance,
                angle=angle,
                amplitude=amplitude,
                frequency=frequency,
                phase=phase,
                wave_strength=strength,
            )
        )

    def step(self) -> None:
        for particle in self.particles:
            particle.step()

        self.particles = [p for p in self.particles if p.active]

        retain_score = 0.0
        fade_score = 0.0

        for p in self.particles:
            influence = p.wave_strength / (1.0 + p.distance)
            if p.polarity > 0:
                retain_score += influence
            else:
                fade_score += influence

        self.core.stability = retain_score - fade_score
        self.core.bias = self.core.stability
        self.core.existence += self.core.stability * 0.018
        self.core.existence = max(0.0, min(2.2, self.core.existence))
        self.core.pulse_phase += 0.18 + 0.03 * len(self.particles)
        self.tick_count += 1

    def reaction(self) -> str:
        if self.core.bias > 0.25:
            return "retain"
        elif self.core.bias < -0.25:
            return "fade"
        return "fluctuate"


def polar_to_xy(distance: float, angle: float) -> tuple[float, float]:
    return distance * math.cos(angle), distance * math.sin(angle)


def build_demo() -> OblivionisV02:
    life = OblivionisV02()
    demo_particles = [
        ("warm_signal",   +1, 1.00, 1.35, 0.20, 0.38, 0.26, 0.0),
        ("memory_trace",  +1, 0.86, 1.80, 1.35, 0.28, 0.18, 0.7),
        ("safe_word",     +1, 0.74, 1.15, 3.85, 0.42, 0.30, 1.4),
        ("loss_signal",   -1, 0.95, 1.45, 2.25, 0.33, 0.24, 0.5),
        ("noise",         -1, 0.58, 1.90, 5.00, 0.48, 0.33, 2.2),
    ]
    for args in demo_particles:
        life.inject(*args)
    return life


def make_animation(output_path: str = "oblivionis_v02_wave_visual.gif", num_frames: int = 54) -> None:
    life = build_demo()
    frames = []

    for _ in range(num_frames):
        frames.append({
            "tick": life.tick_count,
            "existence": life.core.existence,
            "stability": life.core.stability,
            "bias": life.core.bias,
            "reaction": life.reaction(),
            "pulse_phase": life.core.pulse_phase,
            "particles": [
                {
                    "value": p.value,
                    "polarity": p.polarity,
                    "base_strength": p.base_strength,
                    "wave_strength": p.wave_strength,
                    "distance": p.distance,
                    "angle": p.angle,
                    "phase": p.phase,
                    "amplitude": p.amplitude,
                }
                for p in life.particles
            ],
        })
        life.step()

    fig, ax = plt.subplots(figsize=(7.2, 7.2))
    ax.set_aspect("equal")
    ax.set_xlim(-3.6, 3.6)
    ax.set_ylim(-3.6, 3.6)
    ax.set_xlabel("memory field x")
    ax.set_ylabel("memory field y")
    title = ax.set_title("Oblivionis v0.2 — wave interference")

    core_scatter = ax.scatter([0], [0], s=[1000], marker="o", label="core")
    ax.text(0, 0.25, "self_core", ha="center")
    core_ring = plt.Circle((0, 0), radius=0.65, fill=False, linewidth=1.8)
    ax.add_patch(core_ring)

    retain_scatter = ax.scatter([], [], s=[], marker="o", label="retain particles")
    fade_scatter = ax.scatter([], [], s=[], marker="x", label="fade particles")

    max_wave_artists = 12
    wave_rings = []
    for _ in range(max_wave_artists):
        c = plt.Circle((0, 0), radius=0.2, fill=False, linewidth=1.0, alpha=0.4)
        ax.add_patch(c)
        wave_rings.append(c)

    particle_texts = [ax.text(0, 0, "", fontsize=8, ha="center") for _ in range(max_wave_artists)]
    status_text = ax.text(
        0.02, 0.98, "", transform=ax.transAxes, va="top", ha="left", family="monospace"
    )
    ax.legend(loc="lower right")

    def update(frame_idx: int):
        snap = frames[frame_idx]
        particles = snap["particles"]

        retain_xy, retain_sizes = [], []
        fade_xy, fade_sizes = [], []

        for t in particle_texts:
            t.set_text("")
        for ring in wave_rings:
            ring.set_radius(0.01)
            ring.set_alpha(0.0)

        for i, p in enumerate(particles[:max_wave_artists]):
            x, y = polar_to_xy(p["distance"], p["angle"])
            size = max(40, 280 * p["wave_strength"])

            if p["polarity"] > 0:
                retain_xy.append((x, y))
                retain_sizes.append(size)
            else:
                fade_xy.append((x, y))
                fade_sizes.append(size)

            particle_texts[i].set_position((x, y + 0.20))
            particle_texts[i].set_text(textwrap.shorten(p["value"], width=12, placeholder="…"))

            pulse = 0.18 + 0.16 * (1.0 + math.sin(p["phase"])) + 0.08 * p["amplitude"]
            wave_rings[i].center = (x, y)
            wave_rings[i].set_radius(pulse)
            wave_rings[i].set_alpha(min(0.65, 0.15 + 0.5 * p["amplitude"]))

        retain_scatter.set_offsets(retain_xy if retain_xy else [])
        retain_scatter.set_sizes(retain_sizes if retain_sizes else [])
        fade_scatter.set_offsets(fade_xy if fade_xy else [])
        fade_scatter.set_sizes(fade_sizes if fade_sizes else [])

        core_scatter.set_sizes([820 + 420 * snap["existence"] + 120 * abs(snap["bias"])])
        core_radius = 0.55 + 0.08 * math.sin(snap["pulse_phase"]) + 0.05 * abs(snap["bias"])
        core_ring.set_radius(core_radius)
        core_ring.set_alpha(0.35 + 0.25 * min(1.0, abs(snap["bias"])))

        title.set_text(f"Oblivionis v0.2 — wave interference / tick {snap['tick']}")
        status_text.set_text(
            f"reaction    : {snap['reaction']}\\n"
            f"existence   : {snap['existence']:.3f}\\n"
            f"stability   : {snap['stability']:.3f}\\n"
            f"bias        : {snap['bias']:.3f}\\n"
            f"particles   : {len(particles)}\\n"
            f"wave mode   : on"
        )

        return [retain_scatter, fade_scatter, core_scatter, status_text, title, core_ring, *particle_texts, *wave_rings]

    anim = FuncAnimation(fig, update, frames=len(frames), interval=170, blit=False)
    anim.save(output_path, writer=PillowWriter(fps=6))
    plt.close(fig)


if __name__ == "__main__":
    make_animation()
