#!/usr/bin/env python3
"""Synthesizes the Tap Genius background loop (public/audio/bgmusic.m4a). Needs numpy + ffmpeg.
Original composition: 124 bpm, C-Am-F-G, 16 bars (~31s), seamless loop."""
import subprocess, sys, numpy as np
SR = 44100; BPM = 124; BEAT = 60 / BPM; BARS = 16
N = int(SR * BEAT * 4 * BARS); TAIL = int(SR * 1.5)
buf = np.zeros(N + TAIL)
rng = np.random.default_rng(7)
hz = lambda m: 440 * 2 ** ((m - 69) / 12)

def put(t, x):
    i = int(t * SR); x = x[: len(buf) - i]; buf[i:i + len(x)] += x

def env(n, a=0.004, d=0.2):
    t = np.arange(n) / SR
    return np.minimum(t / a, 1) * np.exp(-t / d)

def tone(f, dur, kind='tri', d=0.2, a=0.004):
    n = int(SR * dur); t = np.arange(n) / SR
    ph = 2 * np.pi * f * t
    if kind == 'tri': w = 2 / np.pi * np.arcsin(np.sin(ph))
    elif kind == 'sq': w = np.sign(np.sin(ph)) * 0.5 + 0.5 * np.sin(ph * 2)
    elif kind == 'bell': w = np.sin(ph) + 0.4 * np.sin(ph * 2.01) * np.exp(-t * 6) + 0.2 * np.sin(ph * 3.99) * np.exp(-t * 10)
    else: w = np.sin(ph)
    return w * env(n, a, d)

def lp(x, k):  # one-pole lowpass
    y = np.empty_like(x); s = 0.0
    for i, v in enumerate(x): s += k * (v - s); y[i] = s
    return y

def kick():
    n = int(SR * 0.28); t = np.arange(n) / SR
    f = 45 + 90 * np.exp(-t * 28)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 11) * 0.9

def hat(open_=False):
    n = int(SR * (0.18 if open_ else 0.05)); x = rng.standard_normal(n)
    x = x - lp(x, 0.35)  # highpass-ish
    return x * np.exp(-np.arange(n) / SR * (22 if open_ else 70)) * 0.25

def clap():
    n = int(SR * 0.16); x = rng.standard_normal(n); x = lp(x - lp(x, 0.1), 0.6)
    t = np.arange(n) / SR
    return x * (np.exp(-t * 30) + 0.6 * np.exp(-((t - 0.012) ** 2) * 9e4)) * 0.5

chords = [(60, 64, 67), (57, 60, 64), (53, 57, 60), (55, 59, 62)]   # C Am F G
roots = [36, 33, 29, 31]
# melody (pentatonic hook), per 2-bar phrase: (sixteenth offset, midi, sixteenths length)
hookA = [(0, 76, 2), (3, 79, 1), (4, 76, 2), (6, 74, 2), (8, 72, 3), (12, 74, 1), (14, 76, 2)]
hookB = [(0, 79, 2), (3, 81, 1), (4, 79, 2), (6, 76, 2), (8, 74, 2), (10, 72, 2), (12, 74, 4)]
hookC = [(0, 72, 1), (1, 76, 1), (2, 79, 2), (4, 84, 3), (8, 81, 2), (10, 79, 2), (12, 76, 4)]
hookD = [(0, 74, 2), (2, 77, 2), (4, 79, 2), (6, 77, 2), (8, 74, 4), (12, 71, 2), (14, 74, 2)]
hooks = [hookA, hookB, hookC, hookD]
S = BEAT / 4  # sixteenth

for bar in range(BARS):
    t0 = bar * BEAT * 4; ci = bar % 4; ch = chords[ci]; sec = bar // 4   # sections of 4 bars
    full = sec >= 1
    for beat in range(4):
        tb = t0 + beat * BEAT
        if sec == 0 and bar < 1 and beat < 0: continue
        put(tb, kick() * (0.8 if beat % 2 else 1.0))
        if beat in (1, 3): put(tb, clap() * (0.7 if full else 0.45))
        put(tb + BEAT / 2, hat(beat == 3) * (1.0 if full else 0.7))
        if full:
            put(tb + BEAT / 4, hat() * 0.5); put(tb + 3 * BEAT / 4, hat() * 0.5)
    for e in range(8):  # driving 8th bass
        m = roots[ci] + (12 if e % 4 == 3 else 0)
        put(t0 + e * BEAT / 2, lp(tone(hz(m), BEAT * 0.45, 'tri', 0.18), 0.12) * 1.1)
    for s16 in range(16):  # plucky arp
        pat = [0, 1, 2, 1] if sec % 2 == 0 else [0, 2, 1, 2]
        m = ch[pat[s16 % 4]] + 12 + (12 if s16 % 8 >= 4 and full else 0)
        put(t0 + s16 * S, tone(hz(m), 0.2, 'sq', 0.07) * (0.11 if full else 0.08))
    for m in ch:  # soft pad
        put(t0, lp(tone(hz(m), BEAT * 4, 'sin', 1.6, 0.25), 0.2) * 0.08)
    if sec >= 1 and bar % 2 == 0:  # bell melody, from bar 5
        for off, m, ln in hooks[(bar // 2) % 4 if sec != 2 else (bar // 2 + 1) % 4]:
            put(t0 + off * S, tone(hz(m), ln * S + 0.25, 'bell', 0.25, 0.006) * 0.16)

# wrap the tail back onto the start for a seamless loop
out = buf[:N].copy(); out[:TAIL] += buf[N:]
# gentle glue: soft clip + normalize
out = np.tanh(out * 1.4); out *= 0.38 / np.abs(out).max()
pcm = (out * 32767).astype('<i2').tobytes()
dst = sys.argv[1] if len(sys.argv) > 1 else 'public/audio/bgmusic.m4a'
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 's16le', '-ar', str(SR), '-ac', '1', '-i', '-',
                '-c:a', 'aac', '-b:a', '56k', '-movflags', '+faststart', dst], input=pcm, check=True)
print(dst, round(N / SR, 1), 's')
