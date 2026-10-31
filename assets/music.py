"""Gera trilha original (sem direitos autorais) + efeitos sonoros para os vídeos MX.
uso: python3 music.py saida.wav duracao "t1,t2,..."(whooshes) "t1,t2,..."(pops) [seed]
"""
import sys, numpy as np, wave
SR = 44100
out, dur = sys.argv[1], float(sys.argv[2])
wh = [float(x) for x in sys.argv[3].split(',') if x]
pops = [float(x) for x in sys.argv[4].split(',') if x]
seed = int(sys.argv[5]) if len(sys.argv) > 5 else 1
rng = np.random.default_rng(seed)
N = int(SR * dur)
mix = np.zeros((N, 2))
BPM = 120; beat = 60 / BPM

def add(sig, t, gain=1.0, pan=0.0):
    i = int(t * SR)
    if i >= N: return
    s = sig[: N - i] * gain
    mix[i:i + len(s), 0] += s * (1 - max(pan, 0))
    mix[i:i + len(s), 1] += s * (1 + min(pan, 0))

def env(n, a=0.005, d=0.2):
    t = np.arange(n) / SR
    return np.minimum(t / a, 1) * np.exp(-t / d)

def kick():
    n = int(.35 * SR); t = np.arange(n) / SR
    f = 50 + 120 * np.exp(-t * 30)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9)

def clap():
    n = int(.25 * SR); t = np.arange(n) / SR
    nz = rng.standard_normal(n)
    e = np.exp(-t * 18) + .6 * np.exp(-((t - .012) * 300) ** 2) + .5 * np.exp(-((t - .024) * 300) ** 2)
    # passa-alta simples
    nz = np.diff(np.concatenate([[0], nz]))
    return nz * e * .35

def hat(open_=False):
    n = int((.18 if open_ else .05) * SR); t = np.arange(n) / SR
    nz = np.diff(np.concatenate([[0], rng.standard_normal(n)]))
    return nz * np.exp(-t * (14 if open_ else 70)) * .18

def note(freq, length, kind='pluck'):
    n = int(length * SR); t = np.arange(n) / SR
    if kind == 'pluck':
        s = sum(np.sin(2 * np.pi * freq * k * t) / k ** 1.4 for k in range(1, 6))
        return s * env(n, .003, .18) * .5
    if kind == 'bass':
        s = np.sin(2 * np.pi * freq * t) + .3 * np.sin(2 * np.pi * freq * 2 * t)
        return s * env(n, .005, .25) * .9
    if kind == 'pad':
        s = sum(np.sin(2 * np.pi * freq * (1 + d) * t) for d in (-.004, 0, .004)) / 3
        a = np.minimum(t / .3, 1) * np.minimum((length - t) / .3, 1)
        return s * a * .22

def hz(m): return 440 * 2 ** ((m - 69) / 12)

# Am F C G
prog = [(57, [57, 60, 64]), (53, [53, 57, 60]), (48, [48, 52, 55]), (55, [55, 59, 62])]
bar = 4 * beat
nbars = int(np.ceil(dur / bar))
arp_pat = [0, 1, 2, 1, 2, 0, 2, 1]
for b in range(nbars):
    root, ch = prog[b % 4]
    t0 = b * bar
    for c in ch: add(note(hz(c + 12), bar, 'pad'), t0, .8)
    for i in range(8):
        tt = t0 + i * beat / 2
        add(note(hz(root - 12), beat / 2 * .95, 'bass'), tt, .55)
        add(note(hz(ch[arp_pat[i]] + 24), .3, 'pluck'), tt, .32, pan=(.3 if i % 2 else -.3))
        add(hat(open_=(i % 4 == 3)), tt + (beat / 4 if False else 0), 1.0, pan=.2)
    for i in range(4):
        add(kick(), t0 + i * beat, .9)
        if i in (1, 3): add(clap(), t0 + i * beat, .9)

for t in wh:  # whoosh: ruído filtrado subindo
    n = int(.6 * SR); tt = np.arange(n) / SR
    nz = rng.standard_normal(n)
    k = np.exp(-np.linspace(4, .2, n))
    y = np.zeros(n); acc = 0
    for i in range(n): acc += k[i] * (nz[i] - acc); y[i] = acc
    e = np.sin(np.pi * tt / .6) ** 2
    add(y * e * .9, t - .45, 1.0)
for t in pops:  # pop/blip
    n = int(.12 * SR); tt = np.arange(n) / SR
    f = 900 + 900 * np.exp(-tt * 40)
    add(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 35) * .35, t, 1.0)

# fade in/out e normalização
fi, fo = int(.05 * SR), int(.8 * SR)
mix[:fi] *= np.linspace(0, 1, fi)[:, None]
mix[-fo:] *= np.linspace(1, 0, fo)[:, None]
mix = np.tanh(mix * 1.2)
mix /= np.abs(mix).max() / .89
with wave.open(out, 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((mix * 32767).astype('<i2').tobytes())
