#!/usr/bin/env python3
"""Procedural sound effects for Bonus Braincell (v4, 2026-11-26). All synthesized here: no samples, no licenses.

Use for meaningful events only (a stamp lands, a coin drops, a crack starts, a clock adds a second), at most
about one cue per 3 s. Spec: scene "sfx": [{"at": "phrase or seconds", "sound": "clink", "gain_db": 0}].

Sounds: tick, tock, clink, coins, stamp, thump, whoosh, swoosh_up, paper, crack, pop, chime, beep, register, riser
"""
import numpy as np

SR = 48000

def _env(n, a=0.002, r=0.2):
    t = np.arange(n) / SR
    att = np.clip(t / max(a, 1e-4), 0, 1)
    return att * np.exp(-t / max(r, 1e-4))

def _noise(n, rng):
    return rng.standard_normal(n).astype(np.float32)

def _lp(x, k):
    """one-pole low-pass, k in (0,1): smaller = darker"""
    y = np.empty_like(x); acc = 0.0
    for i in range(len(x)):
        acc += k * (x[i] - acc); y[i] = acc
    return y

def _bp(x, lo, hi):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    X[(f < lo) | (f > hi)] = 0
    return np.fft.irfft(X, len(x)).astype(np.float32)

def _sine(freq, n, phase=0.0):
    t = np.arange(n) / SR
    if callable(freq):
        ph = 2 * np.pi * np.cumsum(freq(t)) / SR
        return np.sin(ph + phase)
    return np.sin(2 * np.pi * freq * t + phase)

def make(name, rng=None):
    rng = rng or np.random.default_rng(1)
    if name == "tick":
        n = int(0.05 * SR); x = _bp(_noise(n, rng), 2500, 9000) * _env(n, 0.0005, 0.008) + 0.4 * _sine(3200, n) * _env(n, 0.0005, 0.01)
    elif name == "tock":
        n = int(0.08 * SR); x = _bp(_noise(n, rng), 800, 3000) * _env(n, 0.0005, 0.012) + 0.6 * _sine(900, n) * _env(n, 0.0005, 0.02)
    elif name == "clink":  # small metal coin: inharmonic partials
        n = int(0.6 * SR); x = sum(a * _sine(f, n) * _env(n, 0.0005, r) for f, a, r in
                                   ((3150, 1.0, 0.16), (5230, 0.6, 0.09), (7640, 0.35, 0.05), (2210, 0.4, 0.22)))
        x += 0.3 * _bp(_noise(n, rng), 4000, 12000) * _env(n, 0.0003, 0.004)
    elif name == "coins":  # several clinks
        n = int(0.9 * SR); x = np.zeros(n)
        for k in range(6):
            c = make("clink", np.random.default_rng(k + 3)) * rng.uniform(0.4, 1.0)
            o = int(rng.uniform(0, 0.45) * SR); m = min(len(c), n - o)
            x[o:o + m] += c[:m] * (0.8 + 0.1 * k / 6)
    elif name == "stamp":  # press / rubber stamp: low body + click
        n = int(0.35 * SR)
        x = 1.0 * _sine(lambda t: 140 * np.exp(-t * 18) + 55, n) * _env(n, 0.001, 0.09)
        x += 0.6 * _lp(_noise(n, rng), 0.25) * _env(n, 0.0005, 0.03)
    elif name == "thump":
        n = int(0.4 * SR); x = _sine(lambda t: 90 * np.exp(-t * 10) + 40, n) * _env(n, 0.002, 0.12)
    elif name in ("whoosh", "swoosh_up"):
        n = int(0.55 * SR); t = np.arange(n) / SR
        shape = np.sin(np.pi * np.clip(t / 0.55, 0, 1)) ** 2
        lo, hi = (300, 2500) if name == "whoosh" else (600, 5000)
        x = _bp(_noise(n, rng), lo, hi) * shape * 0.9
    elif name == "paper":
        n = int(0.45 * SR); x = _bp(_noise(n, rng), 1500, 8000)
        bursts = np.zeros(n)
        for k in range(7):
            o = int(rng.uniform(0, 0.36) * SR); L = int(rng.uniform(0.01, 0.05) * SR)
            bursts[o:o + L] += np.hanning(L) * rng.uniform(0.4, 1)
        x = x * bursts * 0.9
    elif name == "crack":
        n = int(0.7 * SR); x = _bp(_noise(n, rng), 1200, 9000) * _env(n, 0.0003, 0.03) * 1.2
        x += 0.7 * _lp(_noise(n, rng), 0.03) * _env(n, 0.01, 0.25) * 3
    elif name == "pop":
        n = int(0.12 * SR); x = _sine(lambda t: 500 + 900 * np.exp(-t * 60), n) * _env(n, 0.001, 0.04)
    elif name == "chime":
        n = int(1.2 * SR); x = sum(a * _sine(f, n) * _env(n, 0.002, r) for f, a, r in
                                   ((880, 1.0, 0.5), (1320, 0.5, 0.35), (1760, 0.3, 0.25), (2640, 0.12, 0.15)))
    elif name == "beep":
        n = int(0.18 * SR); x = _sine(1000, n) * np.clip(np.minimum(np.arange(n), n - np.arange(n)) / (0.005 * SR), 0, 1) * 0.7
    elif name == "register":  # receipt / counter landing: tick + chime
        x = np.concatenate([make("tick", rng), np.zeros(int(0.03 * SR)), make("chime", rng) * 0.5])
    elif name == "riser":
        n = int(1.0 * SR); t = np.arange(n) / SR
        x = _bp(_noise(n, rng), 400, 6000) * (t / 1.0) ** 2 * 0.8
    else:
        raise ValueError(f"unknown sfx '{name}'")
    x = np.asarray(x, dtype=np.float32)
    pk = np.max(np.abs(x)) or 1
    return x / pk

