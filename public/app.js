(() => {
  const app = document.getElementById('app');
  let ws, S = null, err = '', timerId = null, standKey = null, anim = null, doneKey = null;
  let screen = 'home', hostName = '', liveKey = null, live = null;   // home | mode (game-type picker) | browse (open games); live = running countdown / mini game
  let games = [];
  // each player's head shot (a small JPEG data URL), taken once and remembered on this device
  let face = null, afterCam = 'home', cam = null;
  try { face = localStorage.getItem('tg_face'); hostName = localStorage.getItem('tg_name') || ''; } catch (e) { }
  const faceImg = (av, cls = '') => `<img class="face ${cls}" src="${av ? `/avatar/${esc(av)}.jpg` : '/img/bulb.png'}" alt="" onerror="this.style.visibility='hidden'">`;                                                    // open games, pushed live by the server while browsing

  function connect(then) {
    if (ws && ws.readyState === 1) return then();
    ws = new WebSocket((location.protocol === 'https:' ? 'wss://' : 'ws://') + location.host);
    ws.onopen = then;
    ws.onmessage = (e) => {
      const m = JSON.parse(e.data);
      if (m.type === 'ev') { if (live && live.onEvent) live.onEvent(m); return; }   // in-game events never re-render
      if (m.type === 'list') { games = m.games; if (!S && screen === 'browse') render(); return; }
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
      else if (cur.state === 'reveal') {
        if (cur.myChoice !== null && cur.myChoice === cur.correct) Sfx.play('correct');
        else { Sfx.play('buzzer'); bigX(cur.myChoice === null ? "Time's up!" : 'Wrong!'); }
      }
    } else if (cur.state === 'lobby' && prev.players.length < cur.players.length) Sfx.play('join');
  }
  // Wrong answer: a big red X slams over the whole screen (taps pass through it), then fades.
  function bigX(label) {
    document.querySelectorAll('.bigx').forEach((e) => e.remove());
    const el = document.createElement('div'); el.className = 'bigx';
    el.innerHTML = `<svg viewBox="0 0 100 100" preserveAspectRatio="none" aria-hidden="true"><line x1="8" y1="8" x2="92" y2="92"/><line x1="92" y1="8" x2="8" y2="92"/></svg><span>${esc(label)}</span>`;
    document.body.appendChild(el);
    app.classList.remove('shake'); void app.offsetWidth; app.classList.add('shake');
    setTimeout(() => el.remove(), 1900);
  }
  const send = (o) => ws && ws.readyState === 1 && ws.send(JSON.stringify(o));
  const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;' }[c]));
  const brand = '<div class="brand"><img src="/img/bulb.png" alt=""><span>Tap Genius</span></div>';
  const hero = '<div class="hero"><img src="/img/logo.jpg" alt="Tap Genius"></div><div class="tagline">Tap fast. Think faster!</div>';
  const board = (players) => `<ol class="plist">${players.map((p) => `<li>${faceImg(p.av)}<span class="pn">${esc(p.name)}</span><span class="ps">${p.score}</span></li>`).join('')}</ol>`;

  // ---- camera: fit your head in the oval, tap, confirm ----
  const OV = { W: 300, H: 400, cx: 150, cy: 150, rx: 78, ry: 100 };     // guide geometry in a 300x400 frame; output keeps the oval's shape
  function stopCam() { if (cam) { cam.getTracks().forEach((t) => t.stop()); cam = null; } }
  // crop the oval's bounding box out of a source (video or image) that is shown "cover"-fitted in the frame
  function cropHead(src, sw, sh, mirror) {
    const scale = Math.max(OV.W / sw, OV.H / sh), dx = (OV.W - sw * scale) / 2, dy = (OV.H - sh * scale) / 2;
    const w = (OV.rx * 2) / scale, h = (OV.ry * 2) / scale, y = (OV.cy - OV.ry - dy) / scale;
    let x = (OV.cx - OV.rx - dx) / scale; if (mirror) x = sw - x - w;
    const c = document.createElement('canvas'); c.width = 156; c.height = 200;
    const g = c.getContext('2d'); if (mirror) { g.translate(c.width, 0); g.scale(-1, 1); }
    g.drawImage(src, x, y, w, h, 0, 0, c.width, c.height);
    return c.toDataURL('image/jpeg', 0.82);
  }
  function renderCamera(shot) {
    const guide = `<svg class="camov" viewBox="0 0 ${OV.W} ${OV.H}" preserveAspectRatio="none" aria-hidden="true">
        <defs><mask id="hole"><rect width="${OV.W}" height="${OV.H}" fill="#fff"/><ellipse cx="${OV.cx}" cy="${OV.cy}" rx="${OV.rx}" ry="${OV.ry}" fill="#000"/></mask></defs>
        <rect width="${OV.W}" height="${OV.H}" fill="rgba(3,20,60,.66)" mask="url(#hole)"/>
        <path d="M150 262 C118 262 104 276 96 286 C60 292 34 318 30 400 L270 400 C266 318 240 292 204 286 C196 276 182 262 150 262 Z" fill="rgba(255,255,255,.16)" stroke="#fff" stroke-width="3" stroke-dasharray="9 7"/>
        <ellipse cx="${OV.cx}" cy="${OV.cy}" rx="${OV.rx}" ry="${OV.ry}" fill="none" stroke="#FFE45A" stroke-width="4"/>
      </svg>`;
    if (shot) {                                            // confirm step
      app.innerHTML = `${brand}<h2 class="st-title">Looking good?</h2>
        <div class="shot"><img class="face huge" src="${shot}" alt="Your picture"></div>
        <button id="use">Use this picture</button><button class="secondary" id="again">Retake</button>`;
      document.getElementById('use').onclick = () => {
        face = shot; try { localStorage.setItem('tg_face', face); } catch (e) { }
        screen = afterCam; render(); if (screen === 'browse') connect(() => send({ action: 'list' }));
      };
      document.getElementById('again').onclick = () => renderCamera();
      return;
    }
    app.innerHTML = `${brand}<h2 class="st-title">Take your picture</h2>
      <div class="cam"><video id="vid" playsinline autoplay muted></video>${guide}<div class="camhint" id="camhint">Fit your head in the oval</div></div>
      <button id="snap" disabled>📸 Take picture</button>
      <label class="filebtn">Use a photo instead<input type="file" id="file" accept="image/*" capture="user" hidden></label>
      <button class="secondary small" id="back">← Back</button>`;
    const vid = document.getElementById('vid'), snap = document.getElementById('snap'), hint = document.getElementById('camhint');
    const fail = () => { hint.textContent = 'Camera not available — tap "Use a photo instead"'; hint.classList.add('warn'); };
    stopCam();
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
      navigator.mediaDevices.getUserMedia({ video: { facingMode: 'user', width: { ideal: 640 }, height: { ideal: 480 } }, audio: false })
        .then((st) => { if (screen !== 'camera') { st.getTracks().forEach((t) => t.stop()); return; } cam = st; vid.srcObject = st; vid.onloadedmetadata = () => { snap.disabled = false; }; })
        .catch(fail);
    } else fail();
    snap.onclick = () => { if (!vid.videoWidth) return; Sfx.play('shutter'); const d = cropHead(vid, vid.videoWidth, vid.videoHeight, true); stopCam(); renderCamera(d); };
    document.getElementById('file').onchange = (e) => {
      const f = e.target.files[0]; if (!f) return;
      const im = new Image(); im.onload = () => { const d = cropHead(im, im.naturalWidth, im.naturalHeight, false); URL.revokeObjectURL(im.src); stopCam(); renderCamera(d); };
      im.src = URL.createObjectURL(f);
    };
    document.getElementById('back').onclick = () => { stopCam(); screen = 'home'; render(); };
  }

  function stopLive() { if (live) { live.stop(); live = null; } }

  // Shared intro for every mini game: big 3, 2, 1, GO! with a voice and a beep on each.
  function renderCountdown() {
    const g = S.mini;
    S.players.forEach((pl) => { if (pl.av) new Image().src = `/avatar/${pl.av}.jpg`; });   // warm the cache before the game starts
    app.innerHTML = `${brand}
      <div class="muted">Game ${g.index + 1} / ${g.total}</div>
      <div class="card cd-card"><div class="cd-icon">${g.icon}</div><h2>${esc(g.name)}</h2><p>${esc(g.how)}</p></div>
      <div class="cd-num" id="cdnum"></div>`;
    const el = document.getElementById('cdnum'), timers = [];
    ['3', '2', '1', 'GO!'].forEach((t, i) => timers.push(setTimeout(() => {
      el.textContent = t; el.className = 'cd-num' + (i === 3 ? ' go' : ''); void el.offsetWidth; el.classList.add('pulse');
      Sfx.say(i === 3 ? 'Go!' : t); Sfx.play(i === 3 ? 'go' : 'beep');
    }, i * (g.ms / 4))));
    live = { stop() { timers.forEach(clearTimeout); try { speechSynthesis.cancel(); } catch (e) { } } };
  }

  // A furry mole drawn in SVG (jagged outline = fur). The player's photo is laid over the face area.
  const furPath = (cx, cy, rx, ry, n) => { let d = ''; for (let i = 0; i < n; i++) { const a = (i / n) * Math.PI * 2, k = i % 2 ? 1.08 : 0.95; d += (i ? 'L' : 'M') + (cx + Math.cos(a) * rx * k).toFixed(1) + ' ' + (cy + Math.sin(a) * ry * k).toFixed(1); } return d + 'Z'; };
  const MOLE_SVG = `<svg class="mfur" viewBox="0 0 100 140" aria-hidden="true">
      <path d="${furPath(50, 106, 41, 42, 44)}" fill="#6b4226"/>
      <ellipse cx="50" cy="112" rx="23" ry="27" fill="#b98a5e"/>
      <circle cx="16" cy="28" r="8" fill="#5a361e"/><circle cx="84" cy="28" r="8" fill="#5a361e"/>
      <circle cx="16" cy="28" r="4" fill="#e9a9a2"/><circle cx="84" cy="28" r="4" fill="#e9a9a2"/>
      <path d="${furPath(50, 42, 37, 43, 40)}" fill="#7a4c2b"/>
      <g fill="#f2b3ac" stroke="#c98a84" stroke-width="1"><ellipse cx="19" cy="95" rx="11" ry="7"/><ellipse cx="81" cy="95" rx="11" ry="7"/></g>
      <g stroke="#fff" stroke-width="2" stroke-linecap="round"><path d="M12 98v5M19 100v5M26 98v5M74 98v5M81 100v5M88 98v5"/></g>
    </svg>`;

  // Whack-a-mole: the server says where each head pops up and who tapped it first; we just draw it.
  function renderPlay() {
    const g = S.mini, me = S.you.name;
    app.innerHTML = `${brand}
      <div class="timer"><div id="bar"></div></div>
      <div class="hud"><span id="myhits">You: 0</span><span id="lead"></span></div>
      <div class="field" id="field">${Array.from({ length: g.cells }, (_, i) => `<div class="hole" data-cell="${i}"><div class="mound"></div><div class="pit"></div><div class="burrow"></div></div>`).join('')}</div>`;
    const field = document.getElementById('field'), bar = document.getElementById('bar');
    const moles = new Map(), hits = {}, t0 = Date.now();
    const barTimer = setInterval(() => { bar.style.width = Math.max(0, 100 - ((Date.now() - t0) / g.ms) * 100) + '%'; }, 100);
    const drop = (id, delay) => { const m = moles.get(id); if (!m) return; moles.delete(id); clearTimeout(m.timer); m.el.classList.remove('up'); setTimeout(() => m.el.remove(), delay); };
    const hud = () => {
      document.getElementById('myhits').textContent = `You: ${hits[me] || 0}`;
      const top = Object.entries(hits).sort((a, b) => b[1] - a[1])[0];
      document.getElementById('lead').textContent = top ? `👑 ${top[0]} ${top[1]}` : '';
    };
    live = {
      onEvent(ev) {
        if (ev.ev === 'spawn') {
          const hole = field.children[ev.cell]; if (!hole) return;
          const el = document.createElement('div'); el.className = 'mole'; el.dataset.id = ev.id;
          el.innerHTML = `${MOLE_SVG}<div class="mface"${ev.av ? ` style="background-image:url(/avatar/${ev.av}.jpg)"` : ''}></div>`;   // a random player's head
          el.addEventListener('pointerdown', (e) => { e.preventDefault(); if (el.classList.contains('tapped')) return; el.classList.add('tapped'); send({ action: 'whack', id: ev.id }); });
          hole.querySelector('.burrow').appendChild(el); void el.offsetWidth; el.classList.add('up');
          moles.set(ev.id, { el, timer: setTimeout(() => drop(ev.id, 180), ev.ttl) });
          Sfx.play('pop');
        } else if (ev.ev === 'hit') {
          hits[ev.by] = (hits[ev.by] || 0) + 1; hud();
          const mine = ev.by === me; Sfx.play(mine ? 'mine' : 'bonk');
          const m = moles.get(ev.id); if (!m) return;
          m.el.classList.add('bonked', mine ? 'mine' : 'theirs');
          const tag = document.createElement('span'); tag.className = 'tag' + (mine ? ' mine' : ''); tag.textContent = mine ? '+1' : ev.by; m.el.closest('.hole').appendChild(tag);
          setTimeout(() => tag.remove(), 600);
          drop(ev.id, 380);
        }
      },
      stop() { clearInterval(barTimer); moles.forEach((m) => clearTimeout(m.timer)); moles.clear(); },
    };
  }

  // ---- finale: the top three walk in (3rd, 2nd, then 1st), hop onto the podium, and the winner cheers ----
  function paintDoneCtl() {
    const c = document.getElementById('donectl'); if (!c) return;
    c.innerHTML = S.isHost ? '<button id="again">Play again</button>' : '<p class="muted">Waiting for the host…</p>';
    const b = document.getElementById('again'); if (b) b.onclick = () => send({ action: 'again' });
  }
  function renderPodium() {
    const top = S.players.slice(0, 3);
    const SHIRT = ['#ffc21a', '#c9d3df', '#d98a4b'], H = [104, 74, 54], X = ['50%', '20%', '80%'], LABEL = ['1st', '2nd', '3rd'];
    const toon = (pl, i) => `<div class="toon" data-i="${i}" style="--shirt:${SHIRT[i]};left:${i === 2 ? 'calc(100% + 50px)' : '-50px'}"><div class="toon-in">
        ${faceImg(pl.av, 'thead')}
        <svg class="tbody" viewBox="0 0 60 64" aria-hidden="true">
          <g class="leg l"><line x1="25" y1="36" x2="25" y2="57"/><ellipse cx="26.5" cy="60" rx="6" ry="3.5"/></g>
          <g class="leg r"><line x1="35" y1="36" x2="35" y2="57"/><ellipse cx="36.5" cy="60" rx="6" ry="3.5"/></g>
          <rect class="torso" x="17" y="4" width="26" height="36" rx="10"/>
          <g class="arm l"><line x1="18" y1="11" x2="18" y2="36"/><circle cx="18" cy="38" r="4.8"/></g>
          <g class="arm r"><line x1="42" y1="11" x2="42" y2="36"/><circle cx="42" cy="38" r="4.8"/></g>
        </svg></div></div>`;
    app.innerHTML = `${brand}<h2 class="st-title">🏆 Winners</h2>
      <div class="stage" id="stage">
        ${[1, 0, 2].filter((i) => top[i]).map((i) => `<div class="block" style="height:${H[i]}px;left:${X[i]}"><b>${LABEL[i]}</b><small>${esc(top[i].name)}</small></div>`).join('')}
        ${top.map(toon).join('')}
      </div>
      <div class="card"><b>Final scores</b>${board(S.players)}</div><div id="donectl"></div>`;
    paintDoneCtl();
    const stage = document.getElementById('stage'), timers = [], ivs = [];
    const at = (ms, fn) => timers.push(setTimeout(fn, ms));
    let t = 500;
    [2, 1, 0].filter((i) => top[i]).forEach((i) => {
      const el = stage.querySelector(`.toon[data-i="${i}"]`), W = i === 0 ? 2000 : 1500;
      at(t, () => {                                         // walk to the block
        el.classList.add('walking'); el.style.transition = `left ${W}ms linear`; el.style.left = X[i];
        const iv = setInterval(() => Sfx.play('step'), 230); ivs.push(iv); setTimeout(() => clearInterval(iv), W);
      });
      at(t + W, () => {                                     // hop up onto it
        el.classList.remove('walking'); el.classList.add('hop');
        el.style.transition = 'bottom .45s cubic-bezier(.3,1.5,.5,1)'; el.style.bottom = H[i] + 'px';
      });
      at(t + W + 420, () => { el.classList.remove('hop'); el.classList.add('on'); Sfx.play('land'); });
      t += W + 750;
    });
    at(t, () => {                                           // the winner throws both hands up and cheers
      const w = stage.querySelector('.toon[data-i="0"]'); if (w) w.classList.add('cheer');
      stage.querySelectorAll('.toon:not([data-i="0"])').forEach((e) => e.classList.add('clap'));
      Sfx.play('win'); Sfx.play('cheer'); if (top[0]) Sfx.say(`${top[0].name} wins!`);
      const colors = ['#FFE45A', '#FF9A0A', '#3DE0F5', '#ff5c8a', '#7dffa6', '#fff'];
      for (let k = 0; k < 44; k++) {
        const c = document.createElement('i'); c.className = 'confetti';
        c.style.cssText = `left:${Math.random() * 100}%;background:${colors[k % colors.length]};animation-delay:${(Math.random() * 1.6).toFixed(2)}s;animation-duration:${(2 + Math.random() * 1.6).toFixed(2)}s;transform:rotate(${Math.floor(Math.random() * 360)}deg)`;
        stage.appendChild(c);
      }
    });
    anim = { stop() { timers.forEach(clearTimeout); ivs.forEach(clearInterval); try { speechSynthesis.cancel(); } catch (e) { } } };
  }

  function stopAnim() { if (anim) { anim.stop(); anim = null; } }

  // Between-round screen: rows start in last round's order with last round's scores, the scores count up,
  // then rows glide to their new positions; rank numbers flip up (moved up) or down (moved down).
  function renderStandings() {
    const ROW = 60, rows = S.standings;
    app.innerHTML = `${brand}
      <div class="muted">Round ${S.round.index + 1} / ${S.round.total}</div>
      <h2 class="st-title">${S.isLast ? '🏁 Final standings' : '📊 Standings'}</h2>
      <div class="board" style="height:${rows.length * ROW}px">${rows.map((r) => `
        <div class="srow ${r.you ? 'me' : ''}" data-name="${esc(r.name)}" style="transform:translateY(${r.from * ROW}px)">
          <div class="rk"><span class="rkn">${r.from + 1}</span></div>
          ${faceImg(r.av)}
          <div class="nm">${esc(r.name)}${r.you ? ' <small>(you)</small>' : ''}</div>
          <span class="rdy" title="Ready">✓</span>
          <div class="pts"><span class="sc">${r.prev}</span>${r.gained > 0 ? `<span class="gain">+${r.gained}</span>` : ''}</div>
        </div>`).join('')}</div>
      <p class="muted" id="rdycount"></p>
      <button id="ready" disabled>Ready</button>
      ${S.isHost ? '<button id="next" class="secondary small">Continue without waiting</button>' : ''}`;
    const rb = document.getElementById('ready'); rb.onclick = () => { rb.disabled = true; send({ action: 'ready' }); };
    const next = document.getElementById('next'); if (next) next.onclick = () => send({ action: 'next' });

    const els = [...app.querySelectorAll('.srow')], timers = []; let raf = 0, stopped = false;
    const at = (ms, fn) => timers.push(setTimeout(() => { if (!stopped) fn(); }, ms));
    const COUNT_AT = 800, COUNT_MS = 2200, READY_AT = COUNT_AT + COUNT_MS + 500 + 900;   // Ready unlocks once the rows have settled
    let canReady = false; at(READY_AT, () => { canReady = true; updateReady(); });
    standingsGate = () => canReady;
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
    updateReady();
    anim = { stop() { stopped = true; cancelAnimationFrame(raf); timers.forEach(clearTimeout); standingsGate = () => false; } };
  }

  // live ready state (also called when the server re-broadcasts, which never re-renders the animation)
  let standingsGate = () => false;
  function updateReady() {
    if (!S || S.state !== 'standings') return;
    const ready = new Set(S.ready), total = S.standings.length, me = ready.has(S.you.name);
    app.querySelectorAll('.srow').forEach((el) => el.classList.toggle('isready', ready.has(el.dataset.name)));
    const c = document.getElementById('rdycount'); if (c) c.textContent = `${S.ready.length} of ${S.standings.length} ready`;
    const b = document.getElementById('ready');
    if (b) { b.disabled = me || !standingsGate(); b.textContent = me ? '✓ Ready — waiting for others…' : 'Ready'; b.classList.toggle('waiting', me); }
  }

  function render() {
    clearInterval(timerId);
    if (S && (S.state === 'countdown' || S.state === 'play')) {     // set up once; ignore re-broadcasts while it runs
      const key = S.state + ':' + S.code + ':' + S.mini.index;
      if (key === liveKey) return;
      liveKey = key; stopLive(); stopAnim(); standKey = null;
      return S.state === 'countdown' ? renderCountdown() : renderPlay();
    }
    liveKey = null; stopLive();
    if (S && S.state === 'standings') {                 // animate once per round; ignore re-broadcasts (e.g. someone leaves)
      const key = S.code + ':' + S.round.index;
      if (key === standKey) { updateReady(); return; }
      standKey = key; stopAnim(); return renderStandings();
    }
    if (S && S.state === 'done') {                       // play the podium cutscene once; later broadcasts only refresh the button
      if (doneKey === S.code) return paintDoneCtl();
      standKey = null; stopAnim(); doneKey = S.code; return renderPodium();
    }
    doneKey = null;
    standKey = null; stopAnim();
    let h = S ? brand : hero;
    if (!S && screen === 'camera') return renderCamera();
    stopCam();
    if (!S && screen === 'mode') {                                   // host picks the game type first
      app.innerHTML = `${brand}<h2 class="st-title">Choose a game</h2>
        <button class="modecard" data-mode="trivia"><span class="mi">🧠</span><span><b>Trivia</b><small>Answer questions. The fastest right answer scores the most.</small></span></button>
        <button class="modecard" data-mode="mini"><span class="mi">🎮</span><span><b>Mini Games</b><small>A series of quick tap challenges, party style.</small></span></button>
        <button class="secondary small" id="back">← Back</button>
        <div class="err">${esc(err)}</div>`;
      app.querySelectorAll('.modecard').forEach((b) => (b.onclick = () => connect(() => send({ action: 'create', name: hostName, mode: b.dataset.mode, avatar: face }))));
      document.getElementById('back').onclick = () => { screen = 'home'; err = ''; render(); };
      return;
    }
    if (!S && screen === 'browse') {                                 // live list of open games
      const MODE = { trivia: ['🧠', 'Trivia'], mini: ['🎮', 'Mini Games'] };
      app.innerHTML = `${brand}<h2 class="st-title">Open games</h2>
        ${games.length ? games.map((g) => `<div class="card game">
            ${faceImg(g.av, 'mid')}
            <div class="gt"><b>${esc(g.host)}'s game</b><small>${MODE[g.mode][0]} ${MODE[g.mode][1]} · ${g.players} player${g.players === 1 ? '' : 's'} waiting</small></div>
            <button class="joinbtn" data-id="${esc(g.id)}">Join game</button>
          </div>`).join('') : '<div class="card"><p class="muted">No open games right now.<br>Ask someone to host one — it will appear here automatically.</p></div>'}
        <button class="secondary small" id="back">← Back</button>
        <div class="err">${esc(err)}</div>`;
      app.querySelectorAll('.joinbtn').forEach((b) => (b.onclick = () => send({ action: 'join', name: hostName, id: b.dataset.id, avatar: face })));
      document.getElementById('back').onclick = () => { send({ action: 'unlist' }); screen = 'home'; err = ''; render(); };
      return;
    }
    if (!S) {
      h += `<div class="card">
        ${face ? `<div class="mepic"><img class="face big" src="${face}" alt="Your picture"><button class="chip small" id="retake">Retake picture</button></div>` : ''}
        <input id="name" placeholder="Your name" maxlength="20" value="${esc(hostName)}">
        <button id="join">Join game</button>
        <button id="create" class="secondary">Host a new game</button>
        <div class="err">${esc(err)}</div></div>`;
      app.innerHTML = h;
      const go = (to) => {                                           // both paths need a name, then a picture
        hostName = document.getElementById('name').value.trim();
        if (!hostName) { err = 'Enter a name'; return render(); }
        try { localStorage.setItem('tg_name', hostName); } catch (e) { }
        err = '';
        if (!face) { afterCam = to; screen = 'camera'; return render(); }
        screen = to; render();
        if (to === 'browse') connect(() => send({ action: 'list' }));
      };
      const rt = document.getElementById('retake');
      if (rt) rt.onclick = () => { hostName = document.getElementById('name').value.trim(); afterCam = 'home'; screen = 'camera'; render(); };
      document.getElementById('join').onclick = () => go('browse');
      document.getElementById('create').onclick = () => go('mode');
      return;
    }
    // lobby title; the host can flip between Trivia and Mini Games here while everyone waits
    const lobbyHead = () => `<div class="card"><div class="gname">${esc(S.host)}'s game</div>${S.isHost
      ? `<div class="chips modes">${[['trivia', '🧠 Trivia'], ['mini', '🎮 Mini Games']].map(([m, l]) => `<button class="chip ${S.mode === m ? 'on' : ''}" data-setmode="${m}">${l}</button>`).join('')}</div>`
      : `<div class="muted">${S.mode === 'mini' ? '🎮 Mini Games' : '🧠 Trivia'}</div>`}</div>`;
    if (S.state === 'lobby' && S.mode === 'mini') {
      h += `${lobbyHead()}
        <div class="card"><b>🎮 Mini Games</b> <span class="muted">(${S.mini.rounds} rounds)</span>
          <div class="chips">${S.mini.games.map((g) => `<span class="chip on static">${g.icon} ${esc(g.name)}</span>`).join('')}</div></div>
        <div class="card"><b>Players (${S.players.length})</b>${board(S.players)}</div>
        ${S.isHost ? '<button id="start">Start game</button>' : '<p class="muted">Waiting for host to start…</p>'}`;
    } else if (S.state === 'lobby') {
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
      h += `${lobbyHead()}
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
    }
    h += `<div class="err">${esc(err)}</div>`;
    app.innerHTML = h;

    document.querySelectorAll('.choice').forEach((b) => (b.onclick = () => send({ action: 'answer', choice: +b.dataset.i })));
    const on = (id, a) => { const el = document.getElementById(id); if (el) el.onclick = () => send({ action: a }); };
    on('start', 'start'); on('next', 'next'); on('again', 'again');
    document.querySelectorAll('[data-setmode]').forEach((b) => (b.onclick = () => { if (b.dataset.setmode !== S.mode) send({ action: 'mode', mode: b.dataset.setmode }); }));
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
