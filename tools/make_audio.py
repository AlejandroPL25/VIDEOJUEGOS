#!/usr/bin/env python3
"""
Generador de audio para "Embra: La Llama Eterna".
Sintetiza efectos de sonido y música estilo chiptune con ondas cuadradas/triangulares (módulo wave).
Todo es original. Uso:  python3 tools/make_audio.py   ->  assets/audio/*.wav
"""
import math
import os
import random
import struct
import wave

OUT = os.path.join(os.path.dirname(__file__), "..", "assets", "audio")
os.makedirs(OUT, exist_ok=True)
SR = 22050

def write(name, samples):
    path = os.path.join(OUT, name + ".wav")
    with wave.open(path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        data = b"".join(struct.pack("<h", int(max(-1, min(1, s)) * 32000)) for s in samples)
        w.writeframes(data)

def square(freq, t, duty=0.5):
    return 1.0 if (freq * t) % 1.0 < duty else -1.0

def tri(freq, t):
    p = (freq * t) % 1.0
    return 4 * abs(p - 0.5) - 1

def env(i, n, attack=0.01, release=0.3):
    t = i / SR; dur = n / SR
    a = min(1.0, t / attack) if attack > 0 else 1.0
    r = min(1.0, (dur - t) / (dur * release)) if release > 0 else 1.0
    return max(0.0, min(a, r))

def sweep(f0, f1, dur, vol=0.5, duty=0.5, wave_fn="sq"):
    n = int(SR * dur); out = []; ph = 0.0
    for i in range(n):
        f = f0 + (f1 - f0) * (i / n)
        ph += f / SR
        v = (1.0 if ph % 1.0 < duty else -1.0) if wave_fn == "sq" else (4 * abs((ph % 1.0) - 0.5) - 1)
        out.append(v * vol * env(i, n, 0.005, 0.5))
    return out

def noise_burst(dur, vol=0.5, lp=0.3):
    n = int(SR * dur); out = []; last = 0.0
    for i in range(n):
        last = last + lp * ((random.random() * 2 - 1) - last)
        out.append(last * vol * env(i, n, 0.002, 0.8))
    return out

def concat(*parts):
    r = []
    for p in parts:
        r += p
    return r

def mix(*tracks):
    n = max(len(t) for t in tracks)
    return [sum(t[i] for t in tracks if i < len(t)) for i in range(n)]

random.seed(7)

def make_sfx():
    write("jump", sweep(300, 640, 0.18, 0.35))
    write("spark", concat(sweep(988, 988, 0.06, 0.3), sweep(1319, 1319, 0.14, 0.3)))
    write("stomp", mix(noise_burst(0.12, 0.5, 0.15), sweep(180, 60, 0.12, 0.5, 0.5, "tri")))
    write("fire", mix(noise_burst(0.22, 0.45, 0.5), sweep(520, 200, 0.2, 0.2)))
    write("hurt", concat(sweep(440, 120, 0.35, 0.45, 0.25)))
    write("oneup", concat(sweep(523, 523, 0.09, 0.3), sweep(659, 659, 0.09, 0.3), sweep(784, 784, 0.09, 0.3), sweep(1047, 1047, 0.2, 0.3)))
    write("checkpoint", concat(sweep(392, 392, 0.1, 0.3), sweep(587, 587, 0.18, 0.3)))
    write("hit", mix(noise_burst(0.1, 0.5, 0.4), sweep(300, 150, 0.1, 0.3)))
    write("boss_die", mix(noise_burst(0.9, 0.5, 0.2), sweep(400, 40, 0.9, 0.35, 0.5, "tri")))
    write("shard", sweep(900, 500, 0.15, 0.25, 0.125))
    notas = [523, 659, 784, 1047, 784, 1047, 1319]
    win = []
    for i, f in enumerate(notas):
        win += sweep(f, f, 0.14 if i < len(notas) - 1 else 0.5, 0.3)
    write("win", win)
    over = concat(sweep(392, 392, 0.2, 0.3), sweep(330, 330, 0.2, 0.3), sweep(262, 262, 0.2, 0.3), sweep(196, 196, 0.6, 0.35, 0.5, "tri"))
    write("gameover", over)
    write("click", sweep(800, 800, 0.05, 0.25))

# ---------- Música ----------
NOTE = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}

