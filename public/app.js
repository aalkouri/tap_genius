(() => {
  const app = document.getElementById('app');
  let ws, S = null, err = '', timerId = null, standKey = null, anim = null;

  function connect(then) {
    if (ws && ws.readyState === 1) return then();
    ws = new WebSocket((location.protocol === 'https:' ? 'wss://' : 'ws://') + location.host);
    ws.onopen = then;
    ws.onmessage = (e) => {
      const m = JSON.parse(e.data);
      if (m.type === 'error') { err = m.message; Sfx.play('wrong'); } else { const prev = S; S = m; err = ''; sounds(prev, S); }
      render();
    };
    ws.onclose = () => { err = 'Disconnected. Reload to rejoin.'; render(); };
  }
  // sound effects for state changes (the standings screen plays its own while animating)
  function sounds(prev, cur) {
    const key = (x) => x.state + ':' + (x.question ? x.question.index : x.round ? x.round.index : '');
    if (!prev || key(prev) !== key(cur)) {
      if (cur.state === 'question') Sfx.play(prev && prev.state === 'lobby' ? 'start' : 'question');
      else if (cur.state === 'reveal') Sfx.play(cur.myChoice !== null && cur.myChoice === cur.correct ? 'correct' : 'wrong');
      else if (cur.state === 'done') Sfx.play(cur.players[0] && cur.players[0].name === cur.you.name && cur.players[0].score > 0 ? 'win' : 'done');
    } else if (cur.state === 'lobby' && prev.players.length < cur.players.length) Sfx.play('join');
  }
  const send = (o) => ws && ws.readyState === 1 && ws.send(JSON.stringify(o));
  const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;' }[c]));
  const board = (players) => `<ol>${players.map((p) => `<li>${esc(p.name)}<span>${p.score}</span></li>`).join('')}</ol>`;

  function stopAnim() { if (anim) { anim.stop(); anim = null; } }

  // Between-round screen: rows start in last round's order with last round's scores, the scores count up,
  // then rows glide to their new positions; rank numbers flip up (moved up) or down (moved down).
  function renderStandings() {
    const ROW = 60, rows = S.standings;
    app.innerHTML = `<h1>⚡ Tap Genius</h1>
      <div class="muted">Round ${S.round.index + 1} / ${S.round.total}</div>
      <h2 class="st-title">${S.isLast ? '🏁 Final standings' : '📊 Standings'}</h2>
      <div class="board" style="height:${rows.length * ROW}px">${rows.map((r) => `
        <div class="srow ${r.you ? 'me' : ''}" data-name="${esc(r.name)}" style="transform:translateY(${r.from * ROW}px)">
          <div class="rk"><span class="rkn">${r.from + 1}</span></div>
          <div class="nm">${esc(r.name)}${r.you ? ' <small>(you)</small>' : ''}</div>
          <div class="pts"><span class="sc">${r.prev}</span>${r.gained > 0 ? `<span class="gain">+${r.gained}</span>` : ''}</div>
        </div>`).join('')}</div>
      ${S.isHost ? `<button id="next">${S.isLast ? 'Final results' : 'Continue'}</button>` : '<p class="muted">Next round starting soon…</p>'}`;
    const next = document.getElementById('next'); if (next) next.onclick = () => send({ action: 'next' });

    const els = [...app.querySelectorAll('.srow')], timers = []; let raf = 0, stopped = false;
    const at = (ms, fn) => timers.push(setTimeout(() => { if (!stopped) fn(); }, ms));
    const COUNT_AT = 800, COUNT_MS = 2200;
    // 1) count every score up from its previous value
    at(COUNT_AT, () => {
      els.forEach((el) => { const g = el.querySelector('.gain'); if (g) g.classList.add('go'); });
      const t0 = performance.now(); let lastStep = -1;
      const step = (now) => {
        if (stopped) return;
        const p = Math.min(1, (now - t0) / COUNT_MS), e = 1 - Math.pow(1 - p, 3);
        els.forEach((el, i) => { const r = rows[i]; el.querySelector('.sc').textContent = Math.round(r.prev + (r.score - r.prev) * e); });
        const st = Math.floor(p * 24); if (st !== lastStep && p < 1 && rows.some((r) => r.gained > 0)) { lastStep = st; Sfx.play('count', p); }
        if (p < 1) raf = requestAnimationFrame(step);
      };
      raf = requestAnimationFrame(step);
    });
    // 2) glide to the new order; flip the rank text up or down
    at(COUNT_AT + COUNT_MS + 500, () => {
      let up = false, down = false;
      els.forEach((el, i) => {
        const r = rows[i], rk = el.querySelector('.rkn');
        el.style.transform = `translateY(${r.to * ROW}px)`;
        if (r.to === r.from) return;
        const dir = r.to < r.from ? 'up' : 'down'; (dir === 'up' ? (up = true) : (down = true));
        el.classList.add('moved-' + dir); el.style.zIndex = dir === 'up' ? 3 : 1;
        rk.classList.remove('flip-up', 'flip-down'); void rk.offsetWidth;
        rk.textContent = r.to + 1; rk.classList.add('flip-' + dir);
        const a = document.createElement('span'); a.className = 'arrow ' + dir; a.textContent = dir === 'up' ? '▲' : '▼'; el.querySelector('.rk').appendChild(a);
      });
      if (up) Sfx.play('up'); if (down) setTimeout(() => Sfx.play('down'), up ? 140 : 0);
      if (!up && !down) Sfx.play('whoosh');
      els.forEach((el, i) => { if (rows[i].to === 0) el.classList.add('leader'); });
    });
    anim = { stop() { stopped = true; cancelAnimationFrame(raf); timers.forEach(clearTimeout); } };
  }

  function render() {
    clearInterval(timerId);
    if (S && S.state === 'standings') {                 // animate once per round; ignore re-broadcasts (e.g. someone leaves)
      const key = S.code + ':' + S.round.index;
      if (key === standKey) return;
      standKey = key; stopAnim(); return renderStandings();
    }
    standKey = null; stopAnim();
    let h = '<h1>⚡ Tap Genius</h1>';
    if (!S) {
      h += `<div class="card">
        <input id="name" placeholder="Your name" maxlength="20">
        <input id="code" placeholder="Room code (to join)" maxlength="4" style="text-transform:uppercase">
        <button id="join">Join game</button>
        <button id="create" class="secondary">Host a new game</button>
        <div class="err">${esc(err)}</div></div>`;
      app.innerHTML = h;
      const val = (id) => document.getElementById(id).value;
      document.getElementById('join').onclick = () => connect(() => send({ action: 'join', name: val('name'), code: val('code') }));
      document.getElementById('create').onclick = () => connect(() => send({ action: 'create', name: val('name') }));
      return;
    }
    if (S.state === 'lobby') {
      const cfg = S.config, cat = S.catalog;
      const band = cat.bands.find((b) => b.id === cfg.band);
      const count = (c) => c.counts[cfg.band];
      let picker;
      if (S.isHost) {
        picker = `<div class="card"><b>Age range</b>
          <div class="chips">${cat.bands.map((b) => `<button class="chip ${b.id === cfg.band ? 'on' : ''}" data-band="${b.id}">${esc(b.label)}</button>`).join('')}</div>
          <b>Categories</b> <span class="muted">(${cfg.cats.length} picked)</span>
          <div class="chips">${cat.cats.map((c) => `<button class="chip ${cfg.cats.includes(c.id) ? 'on' : ''}" data-cat="${c.id}" ${count(c) ? '' : 'disabled'}>${c.icon} ${esc(c.name)}</button>`).join('')}</div>
          <div class="chips"><button class="chip small" id="allcats">Select all</button><button class="chip small" id="nocats">Clear</button></div></div>`;
      } else {
        const picked = cat.cats.filter((c) => cfg.cats.includes(c.id));
        picker = `<div class="card"><b>${esc(band.label)}</b><div class="muted">${picked.length ? picked.map((c) => `${c.icon} ${esc(c.name)}`).join(' · ') : 'Host is picking categories…'}</div></div>`;
      }
      h += `<div class="card"><div class="muted">Room code</div><div class="code">${S.code}</div></div>
        ${picker}
        <div class="card"><b>Players (${S.players.length})</b>${board(S.players)}</div>
        ${S.isHost ? `<button id="start" ${cfg.cats.length ? '' : 'disabled'}>Start game</button>${cfg.cats.length ? '' : '<p class="muted">Pick at least one category to start</p>'}` : '<p class="muted">Waiting for host to start…</p>'}`;
    } else if (S.state === 'question' || S.state === 'reveal') {
      const q = S.question, rev = S.state === 'reveal';
      const vis = (kind, val) => kind === 'emoji' ? `<span class="emo">${esc(val)}</span>`
        : kind === 'svg' ? val : `<img src="/img/${esc(val)}" alt="">`;
      const visual = q.visual ? `<div class="qv">${vis(q.visual.t, q.visual.v)}</div>` : '';
      const pics = q.ct !== 'text';
      h += `<div class="muted">Question ${q.index + 1} / ${q.total}</div>
        <div class="timer"><div id="bar"></div></div>
        <div class="card"><h2>${esc(q.text)} ${q.band === '2-5' ? '<button class="say" id="say" title="Read aloud">🔊</button>' : ''}</h2>${visual}</div>
        <div class="choices">${q.choices.map((c, i) => {
          const cls = ['choice', pics ? 'pic' : '', S.myChoice === i ? 'picked' : '', rev && S.correct === i ? 'right' : '', rev && S.correct !== i ? 'dim' : ''].join(' ');
          return `<button class="${cls}" data-i="${i}" ${rev || S.myChoice !== null ? 'disabled' : ''}>${pics ? vis(q.ct, c) : esc(c)}</button>`;
        }).join('')}</div>`;
      if (rev) {
        h += `<div class="card"><b>${S.gained > 0 ? `+${S.gained} points!` : 'No points this round'}</b>${board(S.players)}</div>
          ${S.isHost ? '<button id="next">Standings ▶</button>' : '<p class="muted">Waiting for host…</p>'}`;
      } else {
        h += `<p class="muted">${S.myChoice !== null ? 'Locked in! Waiting for others…' : 'Tap your answer!'} (${S.players.filter((p) => p.answered).length}/${S.players.length} answered)</p>`;
      }
    } else if (S.state === 'done') {
      h += `<div class="card"><h2>🏆 Final scores</h2>${board(S.players)}</div>
        ${S.isHost ? '<button id="again">Play again</button>' : ''}`;
    }
    h += `<div class="err">${esc(err)}</div>`;
    app.innerHTML = h;

    document.querySelectorAll('.choice').forEach((b) => (b.onclick = () => send({ action: 'answer', choice: +b.dataset.i })));
    const on = (id, a) => { const el = document.getElementById(id); if (el) el.onclick = () => send({ action: a }); };
    on('start', 'start'); on('next', 'next'); on('again', 'again');
    document.querySelectorAll('[data-band]').forEach((b) => (b.onclick = () => send({ action: 'config', band: b.dataset.band, cats: S.config.cats })));
    document.querySelectorAll('[data-cat]').forEach((b) => (b.onclick = () => {
      const set = new Set(S.config.cats); set.has(b.dataset.cat) ? set.delete(b.dataset.cat) : set.add(b.dataset.cat);
      send({ action: 'config', cats: [...set] });
    }));
    const allc = document.getElementById('allcats'); if (allc) allc.onclick = () => send({ action: 'config', cats: S.catalog.cats.filter((c) => c.counts[S.config.band]).map((c) => c.id) });
    const noc = document.getElementById('nocats'); if (noc) noc.onclick = () => send({ action: 'config', cats: [] });
    const say = document.getElementById('say');
    if (say) say.onclick = () => { try { speechSynthesis.cancel(); speechSynthesis.speak(new SpeechSynthesisUtterance(S.question.text)); } catch (e) { } };

    if (S.state === 'question') {
      const bar = document.getElementById('bar');
      const total = S.question.ms;
      let lastTick = -1;
      timerId = setInterval(() => {
        const left = S.question.endsAt - Date.now();
        bar.style.width = Math.max(0, (left / total) * 100) + '%';
        const sec = Math.ceil(left / 1000);
        if (S.myChoice === null && sec <= 5 && sec > 0 && sec !== lastTick) { lastTick = sec; Sfx.play('tick'); }   // last-5-seconds countdown
      }, 100);
    }
  }
  const mute = document.getElementById('mute');
  const paintMute = () => (mute.textContent = Sfx.muted ? '🔇' : '🔊');
  mute.onclick = () => { Sfx.toggle(); paintMute(); };
  paintMute();
  document.addEventListener('click', (e) => { const b = e.target.closest('button'); if (b && b !== mute && !b.disabled) Sfx.play('tap'); });
  render();
})();
