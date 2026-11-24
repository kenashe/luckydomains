/* Lucky Domains interactions. Plain JavaScript, no libraries, no build step.

   1. Shared behaviour: sticky header shadow, mobile menu, Services menu, Escape to close,
      FAQ accordion, reveal on scroll, and the "What is holding you back?" diagnostic.
   2. Homepage presence map, the five-layer progression, and the Digital Presence Check.
   3. Footer year, the contact form (Web3Forms), and the article contents list.

   The site is readable and navigable with JavaScript off. Every animation stops under
   prefers-reduced-motion, pauses on a hidden tab, and has a Pause control where it repeats. */

/* ---------------------------------------------------------------- 1. shared behaviour */
(function () {
  'use strict';
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var header = document.getElementById('site-header');
  function onScroll() { if (header) header.classList.toggle('scrolled', window.scrollY > 8); }
  window.addEventListener('scroll', onScroll, { passive: true }); onScroll();
  var toggle = document.getElementById('nav-toggle');
  function setNav(open, focus) {
    header.classList.toggle('nav-open', open); toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    toggle.setAttribute('aria-label', open ? 'Close menu' : 'Open menu'); if (focus) toggle.focus();
  }
  if (toggle && header) {
    toggle.addEventListener('click', function () { setNav(!header.classList.contains('nav-open')); });
    $$('#nav a').forEach(function (a) { a.addEventListener('click', function () { setNav(false); }); });
  }
  $$('.menu-btn').forEach(function (b) {
    var m = document.getElementById(b.getAttribute('aria-controls'));
    b.addEventListener('click', function (e) { e.stopPropagation(); var o = b.getAttribute('aria-expanded') !== 'true'; b.setAttribute('aria-expanded', o); m.classList.toggle('open', o); });
    document.addEventListener('click', function (e) { if (!b.parentNode.contains(e.target)) { b.setAttribute('aria-expanded', 'false'); m.classList.remove('open'); } });
  });
  document.addEventListener('keydown', function (e) {
    if (e.key !== 'Escape') return;
    var open = $$('.menu-btn[aria-expanded="true"]');
    if (open.length) { open.forEach(function (b) { b.setAttribute('aria-expanded', 'false'); document.getElementById(b.getAttribute('aria-controls')).classList.remove('open'); }); open[0].focus(); return; }
    if (header && header.classList.contains('nav-open')) setNav(false, true);
  });
  $$('.faq-q').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var ex = btn.getAttribute('aria-expanded') === 'true', panel = btn.nextElementSibling;
      btn.setAttribute('aria-expanded', ex ? 'false' : 'true'); if (panel) panel.style.maxHeight = ex ? null : panel.scrollHeight + 'px';
    });
  });
  /* without JavaScript the FAQ answers stay open: the original CSS hides them, so open them here only when JS runs */
  var rv = $$('.reveal');
  if (reduce || !('IntersectionObserver' in window)) rv.forEach(function (r) { r.classList.add('in'); });
  else {
    var io = new IntersectionObserver(function (en) { en.forEach(function (x) { if (x.isIntersecting) { x.target.classList.add('in'); io.unobserve(x.target); } }); }, { rootMargin: '0px 0px -8% 0px' });
    rv.forEach(function (r) { io.observe(r); });
  }
  var out = $('.dg-out');
  if (out) {
    var empty = $('.dg-empty', out), ans = $$('.dg-a', out);
    $$('input[name="stuck"]').forEach(function (r) { r.addEventListener('change', function () { empty.hidden = true; ans.forEach(function (a) { a.classList.toggle('on', a.getAttribute('data-for') === r.value); }); document.dispatchEvent(new CustomEvent('v3:diagnostic', { detail: r.value })); }); });
  }
})();

/* ---------------------------------------------------------------- 2. presence map, progression, Digital Presence Check
   The presence map: six signals start scattered, settle around one identity, and one soft pulse
   at a time travels from a signal to the centre. It pauses on hover, focus, a hidden tab, when
   it is off screen, while a signal is selected, and with the Pause button. Signals can be
   selected by mouse, touch, and keyboard. The diagnostic lights the related signals.
   The Digital Presence Check totals answers in the page. Nothing is stored or sent. */