def hz(name):
    # ej: "A4", "C#5"
    n = NOTE[name[0]]
    idx = 1
    if name[1] == "#":
        n += 1; idx = 2
    octave = int(name[idx:])
    midi = 12 * (octave + 1) + n
    return 440.0 * 2 ** ((midi - 69) / 12)

def melody_track(seq, bpm, duty=0.25, vol=0.18):
    beat = 60.0 / bpm / 2.0  # corcheas
    out = []
    for note in seq:
        n = int(SR * beat)
        if note in ("-", "_"):
            out += [0.0] * n
            continue
        f = hz(note)
        for i in range(n):
            t = i / SR
            out.append(square(f, t, duty) * vol * env(i, n, 0.004, 0.45))
    return out

def bass_track(seq, bpm, vol=0.22):
    beat = 60.0 / bpm / 2.0
    out = []
    for note in seq:
        n = int(SR * beat)
        if note in ("-", "_"):
            out += [0.0] * n
            continue
        f = hz(note)
        for i in range(n):
            out.append(tri(f, i / SR) * vol * env(i, n, 0.004, 0.25))
    return out

def drum_track(pattern, bpm, vol=0.12):
    beat = 60.0 / bpm / 2.0
    out = []
    for p in pattern:
        n = int(SR * beat)
        if p == "k":
            seg = sweep(150, 50, beat, 0.45, 0.5, "tri")
        elif p == "h":
            seg = noise_burst(beat * 0.4, vol, 0.9)
        else:
            seg = [0.0]
        seg = seg + [0.0] * max(0, n - len(seg))
        out += seg[:n]
    return out

def make_music():
    zonas = {
        # nombre: (bpm, melodía(32 corcheas), bajo(32), batería(32))
        "music_bosque": (
            100,
            "E4 - G4 - A4 - G4 E4 D4 - E4 - G4 - B4 - A4 - G4 - E4 D4 - E4 - -".split(),
            "A2 - A2 - E2 - E2 - A2 - A2 - G2 - G2 - A2 - A2 - E2 - E2 - D2 - D2 -".split(),
            list("k-h-k-h-" * 4),
        ),
        "music_cuevas": (
            112,
            "A4 - C5 - E5 - C5 A4 G4 - A4 - C5 - D5 - E5 - C5 - A4 - G4 E4 - A4 - -".split(),
            "A2 - E3 - A2 - E3 - F2 - C3 - F2 - C3 - G2 - D3 - G2 - D3 - E2 - B2 -".split(),
            list("k-hhk-hh" * 4),
        ),
        "music_ruinas": (
            108,
            "D4 - F4 - A4 - F4 D4 C4 - D4 - F4 - G4 - A4 - G4 - F4 - D4 C4 - D4 - -".split(),
            "D2 - D2 - A2 - A2 - D2 - D2 - C2 - C2 - Bb2 -".replace("Bb2", "B2").split() + "D2 - D2 - A2 - A2 - G2 - G2 -".split(),
            list("k-h-kkh-" * 4),
        ),
        "music_fortaleza": (
            132,
            "E4 E4 - G4 B4 - A4 G4 E4 - E4 G4 - B4 C5 - B4 A4 G4 - E4 D4 - E4 - -".split(),
            "E2 E2 - E2 G2 - G2 G2 A2 - A2 A2 - C3 C3 - B2 B2 B2 - E2 E2 E2 - E2 -".split(),
            list("kkh-kkh-" * 4),
        ),
        "music_menu": (
            84,
            "C4 - E4 - G4 - E4 - A4 - G4 - E4 - D4 - C4 - E4 - G4 - E4 - D4 - C4 - - -".split(),
            "C2 - - - G2 - - - A2 - - - F2 - - - C2 - - - G2 - - - F2 - - - C2 - - -".split(),
            list("k-------" * 4),
        ),
    }
    for name, (bpm, mel, bass, drums) in zonas.items():
        L = 32
        mel = (mel + ["-"] * L)[:L]
        bass = (bass + ["-"] * L)[:L]
        drums = (drums + ["-"] * L)[:L]
        m = melody_track(mel, bpm)
        b = bass_track(bass, bpm)
        d = drum_track(drums, bpm)
        track = mix(m, b, d)
        # repetimos 2 veces para que el loop dure ~ 20-30 s
        write(name, track * 2)

if __name__ == "__main__":
    make_sfx()
    make_music()
    print("Audio generado en", os.path.abspath(OUT))
