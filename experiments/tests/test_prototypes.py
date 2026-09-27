"""Import/regression tests, not acceptance tests for the future core or recall."""
from __future__ import annotations

import ast
from collections import Counter
from contextlib import contextmanager
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import sys
import unittest

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SUITES = ('early', 'music_baseline', 'music_improv')


@contextmanager
def probe(suite):
    """Isolate legacy absolute imports so the two model versions cannot mix."""
    aliases = ('music_field', 'session', 'improv')
    saved = {name: sys.modules.get(name) for name in aliases}
    loaded = {}
    try:
        for name in aliases:
            sys.modules.pop(name, None)
        for name in aliases:
            path = ROOT / suite / (name + '.py')
            if not path.exists():
                continue
            spec = importlib.util.spec_from_file_location(name, path)
            module = importlib.util.module_from_spec(spec)
            sys.modules[name] = module
            spec.loader.exec_module(module)
            loaded[name] = module
        yield loaded
    finally:
        for name in aliases:
            sys.modules.pop(name, None)
            if saved[name] is not None:
                sys.modules[name] = saved[name]


def assert_metrics(test, actual, expected, path='metrics'):
    if isinstance(expected, dict):
        test.assertEqual(set(actual), set(expected), path)
        for key in expected:
            assert_metrics(test, actual[key], expected[key], path + '.' + key)
    elif isinstance(expected, list):
        test.assertEqual(len(actual), len(expected), path)
        for i, (a, b) in enumerate(zip(actual, expected)):
            assert_metrics(test, a, b, f'{path}[{i}]')
    elif isinstance(expected, float):
        test.assertTrue(math.isclose(actual, expected, rel_tol=1e-12, abs_tol=1e-12),
                        f'{path}: {actual!r} != {expected!r}')
    else:
        test.assertEqual(actual, expected, path)


class PrototypeTests(unittest.TestCase):
    def test_source_integrity_and_syntax(self):
        manifest = json.loads((ROOT / 'provenance.json').read_text(encoding='utf-8'))
        expected = {entry['path'] for entry in manifest['sources']}
        actual = {str(p.relative_to(ROOT.parent)).replace('\\', '/')
                  for suite in SUITES for p in (ROOT / suite).glob('*.py')}
        self.assertEqual(len(expected), 17)
        self.assertEqual(actual, expected)
        for entry in manifest['sources']:
            with self.subTest(path=entry['path']):
                path = ROOT.parent / entry['path']
                self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), entry['sha256'])
                ast.parse(path.read_text(encoding='utf-8'), filename=entry['path'])

    def test_default_versions_match_every_step(self):
        with probe('music_baseline') as modules:
            old = modules['music_field'].MusicField(modules['session'].HARMONICS, seed=0)
            events = modules['session'].compose()
            instruments = modules['session'].INSTR
        with probe('music_improv') as modules:
            new = modules['music_field'].MusicField(modules['session'].HARMONICS, seed=0)
        cursor = total_fired = 0
        for step in range(4000):
            onsets = []
            while cursor < len(events) and events[cursor][0] < (step + 1) * old.p.dt:
                onsets.append(instruments[events[cursor][1]])
                cursor += 1
            fired_old, fired_new = old.step(onsets), new.step(onsets)
            self.assertEqual(fired_old, fired_new, f'step {step}')
            total_fired += len(fired_old)
            for name in ('phi', 'A', 'S', 'K'):
                np.testing.assert_array_equal(getattr(old, name), getattr(new, name))
            self.assertEqual(old.t, new.t)
            self.assertEqual(old.core_phi, new.core_phi)
        self.assertGreater(cursor, 0)
        self.assertGreater(total_fired, 0)
        self.assertGreater(float(old.A.max()), 0)

    def test_seed2_metrics(self):
        expected = json.loads((ROOT / 'results/imported/improv_seed2.json').read_text(encoding='utf-8'))
        self.assertEqual(set(expected), {'memory', 'improv'})
        with probe('music_improv') as modules:
            experiment = modules['improv']
            for name in ('memory', 'improv'):
                with self.subTest(condition=name):
                    field, _, notes = experiment.run(
                        modules['music_field'].MusicParams(**experiment.CONDITIONS[name]), seed=2)
                    assert_metrics(self, experiment.metrics(notes, field), expected[name])

    def test_random_control_preserves_notes_and_bar_membership(self):
        with probe('music_improv') as modules:
            experiment = modules['improv']
            notes = [dict(t=(experiment.C0 + k // 3 + 0.1) * experiment.BAR,
                          n=k % 3 + 1, voice=k % 3, freq=55.0 * (k % 3 + 1), vel=0.4)
                     for k in range(12)]
            pre = dict(notes[0], t=0.1)
            source = [pre, *notes]
            result = experiment.randomized(source, seed=2)
            key = lambda nt: (int(nt['t'] // experiment.BAR), nt['voice'], nt['n'], nt['freq'], nt['vel'])
            self.assertEqual(Counter(map(key, source)), Counter(map(key, result)))
            self.assertEqual(result[0], pre)
            self.assertNotEqual([n['t'] for n in source], [n['t'] for n in result])
            self.assertEqual(result, experiment.randomized(source, seed=2))

    def test_imported_summary_consistency(self):
        table = json.loads((ROOT / 'results/imported/improv_results.json').read_text(encoding='utf-8'))
        self.assertEqual(set(table['rows']), {'memory', 'fluct', 'improv', 'random'})
        self.assertTrue(all(len(rows) == 6 for rows in table['rows'].values()))
        with probe('music_improv') as modules:
            self.assertEqual(table['conditions'], modules['improv'].CONDITIONS)
            assert_metrics(self, modules['improv'].summarize(table['rows']), table['summary'])

    def test_bounded_extended_smoke(self):
        with probe('music_improv') as modules:
            params = modules['music_field'].MusicParams(**modules['improv'].CONDITIONS['improv'])
            field = modules['music_field'].MusicField(modules['session'].HARMONICS, params, seed=2)
            for step in range(1000):
                field.step([(220.0, 0.8)] if step % 50 == 0 else [])
                for name in ('A', 'S', 'K', 'F'):
                    values = getattr(field, name)
                    self.assertTrue(np.isfinite(values).all())
                    self.assertTrue((values >= 0).all())
                    self.assertTrue((values <= 1).all())
                self.assertTrue(0.2 <= field.drive <= 4.0)
                self.assertTrue(np.all(np.diag(field.K) == 0))


if __name__ == '__main__':
    unittest.main()
