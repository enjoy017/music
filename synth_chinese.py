import wave, math, struct, os, random, json

SR = 22050
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "public", "songs", "chinese")
os.makedirs(OUT, exist_ok=True)

# 中国五声音阶（宫商角徵羽）相对半音：宫 商 角 徵 羽
PENTA = [0, 2, 4, 7, 9]


def midi_to_freq(n):
    return 440.0 * (2 ** ((n - 69) / 12.0))


def pluck_wave(freq, dur, amp, sr=SR):
    """近似古筝/琵琶拨弦：快速起音 + 指数衰减 + 少量高次泛音"""
    n = int(dur * sr)
    out = []
    decay = 2.4 / max(0.12, dur)  # 衰减速率
    for i in range(n):
        t = i / sr
        e = math.exp(-decay * t)
        # 拨弦音色：基频 + 2、3 次泛音，高泛音衰减更快
        s = math.sin(2 * math.pi * freq * t)
        s += 0.35 * math.exp(-decay * 1.8 * t) * math.sin(2 * math.pi * 2 * freq * t)
        s += 0.18 * math.exp(-decay * 2.6 * t) * math.sin(2 * math.pi * 3 * freq * t)
        out.append(amp * e * s / 1.5)
    return out


def write_wav(path, sig, sr=SR):
    with wave.open(path, "w") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        frames = b"".join(struct.pack("<h", int(max(-1, min(1, x)) * 32767)) for x in sig)
        w.writeframes(frames)


def make_chinese_melody(rng, root, bpm, bars, emotion):
    beat = 60.0 / bpm
    sig = []
    total = 0.0
    # 不同情绪的速度/力度
    loud = {"happy": 1.0, "sad": 0.7, "angry": 1.0, "surprised": 0.95, "fearful": 0.6, "neutral": 0.75}
    amp = loud.get(emotion, 0.8)
    while total < bars:
        deg = rng.choice(PENTA)
        midi = root + deg + rng.choice([0, 12])  # 八度随机
        b = rng.choice([0.5, 0.5, 1.0, 0.5])
        dur = b * beat
        seg = pluck_wave(midi_to_freq(midi), dur * 1.15, amp)
        sig += seg
        # 偶尔加一个低八度衬音，更有中国民乐层次
        if rng.random() < 0.3:
            seg2 = pluck_wave(midi_to_freq(midi - 12), dur, amp * 0.45)
            sig = [a + b for a, b in zip(sig, seg2 + [0] * (len(sig) - len(seg2)))]
        total += b
    return sig


def normalize(sig):
    peak = max(1e-6, max(abs(x) for x in sig))
    return [x / peak * 0.9 for x in sig]


# (id, 曲名, 艺术家, 情绪, 根音MIDI, bpm, 小节数)
specs = [
    ("c_happy",   "喜洋洋",       "AI 合成·中国风", "happy",     64, 132, 32),
    ("c_sad",     "离人愁",       "AI 合成·中国风", "sad",       60, 66, 30),
    ("c_angry",   "战鼓催",       "AI 合成·中国风", "angry",     57, 158, 30),
    ("c_surprised","惊鸿照影",     "AI 合成·中国风", "surprised", 67, 120, 28),
    ("c_fearful", "夜雨幽窗",     "AI 合成·中国风", "fearful",   58, 62, 26),
    ("c_neutral", "高山流水·静",   "AI 合成·中国风", "neutral",   62, 70, 30),
]

catalog = []
for sid, title, artist, emo, root, bpm, bars in specs:
    rng = random.Random(hash(sid) & 0xFFFF)
    sig = make_chinese_melody(rng, root, bpm, bars, emo)
    sig = normalize(sig)
    fname = f"{sid}.wav"
    write_wav(os.path.join(OUT, fname), sig)
    catalog.append({
        "id": sid,
        "title": title,
        "artist": artist,
        "emotion": emo,
        "bpm": bpm,
        "mode": "pentatonic",
        "energy": round(0.9 if emo in ("happy", "angry") else (0.55 if emo in ("sad", "fearful", "neutral") else 0.8), 2),
        "src": f"songs/chinese/{fname}",
        "local": True,
        "demo": True,  # 标记为 AI 合成器乐演示曲
    })

with open(os.path.join(OUT, "chinese.json"), "w", encoding="utf-8") as f:
    json.dump(catalog, f, ensure_ascii=False, indent=2)

print("generated chinese demo songs:", len(catalog))
print(os.listdir(OUT))
