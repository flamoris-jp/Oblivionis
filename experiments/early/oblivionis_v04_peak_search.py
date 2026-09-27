from dataclasses import dataclass, field
from typing import List
import math
from pathlib import Path

import matplotlib.pyplot as plt
import imageio.v2 as imageio
import numpy as np


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
    threshold: float = 0.22
    decay: float = 0.97
    active: bool = True

    def step(self) -> None:
        if not self.active:
            return
        self.phase += self.frequency
        osc = 1.0 + self.amplitude * math.sin(self.phase)
        self.wave_strength = max(0.0, self.base_strength * osc)
        self.base_strength *= self.decay
        if self.base_strength < 0.05:
            self.active = False


@dataclass
class Core:
    existence: float = 1.0
    stability: float = 0.0


@dataclass
class InputWave:
    value: str
    amplitude: float
    phase: float
    frequency: float = 0.18


@dataclass
class OblivionisV04:
    core: Core = field(default_factory=Core)
    particles: List[Particle] = field(default_factory=list)
    tick_count: int = 0

    def inject(
        self,
        value: str,
        polarity: int,
        base_strength: float = 1.0,
        distance: float = 1.0,
        angle: float = 0.0,
        amplitude: float = 0.4,
        frequency: float = 0.2,
        phase: float = 0.0,
        threshold: float = 0.22,
    ) -> None:
        self.particles.append(
            Particle(
                value=value,
                polarity=1 if polarity >= 0 else -1,
                base_strength=base_strength,
                wave_strength=base_strength,
                distance=distance,
                angle=angle,
                amplitude=amplitude,
                frequency=frequency,
                phase=phase,
                threshold=threshold,
            )
        )

    def particle_interaction(self, p1: Particle, p2: Particle) -> float:
        phase_diff = p1.phase - p2.phase
        dist = abs(p1.distance - p2.distance)
        distance_factor = 1.0 / (1.0 + dist)
        return p1.wave_strength * p2.wave_strength * math.cos(phase_diff) * distance_factor

    def input_interaction(self, input_wave: InputWave, p: Particle) -> float:
        interaction = input_wave.amplitude * p.wave_strength * math.cos(input_wave.phase - p.phase)
        interaction = interaction / (1.0 + p.distance)
        return interaction

    def step(self, input_wave: InputWave):
        for p in self.particles:
            p.step()

        self.particles = [p for p in self.particles if p.active]

        influences = [0.0 for _ in self.particles]
        for i in range(len(self.particles)):
            for j in range(i + 1, len(self.particles)):
                inter = self.particle_interaction(self.particles[i], self.particles[j])
                influences[i] += inter
                influences[j] += inter

        for i, p in enumerate(self.particles):
            drift = influences[i] * 0.02
            p.distance -= drift
            p.distance = max(0.25, min(2.8, p.distance))
            p.angle += 0.02 + 0.01 * math.sin(p.phase)

        peaks = []
        retain = 0.0
        fade = 0.0

        for idx, p in enumerate(self.particles):
            interaction = self.input_interaction(input_wave, p)
            excess = interaction - p.threshold
            if excess > 0.0:
                peaks.append(
                    {
                        "index": idx,
                        "value": p.value,
                        "interaction": interaction,
                        "excess": excess,
                        "polarity": p.polarity,
                    }
                )
                if p.polarity > 0:
                    retain += excess
                else:
                    fade += excess

        self.core.stability = retain - fade
        self.core.existence += self.core.stability * 0.03
        self.core.existence = max(0.0, min(2.5, self.core.existence))

        self.tick_count += 1
        input_wave.phase += input_wave.frequency
        return peaks


def polar_to_xy(distance: float, angle: float):
    return distance * math.cos(angle), distance * math.sin(angle)


def build_demo():
    world = OblivionisV04()
    demo_particles = [
        ("warm_signal", +1, 1.00, 1.25, 0.10, 0.40, 0.21, 0.15, 0.22),
        ("memory_trace", +1, 0.92, 1.55, 0.80, 0.35, 0.17, 0.70, 0.24),
        ("safe_word", +1, 0.86, 1.05, 1.60, 0.42, 0.24, 1.20, 0.22),
        ("music_hint", +1, 0.83, 1.70, 2.35, 0.33, 0.19, 1.90, 0.23),
        ("focus_trace", +1, 0.78, 1.30, 3.10, 0.29, 0.23, 2.70, 0.22),
        ("loss_signal", -1, 0.95, 1.35, 3.90, 0.38, 0.20, 1.70, 0.23),
        ("noise", -1, 0.75, 1.85, 4.60, 0.46, 0.26, 0.40, 0.24),
        ("fear_edge", -1, 0.80, 1.45, 5.20, 0.31, 0.18, 2.40, 0.24),
        ("echo", -1, 0.72, 1.95, 5.80, 0.44, 0.22, 0.90, 0.24),
        ("static", -1, 0.68, 1.60, 0.45, 0.27, 0.16, 2.90, 0.25),
    ]
    for args in demo_particles:
        world.inject(*args)
    input_wave = InputWave(value="music_input", amplitude=1.05, phase=0.0, frequency=0.20)
    return world, input_wave


