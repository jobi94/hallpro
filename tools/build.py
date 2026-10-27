"""Generátor webu HallPro Service.
Obsah služeb je v tools/pages.json (převzato ze stávajícího hallpro.cz), ostatní texty níže.
Spuštění z kořene webu:  python3 tools/build.py
Každá stránka vznikne jako <slug>/index.html, takže adresy zůstávají stejné jako na starém webu (hallpro.cz/servis-strech)."""
import json, os, math, re, html
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGES = json.load(open(os.path.join(ROOT, 'tools', 'pages.json'), encoding='utf-8'))
IMGS = json.load(open(os.path.join(ROOT, 'tools', 'images.json'), encoding='utf-8'))
FONTS_CSS = open(os.path.join(ROOT, 'assets', 'css', 'fonts.css'), encoding='utf-8').read().strip()  # vkládá se přímo do <head>, ušetří jeden požadavek
DOMAIN = 'https://www.hallpro.cz'
FORM_ENDPOINT = ''            # sem později doplnit adresu funkce, která pošle e-mail + Telegram
FORM_MAIL = 'info@hallpro.cz'  # záložní cíl (otevře e-mailového klienta), dokud není endpoint
VERSION = '4'
esc = html.escape

# ---------------------------------------------------------------- firma
CO = dict(name='HallPro Service s.r.o.', phone='+420 731 291 205', tel='+420731291205', mail='info@hallpro.cz',
          addr='Korunní 2569/108, Vinohrady, 101 00 Praha 10', ico='23992646', dic='CZ23992646',
          reg='C 435803, vedená u Městského soudu v Praze',
          fb='https://www.facebook.com/profile.php?id=61575862582524',
          ig='https://www.instagram.com/hallpro_service',
          li='https://www.linkedin.com/in/luk%C3%A1%C5%A1-zeman-242822369/')
TEAM = [
    dict(name='Lukáš Zeman', role='Manažer · pobočka Hradec Králové', phone='+420 731 291 205', mail='servis@hallpro.cz', img='tym-zeman', li=CO['li']),
    dict(name='Renata Čermáková', role='Obchod a spolupráce', phone='+420 601 100 172', mail='cermakova@hallpro.cz', img='tym-cermakova'),
    dict(name='Zuzana Vegerová', role='Pobočka Olomouc', phone='+420 727 990 767', mail='info@hallpro.cz', img='tym-vegerova'),
]

# ---------------------------------------------------------------- struktura služeb (stejná jako na hallpro.cz)
CATS = [
    dict(slug='strechy-293', name='Střechy a hydroizolace', menu='Střechy', h1='Opravy a servis průmyslových střech',
         short='Opravy, renovace, hydroizolace, světlíky, klempířské práce a odborné kontroly střech.',
         kids=[('servis-strech', 'Servis střech'), ('tpo-a-pvc-hydroizolace', 'TPO a PVC hydroizolace'), ('renovace-strech', 'Renovace střech'),
               ('zachytne-systemy', 'Záchytné systémy'), ('klempirske-prace', 'Klempířské práce'), ('kontroly-strech', 'Kontroly střech'), ('svetliky', 'Světlíky')]),
    dict(slug='konstrukce', name='Ocelové konstrukce', menu='Konstrukce', h1='Prohlídky, servis a montáže konstrukcí',
         short='Prohlídky, opravy, montáže, zámečnické práce a ochranné nátěry ocelových konstrukcí.',
         kids=[('prohlidky-ocelovych-konstrukci', 'Prohlídky ocelových konstrukcí'), ('opravy-ocelovych-konstrukci', 'Opravy ocelových konstrukcí'),
               ('zamecnicke-prace', 'Zámečnické práce'), ('montaze-konstrukci', 'Montáže konstrukcí'), ('natery-konstrukci', 'Nátěry konstrukcí')]),
    dict(slug='bezpecnost', name='Bezpečnost', menu='Bezpečnost', h1='Bezpečnost průmyslových a komerčních objektů',
         short='Záchytné systémy, bezpečnost provozu, ochranné prvky a pasivní požární ochrana.',
         kids=[('bezpecnost-provozu', 'Bezpečnost provozu'), ('zachytne-systemy-361', 'Záchytné systémy'), ('pasivni-pozarni-ochrana', 'Pasivní požární ochrana')]),
    dict(slug='kontroly-a-revize', name='Kontroly a revize', menu='Kontroly a revize', h1='Kontroly a technické prohlídky průmyslových objektů',
         short='Preventivní kontroly technického stavu objektů, identifikace závad a návrhy následných oprav.',
         kids=[('kontroly-a-prohlidky-strech', 'Kontroly a prohlídky střech'), ('prohlidky-ocelovych-konstrukci-417', 'Prohlídky ocelových konstrukcí'),
               ('revize-zachytnych-systemu', 'Revize záchytných systémů'), ('kontroly-a-revize-jerabu', 'Kontroly a revize jeřábů')]),
    dict(slug='udrzba-a-servis', name='Údržba a servis', menu='Údržba a servis', h1='Technická údržba průmyslových budov',
         short='Pravidelná technická údržba budov, údržba areálů a zeleně, oplocení a servisní programy.',
         kids=[('technicka-udrzba-budov-373', 'Technická údržba budov'), ('pravidelny-servis', 'Pravidelný servis'),
               ('udrzba-arealu-a-zelene', 'Údržba areálů a zeleně'), ('oploceni-prumyslovych-arealu', 'Oplocení průmyslových areálů')]),
    dict(slug='myti-a-cisteni', name='Mytí a čištění', menu='Mytí a čištění', h1='Mytí a čištění průmyslových objektů',
         short='Mytí střech a fasád, průmyslové čištění hal a konstrukcí a čištění fotovoltaiky.',
         kids=[('myti-strech-a-fasad', 'Mytí střech a fasád'), ('prumyslove-cisteni-interieru', 'Průmyslové čištění interiérů'), ('cisteni-fve', 'Čištění FVE')]),
    dict(slug='vyskove-prace-405', name='Výškové práce', menu='Výškové práce', h1='Výškové a montážní práce',
         short='Montážní, servisní a opravárenské práce pomocí pracovních plošin a lanové techniky.',
         kids=[('opravy-strech-a-fasad', 'Opravy střech a fasád'), ('montaze-technologii-ve-vyskach', 'Montáže technologií ve výškách'),
               ('reklamni-instalacni-prace', 'Reklamní instalační práce')]),
]
CAT_IMG = {'strechy-293': '27c3a4a5', 'konstrukce': 'e7da46d0', 'bezpecnost': 'e97424c2', 'kontroly-a-revize': '5e5328fd',
           'udrzba-a-servis': 'a2796030', 'myti-a-cisteni': '5edaa41d', 'vyskove-prace-405': '2605ee70'}
KID2CAT = {k: c for c in CATS for k, _ in c['kids']}

# ---------------------------------------------------------------- ikony
def ic(name, cls=''):
    P = {
        'arr': '<path d="M5 12h14M13 6l6 6-6 6"/>',
        'arr-ur': '<path d="M7 17L17 7M8 7h9v9"/>',
        'phone': '<path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1.9.4 1.8.7 2.7a2 2 0 0 1-.5 2.1L8 9.8a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.7.7a2 2 0 0 1 1.7 2z"/>',
        'mail': '<rect x="2" y="4" width="20" height="16" rx="2"/><path d="M22 7l-10 6L2 7"/>',
        'check': '<path d="M20 6L9 17l-5-5"/>',
        'pin': '<path d="M12 22s-7-6.2-7-12a7 7 0 0 1 14 0c0 5.8-7 12-7 12z"/><circle cx="12" cy="10" r="2.5"/>',
        'info': '<circle cx="12" cy="12" r="10"/><path d="M12 16v-4M12 8h.01"/>',
        'search': '<circle cx="11" cy="11" r="7"/><path d="M21 21l-4.3-4.3"/>',
        'doc': '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6M8 13h8M8 17h6"/>',
        'wrench': '<path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.8-3.8a6 6 0 0 1-7.9 7.9l-6.9 6.9a2.1 2.1 0 0 1-3-3l6.9-6.9a6 6 0 0 1 7.9-7.9z"/>',
        'cal': '<rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18M8 15l2.5 2.5L16 13"/>',
        'clock': '<circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>',
        'shield': '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="M9 12l2 2 4-4"/>',
        'drop': '<path d="M12 2.7l5.7 5.6a8 8 0 1 1-11.3 0z"/>',
        'roof': '<path d="M3 11l9-7 9 7M5 10v10h14V10"/><path d="M9 20v-6h6v6"/>',
        'beam': '<path d="M4 6h16M4 18h16M8 6v12M16 6v12M8 12l8-6M8 18l8-6"/>',
        'wind': '<path d="M9.6 4.6A2 2 0 1 1 11 8H2M12.6 19.4A2 2 0 1 0 14 16H2M17.7 7.7A2.5 2.5 0 1 1 19.5 12H2"/>',
        'fire': '<path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.4-.5-2-1-3-1.1-2.1-.2-4 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.2.4-2.3 1-3.2.5 1.3 1.4 2.4 2.5 2.7z"/>',
        'door': '<path d="M3 21h18M5 21V4h14v17M5 9h14M5 14h14"/>',
        'alert': '<path d="M10.3 3.9L1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0z"/><path d="M12 9v4M12 17h.01"/>',
        'truck': '<path d="M1 3h15v13H1zM16 8h4l3 3v5h-7z"/><circle cx="5.5" cy="18.5" r="2.5"/><circle cx="18.5" cy="18.5" r="2.5"/>',
    }
    return f'<svg class="{cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{P[name]}</svg>'
