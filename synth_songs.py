import wave, math, struct, os, random, json

SR = 22050
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "public", "songs")

MAJOR = [0, 2, 4, 5, 7, 9, 11]
MINOR = [0, 2, 3, 5, 7, 8, 10]
PENTA = [0, 2, 4, 7, 9]


def midi_to_freq(n):
    return 440.0 * (2 ** ((n - 69) / 12.0))


def note_wave(freq, dur, amp, vibrato=0.0, sr=SR):
    n = int(dur * sr)
    a, r = 0.008, 0.07
    out = []
    for i in range(n):
        t = i / sr
        if t < a:
            e = t / a
        elif t > dur - r:
            e = max(0.0, (dur - t) / r)
        else:
            e = 1.0
        f = freq * (1 + 0.004 * math.sin(2 * math.pi * 5 * t)) if vibrato else freq
        s = math.sin(2 * math.pi * f * t)
        s += 0.5 * math.sin(2 * math.pi * 2 * f * t)
        s += 0.25 * math.sin(2 * math.pi * 3 * f * t)
        out.append(amp * e * s / 1.75)
    return out


def write_wav(path, sig, sr=SR):
    with wave.open(path, "w") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        frames = b"".join(struct.pack("<h", int(max(-1, min(1, x)) * 32767)) for x in sig)
        w.writeframes(frames)


def make_melody(rng, root, scale, bpm, beats_total, character, dissonant=False):
    beat = 60.0 / bpm
    sig = []
    total = 0.0
    while total < beats_total:
        deg = rng.choice(scale)
        midi = root + deg
        if character == "staccato":
            b = rng.choice([0.5, 0.5, 0.25])
        elif character == "legato":
            b = rng.choice([1.0, 1.0, 2.0, 0.5])
        else:
            b = rng.choice([0.5, 1.0, 0.25, 1.0])
        dur = b * beat
        amp = rng.choice([0.8, 0.9, 1.0]) if character == "accent" else 0.9
        seg = note_wave(midi_to_freq(midi), dur, amp, vibrato=(3 if character == "tremolo" else 0))
        sig += seg
        if dissonant and rng.random() < 0.5:
            # add a minor-second cluster for tension
            sig2 = note_wave(midi_to_freq(midi + 1), dur, 0.5, vibrato=3)
            sig = [a + b for a, b in zip(sig, sig2 + [0] * (len(sig) - len(sig2)))]
        total += b
    return sig


def normalize(sig):
    peak = max(1e-6, max(abs(x) for x in sig))
    return [x / peak * 0.9 for x in sig]


# (id, title, artist, emotion, root, scale, bpm, character, dissonant, bars*beats)
specs = [
    ("h1", "Sunny Morning", "Local Demo", "happy", 60, MAJOR, 140, "staccato", False, 32),
    ("h2", "Bubble Dance", "Local Demo", "happy", 64, MAJOR, 150, "staccato", False, 32),
    ("s1", "Rainy Night", "Local Demo", "sad", 57, MINOR, 70, "legato", False, 28),
    ("s2", "Faded Letter", "Local Demo", "sad", 55, MINOR, 64, "legato", False, 28),
    ("a1", "Red Storm", "Local Demo", "angry", 55, MINOR, 165, "staccato", True, 30),
    ("a2", "Iron Fist", "Local Demo", "angry", 53, MINOR, 175, "staccato", True, 30),
    ("su1", "Magic Spark", "Local Demo", "surprised", 62, MAJOR, 125, "accent", False, 28),
    ("su2", "Wow Moment", "Local Demo", "surprised", 66, MAJOR, 130, "accent", False, 28),
    ("f1", "Dark Corner", "Local Demo", "fearful", 53, MINOR, 66, "tremolo", True, 26),
    ("f2", "Cold Sweat", "Local Demo", "fearful", 51, MINOR, 60, "tremolo", True, 26),
    ("n1", "Quiet Lake", "Local Demo", "neutral", 60, PENTA, 64, "legato", False, 28),
    ("n2", "Soft Breeze", "Local Demo", "neutral", 62, PENTA, 70, "legato", False, 28),
]

catalog = []
os.makedirs(OUT, exist_ok=True)
for sid, title, artist, emo, root, scale, bpm, char, dis, beats in specs:
    rng = random.Random(hash(sid) & 0xFFFF)
    sig = make_melody(rng, root, scale, bpm, beats, char, dis)
    sig = normalize(sig)
    fname = f"{sid}.wav"
    write_wav(os.path.join(OUT, fname), sig)
    catalog.append({
        "id": sid,
        "title": title,
        "artist": artist,
        "emotion": emo,
        "bpm": bpm,
        "mode": "major" if scale is MAJOR or scale is PENTA else "minor",
        "energy": round(0.9 if char == "staccato" else (0.5 if char in ("tremolo", "legato") else 0.75), 2),
        "src": f"songs/{fname}",
        "local": True,
    })

with open(os.path.join(OUT, "catalog.json"), "w", encoding="utf-8") as f:
    json.dump(catalog, f, ensure_ascii=False, indent=2)

print("generated", len(catalog), "songs")
print(os.listdir(OUT))
