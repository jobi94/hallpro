/* HallPro – hlavní skript: hlavička, menu, animace při scrollu, čísla, před/po, formulář */
document.documentElement.classList.remove('no-js');
(function () {
  const $ = (s, r = document) => r.querySelector(s), $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* hlavička: průhledná nad hero, bílá po scrollu, schová se při scrollu dolů */
  const hdr = $('.hdr'), fab = $('.fab');
  let lastY = 0;
  const light = document.body.classList.contains('page-light');
  function onScroll() {
    const y = scrollY;
    hdr.classList.toggle('solid', light || y > 40);
    if (document.body.classList.contains('menu-open') || y < hdr.offsetHeight) hdr.classList.remove('hide');
    else if (y > lastY + 2) hdr.classList.add('hide');
    else if (y < lastY - 2) hdr.classList.remove('hide');
    if (fab) fab.classList.toggle('show', y > innerHeight * .6);
    lastY = y;
  }
  addEventListener('scroll', onScroll, { passive: true }); onScroll();

  /* menu overlay */
  const btn = $('.menu-btn');
  function setMenu(open) {
    document.body.classList.toggle('menu-open', open);
    btn.setAttribute('aria-expanded', open);
    btn.querySelector('.t').textContent = open ? 'Zavřít' : 'Menu';
    $('#menu').toggleAttribute('inert', !open);
  }
  btn.addEventListener('click', () => setMenu(!document.body.classList.contains('menu-open')));
  addEventListener('keydown', e => { if (e.key === 'Escape') setMenu(false); });
  $$('#menu a').forEach(a => a.addEventListener('click', () => setMenu(false)));
  /* mobil: kategorie v menu jsou sbalené, kliknutím se rozbalí */
  $$('#menu .cat-tog').forEach(b => b.addEventListener('click', () => {
    const col = b.closest('.reveal-m'), open = !col.classList.contains('open');
    $$('#menu .reveal-m.open').forEach(o => { o.classList.remove('open'); o.querySelector('.cat-tog').setAttribute('aria-expanded', false); });
    col.classList.toggle('open', open); b.setAttribute('aria-expanded', open);
  }));
  $$('#menu .reveal-m').forEach((el, i) => el.style.transitionDelay = (0.12 + i * 0.05) + 's');

  /* reveal při scrollu */
  const io = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } }), { rootMargin: '0px 0px -8% 0px' });
  $$('.rv,.img-rv').forEach(el => io.observe(el));

  /* počítadla */
  const cio = new IntersectionObserver(es => es.forEach(e => {
    if (!e.isIntersecting) return; cio.unobserve(e.target);
    const el = e.target, end = +el.dataset.count, suf = el.dataset.suffix || '';
    if (reduce) { el.textContent = end + suf; return; }
    const t0 = performance.now(), dur = 1600;
    (function tick(t) { const p = Math.min(1, (t - t0) / dur), k = 1 - Math.pow(1 - p, 3); el.textContent = Math.round(end * k) + suf; if (p < 1) requestAnimationFrame(tick); })(t0);
  }), { threshold: .4 });
  $$('[data-count]').forEach(el => cio.observe(el));

  /* parallax obrázků + rotace velkého ozubeného kola podle scrollu */
  /* kolo: kde prohlížeč umí animaci řízenou scrollem (CSS animation-timeline), otáčí ho sám mimo hlavní vlákno; jinak JS níže */
  const pars = $$('[data-par]').map(el => ({ el, box: el.parentElement, k: -(+el.dataset.par || 7) }));
  const gears = (window.CSS && CSS.supports('animation-timeline: --a')) ? [] : $$('.big-gear').map(el => ({ el, box: el.parentElement }));
  const items = [...pars, ...gears];
  if (!reduce && items.length) {
    // počítat jen prvky, které jsou zrovna na obrazovce
    const live = new Set();
    const vio = new IntersectionObserver(es => { es.forEach(e => e.isIntersecting ? live.add(e.target) : live.delete(e.target)); request(); }, { rootMargin: '10% 0px' });
    items.forEach(it => vio.observe(it.box));
    let ticking = false;
    const run = () => {
      ticking = false; const vh = innerHeight;
      const act = items.filter(it => live.has(it.box));
      const rs = act.map(it => it.box.getBoundingClientRect()); // nejdřív všechno přečíst, pak zapsat (bez opakovaného přepočtu layoutu)
      act.forEach((it, i) => {
        const r = rs[i];
        if (it.k) { const p = Math.max(-1, Math.min(1, (r.top + r.height / 2 - vh / 2) / vh)); it.el.style.transform = `translate3d(0,${(p * it.k).toFixed(2)}%,0) scale(1.18)`; }
        else it.el.style.transform = `rotate(${(Math.max(0, Math.min(1, (vh - r.top) / (vh + r.height))) * 300).toFixed(1)}deg)`;
      });
    };
    const request = () => { if (!ticking) { ticking = true; requestAnimationFrame(run); } };
    addEventListener('scroll', request, { passive: true }); addEventListener('resize', request);
  }

  /* logo: po najetí myší kolo protočit znovu */
  $$('.brand').forEach(b => b.addEventListener('mouseenter', () => {
    const g = b.querySelector('.gear'); if (!g) return;
    g.style.animation = 'none'; void g.getBBox(); g.style.animation = 'gearHover .9s cubic-bezier(.2,.7,.1,1)';
  }));

  /* před / po slider */
  $$('.ba').forEach(ba => {
    const inp = ba.querySelector('input');
    const set = v => ba.style.setProperty('--x', v + '%');
    inp.addEventListener('input', () => set(inp.value));
    // krátká ukázka pohybu, když se slider poprvé objeví
    const o = new IntersectionObserver(([e]) => {
      if (!e.isIntersecting || reduce) return; o.disconnect();
      const t0 = performance.now();
      (function a(t) { const p = Math.min(1, (t - t0) / 1800); const v = 50 + Math.sin(p * Math.PI * 2) * 22 * (1 - p); set(v); inp.value = v; if (p < 1) requestAnimationFrame(a); })(t0);
    }, { threshold: .5 });
    o.observe(ba);
  });

  /* poptávkový formulář
     Odeslání: když je v <form data-endpoint="..."> vyplněná adresa (např. serverless funkce pro e-mail + Telegram),
     pošle se JSON přes fetch. Bez ní se otevře e-mailový klient s předvyplněnou zprávou. */
  $$('form.inq').forEach(form => {
    const msg = form.querySelector('.form-msg'), sub = form.querySelector('[type=submit]');
    const preset = new URLSearchParams(location.search).get('sluzba');
    if (preset && form.sluzba) form.sluzba.value = preset;
    function check(f) {
      const wrap = f.closest('.fld') || f.closest('.consent'); if (!wrap) return true;
      let ok = f.checkValidity();
      if (ok && f.name === 'telefon') ok = f.value.replace(/\D/g, '').length >= 9;
      wrap.classList.toggle('bad', !ok); return ok;
    }
    form.addEventListener('input', e => { if (e.target.closest('.bad')) check(e.target); });
    form.addEventListener('submit', async e => {
      e.preventDefault();
      if (form.web && form.web.value) return; // honeypot proti robotům
      const fields = $$('input[required],select[required],textarea[required]', form);
      const bad = fields.filter(f => !check(f));
      if (bad.length) { bad[0].focus(); return; }
      const data = Object.fromEntries(new FormData(form)); delete data.web;
      data.stranka = location.pathname; data.cas = new Date().toISOString();
      sub.disabled = true; msg.className = 'form-msg';
      const ep = form.dataset.endpoint;
      try {
        if (ep) {
          const r = await fetch(ep, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) });
          if (!r.ok) throw new Error(r.status);
          msg.textContent = 'Děkujeme, poptávku jsme přijali. Ozveme se vám obvykle do 24 hodin, v případě havárie volejte +420 731 291 205.';
          msg.className = 'form-msg ok'; form.reset();
        } else {
          // bez serverového endpointu: otevře e-mail s předvyplněnou poptávkou – odeslání musí dokončit návštěvník
          const body = Object.entries(data).map(([k, v]) => `${k}: ${v}`).join('\n');
          location.href = `mailto:${form.dataset.mail}?subject=${encodeURIComponent('Poptávka z webu – ' + (data.sluzba || 'HallPro'))}&body=${encodeURIComponent(body)}`;
          msg.textContent = `Otevřeli jsme vám e-mail s předvyplněnou poptávkou. Dokončete prosím odeslání ve svém e-mailu, nebo nám napište přímo na ${form.dataset.mail} či zavolejte +420 731 291 205.`;
          msg.className = 'form-msg ok';
        }
      } catch (err) {
        msg.textContent = 'Odeslání se nepovedlo. Zkuste to prosím znovu, nebo nám zavolejte na +420 731 291 205.';
        msg.className = 'form-msg ko';
      } finally { sub.disabled = false; }
    });
  });

  /* karusely: ukazatel pozice pod pásem (jen na telefonu, CSS ho jinde schová) */
  $$('[data-carousel]').forEach(car => {
    const bar = document.createElement('div'); bar.className = 'car-bar'; bar.innerHTML = '<i></i>'; car.after(bar);
    const i = bar.firstChild;
    const upd = () => { const max = car.scrollWidth - car.clientWidth, w = car.clientWidth / car.scrollWidth * 100;
      i.style.setProperty('--w', w + '%'); i.style.setProperty('--x', (max > 0 ? car.scrollLeft / max * (100 / w - 1) * 100 : 0) + '%'); };
    car.addEventListener('scroll', upd, { passive: true }); addEventListener('resize', upd); upd();
  });

  $$('[data-year]').forEach(el => el.textContent = new Date().getFullYear());
})();