def build_track(cues, total_s, peak_db=-19.0):
    """cues: [{"t": seconds, "sound": name, "gain_db": 0}] -> mono float32 track at SR."""
    track = np.zeros(int(total_s * SR) + SR, dtype=np.float32)
    rng = np.random.default_rng(11)
    for c in cues:
        x = make(c["sound"], rng) * (10 ** ((peak_db + float(c.get("gain_db", 0))) / 20))
        o = int(max(0, c["t"]) * SR)
        m = min(len(x), len(track) - o)
        if m > 0:
            track[o:o + m] += x[:m]
    return track[: int(total_s * SR)]

def music_bed(total_s, seed=1, peak_db=-30.0, bpm=96, mood="curious"):
    """Procedural music bed (v4.1, 2026-11-26): soft chord pad + a light pulse, no samples, no license.
    Sits ~16 dB under narration peaks. Moods: curious (major 7ths), tense (minor), bright (major)."""
    rng = np.random.default_rng(seed)
    n = int(total_s * SR) + SR
    t = np.arange(n) / SR
    prog = {"curious": [[60, 64, 67, 71], [57, 60, 64, 67], [53, 57, 60, 64], [55, 59, 62, 65]],
            "tense": [[57, 60, 64], [53, 57, 60], [55, 58, 62], [52, 55, 59]],
            "bright": [[60, 64, 67], [55, 59, 62], [57, 60, 64], [53, 57, 60]]}[mood]
    bar = 4 * 60 / bpm * 2          # one chord per two bars
    out = np.zeros(n, dtype=np.float32)
    k = 0
    while k * bar < total_s + bar:
        chord = prog[k % len(prog)]
        s0 = int(k * bar * SR); L = int(bar * SR * 1.15)
        if s0 >= n:
            break
        tt = np.arange(L) / SR
        envl = np.clip(tt / 0.9, 0, 1) * np.clip((bar * 1.15 - tt) / 0.6, 0, 1)
        seg = np.zeros(L)
        for m in chord:
            f = 440 * 2 ** ((m - 69) / 12)
            for det in (-0.6, 0.6):
                seg += np.sin(2 * np.pi * (f + det) * tt + rng.uniform(0, 6.28)) * 0.5
            seg += 0.15 * np.sin(2 * np.pi * f * 2 * tt)
        seg *= envl
        e = min(n, s0 + L)
        out[s0:e] += seg[: e - s0]
        k += 1
    # light pulse on the beat (filtered noise tick + low sine), very quiet
    beat = 60 / bpm
    for b in np.arange(0, total_s, beat):
        s0 = int(b * SR); L = int(0.09 * SR)
        if s0 + L < n:
            tt = np.arange(L) / SR
            out[s0:s0 + L] += 0.25 * np.sin(2 * np.pi * 55 * tt) * np.exp(-tt / 0.05)
    out = _lp(out.astype(np.float32), 0.08) if len(out) < 6_000_000 else out
    pk = np.max(np.abs(out)) or 1
    out = out / pk * (10 ** (peak_db / 20))
    fade = int(1.5 * SR)
    out[:fade] *= np.linspace(0, 1, fade)
    out[int(total_s * SR) - fade:int(total_s * SR)] *= np.linspace(1, 0, fade)
    return out[: int(total_s * SR)]
