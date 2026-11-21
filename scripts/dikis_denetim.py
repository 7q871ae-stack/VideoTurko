# Dikis denetimi (CPU): python -I dikis_denetim.py parcaA.mp4 parcaB.mp4 [...]  (ardisik parcalar)
# Olcu: son3/ilk3 akis (medyan dx,dy + ortalama buyukluk), oran, yon kosinusu, gurultu kapisi (medyan artigi), son5 spike.
# Cikis kodu (uret.ps1 / denetim.py ile ayni dil; yesil yalniz 0): 0 = tek parca olculdu ya da tum dikisler TAMAM;
#   1 = en az bir dikis RED (iki ve ustu parcada; `SONUC: KIRMIZI`); 3 = girdi hatali (arguman yok, `-` ile baslayan arguman, dosya yok);
#   6 = KAPI CALISMADI (opencv/numpy yok, parca okunamadi ya da cok kisa): RED degil ama yesil de degil.
# Yazdirilan `parca ... kare=N gurultu=X ... orta akis=Y` satiri uretim_kapi.ps1 tarafindan ayristirilir: bicimi DEGISMEZ.
# Eski surum (v0.1.2): RED dikis de cikis 0 veriyordu, eksik/kisa/bozuk dosyada izleme dokumu (traceback) basiyordu.
import sys, os

def bitir(kod, sonuc, mesaj=None):
    if mesaj:
        print(mesaj)
    print('SONUC: ' + sonuc)
    sys.exit(kod)

yollar = sys.argv[1:]
if not yollar:
    bitir(3, 'GIRDI HATALI', 'KULLANIM: python -I dikis_denetim.py parca1.mp4 [parca2.mp4 ...]')
for p in yollar:
    if p.startswith('-'):
        bitir(3, 'GIRDI HATALI', 'GIRDI HATALI: bayrak desteklenmiyor (yalniz video dosyasi yollari): ' + p[:40])
    if not os.path.isfile(p):
        bitir(3, 'GIRDI HATALI', 'GIRDI HATALI: dosya yok: ' + os.path.basename(p)[:80])
try:
    import cv2, numpy as np
except ImportError as e:
    bitir(6, 'CALISMADI', 'KAPI CALISMADI: ' + type(e).__name__ + ': ' + str(e)[:160])

def fr(p):
    c=cv2.VideoCapture(p); o=[]
    while True:
        r,f=c.read()
        if not r: break
        o.append(cv2.cvtColor(f,cv2.COLOR_BGR2GRAY))
    return o
def fl(a,b): return cv2.calcOpticalFlowFarneback(a,b,None,.5,3,15,3,5,1.2,0)
def vec(g,idx):
    F=[fl(g[k],g[k+1]) for k in idx]
    return np.mean([[np.median(f[...,0]),np.median(f[...,1])] for f in F],axis=0), np.mean([np.linalg.norm(f,axis=2).mean() for f in F])
def gur(g): return np.mean([np.abs(x.astype(float)-cv2.medianBlur(x,3)).mean() for x in g[::8]])
P=[fr(p) for p in yollar]
for i,g in enumerate(P):
    gerek = 5 if len(P) > 1 else 2   # dikis: son3 ve ilk3 akis icin en az 5 kare; tek parca: en az 1 akis
    if len(g) < gerek:
        bitir(6, 'CALISMADI', 'KAPI CALISMADI: parca %d okunamadi ya da cok kisa (%d kare, en az %d gerek): %s' % (i+1, len(g), gerek, os.path.basename(yollar[i])[:60]))
for i,g in enumerate(P):
    mg=[np.linalg.norm(fl(g[k],g[k+1]),axis=2).mean() for k in range(len(g)-1)]
    print('parca %d: kare=%d gurultu=%.2f (kapi<=1.5, gercek H3 56 kare 0.7-1.14) orta akis=%.2f son5 spike=%s'%(i+1,len(g),gur(g),np.mean(mg),' '.join('%.2f'%x for x in mg[-5:])))
kirmizi=0
for i in range(len(P)-1):
    a,ma=vec(P[i],range(len(P[i])-4,len(P[i])-1)); b,mb=vec(P[i+1],range(1,4))
    cos=float(a@b/(np.linalg.norm(a)*np.linalg.norm(b)+1e-9)); r=mb/max(ma,1e-9)
    tamam = 0.7<=r<=1.4
    if not tamam: kirmizi+=1
    print('dikis %d-%d: buyukluk oran=%.2f (0.7-1.4) medyan vektor kosinus=%.2f (>0.8; kamera ~0 ise anlamsiz) -> %s'%(i+1,i+2,r,cos,'TAMAM' if tamam else 'RED'))
if len(P)>1:
    bitir(1 if kirmizi else 0, 'KIRMIZI' if kirmizi else 'GECTI')