SOC = {
    'li': '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M20.45 20.45h-3.56v-5.57c0-1.33-.02-3.04-1.85-3.04-1.85 0-2.14 1.45-2.14 2.94v5.67H9.35V9h3.41v1.56h.05c.48-.9 1.64-1.85 3.37-1.85 3.6 0 4.27 2.37 4.27 5.46v6.28zM5.34 7.43a2.06 2.06 0 1 1 0-4.13 2.06 2.06 0 0 1 0 4.13zM7.12 20.45H3.56V9h3.56v11.45zM22.22 0H1.77C.79 0 0 .77 0 1.73v20.54C0 23.23.79 24 1.77 24h20.45c.98 0 1.78-.77 1.78-1.73V1.73C24 .77 23.2 0 22.22 0z"/></svg>',
    'fb': '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M24 12.07C24 5.4 18.63 0 12 0S0 5.4 0 12.07C0 18.1 4.39 23.1 10.13 24v-8.44H7.08v-3.49h3.04V9.41c0-3.02 1.8-4.7 4.54-4.7 1.31 0 2.68.24 2.68.24v2.97h-1.5c-1.5 0-1.96.93-1.96 1.89v2.26h3.33l-.53 3.49h-2.8V24C19.62 23.1 24 18.1 24 12.07z"/></svg>',
    'ig': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><rect x="2" y="2" width="20" height="20" rx="5.5"/><circle cx="12" cy="12" r="4.2"/><circle cx="17.6" cy="6.4" r=".6" fill="currentColor"/></svg>',
}
def socials(cls='soc'):
    return (f'<div class="{cls}"><a class="soc-ic" href="{CO["li"]}" target="_blank" rel="noopener" aria-label="LinkedIn – Lukáš Zeman">{SOC["li"]}</a>'
            f'<a class="soc-ic" href="{CO["fb"]}" target="_blank" rel="noopener" aria-label="Facebook HallPro Service">{SOC["fb"]}</a>'
            f'<a class="soc-ic" href="{CO["ig"]}" target="_blank" rel="noopener" aria-label="Instagram HallPro Service">{SOC["ig"]}</a></div>')

# ---------------------------------------------------------------- logo (štít + ozubené kolo, kolo se při načtení a najetí myší protočí)
def gear_path(cx, cy, R, r, teeth=8, tip=0.30, base=0.46):
    pts = []; step = 2 * math.pi / teeth
    for i in range(teeth):
        a = i * step - math.pi / 2
        for ang, rad in ((a - step * base / 2 - step * .02, r), (a - step * tip / 2, R), (a + step * tip / 2, R), (a + step * base / 2 + step * .02, r)):
            pts.append((cx + rad * math.cos(ang), cy + rad * math.sin(ang)))
        # oblouk mezi zuby
        for k in (1, 2, 3):
            ang = a + step * base / 2 + (step * (1 - base)) * k / 4
            pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
    return 'M' + 'L'.join(f'{x:.2f} {y:.2f}' for x, y in pts) + 'Z'
GEAR = gear_path(50, 54, 28, 21.5)
SHIELD = 'M8 15C32 7 62 5 92 11V58C92 87 75 104 51 116C27 104 8 87 8 58Z'
def mark(uid, gear_cls='gear', mono=False):
    if mono:
        return (f'<g class="shield"><path d="{SHIELD}" transform="translate(8 3)" fill="#000" opacity=".35"/><path d="{SHIELD}" fill="#1B1B1D"/>'
                f'<path d="M-2 62C8 104 62 120 108 74C80 108 26 104 -2 62Z" fill="#1B1B1D"/><path d="M0 60C12 98 60 112 104 72" fill="none" stroke="#F25A14" stroke-width="5" stroke-linecap="round"/></g>'
                f'<g class="{gear_cls}"><path d="{GEAR}" fill="#fff"/><circle cx="50" cy="54" r="11.5" fill="#F25A14"/><circle cx="50" cy="54" r="5.5" fill="#fff"/></g>')
    return (f'<defs><linearGradient id="g{uid}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#FF9A12"/><stop offset=".55" stop-color="#F8661A"/><stop offset="1" stop-color="#F24A14"/></linearGradient></defs>'
            f'<g class="shield"><path d="{SHIELD}" transform="translate(8 3)" fill="#1F1F22"/><path d="{SHIELD}" fill="url(#g{uid})"/>'
            f'<path d="M-2 62C8 104 62 120 108 74C80 108 26 104 -2 62Z" fill="url(#g{uid})"/>'
            f'<path class="swoosh" d="M0 60C12 98 60 112 104 72" fill="none" stroke="#fff" stroke-width="5" stroke-linecap="round"/></g>'
            f'<g class="{gear_cls}"><path d="{GEAR}" fill="#fff"/><circle cx="50" cy="54" r="11.5" fill="#F8661A"/><circle cx="50" cy="54" r="5.5" fill="#fff"/></g>')
def big_mark():
    # štít a kolo jako dvě samostatná SVG: kolo se pak otáčí jako celá vrstva na GPU (plynulé i na telefonu)
    sh = mark('t', mono=True).split('<g class="gear">')[0]
    return (f'<div class="tile-mark" aria-hidden="true"><svg viewBox="-4 0 116 124">{sh}</svg>'
            f'<svg class="big-gear" viewBox="21 25 58 58"><path d="{GEAR}" fill="#fff"/><circle cx="50" cy="54" r="11.5" fill="#F25A14"/><circle cx="50" cy="54" r="5.5" fill="#fff"/></svg></div>')
def logo(uid):
    return (f'<svg class="logo" viewBox="-4 0 330 124" role="img" aria-label="HallPro Service">{mark(uid)}'
            f'<text class="wm" x="118" y="62" font-family="Ubuntu,Inter Tight,sans-serif" font-weight="700" font-size="54" fill="currentColor" letter-spacing="-1">HallPro</text>'
            f'<text class="wm2" x="119" y="108" font-family="Ubuntu,Inter Tight,sans-serif" font-weight="500" font-size="48" fill="#F8661A" letter-spacing="-.5">Service</text></svg>')
FAVICON = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-4 0 116 124">{mark("f")}</svg>'

# ---------------------------------------------------------------- obrázky
def img(key, alt, sizes='100vw', cls='', eager=False, attrs=''):
    m = IMGS[key]; ss = m['sizes']; big = ss[-1]
    src = lambda w: f'{P}assets/img/{key}-{w}.webp'
    srcset = ', '.join(f'{src(w)} {w}w' for w in ss)
    mid = next((w for w in ss if w >= 960), big)
    h = round(m['h'] * big / m['w'])
    load = 'fetchpriority="high"' if eager else 'loading="lazy"'
    c = f' class="{cls}"' if cls else ''
    return f'<img{c} src="{src(mid)}" srcset="{srcset}" sizes="{sizes}" width="{big}" height="{h}" alt="{esc(alt)}" {load} decoding="async"{attrs}>'
def img_preload(key, sizes='100vw'):
    ss = IMGS[key]['sizes']
    return (f'<link rel="preload" as="image" href="{P}assets/img/{key}-{next((w for w in ss if w >= 960), ss[-1])}.webp" '
            f'imagesrcset="{", ".join(f"{P}assets/img/{key}-{w}.webp {w}w" for w in ss)}" imagesizes="{sizes}" fetchpriority="high">\n')
def img_url(key, w=960):
    ss = IMGS[key]['sizes']; w = max([x for x in ss if x <= w] or [ss[0]]); return f'{P}assets/img/{key}-{w}.webp'

# ---------------------------------------------------------------- data podstránek
def page_data(slug):
    d = PAGES[slug]; secs = [s for s in d['secs']]
    title = secs[0]['h']; items = secs[0]['items']
    lead, body = None, list(items)
    if items and len(items[0]) < 170 and len(items) > 1: lead, body = items[0], items[1:]
    elif len(items) == 1 and len(items[0]) < 340: lead, body = items[0], []
    cta = next((p for p in d['pre'] if len(p) < 45), 'Poptat službu')
    legal = [p for p in d['pre'] if len(p) > 80]
    why = ' '.join(x for x in d['why'] if len(x) > 60 and not x.startswith('HallPro Service –'))
    claim = next((x for x in d['why'] if x.startswith('HallPro Service –')), '')
    return dict(title=title, lead=lead, body=body, cta=cta[:1].upper() + cta[1:].lower(), legal=legal, secs=secs[1:],
                img=(d['imgs'] or ['27c3a4a5'])[0][:8], why=why, claim=claim)

