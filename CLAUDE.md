# Hall Pro Web

Nový web pro HallPro Service s.r.o. (hallpro.cz), servis průmyslových hal. Majitel/manažer: Lukáš Zeman. Vzhled inspirovaný rollers.com.au.

## Jak to funguje
- Statický web bez frameworku. Stránky se generují skriptem: `python3 tools/build.py` (z kořene složky).
- Texty služeb: `tools/pages.json` (převzato ze starého hallpro.cz). Ostatní texty, kontakty a struktura menu: začátek `tools/build.py`.
- Fotky: zdroje v `tools/source-photos/`, převod do WebP: `python3 tools/images.py` (potřebuje Pillow + numpy).
- Hero: statické fotky, prolínání s prostorovým efektem podle hloubkových map `tools/depth/*.png` (na myš nereaguje – přání klienta).
- URL kopírují starý web (`/servis-strech/`, `/strechy-293/` …), aby se neztratilo SEO.
- Náhled: `python3 -m http.server 8790` a otevřít http://localhost:8790 (port 8765 používá web Správa BOZP)

## Otevřené body
- Poptávkový formulář: zatím otevře e-mail na info@hallpro.cz. Pro e-mail + Telegram doplnit `FORM_ENDPOINT` v build.py (serverless funkce, klíče jen v .env).
- Ochrana osobních údajů: základní text, nechat zkontrolovat.
- Deploy: GitHub → Vercel (vercel.json je připravený). Commit/push jen na pokyn.
