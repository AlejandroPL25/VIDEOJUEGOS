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
    """Efectos del GDD: salto, recolección de chispas, daño y pérdida de vida (más punto de control, victoria, etc.)."""
    write("jump", sweep(300, 640, 0.18, 0.35))
    write("spark", concat(sweep(988, 988, 0.06, 0.3), sweep(1319, 1319, 0.14, 0.3)))
    write("hurt", concat(mix(noise_burst(0.14, 0.4, 0.5), sweep(440, 140, 0.3, 0.4, 0.25))))
    write("lifelost", concat(sweep(392, 392, 0.12, 0.3), sweep(330, 330, 0.12, 0.3), sweep(262, 262, 0.12, 0.3),
                             sweep(196, 120, 0.4, 0.35, 0.5, "tri")))
    write("checkpoint", concat(sweep(392, 392, 0.1, 0.3), sweep(587, 587, 0.18, 0.3)))
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
    n = NOTE[name[0]]
    idx = 1
    if name[1] == "#":
        n += 1; idx = 2
    octave = int(name[idx:])
    midi = 12 * (octave + 1) + n
    return 440.0 * 2 ** ((midi - 69) / 12)

def eighth(bpm):
    return 60.0 / bpm / 2.0

def square_track(seq, bpm, duty=0.25, vol=0.16, release=0.45):
    beat = eighth(bpm); out = []
    for note in seq:
        n = int(SR * beat)
        if note in ("-", "_"):
            out += [0.0] * n; continue
        f = hz(note)
        out += [square(f, i / SR, duty) * vol * env(i, n, 0.004, release) for i in range(n)]
    return out

def tri_track(seq, bpm, vol=0.2):
    beat = eighth(bpm); out = []
    for note in seq:
        n = int(SR * beat)
        if note in ("-", "_"):
            out += [0.0] * n; continue
        f = hz(note)
        out += [tri(f, i / SR) * vol * env(i, n, 0.004, 0.25) for i in range(n)]
    return out

def drum_track(pattern, bpm, vol=0.12):
    beat = eighth(bpm); out = []
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

def fit(seq, n=32):
    return (seq + ["-"] * n)[:n]

def make_music():
    """Cada nivel tiene una pista BASE cálida y ligera y una capa de PELIGRO (arpegios y percusión) de la
    misma duración. El juego mezcla la capa de peligro cuando Embra se acerca a enemigos o zonas de fuego."""
    temas = {
        # nombre: (bpm, melodía, bajo, acordes para los arpegios (4 compases de 8 corcheas))
        "music_bosque": (96,
            "E4 - G4 - A4 - G4 - E4 - D4 - E4 - - - G4 - B4 - A4 - G4 - E4 - D4 - C4 - D4 - E4 - - -".split(),
            "A2 - - - E2 - - - A2 - - - E2 - - - F2 - - - C2 - - - G2 - - - D2 - - -".split(),
            [["A4", "C5", "E5", "C5"], ["F4", "A4", "C5", "A4"], ["C5", "E5", "G5", "E5"], ["G4", "B4", "D5", "B4"]]),
        "music_canon": (104,
            "A4 - C5 - D5 - C5 - A4 - G4 - A4 - - - E4 - G4 - A4 - C5 - D5 - E5 - D5 - C5 - A4 - -".split(),
            "D2 - - - A2 - - - D2 - - - A2 - - - G2 - - - D2 - - - A2 - - - E2 - - -".split(),
            [["D4", "F4", "A4", "F4"], ["A4", "C5", "E5", "C5"], ["G4", "B4", "D5", "B4"], ["E4", "G4", "B4", "G4"]]),
        "music_ruinas": (100,
            "D4 - F4 - A4 - F4 - D4 - C4 - D4 - - - F4 - G4 - A4 - G4 - F4 - D4 - C4 - D4 - - - -".split(),
            "D2 - - - D2 - - - A2 - - - A2 - - - C2 - - - C2 - - - G2 - - - G2 - - -".split(),
            [["D4", "F4", "A4", "F4"], ["A4", "C5", "E5", "C5"], ["C5", "E5", "G5", "E5"], ["G4", "B4", "D5", "B4"]]),
        "music_altar": (112,
            "E4 - G4 - B4 - G4 - E4 - D4 - E4 - - - G4 - A4 - B4 - D5 - B4 - A4 - G4 - E4 - - - -".split(),
            "E2 - - - E2 - - - C2 - - - C2 - - - D2 - - - D2 - - - B1 - - - B1 - - -".split(),
            [["E4", "G4", "B4", "G4"], ["C4", "E4", "G4", "E4"], ["D4", "F#4", "A4", "F#4"], ["B3", "D4", "F#4", "D4"]]),
        "music_menu": (84,
            "C4 - E4 - G4 - E4 - A4 - G4 - E4 - D4 - C4 - E4 - G4 - E4 - D4 - C4 - - - - - - - - - - -".split(),
            "C2 - - - G2 - - - A2 - - - F2 - - - C2 - - - G2 - - - F2 - - - C2 - - -".split(),
            None),
    }
    for name, (bpm, mel, bass, chords) in temas.items():
        mel = fit(mel); bass = fit(bass)
        base = mix(square_track(mel, bpm), tri_track(bass, bpm))
        write(name, base * 2)
        if chords:
            arp = []
            for ch in chords:
                arp += ch * 2                      # 8 corcheas por compás
            arp = fit(arp)
            danger = mix(square_track(arp, bpm, duty=0.125, vol=0.1, release=0.6),
                         drum_track(list("k-hhk-hh" * 4), bpm),
                         tri_track(fit([b if b != "-" else "-" for b in bass]), bpm, vol=0.12))
            write(name + "_danger", danger * 2)

if __name__ == "__main__":
    make_sfx()
    make_music()
    print("Audio generado en", os.path.abspath(OUT))
