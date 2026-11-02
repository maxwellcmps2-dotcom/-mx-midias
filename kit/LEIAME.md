# Kit de vídeo — Campos Logística

Reels 1080x1920 narrados, com 3D (three.js), legendas animadas palavra por palavra e trilha original.

## Preparar (sessão nova)
```bash
cd /home/claude && git clone --depth 1 https://github.com/maxwellcmps2-dotcom/-mx-midias
mkdir -p tts && cd tts && curl -sL -o f.tar.bz2 https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/vits-piper-pt_BR-faber-medium.tar.bz2 && tar xjf f.tar.bz2
pip install --break-system-packages -q piper-tts
mkdir -p /home/claude/v && cd /home/claude/v && npm init -y >/dev/null && npm i three@0.170.0
cp /home/claude/-mx-midias/kit/* .
```

## Produzir
1. `roteiro.json` (ver roteiro-exemplo.json): 4 cenas s1 gancho/curiosidade, s2 mapa 3D, s3 produtos 3D, s4 CTA.
2. `python3 narrar.py roteiro.json .` → narracao.wav + timings.json (cenas e palavras).
3. Editar textos de `narrado-3d.html` (copiar para video.html). As cenas se ajustam sozinhas ao timings.json.
4. Quadros de teste: `node snap.js video.html 2 6 10 14 19` → s_*.png.
5. Trilha + render + mix:
```bash
D=$(python3 -c "import json;print(json.load(open('timings.json'))['dur'])")
W=$(python3 -c "import json;c=json.load(open('timings.json'))['cenas'];print(','.join(str(x['a']) for x in c[1:]))")
python3 trilha.py musica.wav $D "$W" "0.5"
node render3d.js . video.html frames $D 30
ffmpeg -y -i narracao.wav -i musica.wav -filter_complex "[0]aresample=44100,volume=1.6,highpass=f=80,acompressor=threshold=0.1:ratio=3[n];[1]volume=0.22[m];[n][m]amix=inputs=2:duration=longest:normalize=0,alimiter=limit=0.95[a]" -map "[a]" -ac 2 audio.wav
ffmpeg -y -framerate 30 -i frames/f%04d.jpg -i audio.wav -c:v libx264 -preset veryfast -crf 20 -pix_fmt yuv420p -c:a aac -b:a 160k -shortest reel.mp4
```
6. Subir em `AAAA-MM-DD-tema/reel.mp4` neste repo e usar o link raw.githubusercontent.com no Metricool.
