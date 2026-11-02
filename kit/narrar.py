# uso: python3 narrar.py roteiro.json saida_dir
# roteiro.json: {"cenas":[{"id":"s1","falas":["frase 1","frase 2"]}, ...], "gap":0.25, "pausa_cena":0.35}
# Gera narracao.wav (piper pt_BR faber) + timings.json com início/fim de cada cena e de cada palavra.
import json, sys, subprocess, wave, os, re
import numpy as np
MODEL = os.environ.get('PIPER_MODEL', '/home/claude/tts/vits-piper-pt_BR-faber-medium/pt_BR-faber-medium.onnx')
rot = json.load(open(sys.argv[1])); out = sys.argv[2]; os.makedirs(out, exist_ok=True)
gap = rot.get('gap', 0.25); pausa = rot.get('pausa_cena', 0.35); lead = rot.get('inicio', 0.3)
SR = None; pcm = []; t = lead; cenas = []; palavras = []
def synth(txt, fn):
    subprocess.run(['python3', '-m', 'piper', '-m', MODEL, '-f', fn, '--length-scale', str(rot.get('velocidade', 0.92))], input=txt.encode(), check=True, capture_output=True)
    with wave.open(fn) as w:
        sr = w.getframerate(); a = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16)
    # corta silêncio das pontas
    nz = np.where(np.abs(a) > 300)[0]
    if len(nz): a = a[max(0, nz[0] - int(0.02 * sr)): nz[-1] + int(0.05 * sr)]
    return sr, a
buf = []
for c in rot['cenas']:
    ini = t
    for i, f in enumerate(c['falas']):
        sr, a = synth(f, f'{out}/_tmp.wav'); SR = sr
        if not buf: buf.append(np.zeros(int(lead * sr), dtype=np.int16))
        dur = len(a) / sr
        ws = f.split(); pesos = np.array([len(re.sub(r'[^\wÀ-ú]', '', w)) + 2 for w in ws], float)
        acc = np.concatenate([[0], np.cumsum(pesos)]) / pesos.sum() * dur
        for k, w in enumerate(ws):
            palavras.append({'w': w, 'a': round(t + acc[k], 3), 'b': round(t + acc[k + 1], 3), 'cena': c['id'], 'frase': len([1 for x in palavras if False])})
        buf.append(a); t += dur
        g = gap if i < len(c['falas']) - 1 else pausa
        buf.append(np.zeros(int(g * sr), dtype=np.int16)); t += g
    cenas.append({'id': c['id'], 'a': round(ini - (lead if not cenas else 0.15), 3), 'b': round(t, 3)})
cenas[0]['a'] = 0
cauda = rot.get('cauda', 2.0); buf.append(np.zeros(int(cauda * SR), dtype=np.int16)); t += cauda
cenas[-1]['b'] = round(t, 3)
for i in range(1, len(cenas)): cenas[i]['a'] = cenas[i - 1]['b']
# frases para legenda: agrupa em blocos de até 3 palavras
blocos = []; cur = []
for p in palavras:
    cur.append(p)
    if len(cur) == 3 or p['w'][-1] in '.?!,:' :
        blocos.append({'a': cur[0]['a'], 'b': cur[-1]['b'], 'ws': cur}); cur = []
if cur: blocos.append({'a': cur[0]['a'], 'b': cur[-1]['b'], 'ws': cur})
aud = np.concatenate(buf)
with wave.open(f'{out}/narracao.wav', 'w') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(aud.tobytes())
json.dump({'dur': round(t, 3), 'cenas': cenas, 'blocos': blocos}, open(f'{out}/timings.json', 'w'), ensure_ascii=False, indent=1)
os.remove(f'{out}/_tmp.wav')
print('dur', round(t, 2), [ (c['id'], c['a'], c['b']) for c in cenas ])
