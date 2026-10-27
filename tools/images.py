"""Zpracuje zdrojové fotky do WebP ve více šířkách + hloubkové mapy + loga klientů.
Spuštění: python3 tools/images.py  (z kořene webu)"""
from PIL import Image
import os, json, glob
import numpy as np
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC=os.path.join(ROOT,'tools','source-photos'); OUT=os.path.join(ROOT,'assets','img')
WIDTHS=[480,960,1600]
CLIENTS={'14f59206':'kofola','3d9c3fd7':'dhl','473862fc':'vog','4b5ff0d2':'penny','75762a8b':'zoeller','a1dcc8f2':'redbull','a477c53f':'unipap','0a446175':'simoldes'}
meta={}
def save(im,name,widths=WIDTHS,q=74):
    w,h=im.size; done=[]
    for tw in widths:
        if tw>w:
            if done and done[-1]>=w*0.8: continue
            tw=w
        r=im.resize((tw,round(h*tw/w)),Image.LANCZOS) if tw!=w else im
        r.save(os.path.join(OUT,f'{name}-{tw}.webp'),'WEBP',quality=q,method=6); done.append(tw)
    meta[name]={'w':w,'h':h,'sizes':sorted(set(done))}
for f in sorted(glob.glob(SRC+'/*')):
    base=os.path.basename(f); key=base[:8]
    if base.startswith('hallpro-service-sro') or base.startswith('img-9875'): continue
    im=Image.open(f)
    if key in CLIENTS:
        # jednobarevná tmavě šedá silueta z alfa kanálu; žluté/bílé plochy (DHL, Red Bull, Kofola) jsou „díry“
        a=np.asarray(im.convert('RGBA')).astype(float); r,g,b,al=[a[...,i] for i in range(4)]
        yellow=(r>170)&(g>140)&(b<130)&(r-b>90); white=(r>200)&(g>200)&(b>200)
        ink=(white if CLIENTS[key]=='vog' else ~(yellow|white))*al
        h,w=ink.shape; out=np.zeros((h,w,4),'uint8'); out[...,0:3]=(58,58,62); out[...,3]=ink.clip(0,255).astype('uint8')
        out=Image.fromarray(out); out=out.crop(out.getbbox())
        out.thumbnail((900,150),Image.LANCZOS); out.save(os.path.join(OUT,'clients',CLIENTS[key]+'.webp'),'WEBP',lossless=True,method=6)
        meta['client-'+CLIENTS[key]]={'w':out.size[0],'h':out.size[1]}; continue
    if base.startswith('whatsapp-image-2026-01-02-at-195950'): key='tym-vegerova'
    elif base.startswith('whatsapp-image-2026-01-02-at-201735'): key='tym-zeman'
    elif key=='48fda1c2': key='tym-cermakova'
    elif base.endswith('.png'): key='fb-'+base[:-4]
    im=im.convert('RGB')
    if key.startswith('fb-'): im=im.crop((6,4,im.size[0]-6,im.size[1]-4))
    if key=='fb-schody-pred-po':
        w,h=im.size; save(im.crop((0,0,w//2-2,h)),'fb-schody-pred',[480,960]); save(im.crop((w//2+2,0,w,h)),'fb-schody-po',[480,960]); continue
    save(im,key,[400] if key.startswith('tym-') else WIDTHS)
for d in glob.glob(os.path.join(ROOT,'tools','depth','*.png')):
    Image.open(d).convert('L').save(os.path.join(OUT,'depth-'+os.path.basename(d)[6:14]+'.webp'),'WEBP',quality=80)
json.dump(meta,open(os.path.join(ROOT,'tools','images.json'),'w'),indent=1)
print(len(meta),'images')