(function () {
  'use strict';
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var fine = window.matchMedia('(hover: hover) and (pointer: fine)').matches;
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var NS = 'http://www.w3.org/2000/svg';
  var el = function (n, a) { var e = document.createElementNS(NS, n); for (var k in a) e.setAttribute(k, a[k]); return e; };
  var esc = function (s) { var d = document.createElement('div'); d.textContent = s; return d.innerHTML; };

  /* 1. presence map */
  var root = $('[data-map]');
  if (root) (function () {
    var data = JSON.parse($('.pm-data', root).textContent), view = $('.pm-view', root), detail = $('.pm-detail', root), segs = $$('.sg', root), pauseBtn = $('.pm-pause', root);
    var nodes = data.nodes, svg, pulseDot, W, H, G, state = 'recognized', sel = null, timer = 0, turn = 0, touched = false, userPaused = false, hold = false, visible = true, raf = 0;
    /* scattered positions [x, y, tilt] for wide and narrow layouts; each keeps clear of the centre */
    var FRAG = { wide: [[96, 58, -5], [452, 46, 4], [492, 192, -3], [410, 314, 5], [136, 306, -4], [84, 186, 3]],
                 narrow: [[70, 34, -5], [262, 78, 4], [286, 190, -3], [236, 338, 5], [84, 300, -4], [66, 112, 3]] };
    var BROKEN = [[0, 3], [1, 4], [2, 5]];
    function layout() {
      var p = view.clientWidth < 480;
      W = p ? 340 : 560; H = p ? 380 : 360;
      var cx = W / 2, cy = H / 2, rx = p ? 0 : 196, ry = p ? 160 : 132, f = FRAG[p ? 'narrow' : 'wide'];
      nodes.forEach(function (n, i) {
        var a = -Math.PI / 2 + i * 2 * Math.PI / nodes.length, ca = Math.cos(a), sa = Math.sin(a);
        n.w = Math.max(84, n.label.length * 9.2 + 34);
        /* narrow screens: side signals sit against the edges, above and below the centre */
        n.rx = p ? (ca > 0.2 ? W - n.w / 2 - 6 : ca < -0.2 ? n.w / 2 + 6 : cx) : cx + rx * ca;
        n.ry = p ? cy + (Math.abs(ca) < 0.2 ? ry * sa : 92 * (sa > 0 ? 1 : -1)) : cy + ry * sa;
        n.fx = Math.min(Math.max(f[i][0], n.w / 2 + 6), W - n.w / 2 - 6); n.fy = f[i][1]; n.fr = f[i][2];
      });
      G = { p: p, cx: cx, cy: cy };
    }
    function build() {
      layout();
      if (svg) view.removeChild(svg);
      svg = el('svg', { viewBox: '0 0 ' + W + ' ' + H, role: 'group', 'aria-label': 'Presence map: six signals connected to one brand identity. Select a signal for details.' });
      var ge = el('g', {}), gb = el('g', {}), gn = el('g', {});
      nodes.forEach(function (n, i) {
        n.edge = el('line', { 'class': 'edge', x1: G.cx, y1: G.cy, x2: n.rx, y2: n.ry }); ge.appendChild(n.edge);
        var m = nodes[(i + 1) % nodes.length];
        ge.appendChild(el('line', { 'class': 'edge edge-x', x1: n.rx, y1: n.ry, x2: m.rx, y2: m.ry }));
      });
      BROKEN.forEach(function (l) { var a = nodes[l[0]], b = nodes[l[1]], mx = (a.fx + b.fx) / 2, my = (a.fy + b.fy) / 2; gb.appendChild(el('line', { 'class': 'broken', x1: a.fx, y1: a.fy, x2: mx + (a.fx - mx) * 0.45, y2: my + (a.fy - my) * 0.45 })); });
      var core = el('g', { 'class': 'core', transform: 'translate(' + G.cx + ',' + G.cy + ')' });
      core.appendChild(el('circle', { r: 52, 'class': 'core-ring' }));
      core.appendChild(el('circle', { r: 40, fill: '#fff', stroke: '#0C2340', 'stroke-width': 2 }));
      /* the visible pixels of the 128px icon centre at (58.4, 63.9), so the artwork is centred, not its box */
      core.appendChild(el('image', { href: data.icon, x: -21.9, y: -24, width: 48, height: 48 }));
      pulseDot = el('circle', { r: 4.5, 'class': 'pulse' });
      nodes.forEach(function (n) {
        var g = el('g', { 'class': 'nd', tabindex: 0, role: 'button', 'aria-label': n.label + '. ' + n.line, 'aria-pressed': 'false' });
        g.appendChild(el('rect', { 'class': 'nd-b', x: -n.w / 2, y: -19, width: n.w, height: 38, rx: 19 }));
        g.appendChild(el('circle', { 'class': 'nd-d', cx: -n.w / 2 + 16, cy: 0, r: 4.5 }));
        var t = el('text', { x: 8, y: 5, 'text-anchor': 'middle' }); t.textContent = n.label; g.appendChild(t);
        g.addEventListener('click', function () { pick(n.id); });
        g.addEventListener('keydown', function (e) { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); pick(n.id); } });
        n.g = g; gn.appendChild(g);
      });
      svg.appendChild(gb); svg.appendChild(ge); svg.appendChild(pulseDot); svg.appendChild(core); svg.appendChild(gn);
      view.appendChild(svg);
      place(true); paint();
    }
    function place(instant, lean) {
      svg.setAttribute('class', (state === 'recognized' ? 'rec' : 'frag') + (lean ? ' lean' : ''));
      nodes.forEach(function (n) {
        var rec = state === 'recognized', x = (rec ? n.rx : n.fx) + (lean ? n.lx || 0 : 0), y = (rec ? n.ry : n.fy) + (lean ? n.ly || 0 : 0);
        if (instant) n.g.style.transition = 'none';
        n.g.style.transform = 'translate(' + x.toFixed(1) + 'px,' + y.toFixed(1) + 'px)' + (rec ? '' : ' rotate(' + n.fr + 'deg)');
        if (instant) { void n.g.getBoundingClientRect(); n.g.style.transition = ''; }
      });
      segs.forEach(function (s) { s.setAttribute('aria-pressed', s.getAttribute('data-state') === state); });
    }
    function paint() {
      var hot = sel ? sel.ids : null;
      nodes.forEach(function (n) {
        var on = hot && hot.indexOf(n.id) > -1;
        n.g.classList.toggle('hot', !!on); n.g.classList.toggle('cold', !!hot && !on);
        n.g.setAttribute('aria-pressed', !!(sel && sel.kind === 'node' && on));
        n.edge.classList.toggle('hot', !!on); n.edge.classList.toggle('cold', !!hot && !on);
      });
    }
    function show(html) { detail.innerHTML = html; if (!reduce) { detail.classList.remove('swap'); void detail.offsetWidth; detail.classList.add('swap'); } }
    function idle() { show('<p>' + esc(state === 'recognized' ? data.idle : data.fragmented) + '</p>'); }
    function setState(s) { state = s; place(false); if (!sel) idle(); run(); }
    function byId(id) { return nodes.filter(function (n) { return n.id === id; })[0]; }
    function pick(id) {
      touched = true;
      if (sel && sel.kind === 'node' && sel.ids[0] === id) { sel = null; paint(); idle(); run(); return; }
      if (state !== 'recognized') { state = 'recognized'; place(false); }
      var n = byId(id);
      sel = { kind: 'node', ids: [id] }; paint(); run();
      show('<p class="pd-h">' + esc(n.label) + '</p><p>' + esc(n.line) + '</p><ul class="pd-chips" aria-label="Includes">' + n.details.map(function (d) { return '<li>' + esc(d) + '</li>'; }).join('') +
           '</ul><a class="pd-link" href="' + n.href + '">' + esc(n.svcName) + '</a>');
    }
    function problem(pid) {
      var ids = data.problems[pid]; if (!ids) return;
      touched = true;
      if (state !== 'recognized') { state = 'recognized'; place(false); }
      sel = { kind: 'problem', ids: ids }; paint(); run();
      show('<p class="pd-h">' + esc(data.labels[pid]) + '</p><p>Signals involved: ' + esc(ids.map(function (i) { return byId(i).label; }).join(', ')) + '. Select any one for details.</p>');
    }
    /* one soft pulse at a time, from a signal to the centre */
    function pulse() {
      var n = nodes[turn % nodes.length]; turn++;
      if (!pulseDot.animate) return;
      n.edge.classList.add('hot'); setTimeout(function () { if (!sel) n.edge.classList.remove('hot'); }, 1500);
      pulseDot.animate([{ transform: 'translate(' + n.rx + 'px,' + n.ry + 'px)', opacity: 0 }, { opacity: 1, offset: 0.2 }, { opacity: 1, offset: 0.75 },
                        { transform: 'translate(' + G.cx + 'px,' + G.cy + 'px)', opacity: 0 }], { duration: 1500, easing: 'ease-in-out' });
    }
    function run() {
      clearInterval(timer);
      if (reduce || userPaused || hold || !visible || document.hidden || state !== 'recognized' || sel) return;
      timer = setInterval(pulse, 2800);
    }
    segs.forEach(function (s) { s.addEventListener('click', function () { touched = true; sel = null; paint(); setState(s.getAttribute('data-state')); }); });
    pauseBtn.addEventListener('click', function () {
      userPaused = !userPaused; pauseBtn.setAttribute('aria-pressed', userPaused);
      pauseBtn.setAttribute('aria-label', userPaused ? 'Play map animation' : 'Pause map animation'); run();
    });
    root.addEventListener('pointerenter', function () { hold = true; run(); });
    root.addEventListener('pointerleave', function () { hold = false; run(); });
    root.addEventListener('focusin', function () { hold = true; run(); });
    root.addEventListener('focusout', function () { hold = false; run(); });
    document.addEventListener('visibilitychange', run);
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && sel && root.contains(document.activeElement)) { sel = null; paint(); idle(); } });
    /* signals lean a few pixels toward a mouse pointer; the edges end under each label, so they stay attached */
    if (fine && !reduce) {
      view.addEventListener('pointermove', function (e) {
        if (raf) return;
        raf = requestAnimationFrame(function () {
          raf = 0; var r = view.getBoundingClientRect(), px = (e.clientX - r.left) / r.width * W, py = (e.clientY - r.top) / r.height * H;
          nodes.forEach(function (n) { var x = state === 'recognized' ? n.rx : n.fx, y = state === 'recognized' ? n.ry : n.fy; n.lx = Math.max(-5, Math.min(5, (px - x) / 40)); n.ly = Math.max(-5, Math.min(5, (py - y) / 40)); });
          place(false, true);
        });
      });
      view.addEventListener('pointerleave', function () { nodes.forEach(function (n) { n.lx = n.ly = 0; }); place(false, true); });
    }
    build();
    var lastP = G.p;
    window.addEventListener('resize', function () { var p = view.clientWidth < 480; if (p !== lastP) { lastP = p; build(); } });
    if ('IntersectionObserver' in window) new IntersectionObserver(function (en) { visible = en[0].isIntersecting; run(); }, { threshold: 0.25 }).observe(view);
    if (reduce) { state = 'recognized'; place(true); }
    else {
      state = 'fragmented'; place(true); idle();
      setTimeout(function () { if (!touched) setState('recognized'); }, 900);
    }
    document.addEventListener('v3:diagnostic', function (e) { problem(e.detail); });
  })();

  /* 3. five-layer progression: draw the line once */
  var prog = $('[data-prog]');
  if (prog) {
    if (reduce || !('IntersectionObserver' in window)) prog.classList.add('on');
    else { var po = new IntersectionObserver(function (en) { if (en[0].isIntersecting) { prog.classList.add('on'); po.disconnect(); } }, { threshold: 0.2 }); po.observe(prog); }
  }

  /* Digital Presence Check: totals answers in the page. Nothing is stored or sent. */
  var dpc = $('[data-dpc]');
  if (dpc) (function () {
    var cfg = JSON.parse($('.dpc-data').textContent), qs = $$('.dq', dpc), rows = $$('.dpc-areas li', dpc), sum = $('[data-sum]', dpc), next = $('[data-next]', dpc), nextT = $('[data-next-t]', dpc);
    function update() {
      var by = {}, answered = 0;
      qs.forEach(function (q) { var a = q.getAttribute('data-area'), c = $('input:checked', q); (by[a] = by[a] || []).push(c ? c.value : null); if (c) answered++; });
      var look = 0, checkN = 0, first = null;
      rows.forEach(function (li) {
        var v = by[li.getAttribute('data-area')] || [], st = 'none';
        if (v.indexOf('no') > -1) st = 'no'; else if (v.indexOf('unsure') > -1) st = 'unsure';
        else if (v.length && v.every(function (x) { return x === 'yes'; })) st = 'yes'; else if (v.indexOf('yes') > -1) st = 'partial';
        li.setAttribute('data-state', st === 'partial' ? 'yes' : st); $('[data-status]', li).textContent = cfg.status[st];
        if (st === 'no') look++; if (st === 'unsure') checkN++;
        if (!first && (st === 'no' || st === 'unsure')) first = li;
      });
      var t = answered + ' of ' + cfg.total + ' answered.';
      if (!answered) t = 'Answer the questions to see possible areas to investigate.';
      else if (look || checkN) t += ' ' + (look ? look + (look === 1 ? ' area is' : ' areas are') + ' worth a closer look' : '') + (look && checkN ? ', and ' : '') + (checkN ? checkN + (checkN === 1 ? ' area is' : ' areas are') + ' worth checking' : '') + '.';
      else if (answered === cfg.total) t += ' ' + cfg.allYes;
      else t += ' Nothing flagged so far.';
      sum.textContent = t;
      next.hidden = !first;
      if (first) nextT.textContent = $('.da-b a', first).textContent.trim();
    }
    dpc.addEventListener('change', update);
    $('[data-reset]', dpc).addEventListener('click', function () { $$('input:checked', dpc).forEach(function (i) { i.checked = false; }); update(); var f = $('input', dpc); if (f) f.focus(); });
    update();
  })();
})();

