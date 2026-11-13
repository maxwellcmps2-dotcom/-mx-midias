# uso: python3 trilha.py <saida.wav> <segundos> "<tempos_whoosh>" "<tempos_pop>"
import sys, wave, numpy as np
out, dur = sys.argv[1], float(sys.argv[2])
wh = [float(x) for x in sys.argv[3].split(',') if x]
pops = [float(x) for x in sys.argv[4].split(',') if x]
sr = 44100; n = int(sr * dur); t = np.arange(n) / sr
mix = np.zeros(n)
rng = np.random.default_rng(7)
bpm = 104; beat = 60 / bpm

def add(sig, at, gain=1.0):
    i = int(at * sr)
    if i >= n: return
    e = min(n, i + len(sig)); mix[i:e] += gain * sig[:e - i]

# kick
kl = int(0.35 * sr); kt = np.arange(kl) / sr
kick = np.sin(2 * np.pi * (50 + 90 * np.exp(-kt * 30)) * kt) * np.exp(-kt * 9)
# hat
hl = int(0.06 * sr); hat = rng.standard_normal(hl); hat = np.diff(hat, prepend=0) * np.exp(-np.arange(hl) / sr * 70)
k = 0.0
while k < dur - 0.5:
    add(kick, k, 0.55)
    add(hat, k + beat / 2, 0.12)
    k += beat
# pad (Am F C G), 2 compassos cada acorde
chords = [[220, 261.6, 329.6], [174.6, 220, 261.6], [196, 261.6, 329.6], [196, 246.9, 293.7]]
bar = beat * 4
for ci in range(int(dur / bar) + 1):
    fr = chords[ci % 4]; st = ci * bar; ln = int(bar * sr); lt = np.arange(ln) / sr
    env = np.minimum(1, lt / 0.3) * np.minimum(1, (bar - lt) / 0.3)
    s = sum(np.sin(2 * np.pi * f * lt) + 0.3 * np.sin(4 * np.pi * f * lt) for f in fr) * env
    add(s, st, 0.05)
    # baixo
    add(np.sin(2 * np.pi * fr[0] / 2 * lt) * env, st, 0.12)
# whoosh
wl = int(0.6 * sr); wt = np.arange(wl) / sr
nz = rng.standard_normal(wl); nz = np.convolve(nz, np.ones(30) / 30, mode='same')
whoosh = nz * np.sin(np.pi * wt / 0.6) ** 2
for w in wh: add(whoosh, w - 0.3, 0.9)
# pop
pl = int(0.12 * sr); pt = np.arange(pl) / sr
pop = np.sin(2 * np.pi * (900 - 2500 * pt) * pt) * np.exp(-pt * 35)
for q in pops: add(pop, q, 0.45)
# fade
fo = int(1.2 * sr); mix[-fo:] *= np.linspace(1, 0, fo); mix[:int(0.05*sr)] *= np.linspace(0, 1, int(0.05*sr))
mix /= max(1e-9, np.abs(mix).max()) / 0.85
with wave.open(out, 'w') as f:
    f.setnchannels(1); f.setsampwidth(2); f.setframerate(sr)
    f.writeframes((mix * 32767).astype(np.int16).tobytes())
print('ok', out)
