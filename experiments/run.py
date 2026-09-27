"""Run an explicitly selected historical probe in an ignored output directory."""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
PROBES = {
    'early': ('v00.py', 'oblivionis_v01_visual.py', 'oblivionis_v02_wave_visual.py',
              'oblivionis_v04_peak_search.py'),
    'music_baseline': ('session.py', 'seeds.py', 'tune.py', 'plot_session.py'),
    'music_improv': ('session.py', 'seeds.py', 'tune.py', 'plot_session.py',
                     'improv.py', 'render_improv.py'),
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('suite', choices=PROBES)
    parser.add_argument('script', help='An allowed script filename within the suite')
    parser.add_argument('args', nargs=argparse.REMAINDER)
    args = parser.parse_args()
    if args.script not in PROBES[args.suite]:
        parser.error('script must be one of: ' + ', '.join(PROBES[args.suite]))
    output = ROOT / 'outputs' / args.suite
    output.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env['MPLBACKEND'] = 'Agg'
    process = subprocess.run(
        [sys.executable, str(ROOT / args.suite / args.script), *args.args],
        cwd=output, env=env, check=False,
    )
    return process.returncode


if __name__ == '__main__':
    raise SystemExit(main())
