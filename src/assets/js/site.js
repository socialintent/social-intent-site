// Social Intent – small helpers, no framework.
(function () {
  document.documentElement.classList.add('js');
  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // Mobile navigation
  var toggle = document.querySelector('.nav-toggle');
  var nav = document.getElementById('site-nav');
  if (toggle && nav) {
    toggle.addEventListener('click', function () {
      var open = toggle.getAttribute('aria-expanded') === 'true';
      toggle.setAttribute('aria-expanded', String(!open));
      nav.classList.toggle('is-open', !open);
    });
  }

  // Contact form: on Netlify the form posts for real. In a preview, show the thank-you panel instead.
  var form = document.querySelector('form[data-netlify]');
  if (form) {
    var isPreview = /claude\.ai|claudeusercontent|localhost|127\.0\.0\.1/.test(location.hostname) || location.protocol === 'file:';
    form.addEventListener('submit', function (e) {
      if (!isPreview) return;
      e.preventDefault();
      var panel = document.getElementById('form-preview-note');
      if (panel) { panel.hidden = false; panel.focus(); }
    });
  }

  // Self-hosted video: show the sound button only once a file has actually loaded; restart with sound on click.
  document.querySelectorAll('.video').forEach(function (fig) {
    var v = fig.querySelector('video'), btn = fig.querySelector('[data-video-sound]');
    if (!v || !btn) return;
    v.addEventListener('loadeddata', function () { if (v.videoWidth > 0) btn.hidden = false; });
    v.addEventListener('error', function () { btn.hidden = true; fig.classList.add('video-missing'); }, true);
    btn.addEventListener('click', function () {
      v.muted = false; v.loop = false; v.controls = true; v.currentTime = 0; v.play().catch(function () {});
      btn.hidden = true;
      v.addEventListener('ended', function () { v.muted = true; v.loop = true; v.controls = false; btn.hidden = false; v.play().catch(function () {}); }, { once: true });
    });
  });

  // Copy buttons
  document.querySelectorAll('[data-copy]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var text = btn.getAttribute('data-copy');
      var done = function () { btn.textContent = 'Copied'; setTimeout(function () { btn.textContent = 'Copy'; }, 1800); };
      var fallback = function () { try { window.getSelection().selectAllChildren(btn.previousElementSibling); } catch (e) {} };
      if (navigator.clipboard && navigator.clipboard.writeText) { navigator.clipboard.writeText(text).then(done).catch(fallback); } else { fallback(); }
    });
  });

  // Client logo strip: if a logo file is missing, drop its tile rather than leave an empty one.
  document.querySelectorAll('.marquee li img').forEach(function (img) {
    var drop = function () { img.parentElement.classList.add('is-missing'); };
    img.addEventListener('error', drop);
    if (img.complete && img.naturalWidth === 0 && img.src) { img.src = img.src; }
  });

  // Hero: a field of yellow dots that drifts in and settles into the three rings of the logo.
  // One dot per "person or data point"; the shape only exists when they're all there.
  // On small screens the canvas is hidden by CSS and static dotted SVG rings take its place.
  var canvas = document.getElementById('hero-canvas');
  if (!canvas || !canvas.getContext) return;
  var ctx = canvas.getContext('2d');
  var dpr = Math.min(window.devicePixelRatio || 1, 2);
  var W = 0, H = 0, dots = [], mouse = { x: -1e4, y: -1e4 }, t0 = performance.now(), raf, running = false;

  function visible() { return canvas.offsetParent !== null && getComputedStyle(canvas).display !== 'none'; }

  function layout() {
    if (!visible()) { W = H = 0; return; }
    var r = canvas.getBoundingClientRect();
    if (r.width < 2 || r.height < 2) { W = H = 0; return; }
    W = r.width; H = r.height;
    var bw = Math.round(W * dpr), bh = Math.round(H * dpr);
    if (canvas.width !== bw || canvas.height !== bh) { canvas.width = bw; canvas.height = bh; }
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    // Ring geometry: big ring plus two small ones, sitting right of centre
    var wide = W > 860;
    var R = Math.min(W, H) * (wide ? 0.25 : 0.2);
    var cx = wide ? W * 0.74 : W * 0.5;
    var cy = wide ? H * 0.40 : H - R * 1.1 - 24;
    var rings = [
      { x: cx - R * 0.35, y: cy, r: R, n: wide ? 150 : 84 },
      { x: cx + R * 0.75, y: cy - R * 0.72, r: R * 0.42, n: wide ? 50 : 30 },
      { x: cx + R * 0.75, y: cy + R * 0.72, r: R * 0.42, n: wide ? 50 : 30 }
    ];
    var targets = [];
    rings.forEach(function (ring) {
      for (var i = 0; i < ring.n; i++) {
        var a = (i / ring.n) * Math.PI * 2;
        targets.push({ x: ring.x + Math.cos(a) * ring.r, y: ring.y + Math.sin(a) * ring.r, big: ring.r === R });
      }
    });
    if (!dots.length) {
      dots = targets.map(function (t, i) {
        return { x: (wide ? W * 0.42 : 0) + Math.random() * (wide ? W * 0.58 : W), y: Math.random() * H, vx: 0, vy: 0, tx: t.x, ty: t.y, r: wide ? (t.big ? 3.2 : 2.6) : (t.big ? 2.4 : 2), seed: Math.random() * 1000, delay: Math.random() * 1400 };
      });
    } else {
      dots.forEach(function (d, i) { var t = targets[i % targets.length]; d.tx = t.x; d.ty = t.y; });
    }
  }

  function frame(now) {
    if (!W || !H) { running = false; return; }
    var elapsed = now - t0;
    ctx.clearRect(0, 0, W, H);
    // faint connecting field behind the rings
    ctx.fillStyle = '#FEDB00';
    for (var i = 0; i < dots.length; i++) {
      var d = dots[i];
      if (reduceMotion) { d.x = d.tx; d.y = d.ty; }
      else {
        var k = elapsed > d.delay ? 0.045 : 0.004;
        var wob = 2.2;
        var tx = d.tx + Math.sin(now / 1400 + d.seed) * wob, ty = d.ty + Math.cos(now / 1700 + d.seed) * wob;
        var dx = mouse.x - d.x, dy = mouse.y - d.y, dist2 = dx * dx + dy * dy;
        if (dist2 < 120 * 120) { var f = (120 - Math.sqrt(dist2)) / 120; tx -= dx * f * 0.9; ty -= dy * f * 0.9; }
        d.vx += (tx - d.x) * k; d.vy += (ty - d.y) * k;
        d.vx *= 0.84; d.vy *= 0.84;
        d.x += d.vx; d.y += d.vy;
      }
      ctx.beginPath(); ctx.arc(d.x, d.y, d.r, 0, Math.PI * 2); ctx.fill();
    }
    if (!reduceMotion) raf = requestAnimationFrame(frame);
  }

  // Start (or restart) drawing whenever the canvas is visible and has a size; stop when it isn't.
  function start() {
    layout();
    if (!W || !H) { if (running) { cancelAnimationFrame(raf); running = false; } return; }
    if (reduceMotion) { frame(performance.now()); return; }
    if (!running) { running = true; raf = requestAnimationFrame(frame); }
  }
  var pending;
  function queueLayout() { cancelAnimationFrame(pending); pending = requestAnimationFrame(start); }

  start();
  // Re-measure when the hero changes size for any reason: viewport resize, orientation, the
  // address bar collapsing, web fonts arriving and reflowing the headline.
  if ('ResizeObserver' in window) { new ResizeObserver(queueLayout).observe(canvas.parentElement); }
  window.addEventListener('resize', queueLayout);
  window.addEventListener('orientationchange', queueLayout);
  if (document.fonts && document.fonts.ready) { document.fonts.ready.then(queueLayout); }
  window.addEventListener('load', queueLayout);

  canvas.parentElement.addEventListener('pointermove', function (e) { var r = canvas.getBoundingClientRect(); mouse.x = e.clientX - r.left; mouse.y = e.clientY - r.top; });
  canvas.parentElement.addEventListener('pointerleave', function () { mouse.x = -1e4; mouse.y = -1e4; });
  document.addEventListener('visibilitychange', function () {
    if (reduceMotion) return;
    if (document.hidden) { cancelAnimationFrame(raf); running = false; } else { start(); }
  });
})();
