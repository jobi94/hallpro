/* Hero: statické fotky, které se střídají prolínáním s prostorovým posunem podle hloubkové mapy. Bez WebGL nebo při prefers-reduced-motion zůstane statická fotka. */
(function () {
  const box = document.querySelector('[data-hero3d]');
  if (!box || matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  const slides = JSON.parse(box.dataset.hero3d); // [{img, depth?}]
  const canvas = document.createElement('canvas');
  const gl = canvas.getContext('webgl', { alpha: false, antialias: false, powerPreference: 'low-power' });
  if (!gl) return;

  const vs = 'attribute vec2 p;varying vec2 v;void main(){v=p*.5+.5;v.y=1.-v.y;gl_Position=vec4(p,0,1);}';
  const fs = `precision mediump float;varying vec2 v;
uniform sampler2D t0,t1,d0,d1;uniform vec2 res,s0,s1,m;uniform float pr,tm,h0,h1,sc;
vec2 cover(vec2 uv,vec2 s){float r=res.x/res.y,i=s.x/s.y;vec2 k=r>i?vec2(1.,i/r):vec2(r/i,1.);return (uv-.5)*k+.5;}
float dep(sampler2D d,float has,vec2 uv){return has>.5?texture2D(d,uv).r:smoothstep(.3,1.,uv.y)*.85;}
vec4 shot(sampler2D t,sampler2D d,float has,vec2 s,float z){
  vec2 uv=cover(v,s);
  float dd=dep(d,has,uv);
  uv+=vec2(z*.02*(dd-.35),0.);                // pohyb podle hloubky jen během přechodu mezi snímky
  return texture2D(t,clamp(uv,.001,.999));
}
void main(){
  float n=fract(sin(dot(floor(v*vec2(14.,9.)),vec2(12.9898,78.233)))*43758.5453);
  float w=smoothstep(0.,1.,clamp((pr*1.5-.25-v.x*.5+n*.08),0.,1.));
  vec4 a=shot(t0,d0,h0,s0,pr);
  vec4 b=shot(t1,d1,h1,s1,1.-pr);
  gl_FragColor=mix(a,b,w);
}`;
  function sh(type, src) { const s = gl.createShader(type); gl.shaderSource(s, src); gl.compileShader(s); return s; }
  const prog = gl.createProgram();
  gl.attachShader(prog, sh(gl.VERTEX_SHADER, vs)); gl.attachShader(prog, sh(gl.FRAGMENT_SHADER, fs));
  gl.linkProgram(prog);
  if (!gl.getProgramParameter(prog, gl.LINK_STATUS)) return;
  gl.useProgram(prog);
  const buf = gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER, buf);
  gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 1, -1, -1, 1, 1, 1]), gl.STATIC_DRAW);
  const loc = gl.getAttribLocation(prog, 'p'); gl.enableVertexAttribArray(loc); gl.vertexAttribPointer(loc, 2, gl.FLOAT, false, 0, 0);
  const U = n => gl.getUniformLocation(prog, n);
  ['t0', 't1', 'd0', 'd1'].forEach((n, i) => gl.uniform1i(U(n), i));

  const load = src => new Promise((ok, ko) => { const i = new Image(); i.decoding = 'async'; i.onload = () => ok(i); i.onerror = ko; i.src = src; });
  function tex(img) {
    const t = gl.createTexture(); gl.bindTexture(gl.TEXTURE_2D, t);
    gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL, false);
    gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGB, gl.RGB, gl.UNSIGNED_BYTE, img);
    [gl.TEXTURE_WRAP_S, gl.TEXTURE_WRAP_T].forEach(p => gl.texParameteri(gl.TEXTURE_2D, p, gl.CLAMP_TO_EDGE));
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
    return t;
  }
  const W = innerWidth > 1100 ? 1600 : 960;
  const pick = s => s.img.replace('{w}', Math.min(W, s.max || W));
  const loaded = [];
  async function get(i) {
    if (loaded[i]) return loaded[i];
    const s = slides[i];
    const [im, dm] = await Promise.all([load(pick(s)), s.depth ? load(s.depth) : null]);
    return (loaded[i] = { t: tex(im), d: dm ? tex(dm) : null, size: [im.naturalWidth, im.naturalHeight] });
  }
  const dummy = tex(new ImageData(1, 1));

  let cur = 0, nxt = 0, pr = 0, trans = null, mx = 0, my = 0, tx = 0, ty = 0, visible = true, raf = 0, sc = 0;
  const t0 = performance.now();
  function bind(a, b) {
    gl.activeTexture(gl.TEXTURE0); gl.bindTexture(gl.TEXTURE_2D, a.t);
    gl.activeTexture(gl.TEXTURE1); gl.bindTexture(gl.TEXTURE_2D, b.t);
    gl.activeTexture(gl.TEXTURE2); gl.bindTexture(gl.TEXTURE_2D, a.d || dummy);
    gl.activeTexture(gl.TEXTURE3); gl.bindTexture(gl.TEXTURE_2D, b.d || dummy);
    gl.uniform2fv(U('s0'), a.size); gl.uniform2fv(U('s1'), b.size);
    gl.uniform1f(U('h0'), a.d ? 1 : 0); gl.uniform1f(U('h1'), b.d ? 1 : 0);
  }
  function resize() {
    const dpr = Math.min(devicePixelRatio || 1, 1.5);
    canvas.width = Math.round(box.clientWidth * dpr); canvas.height = Math.round(box.clientHeight * dpr);
    gl.viewport(0, 0, canvas.width, canvas.height); gl.uniform2f(U('res'), canvas.width, canvas.height);
  }
  function frame(now) {
    raf = 0; if (!visible) return;
    mx += (tx - mx) * .06; my += (ty - my) * .06;
    if (trans) { pr = Math.min(1, (now - trans) / 1600); if (pr >= 1) { cur = nxt; pr = 0; trans = null; bind(loaded[cur], loaded[cur]); } }
    gl.uniform1f(U('pr'), trans ? pr : 0);
    gl.uniform1f(U('tm'), (now - t0) / 1000);
    gl.uniform2f(U('m'), mx, my);
    gl.uniform1f(U('sc'), sc);
    gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
    if (trans) raf = requestAnimationFrame(frame);
  }
  const kick = () => { if (!raf && visible) raf = requestAnimationFrame(frame); };

  const dots = [...document.querySelectorAll('.hero-dots button')];
  const caps = [...document.querySelectorAll('[data-hero-cap]')];
  let timer;
  async function go(i) {
    if (trans || i === cur || !loaded[cur]) return;
    await get(i); nxt = i; bind(loaded[cur], loaded[nxt]); trans = performance.now(); kick();
    mark(i); schedule();
  }
  function mark(i) {
    dots.forEach((d, k) => { d.classList.toggle('on', k === i); d.setAttribute('aria-current', k === i); });
    caps.forEach((c, k) => c.hidden = k !== i);
  }
  function schedule() { clearTimeout(timer); if (slides.length > 1) timer = setTimeout(() => go((nxt + 1) % slides.length), 7000); }
  dots.forEach((d, i) => d.addEventListener('click', () => go(i)));

  addEventListener('resize', () => { resize(); kick(); });
  new IntersectionObserver(([en]) => { visible = en.isIntersecting && !document.hidden; kick(); }).observe(box);
  document.addEventListener('visibilitychange', () => { visible = !document.hidden; kick(); });

  get(0).then(a => {
    box.appendChild(canvas); resize(); bind(a, a); kick();
    requestAnimationFrame(() => box.classList.add('gl'));
    mark(0); schedule();
    slides.forEach((_, i) => i && setTimeout(() => get(i), 1200 * i)); // ostatní snímky dotáhnout potichu
  }).catch(() => {});
})();