def render_gif(output_path: str = "oblivionis_v04_peak_search.gif", num_frames: int = 72) -> None:
    world, input_wave = build_demo()
    frames = []

    for frame_no in range(num_frames):
        peaks = world.step(input_wave)

        fig, ax = plt.subplots(figsize=(7, 7))
        ax.set_aspect("equal")
        ax.set_xlim(-3.2, 3.2)
        ax.set_ylim(-3.2, 3.2)
        ax.set_xlabel("memory field x")
        ax.set_ylabel("memory field y")
        ax.set_title(f"Oblivionis v0.4 — peak search / tick {world.tick_count}")

        core_size = 700 + 450 * world.core.existence
        ax.scatter([0], [0], s=[core_size], marker="o", label="core")
        core_ring = plt.Circle((0, 0), radius=0.55 + 0.06 * math.sin(frame_no * 0.25), fill=False, linewidth=1.8, alpha=0.5)
        ax.add_patch(core_ring)
        ax.text(0, 0.22, "self_core", ha="center", fontsize=9)

        retain_xy, retain_sizes = [], []
        fade_xy, fade_sizes = [], []
        peak_xy, peak_sizes = [], []

        peak_indices = {p["index"]: p for p in peaks}
        wave_x = 2.6 * math.cos(input_wave.phase)
        wave_y = 2.6 * math.sin(input_wave.phase)

        for idx, p in enumerate(world.particles):
            x, y = polar_to_xy(p.distance, p.angle)
            base_size = max(30, 180 * p.wave_strength)

            if p.polarity > 0:
                retain_xy.append((x, y))
                retain_sizes.append(base_size)
            else:
                fade_xy.append((x, y))
                fade_sizes.append(base_size)

            ax.text(x, y + 0.16, p.value, ha="center", fontsize=7)

            if idx in peak_indices:
                peak = peak_indices[idx]
                peak_xy.append((x, y))
                peak_sizes.append(260 + 900 * peak["excess"])
                ax.plot([wave_x, x], [wave_y, y], linewidth=1.2, alpha=0.5)

        if retain_xy:
            ax.scatter([x for x, _ in retain_xy], [y for _, y in retain_xy], s=retain_sizes, marker="o", label="retain")
        if fade_xy:
            ax.scatter([x for x, _ in fade_xy], [y for _, y in fade_xy], s=fade_sizes, marker="x", label="fade")
        if peak_xy:
            ax.scatter(
                [x for x, _ in peak_xy],
                [y for _, y in peak_xy],
                s=peak_sizes,
                marker="o",
                facecolors="none",
                linewidths=2.0,
                label="peaks",
            )

        ax.scatter([wave_x], [wave_y], s=[240], marker="*", label="input wave")
        ax.text(wave_x, wave_y + 0.18, input_wave.value, ha="center", fontsize=8)

        reaction = "no_peak"
        if peaks:
            if world.core.stability > 0.2:
                reaction = "retain"
            elif world.core.stability < -0.2:
                reaction = "fade"
            else:
                reaction = "fluctuate"

        status = (
            f"reaction   : {reaction}\n"
            f"existence  : {world.core.existence:.3f}\n"
            f"stability  : {world.core.stability:.3f}\n"
            f"peak_count : {len(peaks)}\n"
            f"input_phase: {input_wave.phase:.3f}"
        )
        ax.text(0.02, 0.98, status, transform=ax.transAxes, va="top", ha="left", family="monospace")
        ax.legend(loc="lower right")

        fig.canvas.draw()
        frame = np.asarray(fig.canvas.buffer_rgba())
        frames.append(frame.copy())
        plt.close(fig)

    imageio.mimsave(Path(output_path), frames, duration=0.12, loop=0)


if __name__ == "__main__":
    render_gif()