NORM = re.compile(r'^(ČSN|Nařízení|Zákon|Technické předpisy)')
def blocks(secs):
    out = []
    for s in secs:
        it = [x for x in s['items'] if x and not x.isupper()]
        if not it: continue
        h = f'<h2>{esc(s["h"].rstrip(":"))}</h2>'
        norms = [x for x in it if NORM.match(x)]
        if len(norms) >= 2:
            rows = ''.join(f'<li><b>{esc(x.split(" – ")[0])}</b><span>{esc(" – ".join(x.split(" – ")[1:]) or "")}</span></li>' if ' – ' in x else '' for x in norms)
            ps = ''.join(f'<p>{esc(x)}</p>' for x in it if x not in norms or ' – ' not in x)
            pre = [x for x in it[:it.index(norms[0])]]; post = [x for x in it if x not in norms and x not in pre]
            out.append(f'<div class="blk rv">{h}{"".join(f"<p>{esc(x)}</p>" for x in pre)}<ul class="norms">{rows}</ul>{"".join(f"<p class=small>{esc(x)}</p>" for x in post)}</div>'); continue
        if len(it) >= 4 and len(it) % 2 == 0 and all(len(it[i]) < 50 for i in range(0, len(it), 2)) and all(len(it[i]) > 70 for i in range(1, len(it), 2)):
            cards = ''.join(f'<div><h3>{esc(it[i])}</h3><p>{esc(it[i+1])}</p></div>' for i in range(0, len(it), 2))
            out.append(f'<div class="blk rv">{h}<div class="trio">{cards}</div></div>'); continue
        intro = [x for x in it if x.endswith(':') or len(x) > 110]
        lst = [x for x in it if x not in intro]
        lens = sorted(len(x) for x in lst)
        if len(lst) >= 3 and lens[len(lens) // 2] < 95:
            li = ''.join(f'<li>{ic("check")}<span>{esc(x.rstrip("."))}</span></li>' for x in lst)
            out.append(f'<div class="blk rv">{h}{"".join(f"<p>{esc(x)}</p>" for x in intro)}<ul class="checks">{li}</ul></div>')
        else:
            out.append(f'<div class="blk rv">{h}{"".join(f"<p>{esc(x)}</p>" for x in it)}</div>')
    return ''.join(out)

# ---------------------------------------------------------------- společné části
def head(title, desc, path, og_img='50c1daf8', extra='', preload=''):
    url = DOMAIN + '/' + path
    if path == '404': extra = '<meta name="robots" content="noindex">\n' + extra
    return f'''<!doctype html>
<html lang="cs" class="no-js">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
{"" if path == "404" else f'<link rel="canonical" href="{url}">'}
<meta name="theme-color" content="#F25A14">
<meta property="og:type" content="website"><meta property="og:locale" content="cs_CZ">
<meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{url}"><meta property="og:image" content="{DOMAIN}/assets/img/{og_img}-{IMGS[og_img]["sizes"][-1]}.webp">
<link rel="icon" href="{P}favicon.svg" type="image/svg+xml">
{"".join(f'<link rel="preload" href="{P}assets/fonts/{f}.woff2" as="font" type="font/woff2" crossorigin>' + chr(10) for f in ('intertight-400-600-latin', 'inter-400-600-latin', 'intertight-400-600-cs', 'inter-400-600-cs'))}{preload}<style>{FONTS_CSS.replace('../fonts/', P + 'assets/fonts/')}</style>
<link rel="stylesheet" href="{P}assets/css/style.css?v={VERSION}">
{extra}</head>'''

def menu_col(name, href, links, all_label):
    uid = re.sub(r'[^a-z0-9]+', '-', href.lower()).strip('-') or 'home'
    chev = '<svg class="chev" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" aria-hidden="true"><path d="M6 9l6 6 6-6"/></svg>'
    lis = ''.join(f'<li><a href="{h}">{esc(n)}</a></li>' for n, h in links)
    return (f'<div class="reveal-m"><h3><a href="{href}">{esc(name)} {ic("arr-ur")}</a>'
            f'<button class="cat-tog" type="button" aria-expanded="false" aria-controls="m-{uid}">{esc(name)}{chev}</button></h3>'
            f'<div class="sub" id="m-{uid}"><ul><li class="cat-all"><a href="{href}">{esc(all_label)} →</a></li>{lis}</ul></div></div>')

def header(light=False):
    return f'''<a class="skip" href="#obsah">Přeskočit na obsah</a>
<header class="hdr">
 <div class="wrap">
  <a class="brand" href="{P or './'}" aria-label="HallPro Service – úvod">{logo('h')}</a>
  <div class="hdr-bar" aria-hidden="true"><span>Servis průmyslových hal</span><i></i><span>Střechy · Konstrukce · Bezpečnost</span><i></i><span>Po celé ČR</span></div>
  <a class="hdr-call" href="tel:{CO["tel"]}"><span class="pulse" aria-hidden="true"></span><span><small>Servis 24/7</small>{CO["phone"]}</span></a>
  <a class="btn btn-o hdr-cta" href="{P}kontakt/#poptavka">Poptávka</a>
  <button class="menu-btn" aria-expanded="false" aria-controls="menu"><span class="t">Menu</span><span class="bars" aria-hidden="true"></span></button>
 </div>
</header>
<nav class="menu" id="menu" aria-label="Hlavní menu" inert>
 <div class="wrap">
  <div class="menu-grid">
   {"".join(menu_col(c["name"], f"{P}{c['slug']}/", [(n, f"{P}{k}/") for k, n in c["kids"]], "Přehled: " + c["name"]) for c in CATS)}
   {menu_col("Havarijní servis 24/7", f"{P}havarijni-servis-247/", [("O nás", f"{P}o-nas-hallpro-service/"), ("Před a po", f"{P}#realizace"), ("Kontakt", f"{P}kontakt/"), ("Poptávkový formulář", f"{P}kontakt/#poptavka")], "Havarijní servis 24/7")}
  </div>
  <div class="menu-foot reveal-m">
   <a class="big-tel" href="tel:{CO["tel"]}" style="font-size:clamp(1.6rem,3vw,2.4rem)">{ic("phone","")}{CO["phone"]}</a>
   {socials()}
  </div>
 </div>
</nav>
<main id="obsah">'''

def cta_band(title='Technický stav budov pod kontrolou. Stačí jeden krok.', sub='Vstupní prohlídka objektu je zdarma. Připravíme návrh servisního postupu i cenovou nabídku.'):
    return f'''<section class="cta-band"><svg class="bg-gear" viewBox="20 24 60 60" aria-hidden="true"><path d="{GEAR}" fill="currentColor"/></svg>
 <div class="wrap"><div><h2 class="d3 rv">{esc(title)}</h2><p class="rv rv-d1" style="margin:14px 0 0;max-width:52ch;opacity:.92">{esc(sub)}</p></div>
 <div class="btns rv rv-d2"><a class="btn btn-d" href="#poptavka">Objednat vstupní prohlídku {ic("arr","arr")}</a><a class="btn btn-ghost" href="tel:{CO["tel"]}">{ic("phone","arr")} Zavolat</a></div></div></section>'''

SERVICE_OPTS = [c['name'] for c in CATS] + ['Havarijní servis 24/7', 'Jiné']
def form(title='Zanechte nám kontakt a připravíme vám návrh servisního postupu.', preset=''):
    opts = ''.join(f'<option{" selected" if o == preset else ""}>{esc(o)}</option>' for o in SERVICE_OPTS)
    return f'''<section class="sec dark" id="poptavka"><div class="wrap form-sec">
 <div class="form-aside">
  <span class="tag rv">Poptávka</span>
  <h2 class="d2 rv">{esc(title.split(".")[0])}.</h2>
  <p class="lead rv rv-d1" style="margin-top:20px">Ozveme se obvykle do 24 hodin. Vstupní prohlídka objektu je zdarma a nezávazná.</p>
  <ul class="rv rv-d2"><li>{ic("check")}Prohlídka objektu a návrh řešení</li><li>{ic("check")}Protokol a fotodokumentace dle ČSN</li><li>{ic("check")}Cenová nabídka bez závazků</li><li>{ic("check")}Servis po celé České republice</li></ul>
  <a class="hot rv rv-d3" href="tel:{CO["tel"]}"><span class="sq">{ic("phone")}</span><span><small>Havárie? Volejte nonstop</small><b>{CO["phone"]}</b></span></a>
 </div>
 <form class="inq rv" novalidate data-endpoint="{FORM_ENDPOINT}" data-mail="{FORM_MAIL}">
  <div class="fld"><label for="f-jmeno">Jméno / společnost <i>*</i></label><input id="f-jmeno" name="jmeno" required autocomplete="name"><span class="err">Vyplňte prosím jméno nebo název firmy.</span></div>
  <div class="fld"><label for="f-tel">Telefon <i>*</i></label><input id="f-tel" name="telefon" type="tel" required autocomplete="tel" inputmode="tel"><span class="err">Zadejte telefon (alespoň 9 číslic).</span></div>
  <div class="fld"><label for="f-mail">E-mail <i>*</i></label><input id="f-mail" name="email" type="email" required autocomplete="email"><span class="err">Zadejte platný e-mail.</span></div>
  <div class="fld"><label for="f-misto">Místo objektu</label><input id="f-misto" name="misto" placeholder="Město / areál" autocomplete="address-level2"></div>
  <div class="fld f-full"><label for="f-sluzba">Služba <i>*</i></label><select id="f-sluzba" name="sluzba" required><option value="">Vyberte službu</option>{opts}</select><span class="err">Vyberte prosím službu.</span></div>
  <fieldset class="fld f-full" style="border:0;padding:0;margin:0"><legend class="sr-only">Typ požadavku</legend><label as="span">Jaký je váš požadavek</label>
   <div class="radios"><label><input type="radio" name="pozadavek" value="Potřebuji vstupní prohlídku" checked><span>Potřebuji vstupní prohlídku</span></label><label><input type="radio" name="pozadavek" value="Mám problém, potřebuji řešit závadu"><span>Řeším závadu</span></label><label><input type="radio" name="pozadavek" value="Chci více informací"><span>Chci více informací</span></label></div></fieldset>
  <div class="fld f-full"><label for="f-zprava">Zpráva</label><textarea id="f-zprava" name="zprava" placeholder="Popište stručně objekt a co potřebujete řešit (např. zatéká u světlíku, hala 4 000 m²)"></textarea></div>
  <div class="hp" aria-hidden="true"><label>Web<input name="web" tabindex="-1" autocomplete="off"></label></div>
  <label class="consent f-full"><input type="checkbox" name="souhlas" value="ano" required><span>Souhlasím se <a href="{P}ochrana-osobnich-udaju/">zpracováním osobních údajů</a> za účelem vyřízení poptávky.</span></label>
  <div class="form-foot f-full"><button class="btn btn-o" type="submit">Odeslat poptávku {ic("arr","arr")}</button><span class="small" style="color:var(--muted)">* povinné údaje</span></div>
  <div class="form-msg f-full" role="status" aria-live="polite"></div>
 </form>
</div></section>'''

def footer():
    cols = ''.join(f'<li><a href="{P}{c["slug"]}/">{esc(c["name"])}</a></li>' for c in CATS)
    return f'''</main>
<footer class="ftr"><div class="wrap">
 <div class="ftr-top">
  <div><a class="brand" href="{P or './'}" aria-label="HallPro Service">{logo('f')}</a><p style="max-width:34ch">Servis a opravy průmyslových hal, skladů a areálů po celé ČR. Kontrolujeme, udržujeme, opravujeme.</p>{socials()}</div>
  <div><h4>Služby</h4><ul>{cols}<li><a href="{P}havarijni-servis-247/">Havarijní servis 24/7</a></li></ul></div>
  <div><h4>Kontakt</h4><ul><li><a href="tel:{CO["tel"]}">{CO["phone"]}</a></li><li><a href="mailto:{CO["mail"]}">{CO["mail"]}</a></li><li><a href="mailto:servis@hallpro.cz">servis@hallpro.cz</a></li><li>Pobočky Hradec Králové a Olomouc</li><li><a href="{P}kontakt/#poptavka">Poptávkový formulář</a></li></ul></div>
  <div><h4>Fakturační údaje</h4><address>{CO["name"]}<br>{CO["addr"]}<br>IČO: {CO["ico"]} · DIČ: {CO["dic"]}<br><span class="small">Spisová značka {CO["reg"]}</span></address></div>
 </div>
 <div class="ftr-bot"><span>© <span data-year>2026</span> {CO["name"]}</span><span><a href="{P}o-nas-hallpro-service/">O nás</a> · <a href="{P}ochrana-osobnich-udaju/">Ochrana osobních údajů</a></span></div>
</div></footer>
<div class="fab"><a class="c" href="tel:{CO["tel"]}" aria-label="Zavolat">{ic("phone")}</a><a href="{P}kontakt/#poptavka">Poptávka {ic("arr")}</a></div>
<script src="{P}assets/js/main.js?v={VERSION}" defer></script>'''

def ld_business():
    return '<script type="application/ld+json">' + json.dumps({
        "@context": "https://schema.org", "@type": "HomeAndConstructionBusiness", "name": CO['name'], "url": DOMAIN,
        "telephone": CO['tel'], "email": CO['mail'], "logo": DOMAIN + '/favicon.svg', "image": DOMAIN + '/assets/img/50c1daf8-1280.webp',
        "address": {"@type": "PostalAddress", "streetAddress": "Korunní 2569/108", "addressLocality": "Praha 10", "postalCode": "101 00", "addressCountry": "CZ"},
        "areaServed": "CZ", "openingHours": "Mo-Su 00:00-23:59", "vatID": CO['dic'], "taxID": CO['ico'],
        "sameAs": [CO['fb'], CO['ig'], CO['li']]}, ensure_ascii=False) + '</script>\n'

def write(path, content):
    full = os.path.join(ROOT, path, 'index.html') if path else os.path.join(ROOT, 'index.html')
    os.makedirs(os.path.dirname(full), exist_ok=True)
    open(full, 'w', encoding='utf-8').write(re.sub(r'\n\s*\n', '\n', content))

def sub_hero(title, lead, key, crumbs, cta, cta_href='#poptavka', depth=None):
    slides = [{'img': f'{P}assets/img/{key}-{{w}}.webp', 'max': IMGS[key]['sizes'][-1]}]
    if depth: slides[0]['depth'] = depth
    cr = ' <span aria-hidden="true">/</span> '.join(f'<a href="{h}">{esc(n)}</a>' if h else f'<span>{esc(n)}</span>' for n, h in crumbs)
    return f'''<section class="hero sm on-photo">
 <div class="hero-media" data-hero3d='{json.dumps(slides)}'>{img(key, title, eager=True)}</div>
 <div class="wrap hero-in"><div>
  <nav class="crumbs" aria-label="Drobečková navigace">{cr}</nav>
  <h1 class="d1"><span class="ln"><span>{esc(title)}</span></span></h1>
  {f'<p class="sub">{esc(lead)}</p>' if lead else ''}
  <div class="btns" style="margin-top:26px"><a class="btn btn-o" href="{cta_href}">{esc(cta)} {ic("arr","arr")}</a><a class="btn btn-ghost" href="tel:{CO["tel"]}">{ic("phone","arr")} {CO["phone"]}</a></div>
 </div></div>
</section>'''
HERO_JS = lambda: f'<script src="{P}assets/js/hero3d.js?v={VERSION}" defer></script>'

def why_rows(items):
    return '<div class="why" data-carousel>' + ''.join(f'<div class="rv{" rv-d1" if i % 2 else ""}"><b>{i+1:02d}</b><h3>{esc(t)}</h3><p>{esc(d)}</p></div>' for i, (t, d) in enumerate(items)) + '</div>'
WHY = [
    ('Vstupní prohlídka zdarma', 'Prohlédneme objekt, vytipujeme riziková místa a navrhneme konkrétní postup včetně cenové nabídky. Nezávazně.'),
    ('Havarijní servis 24/7', 'Zatékání, vichřice, náraz manipulační techniky nebo porucha vrat. Vyjíždíme nonstop a objekt zajistíme.'),
    ('Práce bez lešení', 'Pracovní plošiny a lanová technika. Opravíme i místa, kam se běžná technika nedostane, a šetříme čas i náklady.'),
    ('Certifikovaný partner ROOFIX', 'Návrh, montáž a pravidelné revize záchytných a kotvicích systémů pro bezpečnou práci ve výškách.'),
    ('Kontroly dle ČSN s protokolem', 'Prohlídky ocelových konstrukcí dle ČSN 73 2604, střech dle ČSN 73 1901 a další. Vždy s fotodokumentací.'),
    ('Jeden partner pro celý objekt', 'Od výměny střešního šroubu po kompletní renovaci pláště. Minimalizujeme omezení vašeho provozu.'),
]
STEPS = [('search', 'Prohlídka', 'Technik prohlédne objekt, střechu nebo konstrukci a zmapuje skutečný stav.'),
         ('doc', 'Protokol', 'Dostanete záznam o stavu, fotodokumentaci závad a doporučená opatření s prioritami.'),
         ('wrench', 'Oprava', 'Zjištěné závady odstraní naši vlastní servisní technici, bez zbytečných subdodávek.'),
         ('cal', 'Údržba', 'Nastavíme pravidelný servis, aby se problémy už neopakovaly a budova byla pod kontrolou.')]
def steps():
    return '<div class="steps">' + ''.join(f'<div class="step rv rv-d{i}"><div class="ic">{ic(k)}</div><h3>{t}</h3><p>{d}</p></div>' for i, (k, t, d) in enumerate(STEPS)) + '</div>'

def team_cards():
    out = []
    for t in TEAM:
        li = f'<div class="soc"><a class="soc-ic" href="{t["li"]}" target="_blank" rel="noopener" aria-label="LinkedIn – {t["name"]}">{SOC["li"]}</a></div>' if t.get('li') else ''
        out.append(f'<article class="person rv"><div class="ph">{img(t["img"], t["name"], "110px")}</div><div class="tx"><span class="role">{esc(t["role"])}</span><h3>{esc(t["name"])}</h3>'
                   f'<a class="l" href="tel:{t["phone"].replace(" ", "")}">{ic("phone")}{t["phone"]}</a><a class="l" href="mailto:{t["mail"]}">{ic("mail")}{t["mail"]}</a>{li}</div></article>')
    return '<div class="team">' + ''.join(out) + '</div>'

CLIENTS = ['kofola', 'dhl', 'redbull', 'penny', 'vog', 'simoldes', 'unipap', 'zoeller']
NAMES = {'kofola': 'Kofola', 'dhl': 'DHL', 'redbull': 'Red Bull', 'penny': 'Penny', 'vog': 'VOG', 'simoldes': 'Simoldes Plasticos', 'unipap': 'Unipap Packaging', 'zoeller': 'Zoeller'}
def clients(cls=''):
    li = ''
    for c in CLIENTS:
        m = IMGS['client-' + c]; ratio = m['w'] / m['h']
        h = max(.85, min(1.3, (3.4 / ratio) ** .5))  # opticky srovnat široká a vysoká loga
        li += f'<li><img src="{P}assets/img/clients/{c}.webp" alt="{NAMES[c]}" width="{m["w"]}" height="{m["h"]}" style="--k:{h:.2f}" decoding="async"></li>'
    return f'<div class="refs {cls}" aria-label="Naši klienti"><div class="marquee"><ul>{li}</ul><ul aria-hidden="true">{li}</ul></div></div>'

# ================================================================= STRÁNKY
P = ''
def build_home():
    global P; P = ''
    slides = [
        {'img': 'assets/img/50c1daf8-{w}.webp', 'max': 1280, 'depth': 'assets/img/depth-50c1daf8.webp'},
        {'img': 'assets/img/2605ee70-{w}.webp', 'max': 1600, 'depth': 'assets/img/depth-2605ee70.webp'},
        {'img': 'assets/img/5e5328fd-{w}.webp', 'max': 1600, 'depth': 'assets/img/depth-5e5328fd.webp'},
    ]
    cards = ''.join(f'''<a class="card rv" href="{c["slug"]}/"><div class="ph">{img(CAT_IMG[c["slug"]], c["name"], "(min-width:640px) 45vw, 100vw")}</div>
  <div class="meta"><div><span class="num">{i+1:02d}</span><h3>{esc(c["name"])}</h3><p>{esc(c["short"])}</p></div><span class="sq">{ic("arr")}</span></div></a>''' for i, c in enumerate(CATS))
    cards += f'''<a class="card rv" href="havarijni-servis-247/"><div class="ph">{img("e1a4366f", "Havarijní servis 24/7", "(min-width:640px) 45vw, 100vw")}</div>
  <div class="meta"><div><span class="num">24/7</span><h3>Havarijní servis</h3><p>Zatékání, poškozená konstrukce nebo havárie po větru či nárazu. Vyjíždíme nonstop.</p></div><span class="sq">{ic("arr")}</span></div></a>'''
    svc = ''.join(f'<li class="rv"><a href="{c["slug"]}/"><h3>{esc(c["name"])}</h3><p>{esc(c["short"])}</p><span class="sq">{ic("arr-ur")}</span></a></li>' for c in CATS)
    field = [('fb-vpust-1', 'Kontrola a čištění střešních vpustí'), ('fb-svetliky-2', 'Servis světlíkových pásů'), ('fb-plosina-fasada', 'Práce z plošiny na fasádě haly'), ('fb-svetliky-1', 'Údržba světlíků na střeše s FVE')]
    gal = ''.join(f'<figure class="rv rv-d{i % 3}">{img(k, t, "(min-width:700px) 25vw, 50vw")}<figcaption>{esc(t)}</figcaption></figure>' for i, (k, t) in enumerate(field))
    html_ = head('HallPro Service – servis průmyslových hal, střech a konstrukcí | 24/7',
                 'Servis a opravy průmyslových hal, střech, ocelových konstrukcí a bezpečnostních prvků po celé ČR. Kontroly dle ČSN, výškové práce, havarijní servis 24/7. Vstupní prohlídka zdarma.',
                 '', preload=img_preload('50c1daf8'), extra=ld_business()) + f'''
<body>
{header()}
<section class="hero on-photo" aria-label="Úvod">
 <div class="hero-media" data-hero3d='{json.dumps(slides)}'>{img("50c1daf8", "Technici HallPro na střeše průmyslové haly při západu slunce", eager=True)}</div>
 <div class="wrap hero-in">
  <div>
   <span class="kicker">Kontrolujeme <b>•</b> Udržujeme <b>•</b> Opravujeme</span>
   <h1 class="d1"><span class="ln"><span>Když hala potřebuje servis,</span></span><span class="ln"><span>HallPro dorazí.</span></span></h1>
   <p class="sub">Servis a opravy průmyslových hal, skladů a areálů po celé České republice. Vlastní tým techniků, výšková technika a havarijní výjezdy 24/7.</p>
   <div class="hero-dots" aria-label="Snímky">{"".join(f'<button aria-label="Snímek {i+1}"><span></span></button>' for i in range(len(slides)))}</div>
  </div>
  <a class="hero-card" href="kontakt/#poptavka">
   <div class="ph">{img("9a034737", "Technik HallPro s tabletem před halou", "180px")}</div>
   <div class="tx"><strong>Vstupní prohlídka objektu zdarma</strong><span class="btns"><span class="btn btn-d">Objednat</span><span class="btn btn-o">Služby {ic("arr","arr")}</span></span></div>
  </a>
 </div>
 {clients("in-hero")}
</section>

<section class="sec no-line"><div class="wrap">
 <span class="tag rv">Kdo jsme</span>
 <h2 class="d2 statement rv">Servis průmyslových budov, <span class="o">od lidí, kteří znají provoz.</span></h2>
</div></section>

<section class="sec" style="padding-top:0;border-top:0"><div class="wrap split ruled" style="border-top:1px solid var(--line);padding-top:clamp(48px,6vw,96px)">
 <div class="about-img par-box img-rv">{img("9a034737", "Technik HallPro Service před průmyslovou halou", "(min-width:900px) 50vw, 100vw", attrs=' data-par="7"')}</div>
 <div class="about-copy">
  <h2 class="d3 rv"><span class="o">Vlastní tým techniků.</span> Servis po celé České republice.</h2>
  <p class="rv rv-d1">Jsme HallPro Service – profesionální servisní síť specializovaná na komplexní technickou správu, údržbu a servis průmyslových hal, skladů, bytových domů a komerčních provozů.</p>
  <p class="rv rv-d1">Hlavní devizou je vlastní tým vyškolených techniků připravených okamžitě zasáhnout v terénu, podpořený moderním dispečinkem a spolehlivým vozovým parkem. Pobočky máme v Hradci Králové a Olomouci, sídlo v Praze.</p>
  <div class="btns rv rv-d2"><a class="btn btn-d" href="o-nas-hallpro-service/">O nás</a><a class="btn btn-o" href="#sluzby">Naše služby {ic("arr","arr")}</a></div>
 </div>
</div></section>

<section class="tile-row" aria-label="Co děláme">
 <div class="logo-tile"><p>Kontrolujeme · Udržujeme · Opravujeme</p>{big_mark()}</div>
 <div class="tile-copy"><span class="tag rv">Co děláme</span><h2 class="d2 rv">Technický stav budov, <span class="o">pod kontrolou.</span></h2></div>
</section>

<section class="sec"><div class="wrap split ruled">
 <div><div class="sticky"><h2 class="d3 rv" style="max-width:16ch"><span class="o">Střechy, konstrukce, bezpečnost i výškové práce</span> od jednoho servisního partnera.</h2>
  <p class="lead rv rv-d1" style="margin-top:22px">Od výměny střešního šroubu až po kompletní renovaci střešního pláště, hydroizolací a systémů odvodnění. Máte jednoho partnera, který se postará o technický stav celé budovy.</p></div></div>
 <ul class="svc-list">{svc}</ul>
</div></section>

<section class="sec" style="padding:0" aria-label="HallPro v číslech"><div class="wrap" style="padding:0">
 <div class="stats">
  <div class="stat rv"><b data-count="9">9</b><span>aktuálně realizovaných projektů v ČR</span></div>
  <div class="stat rv rv-d1"><b data-count="12">12</b><span>techniků připravených každý den pomáhat firmám</span></div>
  <div class="stat rv rv-d2"><b data-count="300" data-suffix="+">300+</b><span>kontrol a prohlídek konstrukcí každý rok</span></div>
  <div class="stat rv rv-d3"><b data-count="100" data-suffix="+">100+</b><span>firem, které nám svěřují údržbu svých objektů</span></div>
 </div>
</div></section>

<section class="sec" id="sluzby"><div class="wrap">
 <div class="fleet-head">
  <div><span class="tag rv">Služby</span><h2 class="d2 rv">Kompletní péče o <span class="o">průmyslové haly,</span> sklady a areály.</h2></div>
 </div>
 <div class="fleet" data-carousel>{cards}</div>
</div></section>

<section class="sec no-line" id="realizace"><div class="wrap ba-wrap">
 <div class="ba rv" style="--x:50%">
  {img("fb-schody-pred", "Venkovní schodiště před úpravou", "440px")}
  {img("fb-schody-po", "Schodiště po doplnění protiskluzových a výstražných prvků", "440px", cls="after")}
  <span class="lbl l">Před</span><span class="lbl r">Po</span><span class="handle" aria-hidden="true"></span>
  <input type="range" min="0" max="100" value="50" aria-label="Porovnání před a po">
 </div>
 <div>
  <span class="tag rv">Před a po</span>
  <h2 class="d2 rv">Reálná práce, <span class="o">viditelný výsledek.</span></h2>
  <p class="lead rv rv-d1" style="margin-top:22px">Na venkovní schodiště průmyslového areálu jsme doplnili protiskluzové a výstražné prvky. Drobná úprava, která každý den snižuje riziko úrazu.</p>
  <p class="rv rv-d1" style="color:var(--muted)">Pro firmy a areály zajišťujeme kompletní bezpečnostní prvky: značení, ochrany regálů a konstrukcí, protiskluzová řešení a zábrany. Posuňte jezdcem a porovnejte.</p>
  <div class="btns rv rv-d2" style="margin-top:24px"><a class="btn btn-d" href="bezpecnost-provozu/">Bezpečnost provozu</a><a class="btn btn-o" href="#poptavka">Chci audit zdarma {ic("arr","arr")}</a></div>
 </div>
</div>
<div class="wrap"><div class="field">{gal}</div><p class="small rv" style="color:var(--muted);margin-top:12px">Fotky z našich zakázek. Další najdete na <a href="{CO["fb"]}" target="_blank" rel="noopener" style="color:var(--o-ink);text-decoration:underline">Facebooku</a> a <a href="{CO["li"]}" target="_blank" rel="noopener" style="color:var(--o-ink);text-decoration:underline">LinkedInu</a>.</p></div>
</section>

<section class="sec dark"><div class="wrap">
 <div class="why-head"><div><span class="tag rv">Proč HallPro</span><h2 class="d2 rv">Nejsme jen další servisní firma. <span class="o">Jsme váš technický partner.</span></h2></div>
 <p class="lead rv rv-d1">Specializovaný servis s důrazem na prevenci, rychlé řešení závad a dlouhou životnost průmyslových budov.</p></div>
 {why_rows(WHY)}
</div></section>

<section class="sec soft"><div class="wrap cert">
 <div class="ph img-rv">{img("fb-roofix", "Kotvicí bod ROOFIX na střeše s fotovoltaikou", "(min-width:900px) 50vw, 100vw")}</div>
 <div><span class="tag o-tag rv">Certifikace</span><h2 class="d3 rv">Certifikovaný partner <span class="o">ROOFIX</span> pro záchytné a kotvicí systémy.</h2>
  <p class="rv rv-d1" style="margin-top:18px;color:var(--muted)">Navrhujeme, dodáváme a montujeme lanové systémy a kotvicí body, a to i na střechy s fotovoltaikou. Následně provádíme pravidelné kontroly a revize. Pracujeme podle platných norem a předpisů:</p>
  <ul class="chips rv rv-d2"><li>ČSN 73 2604</li><li>ČSN 73 1901</li><li>ČSN EN 795</li><li>ČSN EN 365</li><li>ČSN ISO 9927-1</li><li>NV 362/2005 Sb.</li><li>NV 193/2022 Sb.</li></ul>
  <div class="btns rv rv-d2" style="margin-top:26px"><a class="btn btn-d" href="zachytne-systemy/">Záchytné systémy {ic("arr","arr")}</a></div></div>
</div></section>

<section class="sec"><div class="wrap">
 <div class="fleet-head" style="margin-bottom:40px"><div><span class="tag rv">Kontakty</span><h2 class="d2 rv">Lidé, kteří <span class="o">zvednou telefon.</span></h2></div>
 <p class="lead rv rv-d1" style="justify-self:end">Sídlo v Praze, pobočky v Hradci Králové a Olomouci. Servis po celé ČR.</p></div>
 {team_cards()}
</div></section>

{form()}
{footer()}
{HERO_JS()}
</body></html>'''
    write('', html_)

def build_category(c):
    global P; P = '../'
    d = PAGES[c['slug']]
    kids = [(k, n, page_data(k)) for k, n in c['kids']]
    titles = {kd['title'].lower() for _, _, kd in kids}
    secs = d['secs']; rich = next((i for i, s in enumerate(secs) if len(s['items']) >= 2), len(secs))
    content = [s for i, s in enumerate(secs) if s['items'] and s['h'].lower() not in titles and not (i < rich and len(s['items']) <= 1)]
    intro = content[0] if content else None
    cards = ''.join(f'''<a class="card rv" href="../{k}/"><div class="ph">{img(kd["img"], n, "(min-width:1100px) 30vw, (min-width:640px) 45vw, 100vw")}</div>
  <div class="meta"><div><span class="num">{i+1:02d}</span><h3>{esc(n)}</h3><p>{esc(kd["lead"] or "")}</p></div><span class="sq">{ic("arr")}</span></div></a>''' for i, (k, n, kd) in enumerate(kids))
    why = ' '.join(x for x in d['why'] if len(x) > 60 and not x.startswith('HallPro Service –')) or WHY[5][1]
    lead = intro['items'][0] if intro and len(intro['items'][0]) < 200 else c['short']
    html_ = head(f'{c["name"]} | HallPro Service', f'{c["short"]} {lead}'[:300], c['slug'] + '/', CAT_IMG[c['slug']]) + f'''
<body>
{header()}
{sub_hero(c["h1"], lead, CAT_IMG[c["slug"]], [("Úvod", "../"), ("Služby", "../#sluzby"), (c["name"], None)], "Poptat " + c["name"].lower())}
<section class="sec no-line"><div class="wrap">
 <div class="fleet-head"><div><span class="tag rv">{esc(c["name"])}</span><h2 class="d2 rv">{esc(intro["h"] if intro else c["name"])}</h2></div>
 <p class="lead rv rv-d1" style="justify-self:end">{esc(c["short"])}</p></div>
 <div class="fleet three" data-carousel>{cards}</div>
</div></section>
<section class="sec"><div class="wrap svc-layout">
 <div>{blocks([dict(h=intro["h"], items=intro["items"][1:] if lead == intro["items"][0] else intro["items"])] + content[1:] if intro else [])}</div>
 {aside(c, None)}
</div></section>
<section class="sec dark tight"><div class="wrap"><div class="why-head" style="margin:0"><div><span class="tag">Proč HallPro Service?</span><h2 class="d3">{esc(why)}</h2></div><div class="btns" style="justify-self:end"><a class="btn btn-o" href="#poptavka">Poptat {esc(c["name"].lower())} {ic("arr","arr")}</a></div></div></div></section>
{form(preset=c["name"])}
{footer()}
{HERO_JS()}
</body></html>'''
    write(c['slug'], html_)

def aside(c, current):
    links = ''.join(f'<a href="../{k}/"{" aria-current=page" if k == current else ""}>{esc(n)} {ic("arr")}</a>' for k, n in c['kids'])
    return f'''<aside class="svc-aside"><div class="box rv"><strong>Potřebujete řešit {esc(c["name"].lower())}?</strong><p>Vstupní prohlídka zdarma. Ozveme se obvykle do 24 hodin.</p>
  <a class="tel" href="tel:{CO["tel"]}">{ic("phone","arr")}{CO["phone"]}</a><a class="btn btn-o" href="#poptavka">Nezávazná poptávka {ic("arr","arr")}</a></div>
  <nav aria-label="{esc(c["name"])}"><b>{esc(c["name"])}</b><a href="../{c["slug"]}/">Přehled kategorie {ic("arr")}</a>{links}</nav></aside>'''

def build_detail(slug, name, c):
    global P; P = '../'
    kd = page_data(slug)
    legal = ''.join(f'<div class="legal rv">{ic("info")}<span>{esc(x)}</span></div>' for x in kd['legal'])
    first = blocks([dict(h='O službě', items=kd['body'])]) if kd['body'] else ''
    rel = [(k, n) for k, n in c['kids'] if k != slug][:3]
    relc = ''.join(f'''<a class="card rv" href="../{k}/"><div class="ph">{img(page_data(k)["img"], n, "(min-width:1100px) 30vw, (min-width:640px) 45vw, 100vw")}</div>
  <div class="meta"><div><h3>{esc(n)}</h3><p>{esc(page_data(k)["lead"] or "")}</p></div><span class="sq">{ic("arr")}</span></div></a>''' for k, n in rel)
    desc = (kd['lead'] or '') + ' ' + (kd['body'][0] if kd['body'] else '')
    html_ = head(f'{name} – {c["name"]} | HallPro Service', desc.strip()[:300], slug + '/', kd['img']) + f'''
<body>
{header()}
{sub_hero(kd["title"], kd["lead"], kd["img"], [("Úvod", "../"), (c["name"], f"../{c['slug']}/"), (name, None)], kd["cta"])}
<section class="sec no-line"><div class="wrap svc-layout">
 <div>{legal}{first}{blocks(kd["secs"])}
  <div class="blk rv"><h2>Proč HallPro Service?</h2><p>{esc(kd["why"] or WHY[2][1])}</p>{f'<p class="small" style="color:var(--o-ink);font-weight:600">{esc(kd["claim"])}</p>' if kd["claim"] else ''}</div>
 </div>
 {aside(c, slug)}
</div></section>
{cta_band()}
{f'<section class="sec no-line"><div class="wrap"><div class="fleet-head" style="margin-bottom:40px"><div><span class="tag rv">Související služby</span><h2 class="d3 rv">{esc(c["name"])}</h2></div></div><div class="fleet three">{relc}</div></div></section>' if rel else ''}
{form(preset=c["name"])}
{footer()}
{HERO_JS()}
</body></html>'''
    write(slug, html_)

def build_emergency():
    global P; P = '../'
    sos = [('drop', 'Zatéká do budovy'), ('roof', 'Poškozená střecha nebo opláštění'), ('beam', 'Uvolněná konstrukce'), ('fire', 'Požár nebo povodeň'), ('door', 'Nejdou zavřít vrata'), ('alert', 'Hrozí omezení provozu')]
    st = [('phone', 'Zavoláte', 'Okamžitá konzultace s technikem po telefonu.'), ('truck', 'Technik vyjíždí', 'Na místo míří technik s potřebným vybavením.'), ('shield', 'Zajištění a plán opravy', 'Zajistíme objekt, minimalizujeme škody a navrhneme trvalé řešení.')]
    html_ = head('Havarijní servis 24/7 – porucha na budově | HallPro Service', 'Zatékání, poškozená konstrukce, havárie po větru nebo nárazu? HallPro Service vyjíždí 24/7. Zajistíme objekt a opravíme střechy, stěny, vrata i konstrukce.', 'havarijni-servis-247/', 'e1a4366f') + f'''
<body>
{header()}
{sub_hero("Porucha na budově? Vyjíždíme 24/7", "Zatékání, poškozená konstrukce, havárie po větru nebo nárazu? Jsme připraveni zasáhnout okamžitě.", "3f04a00b", [("Úvod", "../"), ("Havarijní servis 24/7", None)], "Nahlásit poruchu online")}
<section class="sec dark no-line"><div class="wrap">
 <div class="why-head"><div><span class="tag rv">Volejte nonstop</span><a class="big-tel rv" href="tel:{CO["tel"]}">{ic("phone","")}{CO["phone"]}</a></div><p class="lead rv rv-d1">Když jde o provoz, rozhodují hodiny. Zajistíme objekt, minimalizujeme škody a obnovíme bezpečný provoz.</p></div>
 <h2 class="d4 rv" style="margin-bottom:20px">Kdy volat expresní servis?</h2>
 <div class="sos">{"".join(f'<div class="rv">{ic(k)}<span>{esc(t)}</span></div>' for k, t in sos)}</div>
</div></section>
<section class="sec no-line"><div class="wrap">
 <div class="fleet-head" style="margin-bottom:40px"><div><span class="tag rv">Jak probíhá zásah</span><h2 class="d2 rv">Tři kroky <span class="o">k bezpečnému provozu.</span></h2></div></div>
 <div class="steps" style="grid-template-columns:repeat(auto-fit,minmax(240px,1fr))">{"".join(f'<div class="step rv"><div class="ic">{ic(k)}</div><h3>{t}</h3><p>{d}</p></div>' for k, t, d in st)}</div>
 <div class="split ruled" style="margin-top:clamp(48px,6vw,96px);align-items:center">
  <div class="about-img img-rv">{img("e1a4366f", "Technik HallPro Service u haly", "(min-width:900px) 50vw, 100vw")}</div>
  <div><h2 class="d3 rv">Požár, povodeň, náraz techniky nebo silný vítr?</h2><p class="lead rv rv-d1" style="margin-top:18px">Jsme připraveni zasáhnout okamžitě a opravit střechy, stěny, vrata i konstrukce. Havarijní utěsnění, zabezpečení objektu proti dalším škodám a návrh trvalého řešení.</p>
  <div class="btns rv rv-d2" style="margin-top:24px"><a class="btn btn-o" href="tel:{CO["tel"]}">{ic("phone","arr")} Zavolat servis 24/7</a><a class="btn btn-d" href="#poptavka">Nahlásit online</a></div></div>
 </div>
</div></section>
{form("Nahlaste poruchu. Ozveme se co nejdříve.", "Havarijní servis 24/7")}
{footer()}
{HERO_JS()}
</body></html>'''
    write('havarijni-servis-247', html_)

def build_about():
    global P; P = '../'
    vals = [('Profesionalita', 'Služby provádějí kvalifikovaní technici s dlouholetou praxí.'), ('Rychlost a flexibilita', 'Jsme vždy připraveni okamžitě reagovat na potřeby klientů.'),
            ('Osobní přístup', 'Ke každému zákazníkovi přistupujeme individuálně a hledáme řešení na míru.'), ('Transparentnost', 'Jasná komunikace a férové podmínky jsou pro nás samozřejmostí.'),
            ('Bezpečnost', 'Dbáme na dodržování všech bezpečnostních a legislativních požadavků včetně BOZP.'), ('Nonstop péče', 'O budovy se staráme nonstop, havarijní výjezdy v režimu HallPro Express 24/7.')]
    svc = ['Pravidelný servis a technická správa budov', 'Havarijní výjezdy v režimu HallPro Express 24/7', 'Servis a opravy technologických zařízení v halách', 'Zajištění BOZP, revizí a provozní dokumentace',
           'Mytí halových konstrukcí a plášťů, zámkové dlažby a fasád', 'Komplexní péče o technický stav hal a skladů', 'Servis plachtových hal: konstrukce, opravy a svařování plachet, mytí pláště',
           'Facility management: provoz technologií, letní a zimní údržba areálu, PO a BOZP']
    html_ = head('O nás – HallPro Service s.r.o.', 'HallPro Service – profesionální servisní síť pro technickou správu, údržbu a servis budov, hal, skladů a komerčních provozů po celé ČR. Vlastní tým techniků, dispečink a vozový park.', 'o-nas-hallpro-service/', '9a034737') + f'''
<body>
{header()}
{sub_hero("Víme, co potřebuje vaše budova", "Jsme více než jen servis. O budovy se staráme nonstop.", "50c1daf8", [("Úvod", "../"), ("O nás", None)], "Kontaktujte nás", depth="../assets/img/depth-50c1daf8.webp")}
<section class="sec no-line"><div class="wrap">
 <span class="tag rv">O nás</span>
 <h2 class="d2 statement rv" style="max-width:26ch">Jsme HallPro Service. <span class="o">Profesionální servisní síť po celé České republice.</span></h2>
</div></section>
<section class="sec" style="border-top:0;padding-top:0"><div class="wrap split ruled" style="border-top:1px solid var(--line);padding-top:clamp(48px,6vw,96px)">
 <div class="about-img par-box img-rv">{img("9a034737", "Technik HallPro Service", "(min-width:900px) 50vw, 100vw", attrs=' data-par="7"')}</div>
 <div class="about-copy"><p class="lead rv">Specializujeme se na komplexní technickou správu, údržbu a servis budov, bytových domů, skladů a komerčních provozů. Hlavní devizou HallPro je vlastní tým vyškolených techniků, připravených okamžitě zasáhnout přímo v terénu, podpořený moderním dispečinkem a spolehlivým vozovým parkem.</p>
  <div class="blk rv" style="border:0;padding-bottom:0"><h2>Naše služby</h2><ul class="checks" style="grid-template-columns:1fr">{"".join(f"<li>{ic('check')}<span>{esc(s)}</span></li>" for s in svc)}</ul></div></div>
</div></section>
<section class="sec soft"><div class="wrap split ruled">
 <div><span class="tag rv">Náš tým</span><h2 class="d3 rv">Zkušení profesionálové jsou <span class="o">srdcem celé společnosti.</span></h2></div>
 <div><p class="rv">Naši technici jsou vyškolení odborníci s praktickými zkušenostmi z oboru, kteří pravidelně absolvují školení a mají přehled o nejnovějších technologiích a trendech.</p>
 <p class="rv rv-d1">Dispečeři koordinují výjezdy tak, aby každý požadavek byl vyřešen co nejrychleji a efektivně. Manažerský tým dohlíží na kvalitu služeb a rozvoj společnosti, aby HallPro byl stabilním a spolehlivým partnerem pro všechny klienty.</p></div>
</div></section>
<section class="sec dark"><div class="wrap">
 <div class="why-head"><div><span class="tag rv">Hodnoty a přístup</span><h2 class="d2 rv">Základ úspěchu je <span class="o">důvěra a spolehlivost.</span></h2></div><p class="lead rv rv-d1">Naše služby nejsou jen o technice, ale o tom, jak zákazníkům ulehčit každodenní provoz a zajistit bezstarostný chod jejich objektů.</p></div>
 {why_rows(vals)}
</div></section>
<section class="sec no-line" style="padding:0"><div class="wrap" style="padding:0"><div class="stats">
  <div class="stat rv"><b data-count="9">9</b><span>aktuálně realizovaných projektů v ČR</span></div>
  <div class="stat rv rv-d1"><b data-count="12">12</b><span>techniků připravených každý den</span></div>
  <div class="stat rv rv-d2"><b data-count="300" data-suffix="+">300+</b><span>kontrol a prohlídek konstrukcí ročně</span></div>
  <div class="stat rv rv-d3"><b data-count="100" data-suffix="+">100+</b><span>firem, které nám svěřují své objekty</span></div>
</div></div></section>
{clients()}
<section class="sec no-line"><div class="wrap"><div class="fleet-head" style="margin-bottom:40px"><div><span class="tag rv">Kontakty</span><h2 class="d2 rv">Kdo se o vás <span class="o">postará.</span></h2></div></div>{team_cards()}</div></section>
{form()}
{footer()}
{HERO_JS()}
</body></html>'''
    write('o-nas-hallpro-service', html_)

def build_contact():
    global P; P = '../'
    html_ = head('Kontakt – HallPro Service | +420 731 291 205', 'Kontakt na HallPro Service s.r.o. Servis 24/7: +420 731 291 205, info@hallpro.cz. Pobočky Hradec Králové a Olomouc, sídlo Praha. Poptávkový formulář.', 'kontakt/', '9a034737') + f'''
<body>
{header()}
{sub_hero("Potřebujete servis budovy? Zavolejte nám.", "Zajistěte bezpečný provoz vašeho objektu ještě dnes. Nechte nám zprávu a my se vám obratem ozveme.", "50c1daf8", [("Úvod", "../"), ("Kontakt", None)], "Vyplnit poptávku", depth="../assets/img/depth-50c1daf8.webp")}
<section class="sec no-line"><div class="wrap">
 <div class="fleet-head" style="margin-bottom:40px"><div><span class="tag rv">Kontakty</span><h2 class="d2 rv">Ozvěte se <span class="o">přímo lidem.</span></h2></div>
 <div class="rv rv-d1" style="justify-self:end"><a class="big-tel" href="tel:{CO["tel"]}" style="color:var(--ink);font-size:clamp(1.6rem,3vw,2.6rem)">{ic("phone","")}{CO["phone"]}</a><p class="small" style="color:var(--muted);margin:8px 0 0">Servis a havárie 24/7 · <a href="mailto:{CO["mail"]}" style="text-decoration:underline">{CO["mail"]}</a></p></div></div>
 {team_cards()}
 <div class="split ruled" style="margin-top:clamp(48px,6vw,80px);padding-top:40px;border-top:1px solid var(--line)">
  <div class="rv"><h2 class="d4" style="margin-bottom:14px">Fakturační údaje</h2><address style="font-style:normal;line-height:1.8;color:#3d3d42">{CO["name"]}<br>Sídlo: {CO["addr"]}<br>IČO: {CO["ico"]}<br>DIČ: {CO["dic"]}<br>Spisová značka: {CO["reg"]}</address></div>
  <div class="rv rv-d1"><h2 class="d4" style="margin-bottom:14px">Sledujte naši práci</h2><p style="color:var(--muted)">Novinky a fotky z realizací sdílíme na sociálních sítích.</p>{socials()}</div>
 </div>
</div></section>
{form("Zanechte nám kontakt. Ozveme se obratem.")}
{footer()}
{HERO_JS()}
</body></html>'''
    write('kontakt', html_)

def build_privacy():
    global P; P = '../'
    html_ = head('Ochrana osobních údajů | HallPro Service', 'Zásady zpracování osobních údajů společnosti HallPro Service s.r.o.', 'ochrana-osobnich-udaju/') + f'''
<body class="page-light">
{header()}
<section class="sec no-line" style="padding-top:calc(var(--hdr) + 64px)"><div class="wrap" style="max-width:860px">
 <span class="tag">Dokument</span><h1 class="d2" style="margin-bottom:32px">Ochrana osobních údajů</h1>
 <div class="blk"><h2>Správce údajů</h2><p>{CO["name"]}, {CO["addr"]}, IČO {CO["ico"]}, zapsaná pod spisovou značkou {CO["reg"]}. Kontakt: <a href="mailto:{CO["mail"]}">{CO["mail"]}</a>.</p></div>
 <div class="blk"><h2>Jaké údaje zpracováváme a proč</h2><p>Údaje z poptávkového formuláře (jméno nebo název firmy, telefon, e-mail, místo objektu a obsah zprávy) zpracováváme výhradně za účelem vyřízení vaší poptávky a přípravy nabídky. Právním základem je jednání o smlouvě na vaši žádost a váš souhlas.</p></div>
 <div class="blk"><h2>Jak dlouho údaje uchováváme</h2><p>Po dobu nezbytnou k vyřízení poptávky, nejdéle 3 roky, pokud nevznikne smluvní vztah. Údaje nepředáváme třetím stranám kromě zpracovatelů nezbytných pro provoz webu a komunikace.</p></div>
 <div class="blk"><h2>Vaše práva</h2><p>Máte právo na přístup k údajům, jejich opravu nebo výmaz, omezení zpracování, odvolání souhlasu a podání stížnosti u Úřadu pro ochranu osobních údajů (uoou.gov.cz).</p></div>
 <div class="blk"><h2>Cookies</h2><p>Tento web nepoužívá marketingové ani analytické cookies. Ukládá pouze technicky nezbytná data pro jeho fungování.</p></div>
</div></section>
{footer()}
</body></html>'''
    write('ochrana-osobnich-udaju', html_)

def build_404():
    global P; P = '/'
    html_ = head('Stránka nenalezena | HallPro Service', 'Stránka nebyla nalezena.', '404') + f'''
<body class="page-light">
{header()}
<section class="sec no-line" style="padding-top:calc(var(--hdr) + 80px);min-height:70vh"><div class="wrap">
 <span class="tag">Chyba 404</span><h1 class="d1">Tady nic <span class="o">není.</span></h1><p class="lead" style="margin:20px 0 28px">Stránku jsme přesunuli nebo už neexistuje. Zkuste úvod nebo nám rovnou zavolejte.</p>
 <div class="btns"><a class="btn btn-d" href="/">Na úvod</a><a class="btn btn-o" href="tel:{CO["tel"]}">{ic("phone","arr")} {CO["phone"]}</a></div>
</div></section>
{footer()}
</body></html>'''
    open(os.path.join(ROOT, '404.html'), 'w', encoding='utf-8').write(html_)

# ================================================================= běh
if __name__ == '__main__':
    open(os.path.join(ROOT, 'favicon.svg'), 'w').write(FAVICON)
    build_home()
    for c in CATS:
        build_category(c)
        for k, n in c['kids']: build_detail(k, n, c)
    build_emergency(); build_about(); build_contact(); build_privacy(); build_404()
    urls = [''] + [c['slug'] + '/' for c in CATS] + [k + '/' for c in CATS for k, _ in c['kids']] + ['havarijni-servis-247/', 'o-nas-hallpro-service/', 'kontakt/', 'ochrana-osobnich-udaju/']
    open(os.path.join(ROOT, 'sitemap.xml'), 'w').write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + ''.join(f'<url><loc>{DOMAIN}/{u}</loc></url>' for u in dict.fromkeys(urls)) + '</urlset>\n')
    open(os.path.join(ROOT, 'robots.txt'), 'w').write(f'User-agent: *\nAllow: /\nSitemap: {DOMAIN}/sitemap.xml\n')
    print('hotovo:', len(set(urls)), 'stránek')