/* ---------------------------------------------------------------- 3. footer year, contact form, article contents list */
(function () {
  "use strict";

  // Footer year
  var yr = document.getElementById("year");
  if (yr) yr.textContent = new Date().getFullYear();

  // Contact form (Web3Forms). Replace WEB3FORMS_ACCESS_KEY with your real key.
  var form = document.getElementById("contact-form");
  if (form) {
    var status = document.getElementById("form-status");
    var ACCESS_KEY = form.getAttribute("data-access-key") || "";
    function setStatus(msg, kind) {
      if (!status) return;
      status.textContent = msg;
      status.className = "form-status show " + kind;
    }
    // Prefill the "I need help with" select from ?need=website|seo|ai|entity|buying|selling.
    var needSel = form.querySelector("#need");
    var needParam = (new URLSearchParams(window.location.search).get("need") || "").toLowerCase();
    if (needSel && needParam) {
      var map = {"website": "Website design or development", "seo": "SEO and search visibility", "ai": "AI visibility and brand authority", "entity": "Entity SEO and digital identity", "buying": "Buying a domain", "selling": "Selling a domain"};
      if (map[needParam]) needSel.value = map[needParam];
    }
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      // Qualifying fields: the form uses novalidate, so check required fields here.
      var missing = [];
      form.querySelectorAll("[required]").forEach(function (el) {
        if (!String(el.value || "").trim()) {
          missing.push(el);
        }
      });
      if (missing.length) {
        setStatus("Please fill in the highlighted fields so Ken can prepare for the call.", "err");
        missing[0].focus();
        return;
      }
      // If the access key hasn't been configured yet, guide instead of failing silently.
      if (!ACCESS_KEY || ACCESS_KEY.indexOf("YOUR_") === 0) {
        setStatus("Form not yet connected. Add your free Web3Forms access key to enable submissions, or email us directly at info@luckydomains.io.", "err");
        return;
      }
      var btn = form.querySelector("button[type=submit]");
      var original = btn ? btn.textContent : "";
      if (btn) { btn.disabled = true; btn.textContent = "Sending…"; }
      var data = new FormData(form);
      data.append("access_key", ACCESS_KEY);
      // Put the need and target in the email subject so inquiries are triaged at a glance.
      var need = data.get("need") || "Inquiry";
      var target = data.get("target") || "";
      data.set("subject", "luckydomains.io: " + need + (target ? " / " + target : ""));
      fetch("https://api.web3forms.com/submit", {
        method: "POST",
        body: data,
        headers: { Accept: "application/json" }
      })
        .then(function (r) { return r.json(); })
        .then(function (json) {
          if (json.success) {
            form.reset();
            setStatus("Thanks! Your message is on its way. Ken will reply within one business day.", "ok");
          } else {
            setStatus("Something went wrong. Please email info@luckydomains.io and we'll jump on it.", "err");
          }
        })
        .catch(function () {
          setStatus("Network hiccup. Please email info@luckydomains.io directly.", "err");
        })
        .finally(function () {
          if (btn) { btn.disabled = false; btn.textContent = original; }
        });
    });
  }

  // Article contents list: mark the section being read. The list works as plain links without this.
  var toc = document.querySelector(".art-toc");
  if (toc && "IntersectionObserver" in window) {
    var links = {};
    toc.querySelectorAll("a").forEach(function (a) { links[a.getAttribute("href").slice(1)] = a; });
    var mark = function (id) {
      Object.keys(links).forEach(function (k) { links[k].removeAttribute("aria-current"); });
      if (links[id]) links[id].setAttribute("aria-current", "true");
    };
    var spy = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) { if (e.isIntersecting) mark(e.target.id); });
    }, { rootMargin: "-12% 0px -72% 0px" });
    Object.keys(links).forEach(function (id) {
      var el = document.getElementById(id);
      if (el) spy.observe(el.tagName === "SECTION" ? (el.querySelector("h2") || el) : el);
    });
  }
})();
