import wave,numpy as np,subprocess,json,re
TEMPO=1.3; SR=24000
FAL={'s1':"Faltam 10 dias pra Black Friday do Paraguai… e você mora longe da fronteira?",
 's2':"Ano passado, foram mais de 300 mil visitantes. E quem mora longe, fica de fora?",
 's3':"A Campos Logística envia do Paraguai pra todo o Brasil. Transportamos qualquer mercadoria!",
 's4':"Chama no WhatsApp e envie com a Campos Logística!"}
PESO={'10':'dez','300':'trezentos'}
def load(f):
    w=wave.open(f);a=np.frombuffer(w.readframes(w.getnframes()),np.int16).astype(float);return a
def proc(i):
    a=load(f'voz/s{i}.raw'); win=int(0.02*SR)
    e=np.sqrt(np.convolve(a**2,np.ones(win)/win,'same')); loud=e>250
    nz=np.where(loud)[0]; a=a[max(0,nz[0]-int(.03*SR)):nz[-1]+int(.06*SR)]; loud=loud[max(0,nz[0]-int(.03*SR)):nz[-1]+int(.06*SR)]
    out=[];k=0;n=len(a);maxs=int(0.09*SR)
    while k<n:
        if not loud[k]:
            j=k
            while j<n and not loud[j]:j+=1
            seg=a[k:j]
            if len(seg)>maxs: seg=np.concatenate([seg[:maxs//2],seg[-maxs//2:]])
            out.append(seg);k=j
        else:
            j=k
            while j<n and loud[j]:j+=1
            out.append(a[k:j]);k=j
    b=np.concatenate(out).astype(np.int16)
    with wave.open(f'voz/c{i}.wav','w') as w: w.setnchannels(1);w.setsampwidth(2);w.setframerate(SR);w.writeframes(b.tobytes())
    subprocess.run(['ffmpeg','-y','-v','error','-i',f'voz/c{i}.wav','-filter:a',f'atempo={TEMPO}','-ar',str(SR),f'voz/f{i}.wav'],check=True)
    return load(f'voz/f{i}.wav').astype(np.int16)
lead=0.05; gap=0.15; tail=0.9
buf=[np.zeros(int(lead*SR),np.int16)]; t=lead; cenas=[]; palavras=[]
for i,sid in enumerate(['s1','s2','s3','s4'],1):
    a=proc(i); dur=len(a)/SR; ws=FAL[sid].split()
    pes=np.array([len(re.sub(r'[^\wÀ-ú]','',PESO.get(w,w)))+2 for w in ws],float)
    acc=np.concatenate([[0],np.cumsum(pes)])/pes.sum()*dur
    for k,w in enumerate(ws): palavras.append({'w':w,'a':round(t+acc[k],3),'b':round(t+acc[k+1],3),'cena':sid})
    cenas.append({'id':sid,'a':round(t-0.12,3),'b':round(t+dur,3)})
    buf.append(a); t+=dur
    g=gap if sid!='s4' else tail; buf.append(np.zeros(int(g*SR),np.int16)); t+=g
cenas[0]['a']=0; cenas[-1]['b']=round(t,3)
for i in range(1,len(cenas)): cenas[i-1]['b']=cenas[i]['a']
blocos=[];cur=[]
for p in palavras:
    cur.append(p)
    if len(cur)==3 or p['w'][-1] in '.?!,:…':
        blocos.append({'a':cur[0]['a'],'b':cur[-1]['b'],'ws':cur});cur=[]
if cur: blocos.append({'a':cur[0]['a'],'b':cur[-1]['b'],'ws':cur})
aud=np.concatenate(buf)
with wave.open('narracao.wav','w') as w: w.setnchannels(1);w.setsampwidth(2);w.setframerate(SR);w.writeframes(aud.tobytes())
json.dump({'dur':round(t,3),'cenas':cenas,'blocos':blocos},open('timings.json','w'),ensure_ascii=False,indent=1)
print('dur',round(t,2),[(c['id'],c['a'],c['b']) for c in cenas])
