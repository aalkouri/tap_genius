(() => {
  const app = document.getElementById('app');
  let ws, S = null, err = '', timerId = null, standKey = null, anim = null, doneKey = null;
  let screen = 'home', hostName = '', liveKey = null, live = null;   // home | mode (game-type picker) | browse (open games); live = running countdown / mini game
  let games = [];
  // each player's head shot (a small JPEG data URL), taken once and remembered on this device
  let face = null, afterCam = 'home', cam = null;
  try { face = localStorage.getItem('tg_face'); hostName = localStorage.getItem('tg_name') || ''; } catch (e) { }
  const faceImg = (av, cls = '') => `<img class="face ${cls}" src="${av ? `/avatar/${esc(av)}.jpg` : '/img/bulb.png'}" alt="" onerror="this.style.visibility='hidden'">`;                                                    // open games, pushed live by the server while browsing

  // ---- connection: if the phone drops the socket (minimised, locked, signal lost) we quietly reconnect and take our seat back ----
  let token = null, reconnecting = false, retryT = 0, pongOk = true;
  try { token = localStorage.getItem('tg_sess'); } catch (e) { }
  const saveToken = (t) => { token = t; try { t ? localStorage.setItem('tg_sess', t) : localStorage.removeItem('tg_sess'); } catch (e) { } };
  const wsUrl = () => (location.protocol === 'https:' ? 'wss://' : 'ws://') + location.host;
  function banner(on) {
    let el = document.getElementById('reconn');
    if (!on) { if (el) el.remove(); return; }
    if (!el) { el = document.createElement('div'); el.id = 'reconn'; el.textContent = '📡 Reconnecting…'; document.body.appendChild(el); }
  }
  function attach(sock) {
    sock.onmessage = (e) => {
      const m = JSON.parse(e.data);
      if (m.type === 'ev') { if (live && live.onEvent) live.onEvent(m); return; }   // in-game events never re-render
      if (m.type === 'list') { games = m.games; if (!S && screen === 'browse') render(); return; }
      if (m.type === 'pong') { pongOk = true; return; }
      if (m.type === 'session') {
        if (m.expired) return giveUp('Your game has ended, or you were away too long.');
        saveToken(m.token); const was = reconnecting; reconnecting = false; banner(false); if (was && !S) render(); return;
      }
      if (m.type === 'left') { S = null; saveToken(null); screen = 'home'; err = m.msg || ''; reconnecting = false; banner(false); try { sock.close(); } catch (x) { } return render(); }
      if (m.type === 'error') { err = m.message; Sfx.play('wrong'); } else { const prev = S; S = m; err = ''; sounds(prev, S); }
      render();
    };
    sock.onclose = () => {
      if (sock !== ws) return;                                  // an old socket we already replaced
      if (reconnecting) return;                                 // the retry loop is already handling it
      if (S && token) { reconnecting = true; banner(true); scheduleRetry(0); }
      else if (S) { err = 'Disconnected. Reload to rejoin.'; render(); }
    };
  }
  function giveUp(message) {                                    // the server no longer has our seat
    reconnecting = false; clearTimeout(retryT); saveToken(null); banner(false);
    S = null; screen = 'home'; err = message; stopLive(); stopAnim(); liveKey = null; standKey = null; doneKey = null; render();
  }
  function scheduleRetry(n) {
    clearTimeout(retryT);
    if (n > (S ? 75 : 10)) return giveUp('Could not reconnect to your game.');   // ~3 minutes in a game (the server holds the seat that long), ~20s on a fresh page load
    retryT = setTimeout(() => {
      if (!reconnecting || (ws && ws.readyState === 1)) return;
      const sock = new WebSocket(wsUrl()); ws = sock; attach(sock);
      sock.onopen = () => sock.send(JSON.stringify({ action: 'resume', token }));
      const next = () => { if (sock === ws && reconnecting) scheduleRetry(n + 1); };
      sock.addEventListener('close', next);
    }, Math.min(3000, 400 * (n + 1)));
  }
  const wake = () => {                                         // tab visible again / network back: is our connection still alive?
    if (!S || !token) return;
    if (reconnecting) return scheduleRetry(0);
    if (!ws || ws.readyState > 1) { reconnecting = true; banner(true); return scheduleRetry(0); }
    pongOk = false; send({ action: 'ping' });                  // a socket that died while we were away can still look open: test it
    setTimeout(() => { if (!pongOk && !reconnecting && S) { const dead = ws; reconnecting = true; banner(true); try { dead.close(); } catch (e) { } scheduleRetry(0); } }, 1500);
  };
  document.addEventListener('visibilitychange', () => { if (!document.hidden) wake(); });
  window.addEventListener('online', wake); window.addEventListener('pageshow', wake); window.addEventListener('focus', wake);
  function connect(then) {
    if (ws && ws.readyState === 1) return then();
    ws = new WebSocket(wsUrl()); attach(ws);
    ws.onopen = then;
  }
  // The page was reloaded (or the browser discarded the tab) while we were in a game: try to take our seat back
  if (token) { reconnecting = true; scheduleRetry(0); }
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
  const hero = '<div class="hero"><video src="/img/logo.mp4" poster="/img/logo.jpg" autoplay muted playsinline preload="auto" disablepictureinpicture aria-label="Tap Genius"></video></div><div class="tagline">Tap fast. Think faster!</div>';
  const board = (players) => `<ol class="plist">${players.map((p) => `<li class="${p.away ? 'away' : ''}">${faceImg(p.av)}<span class="pn">${esc(p.name)}${p.away ? ' 💤' : ''}</span><span class="ps">${p.score}</span></li>`).join('')}</ol>`;

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
      <div class="card cd-card"><div class="cd-icon">${g.icon}</div><h2>${esc(g.name)}</h2><p>${esc(g.how)}</p>
        ${g.pic ? `<p class="cd-who">${g.pic.you ? "🎨 You're drawing!" : `🎨 ${esc(g.pic.drawer)} is drawing!`}</p>` : ''}</div>
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
    const moles = new Map(), hits = {}, done = new Set(), t0 = Date.now();
    S.players.forEach((pl) => { hits[pl.name] = 0; });      // everyone starts the round on 0, so the leader shown is right even after misses
    const barTimer = setInterval(() => { bar.style.width = Math.max(0, 100 - ((Date.now() - t0) / g.ms) * 100) + '%'; }, 100);
    const drop = (id, delay) => { const m = moles.get(id); if (!m) return; moles.delete(id); clearTimeout(m.timer); m.el.classList.remove('up'); setTimeout(() => m.el.remove(), delay); };
    const whack = (el) => { if (el.classList.contains('tapped')) return; el.classList.add('tapped'); send({ action: 'whack', id: +el.dataset.id }); };
    // Tapping a square: if a mole is up in it, that counts as tapping the mole. An empty square is a miss (-1, 1s lockout).
    let lockUntil = 0, pending = 0;
    field.addEventListener('pointerdown', (e) => {
      const hole = e.target.closest('.hole'); if (!hole) return;
      e.preventDefault();
      const up = hole.querySelector('.mole.up:not(.bonked)');
      if (up) return whack(up);
      if (hole.querySelector('.mole')) return;              // one is just leaving: not a miss
      const now = Date.now(); if (now < lockUntil || now < pending) return;
      pending = now + 250; send({ action: 'miss', cell: +hole.dataset.cell });
    });
    const hud = () => {
      document.getElementById('myhits').textContent = `You: ${hits[me] || 0}`;
      const top = Object.entries(hits).sort((a, b) => b[1] - a[1])[0];
      document.getElementById('lead').textContent = top && top[1] > 0 ? `👑 ${top[0]} ${top[1]}` : '';
    };
    live = {
      onEvent(ev) {
        if (ev.ev === 'spawn') {
          const hole = field.children[ev.cell]; if (!hole) return;
          const el = document.createElement('div'); el.className = 'mole'; el.dataset.id = ev.id;
          el.innerHTML = `${MOLE_SVG}<div class="mface"${ev.av ? ` style="background-image:url(/avatar/${ev.av}.jpg)"` : ''}></div>`;   // a random player's head
          el.addEventListener('pointerdown', (e) => { e.preventDefault(); e.stopPropagation(); whack(el); });
          hole.querySelector('.burrow').appendChild(el); void el.offsetWidth; el.classList.add('up');
          moles.set(ev.id, { el, timer: setTimeout(() => drop(ev.id, 180), ev.ttl) });
          Sfx.play('pop');
        } else if (ev.ev === 'miss') {
          hits[ev.by] = ev.n; hud();
          if (ev.by !== me) return;
          lockUntil = Date.now() + 1000;
          Sfx.play('buzzer'); app.classList.remove('shake'); void app.offsetWidth; app.classList.add('shake');
          const hole = field.children[ev.cell]; if (!hole) return;
          const x = document.createElement('div'); x.className = 'missx';
          x.innerHTML = '<svg viewBox="0 0 100 100" aria-hidden="true"><line x1="16" y1="16" x2="84" y2="84"/><line x1="84" y1="16" x2="16" y2="84"/></svg><b>-1</b>';
          hole.appendChild(x); field.classList.add('locked');
          setTimeout(() => { x.remove(); if (Date.now() >= lockUntil) field.classList.remove('locked'); }, 1000);
        } else if (ev.ev === 'hit') {
          if (done.has(ev.id)) return; done.add(ev.id);                     // never count a mole twice
          hits[ev.by] = ev.n !== undefined ? ev.n : (hits[ev.by] || 0) + 1; hud();   // show the server's count
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
    c.innerHTML = (S.isHost ? '<button id="again">Play again</button>' : '<p class="muted">Waiting for the host…</p>') + '<button class="secondary small" id="leave2">Leave game</button>';
    const b = document.getElementById('again'); if (b) b.onclick = () => send({ action: 'again' });
    document.getElementById('leave2').onclick = () => send({ action: 'leave' });
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
          <g class="arm l"><line x1="18" y1="11" x2="18" y2="36"/><circle cx="18" cy="38" r="4.8"/><g class="bent"><line x1="18" y1="11" x2="14" y2="28"/><g class="fore"><line x1="14" y1="28" x2="29" y2="21"/><circle cx="29" cy="21" r="4.8"/></g></g></g>
          <g class="arm r"><line x1="42" y1="11" x2="42" y2="36"/><circle cx="42" cy="38" r="4.8"/><g class="bent"><line x1="42" y1="11" x2="46" y2="28"/><g class="fore"><line x1="46" y1="28" x2="31" y2="21"/><circle cx="31" cy="21" r="4.8"/></g></g></g>
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

  // ---- Brain Bash: tap the copy of the object that is the RIGHT colour; the colour words underneath are lies ----
  const BBHEX = { red: '#E53935', orange: '#FB8C00', yellow: '#FDD835', green: '#43A047', blue: '#1E88E5', purple: '#8E24AA', pink: '#F48FB1', brown: '#6D4C41', black: '#212121', white: '#ffffff' };
  function bbSvg(obj, f, o) {
    const F = BBHEX[f], O = BBHEX[o], st = `fill="${F}" stroke="${O}" stroke-width="5" stroke-linejoin="round" stroke-linecap="round"`, ln = `fill="none" stroke="${O}" stroke-width="4" stroke-linecap="round"`;
    let b = '';
    switch (obj) {
      case 'banana': b = `<path ${st} d="M16 30 Q28 80 78 80 Q92 80 88 66 Q60 68 42 42 Q36 24 26 20 Q14 20 16 30 Z"/>`; break;
      case 'carrot': b = `<path ${st} d="M24 26 Q50 8 76 26 Q62 60 50 94 Q38 60 24 26 Z"/><path ${ln} d="M38 36 L48 38 M56 52 L64 50 M46 66 L54 66"/>`; break;
      case 'leaf': b = `<path ${st} d="M50 92 Q8 62 18 20 Q60 8 84 30 Q94 72 50 92 Z"/><path ${ln} d="M50 92 Q46 60 30 36"/>`; break;
      case 'sun': { let p = ''; for (let k = 0; k < 16; k++) { const a = k * Math.PI / 8, r = k % 2 ? 30 : 46; p += `${k ? 'L' : 'M'}${(50 + r * Math.cos(a)).toFixed(1)} ${(50 + r * Math.sin(a)).toFixed(1)} `; } b = `<path ${st} d="${p}Z"/>`; break; }
      case 'drop': b = `<path ${st} d="M50 8 Q86 52 80 66 A30 30 0 0 1 20 66 Q14 52 50 8 Z"/>`; break;
      case 'grapes': b = [[34, 36], [58, 36], [24, 56], [46, 56], [68, 56], [34, 76], [58, 76], [46, 92]].map(([x, y]) => `<circle ${st} cx="${x}" cy="${y - 8}" r="12"/>`).join('') + `<path ${ln} d="M46 18 Q50 8 60 6"/>`; break;
      case 'tomato': b = `<circle ${st} cx="50" cy="56" r="34"/><path ${ln} d="M36 26 L50 36 L64 26 M50 36 L50 20"/>`; break;
      case 'pumpkin': b = `<ellipse ${st} cx="50" cy="56" rx="40" ry="32"/><path ${ln} d="M36 28 Q26 56 36 84 M64 28 Q74 56 64 84 M50 26 L50 10"/>`; break;
      case 'lemon': b = `<path ${st} d="M6 50 Q30 16 50 16 Q70 16 94 50 Q70 84 50 84 Q30 84 6 50 Z"/>`; break;
      case 'cherry': b = `<path ${ln} d="M30 70 Q40 30 66 10 M70 72 Q70 36 66 10"/><circle ${st} cx="30" cy="72" r="17"/><circle ${st} cx="70" cy="74" r="17"/>`; break;
      case 'heart': b = `<path ${st} d="M50 90 L10 48 A22 22 0 0 1 50 24 A22 22 0 0 1 90 48 Z"/>`; break;
      case 'fish': b = `<path ${st} d="M8 50 Q34 14 62 34 L92 16 L84 50 L92 84 L62 66 Q34 86 8 50 Z"/><circle cx="28" cy="46" r="4" fill="${O}"/>`; break;
      case 'bear': b = `<circle ${st} cx="24" cy="26" r="14"/><circle ${st} cx="76" cy="26" r="14"/><circle ${st} cx="50" cy="54" r="38"/><circle cx="36" cy="46" r="4.5" fill="${O}"/><circle cx="64" cy="46" r="4.5" fill="${O}"/><ellipse cx="50" cy="64" rx="7" ry="5" fill="${O}"/>`; break;
      case 'pig': b = `<path ${st} d="M20 36 L18 12 L40 24 Z M80 36 L82 12 L60 24 Z"/><circle ${st} cx="50" cy="54" r="38"/><ellipse ${ln} cx="50" cy="62" rx="15" ry="11"/><circle cx="44" cy="62" r="3" fill="${O}"/><circle cx="56" cy="62" r="3" fill="${O}"/><circle cx="34" cy="44" r="4" fill="${O}"/><circle cx="66" cy="44" r="4" fill="${O}"/>`; break;
      case 'acorn': b = `<path ${st} d="M22 44 Q22 90 50 94 Q78 90 78 44 Z"/><path ${st} d="M16 46 Q16 18 50 18 Q84 18 84 46 Z"/><path ${ln} d="M50 18 L50 6"/>`; break;
      case 'eggplant': b = `<path ${st} d="M62 22 Q94 42 72 72 Q50 98 26 84 Q8 66 34 44 Q50 32 62 22 Z"/><path ${st} d="M56 26 L74 10 L82 28 Z"/>`; break;
    }
    return `<svg viewBox="0 0 100 100" aria-hidden="true">${b}</svg>`;
  }
  function renderBb() {
    const g = S.mini, me = S.you.name, cars = g.cars, mine = cars.find((c) => c.name === me), myId = mine ? mine.i : -1;
    let raf = 0, phase = 'wait', startAt = 0, ms = 1, answered = false, scores = {}, ans = {};
    const timers = [];
    app.innerHTML = `<div class="timer"><div id="bar"></div></div>
      <div class="hud rchud"><span id="bbstat">Get ready…</span><span id="bbme">You: 0</span></div>
      <div class="bbask" id="bbask">&nbsp;</div>
      <div class="bbgrid" id="bbgrid"></div>
      <div class="bbplayers" id="bbpl"></div>`;
    const grid = document.getElementById('bbgrid'), bar = document.getElementById('bar'), ask = document.getElementById('bbask');
    const stat = (t) => { document.getElementById('bbstat').textContent = t; };
    const board = () => {
      document.getElementById('bbme').textContent = `You: ${scores[myId] || 0}`;
      document.getElementById('bbpl').innerHTML = cars.slice().sort((a, b) => (scores[b.i] || 0) - (scores[a.i] || 0)).map((c) => `<div class="bbp ${c.i === myId ? 'me' : ''} ${ans[c.i] === true ? 'ok' : ans[c.i] === false ? 'bad' : ''}">${faceImg(c.av)}<b>${esc(c.name)}</b><span>${ans[c.i] === true ? '✓ ' : ans[c.i] === false ? '✗ ' : ''}${scores[c.i] || 0}</span></div>`).join('');
    };
    const setRound = (ev, remaining, state) => {
      phase = state || 'play'; ms = ev.ms; startAt = performance.now() - (ev.full === false ? 0 : 0) - (ms - remaining); answered = false; ans = {}; scores = ev.scores || scores;
      ask.innerHTML = `Round ${ev.r}/${ev.n} — tap the<br><b class="bbtarget" style="color:${BBHEX[ev.color]}">${esc(ev.color)} ${esc(ev.name)}</b>`;
      if (!state) Sfx.say(`Tap the ${ev.color} ${ev.name}`);
      grid.innerHTML = ev.tiles.map((t, i) => `<button class="bbtile" data-i="${i}" ${phase === 'play' ? '' : 'disabled'}>${bbSvg(ev.obj, t.f, t.o)}<span class="bbw" style="color:${BBHEX[t.wc]};--sh:${t.wc === 'black' ? '#fff' : '#111'}">${esc(t.w.toUpperCase())}</span></button>`).join('');
      stat('Go!'); board();
    };
    grid.addEventListener('click', (e) => {
      const b = e.target.closest('.bbtile'); if (!b || phase !== 'play' || answered) return;
      answered = true; send({ action: 'bbpick', i: +b.dataset.i }); b.classList.add('picked');
      grid.querySelectorAll('.bbtile').forEach((x) => { x.disabled = true; });
    });
    const frame = (now) => { raf = requestAnimationFrame(frame); bar.style.width = phase === 'play' ? Math.max(0, 100 - ((now - startAt) / ms) * 100) + '%' : '100%'; };
    raf = requestAnimationFrame(frame);
    const reveal = (correct) => {
      phase = 'reveal'; grid.querySelectorAll('.bbtile').forEach((x, i) => { x.disabled = true; if (i === correct) x.classList.add('right'); });
      if (!answered) { stat("Time's up!"); Sfx.play('buzzer'); bigX("Time's up!"); } else stat('Next…'); board();
    };
    board();
    live = {
      onEvent(ev) {
        if (ev.ev === 'bbround') setRound(ev, ev.ms);
        else if (ev.ev === 'bbsync') {
          setRound(ev, ev.ms, ev.phase === 'play' ? 'play' : 'reveal');
          if (ev.mine >= 0) { answered = true; const t = grid.children[ev.mine]; if (t) t.classList.add('picked'); grid.querySelectorAll('.bbtile').forEach((x) => { x.disabled = true; }); }
          if (ev.phase === 'reveal') reveal(ev.correct);
        }
        else if (ev.ev === 'bbok') { const t = grid.children[ev.i]; if (t) t.classList.add('right'); Sfx.play('correct'); stat(`✅ +${ev.pts}`); }
        else if (ev.ev === 'bbbad') { const t = grid.children[ev.i]; if (t) { t.classList.add('wrong'); t.insertAdjacentHTML('beforeend', '<i class="bbx">✗</i>'); } Sfx.play('buzzer'); bigX('Wrong!'); stat('❌ Wrong'); }
        else if (ev.ev === 'bbans') { ans[ev.i] = ev.ok; if (typeof ev.total === 'number') scores[ev.i] = ev.total; board(); }
        else if (ev.ev === 'bbreveal') { scores = ev.scores || scores; reveal(ev.correct); }
      },
      stop() { cancelAnimationFrame(raf); timers.forEach(clearTimeout); },
    };
  }

  // ---- Number Sniper: read the number over a player when they stop, type it to eliminate them ----
  function renderNs() {
    const g = S.mini, me = S.you.name, cars = g.cars, mine = cars.find((c) => c.name === me), myId = mine ? mine.i : -1;
    app.innerHTML = `<div class="timer"><div id="bar"></div></div>
      <div class="hud rchud"><span id="nsme">You: 0</span><span id="nsleft"></span></div>
      <canvas id="nsv"></canvas>
      <div class="nsfeed" id="nsfeed"></div>
      <div class="nsin"><div class="nsboxes" id="nsboxes">${'<span class="nb"></span>'.repeat(4)}</div><div class="nsmsg" id="nsmsg">Type a number to snipe</div></div>
      <div class="keypad" id="keypad">${[1, 2, 3, 4, 5, 6, 7, 8, 9].map((d) => `<button data-k="${d}">${d}</button>`).join('')}<button data-k="back" class="kb">⌫</button><button data-k="0">0</button><button data-k="clr" class="kb">✕</button></div>`;
    const cv = document.getElementById('nsv'), ctx = cv.getContext('2d'), bar = document.getElementById('bar'), feed = document.getElementById('feed') || document.getElementById('nsfeed');
    const now0 = performance.now(), imgs = {}, st = new Map(), skulls = [], sparks = [], floats = [], score = {}, dead = new Set(g.dead || []);
    cars.forEach((c) => { score[c.i] = 0; st.set(c.i, { ...c, x: -999, y: -999, tx: 0, ty: 0, mv: 0, bl: 0, num: -1, seen: false, flash: -1e9 }); if (c.av) { const im = new Image(); im.src = `/avatar/${c.av}.jpg`; imgs[c.i] = im; } });
    const idxName = (i) => (cars.find((c) => c.i === i) || {}).name || '?';
    let W = 0, dpr = 1, raf = 0, floor = null, entered = '', lockUntil = 0, outMe = dead.has(myId);
    const size = () => {
      dpr = Math.min(2, window.devicePixelRatio || 1); W = Math.max(250, Math.min(app.clientWidth, 560, window.innerHeight - 440));
      cv.style.width = W + 'px'; cv.style.height = W + 'px'; cv.width = Math.round(W * dpr); cv.height = Math.round(W * dpr);
      floor = document.createElement('canvas'); floor.width = cv.width; floor.height = cv.height; const f = floor.getContext('2d'); f.scale(dpr, dpr);
      f.fillStyle = '#2d4a3e'; f.fillRect(0, 0, W, W); f.strokeStyle = 'rgba(255,255,255,.07)'; f.lineWidth = 1;
      for (let k = 1; k < 10; k++) { f.beginPath(); f.moveTo(k * W / 10, 0); f.lineTo(k * W / 10, W); f.moveTo(0, k * W / 10); f.lineTo(W, k * W / 10); f.stroke(); }
      f.strokeStyle = 'rgba(255,255,255,.13)'; f.lineWidth = 2; f.beginPath(); f.arc(W / 2, W / 2, W * 0.16, 0, 7); f.stroke();
      f.lineWidth = 6; f.strokeStyle = '#6b4a2b'; f.strokeRect(1.5, 1.5, W - 3, W - 3);
      f.font = `900 ${W * 0.1}px system-ui,sans-serif`; f.fillStyle = 'rgba(255,255,255,.06)'; f.textAlign = 'center'; f.fillText('NUMBER SNIPER', W / 2, W / 2 + W * 0.035);
    };
    size(); window.addEventListener('resize', size);
    const sx = (x) => x / 1000 * W, fmt4 = (n) => String(n).padStart(4, '0');
    const smear = (txt, x, y, now, big) => {                                      // a number that cannot be read: a real blur where the browser supports it, a heavy haze where it does not
      if ('filter' in ctx) { ctx.save(); ctx.filter = `blur(${Math.max(4, big * 0.3)}px)`; ctx.fillStyle = 'rgba(225,235,255,.9)'; ctx.fillText(txt, x, y); ctx.restore(); return; }
      ctx.fillStyle = 'rgba(225,235,255,.1)';
      for (let k = 0; k < 14; k++) { const a = k * 0.9 + now / 120, r = big * (0.1 + 0.12 * ((k % 3) / 2)); ctx.fillText(txt, x + Math.cos(a) * r, y + Math.sin(a) * r); }
    };
    const drawPlayer = (c, now) => {
      const x = sx(c.x), y = sx(c.y), hw = W * 0.105, hh = hw * 1.28, mineC = c.i === myId, flashing = now - c.flash < 1000;
      const bob = c.mv ? Math.sin(now / 90 + c.i) * 1.6 : 0;
      ctx.fillStyle = 'rgba(0,0,0,.25)'; ctx.beginPath(); ctx.ellipse(x, y + hh * 0.5, hw * 0.45, hh * 0.12, 0, 0, 7); ctx.fill();
      ctx.save(); ctx.beginPath(); ctx.ellipse(x, y + bob, hw / 2, hh / 2, 0, 0, 7); ctx.clip();
      const im = imgs[c.i]; if (im && im.complete && im.naturalWidth) ctx.drawImage(im, x - hw / 2, y - hh / 2 + bob, hw, hh); else { ctx.fillStyle = '#c89a6b'; ctx.fillRect(x - hw / 2, y - hh / 2, hw, hh); }
      if (flashing) { ctx.fillStyle = `rgba(255,255,255,${0.55 * (1 - (now - c.flash) / 1000)})`; ctx.fillRect(x - hw, y - hh, hw * 2, hh * 2); }
      ctx.restore();
      ctx.lineWidth = mineC ? 3 : 2; ctx.strokeStyle = mineC ? '#ffd35a' : 'rgba(255,255,255,.85)'; ctx.beginPath(); ctx.ellipse(x, y + bob, hw / 2, hh / 2, 0, 0, 7); ctx.stroke();
      // the number plate: readable only while the server says so
      const fs = Math.max(11, W * 0.05), ty = y - hh / 2 - fs * 0.95; ctx.font = `800 ${fs}px ui-monospace,Menlo,Consolas,monospace`; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
      const tw = ctx.measureText('0000').width + fs * 0.7, readable = c.num >= 0;
      ctx.fillStyle = readable ? 'rgba(10,20,40,.88)' : 'rgba(10,20,40,.7)'; ctx.beginPath(); ctx.roundRect(x - tw / 2, ty - fs * 0.62, tw, fs * 1.24, fs * 0.3); ctx.fill();
      ctx.strokeStyle = readable ? '#7dffa6' : c.bl ? '#ff9a9a' : 'rgba(255,255,255,.3)'; ctx.lineWidth = readable ? 2 : 1; ctx.stroke();
      if (readable) { ctx.fillStyle = '#7dffa6'; ctx.fillText(fmt4(c.num), x, ty + 1); }
      else { const fake = String(Math.floor(now / 70 + c.i * 37) % 10000).padStart(4, '0'); smear(fake, x, ty + 1, now, fs); if (c.bl) { ctx.fillStyle = 'rgba(255,120,120,.9)'; ctx.font = `900 ${fs * 0.7}px system-ui`; ctx.fillText('💫', x + tw / 2 - fs * 0.2, ty - fs * 0.5); } }
      ctx.font = `800 ${Math.max(9, W * 0.027)}px system-ui,sans-serif`; const lbl = mineC ? 'YOU' : c.name.slice(0, 9), lw = ctx.measureText(lbl).width;
      ctx.fillStyle = mineC ? '#ffd35a' : 'rgba(0,0,0,.55)'; ctx.beginPath(); ctx.roundRect(x - lw / 2 - 5, y + hh / 2 + 3, lw + 10, 15, 7); ctx.fill(); ctx.fillStyle = mineC ? '#3a2400' : '#fff'; ctx.fillText(lbl, x, y + hh / 2 + 11);
    };

    // ---- the number pad: the 4th digit fires
    const boxes = [...document.querySelectorAll('.nb')], msg = document.getElementById('nsmsg'), pad = document.getElementById('keypad');
    const paintIn = () => boxes.forEach((b, k) => { b.textContent = entered[k] || ''; b.classList.toggle('on', k === entered.length); });
    const say = (t, cls = '') => { msg.textContent = t; msg.className = 'nsmsg ' + cls; };
    const padOn = () => { const ok = !outMe && performance.now() >= lockUntil; pad.classList.toggle('off', !ok); };
    const press = (k) => {
      if (outMe || performance.now() < lockUntil) return;
      if (k === 'back') entered = entered.slice(0, -1); else if (k === 'clr') entered = ''; else if (entered.length < 4) entered += k;
      paintIn();
      if (entered.length === 4) { send({ action: 'nsfire', num: entered }); setTimeout(() => { entered = ''; paintIn(); }, 180); }
    };
    pad.addEventListener('pointerdown', (e) => { const b = e.target.closest('button'); if (!b) return; e.preventDefault(); b.classList.add('held'); setTimeout(() => b.classList.remove('held'), 90); press(b.dataset.k); });
    pad.addEventListener('contextmenu', (e) => e.preventDefault());
    const kd = (e) => { if (/^[0-9]$/.test(e.key)) press(e.key); else if (e.key === 'Backspace') press('back'); else if (e.key === 'Escape') press('clr'); };
    document.addEventListener('keydown', kd);
    const addFeed = (html, cls = '') => { const d = document.createElement('div'); d.className = 'fl ' + cls; d.innerHTML = html; feed.appendChild(d); while (feed.children.length > 3) feed.firstChild.remove(); };
    const hud = () => { document.getElementById('nsme').textContent = `You: ${score[myId] || 0}`; document.getElementById('nsleft').textContent = `${cars.length - dead.size} left`; };
    (g.log || []).forEach((e) => addFeed(e.self ? `<b>${esc(e.victim)}</b> eliminated themselves` : `<b>${esc(e.by)}</b> 🎯 <b>${esc(e.victim)}</b>`));
    paintIn(); padOn(); hud(); if (outMe) say("You're out — watch!", 'bad');

    const frame = (now) => {
      raf = requestAnimationFrame(frame);
      st.forEach((c) => { if (c.seen) { c.x += (c.tx - c.x) * 0.45; c.y += (c.ty - c.y) * 0.45; } });
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0); ctx.drawImage(floor, 0, 0, W, W);
      const order = [...st.values()].filter((c) => c.seen && !dead.has(c.i)).sort((a, b) => a.y - b.y); order.forEach((c) => drawPlayer(c, now));
      for (let k = skulls.length - 1; k >= 0; k--) { const s = skulls[k], a = (now - s.t0) / 2400; if (a >= 1) { skulls.splice(k, 1); continue; } ctx.globalAlpha = 1 - a; ctx.font = `${W * 0.085}px system-ui`; ctx.textAlign = 'center'; ctx.fillText(s.self ? '🤦' : '💀', sx(s.x), sx(s.y) - a * 14); ctx.globalAlpha = 1; }
      for (let k = sparks.length - 1; k >= 0; k--) { const s = sparks[k], a = (now - s.t0) / 700; if (a >= 1) { sparks.splice(k, 1); continue; } ctx.globalAlpha = 1 - a; ctx.font = `${W * (0.06 + a * 0.05)}px system-ui`; ctx.textAlign = 'center'; ctx.fillText('💥', sx(s.x), sx(s.y)); ctx.globalAlpha = 1; }
      for (let k = floats.length - 1; k >= 0; k--) { const f = floats[k], a = (now - f.t0) / 1100; if (a >= 1) { floats.splice(k, 1); continue; } ctx.globalAlpha = 1 - a; ctx.font = `900 ${W * 0.07}px system-ui`; ctx.textAlign = 'center'; ctx.lineWidth = 4; ctx.strokeStyle = '#06331a'; ctx.strokeText(f.text, sx(f.x), sx(f.y) - a * 36); ctx.fillStyle = f.color; ctx.fillText(f.text, sx(f.x), sx(f.y) - a * 36); ctx.globalAlpha = 1; }
      bar.style.width = Math.max(0, 100 - ((now - now0) / g.ms) * 100) + '%'; padOn();
    };
    raf = requestAnimationFrame(frame);

    live = {
      onEvent(ev) {
        const now = performance.now();
        if (ev.ev === 'ns') { ev.c.forEach(([i, x, y, fl, num]) => { const c = st.get(i); if (!c) return; if (!c.seen) { c.x = x; c.y = y; c.seen = true; } c.tx = x; c.ty = y; c.mv = fl & 1; c.bl = fl & 2; c.num = num; }); }
        else if (ev.ev === 'nscol') { Sfx.play('thunk'); [ev.a, ev.b].forEach((i) => { const c = st.get(i); if (c) c.flash = now; }); sparks.push({ x: ev.x, y: ev.y, t0: now }); }
        else if (ev.ev === 'nsout') {
          const v = st.get(ev.i); dead.add(ev.i); skulls.push({ x: v ? v.tx : 500, y: v ? v.ty : 500, t0: now, self: ev.self }); Sfx.play('shot');
          if (!ev.self) score[ev.by] = ev.pts; hud();
          addFeed(ev.self ? `<b>${esc(idxName(ev.i))}</b> eliminated themselves 🤦` : `<b>${esc(idxName(ev.by))}</b> 🎯 <b>${esc(idxName(ev.i))}</b>`, ev.by === myId || ev.i === myId ? 'me' : '');
          if (ev.i === myId) {                                                         // I am out: the big red X, the buzzer, and who did it
            outMe = true; entered = ''; paintIn(); setTimeout(() => Sfx.play('buzzer'), 120);
            bigX(ev.self ? 'You eliminated yourself' : `${idxName(ev.by)} eliminated you`); say("You're out — watch!", 'bad');
          } else if (ev.by === myId && !ev.self) { Sfx.play('correct'); say(`🎯 You eliminated ${idxName(ev.i)}! +1`, 'ok'); if (v) floats.push({ x: v.tx, y: v.ty, text: '+1', color: '#7dffa6', t0: now }); }
          else Sfx.play('pop');
        } else if (ev.ev === 'nsmiss') {
          lockUntil = performance.now() + ev.ms; entered = ''; paintIn(); say('No player has that number', 'bad'); Sfx.play('wrong');
          app.classList.remove('shake'); void app.offsetWidth; app.classList.add('shake'); setTimeout(() => { if (!outMe) say('Type a number to snipe'); }, ev.ms);
        }
      },
      stop() { cancelAnimationFrame(raf); window.removeEventListener('resize', size); document.removeEventListener('keydown', kd); },
    };
  }

  // ---- Pie Fight: everyone rides the edge of a square arena; throw pies across it at faces ----
  function renderPf() {
    const g = S.mini, me = S.you.name, cars = g.cars, mine = cars.find((c) => c.name === me), myId = mine ? mine.i : -1;
    app.innerHTML = `<div class="timer"><div id="bar"></div></div>
      <div class="hud rchud"><span id="pfme">You: 0</span><span id="pflead"></span></div>
      <canvas id="pfv"></canvas>
      <div class="pfpad"><div class="pfmoves"><button class="pfb mv" id="pfl" aria-label="Run left">◀</button><button class="pfb mv" id="pfr" aria-label="Run right">▶</button></div>
        <button class="pfb throw" id="pft">🥧 THROW</button></div>`;
    const cv = document.getElementById('pfv'), ctx = cv.getContext('2d'), bar = document.getElementById('bar'), tbtn = document.getElementById('pft');
    const now0 = performance.now(), imgs = {}, state = new Map(), pies = new Map(), splats = [], floats = [], score = {};
    cars.forEach((c) => { score[c.i] = 0; state.set(c.i, { ...c, dt: c.t, dir: 0, lock: 0, stun: 0, at: now0, windAt: -1e9, hitAt: -1e9 }); if (c.av) { const im = new Image(); im.src = `/avatar/${c.av}.jpg`; imgs[c.i] = im; } });
    let W = 0, dpr = 1, raf = 0, floor = null;
    const PT = (t) => { t = ((t % 4000) + 4000) % 4000; const sd = Math.floor(t / 1000), u = t - sd * 1000; return sd === 0 ? [u, 0] : sd === 1 ? [1000, u] : sd === 2 ? [1000 - u, 1000] : [0, 1000 - u]; };
    const NM = (t) => [[0, 1], [-1, 0], [0, -1], [1, 0]][Math.floor((((t % 4000) + 4000) % 4000) / 1000)];
    let I = 0, SC = 0;
    const px = (x, y) => [I + x * SC, I + y * SC];
    const size = () => {
      dpr = Math.min(2, window.devicePixelRatio || 1); W = Math.max(240, Math.min(app.clientWidth, 560, window.innerHeight - 290));
      cv.style.width = W + 'px'; cv.style.height = W + 'px'; cv.width = Math.round(W * dpr); cv.height = Math.round(W * dpr);
      I = W * 0.085; SC = (W - 2 * I) / 1000;
      floor = document.createElement('canvas'); floor.width = cv.width; floor.height = cv.height;           // the tiled floor never changes: draw it once
      const f = floor.getContext('2d'); f.scale(dpr, dpr); const n = 10, ts = W / n;
      for (let r = 0; r < n; r++) for (let q = 0; q < n; q++) { f.fillStyle = (r + q) % 2 ? '#f7e6bd' : '#fff3d1'; f.fillRect(q * ts, r * ts, ts + 1, ts + 1); }
      f.strokeStyle = 'rgba(120,70,20,.35)'; f.lineWidth = 2; f.setLineDash([6, 8]); f.strokeRect(I, I, W - 2 * I, W - 2 * I);   // the track everyone runs on
      f.setLineDash([]); f.lineWidth = 6; f.strokeStyle = '#8a5a2b'; f.strokeRect(1.5, 1.5, W - 3, W - 3);
      cars.forEach((c) => { if (c.lo === undefined) return;                                                        // two players: mark each one's own side
        const [x0, y0] = PT(c.lo), [x1, y1] = PT(c.hi === 1000 ? 999.9 : c.hi - 0.1); f.strokeStyle = c.i === myId ? 'rgba(255,190,40,.9)' : 'rgba(120,70,20,.55)'; f.lineWidth = 5; f.lineCap = 'round';
        f.beginPath(); f.moveTo(I + x0 * SC, I + y0 * SC); f.lineTo(I + x1 * SC, I + y1 * SC); f.stroke(); });
      f.font = `900 ${W * 0.11}px system-ui,sans-serif`; f.fillStyle = 'rgba(160,110,50,.18)'; f.textAlign = 'center'; f.fillText('PIE FIGHT', W / 2, W / 2 + W * 0.04);
    };
    size(); window.addEventListener('resize', size);

    const drawPie = (x, y, r, rot) => {
      ctx.save(); ctx.translate(x, y); ctx.rotate(rot);
      ctx.fillStyle = 'rgba(0,0,0,.2)'; ctx.beginPath(); ctx.ellipse(2, r * 0.9, r, r * 0.35, 0, 0, 7); ctx.fill();
      ctx.fillStyle = '#b8742a'; ctx.beginPath(); ctx.arc(0, 0, r, 0, 7); ctx.fill();
      ctx.strokeStyle = '#8a531a'; ctx.lineWidth = Math.max(1, r * 0.12); ctx.setLineDash([r * 0.25, r * 0.2]); ctx.beginPath(); ctx.arc(0, 0, r * 0.95, 0, 7); ctx.stroke(); ctx.setLineDash([]);
      ctx.fillStyle = '#fffaf0'; ctx.beginPath(); ctx.arc(0, 0, r * 0.78, 0, 7); ctx.fill();
      ctx.strokeStyle = '#f0dcc0'; ctx.lineWidth = Math.max(1, r * 0.1); ctx.beginPath(); ctx.arc(0, 0, r * 0.45, 0.4, 5.6); ctx.stroke();
      ctx.fillStyle = '#e53935'; ctx.beginPath(); ctx.arc(-r * 0.1, -r * 0.12, r * 0.18, 0, 7); ctx.fill();
      ctx.restore();
    };
    const splat = (x, y, r, seed) => {                                    // a cream splat on the floor
      ctx.save(); ctx.translate(x, y); ctx.fillStyle = seed % 3 === 0 ? '#ffe9f0' : seed % 3 === 1 ? '#fffdf5' : '#fff3c4'; ctx.strokeStyle = 'rgba(160,110,50,.25)'; ctx.lineWidth = 1;
      ctx.beginPath(); for (let k = 0; k < 9; k++) { const a = (k / 9) * Math.PI * 2, rr = r * (0.7 + ((seed * (k + 3)) % 7) / 10); ctx.lineTo(Math.cos(a) * rr, Math.sin(a) * rr); } ctx.closePath(); ctx.fill(); ctx.stroke();
      for (let k = 0; k < 4; k++) { const a = (k * 1.7 + seed), d = r * 1.25; ctx.beginPath(); ctx.arc(Math.cos(a) * d, Math.sin(a) * d, r * 0.18, 0, 7); ctx.fill(); }
      ctx.restore();
    };
    const drawHead = (c, now) => {
      const [bx, by] = PT(c.dt), nrm = NM(c.dt), [cx, cy] = px(bx, by), hw = W * 0.115, hh = hw * 1.28;
      const wind = now - c.windAt, windP = wind / 1500;
      let lean = 0; if (windP >= 0 && windP < 1) lean = (wind < 350 ? -(wind / 350) * 0.5 : Math.sin(Math.min(1, (wind - 350) / 250) * Math.PI) * 1.1) * hw * 0.22;   // pulls back, then lunges at the throw
      const x = cx + nrm[0] * lean * 1.0, y = cy + nrm[1] * lean;
      const hitAge = Math.max(0, now - c.hitAt), stunned = now - c.hitAt < 1400, mineC = c.i === myId;      // (the hit message can arrive a hair before the next frame: never go negative)
      // arm + pie held while winding up
      if (wind >= 0 && wind < 350) { const ax = x + nrm[0] * hh * 0.62, ay = y + nrm[1] * hh * 0.62; ctx.strokeStyle = '#f2c9a0'; ctx.lineWidth = hw * 0.16; ctx.lineCap = 'round'; ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(ax, ay); ctx.stroke(); drawPie(ax, ay, hw * 0.34, wind / 90); }
      ctx.save(); if (stunned) ctx.translate(Math.sin(now / 30) * 1.5, 0);
      ctx.fillStyle = 'rgba(0,0,0,.18)'; ctx.beginPath(); ctx.ellipse(x + 2, y + hh * 0.46, hw * 0.45, hh * 0.12, 0, 0, 7); ctx.fill();
      ctx.save(); ctx.beginPath(); ctx.ellipse(x, y, hw / 2, hh / 2, 0, 0, 7); ctx.clip();
      const im = imgs[c.i]; if (im && im.complete && im.naturalWidth) ctx.drawImage(im, x - hw / 2, y - hh / 2, hw, hh); else { ctx.fillStyle = '#c89a6b'; ctx.fillRect(x - hw / 2, y - hh / 2, hw, hh); }
      if (stunned) {                                                      // cream in the face
        const k = Math.min(1, hitAge / 150); ctx.fillStyle = '#fffdf5'; ctx.beginPath(); ctx.arc(x, y - hh * 0.04, hw * 0.46 * k, 0, 7); ctx.fill();
        ctx.beginPath(); ctx.arc(x - hw * 0.28, y + hh * 0.1, hw * 0.2 * k, 0, 7); ctx.arc(x + hw * 0.3, y - hh * 0.2, hw * 0.18 * k, 0, 7); ctx.fill();
        ctx.fillStyle = '#fff'; for (let j = 0; j < 3; j++) { const dx = x - hw * 0.3 + j * hw * 0.3, drip = (hh * 0.35) * Math.min(1, hitAge / 900); ctx.beginPath(); ctx.roundRect(dx - hw * 0.05, y, hw * 0.1, drip * (0.6 + 0.4 * ((j * 7) % 3) / 2), hw * 0.05); ctx.fill(); }
        ctx.fillStyle = '#e53935'; ctx.beginPath(); ctx.arc(x + hw * 0.05, y - hh * 0.3, hw * 0.07, 0, 7); ctx.fill();
      }
      ctx.restore();
      ctx.lineWidth = mineC ? 3 : 2; ctx.strokeStyle = mineC ? '#ffd35a' : 'rgba(255,255,255,.9)'; ctx.beginPath(); ctx.ellipse(x, y, hw / 2, hh / 2, 0, 0, 7); ctx.stroke();
      ctx.restore();
      if (stunned) { ctx.font = `${hw * 0.3}px system-ui`; ctx.textAlign = 'center'; for (let j = 0; j < 3; j++) { const a = now / 160 + j * 2.1; ctx.fillText('✨', x + Math.cos(a) * hw * 0.55, y - hh * 0.55 + Math.sin(a) * 4); } }
      // reload ring around the head while the 1.5 s freeze runs
      if (windP >= 0 && windP < 1) { ctx.strokeStyle = 'rgba(255,170,30,.95)'; ctx.lineWidth = 3; ctx.beginPath(); ctx.arc(x, y, hh * 0.62, -Math.PI / 2, -Math.PI / 2 + (1 - windP) * Math.PI * 2); ctx.stroke(); }
      // name tag toward the middle of the arena
      ctx.font = `800 ${Math.max(9, W * 0.028)}px system-ui,sans-serif`; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
      const lx = x + nrm[0] * (hh * 0.78), ly = y + nrm[1] * (hh * 0.78); const label = mineC ? 'YOU' : c.name.slice(0, 9); const tw = ctx.measureText(label).width;
      ctx.fillStyle = mineC ? '#ffd35a' : 'rgba(40,20,0,.7)'; ctx.beginPath(); ctx.roundRect(lx - tw / 2 - 5, ly - 8, tw + 10, 16, 8); ctx.fill(); ctx.fillStyle = mineC ? '#3a2400' : '#fff'; ctx.fillText(label, lx, ly + 0.5);
    };

    // ---- controls: ◀ / ▶ are held, THROW is tapped (or A/D/arrow keys and space)
    let L = false, R = false, lastD = 0;
    const upd = () => { const d = (L ? 1 : 0) - (R ? 1 : 0); if (d !== lastD) { lastD = d; send({ action: 'pfmove', d }); } };       // left = clockwise around the arena
    const hold = (el, set) => { el.addEventListener('pointerdown', (e) => { e.preventDefault(); try { el.setPointerCapture(e.pointerId); } catch (x) { } set(true); el.classList.add('held'); upd(); });
      ['pointerup', 'pointercancel', 'lostpointercapture'].forEach((n) => el.addEventListener(n, () => { set(false); el.classList.remove('held'); upd(); })); el.addEventListener('contextmenu', (e) => e.preventDefault()); };
    hold(document.getElementById('pfl'), (v) => { L = v; }); hold(document.getElementById('pfr'), (v) => { R = v; });
    const doThrow = () => send({ action: 'pfthrow' });
    tbtn.addEventListener('pointerdown', (e) => { e.preventDefault(); tbtn.classList.add('held'); doThrow(); });
    ['pointerup', 'pointercancel', 'pointerleave'].forEach((n) => tbtn.addEventListener(n, () => tbtn.classList.remove('held'))); tbtn.addEventListener('contextmenu', (e) => e.preventDefault());
    const kd = (e) => { if (e.repeat) return; if (['ArrowLeft', 'KeyA'].includes(e.code)) { L = true; upd(); } else if (['ArrowRight', 'KeyD'].includes(e.code)) { R = true; upd(); } else if (['Space', 'Enter', 'ArrowUp', 'KeyW'].includes(e.code)) { e.preventDefault(); doThrow(); } };
    const ku = (e) => { if (['ArrowLeft', 'KeyA'].includes(e.code)) { L = false; upd(); } else if (['ArrowRight', 'KeyD'].includes(e.code)) { R = false; upd(); } };
    document.addEventListener('keydown', kd); document.addEventListener('keyup', ku);

    const hud = () => { document.getElementById('pfme').textContent = `You: ${score[myId] || 0}`; const top = Object.entries(score).sort((a, b) => b[1] - a[1])[0]; const c = top && cars.find((x) => x.i === +top[0]); document.getElementById('pflead').textContent = c && top[1] > 0 ? `👑 ${c.name} ${top[1]}` : ''; };
    const frame = (now) => {
      raf = requestAnimationFrame(frame);
      state.forEach((c) => {                                              // smooth the 30 Hz snapshots (and run around corners, never jumping)
        const age = Math.min(100, now - c.at) / 1000, raw = c.t + (c.lock > 0 ? 0 : c.dir * 520 * age);
        if (c.lo !== undefined) c.dt += (Math.max(c.lo, Math.min(c.hi, raw)) - c.dt) * 0.5;                       // confined to one side: no wrapping
        else { const est = (raw + 4000) % 4000; c.dt = (c.dt + (((est - c.dt + 6000) % 4000) - 2000) * 0.5 + 4000) % 4000; }
      });
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0); ctx.drawImage(floor, 0, 0, W, W);
      splats.forEach((s) => { const [sx, sy] = px(s.x, s.y); splat(sx, sy, s.r * W / 360, s.seed); });
      pies.forEach((p) => { const e = (now - p.t0) / 1000, x = p.x + p.dx * p.sp * e, y = p.y + p.dy * p.sp * e; const [sx, sy] = px(x, y); drawPie(sx, sy, W * 0.034, e * 14); });
      const order = [...state.values()].sort((a, b) => PT(a.dt)[1] - PT(b.dt)[1]); order.forEach((c) => drawHead(c, now));
      for (let k = floats.length - 1; k >= 0; k--) { const f = floats[k], a = (now - f.t0) / 1100; if (a >= 1) { floats.splice(k, 1); continue; } const [fx, fy] = px(f.x, f.y);
        ctx.globalAlpha = 1 - a; ctx.font = `900 ${W * 0.07}px system-ui,sans-serif`; ctx.textAlign = 'center'; ctx.lineWidth = 4; ctx.strokeStyle = '#fff'; ctx.strokeText(f.text, fx, fy - a * 40); ctx.fillStyle = f.color; ctx.fillText(f.text, fx, fy - a * 40); ctx.globalAlpha = 1; }
      bar.style.width = Math.max(0, 100 - ((now - now0) / g.ms) * 100) + '%';
      const my = state.get(myId), cd = my ? Math.max(0, 1 - (now - my.windAt) / 1500) : 0; tbtn.style.setProperty('--cd', (cd * 100).toFixed(0) + '%'); tbtn.classList.toggle('cool', cd > 0);
    };
    raf = requestAnimationFrame(frame); hud();

    live = {
      onEvent(ev) {
        const now = performance.now();
        if (ev.ev === 'pf') { for (const [i, t, lock, stun, dir] of ev.c) { const c = state.get(i); if (!c) continue; c.t = t; c.lock = lock; c.stun = stun; c.dir = dir; c.at = now; } }
        else if (ev.ev === 'pfwind') { const c = state.get(ev.i); if (c) c.windAt = now; }
        else if (ev.ev === 'pfpie') { pies.set(ev.id, { x: ev.x, y: ev.y, dx: ev.dx, dy: ev.dy, sp: ev.sp, t0: now - 20 }); Sfx.play('pie', ev.i === myId ? 1 : 0.45); }
        else if (ev.ev === 'pfland') { pies.delete(ev.id); splats.push({ x: ev.x, y: ev.y, r: 14 + (ev.id % 4) * 3, seed: ev.id }); if (splats.length > 60) splats.shift(); Sfx.play('splat', 0.7); }
        else if (ev.ev === 'pfhit') {
          pies.delete(ev.id); Object.assign(score, ev.sc); hud();
          const v = state.get(ev.to), by = state.get(ev.by); if (v) v.hitAt = now;
          floats.push({ x: ev.x, y: ev.y, text: '-1', color: '#e53935', t0: now });
          if (by) { const [bx, by2] = PT(by.dt); floats.push({ x: bx, y: by2, text: '+1', color: '#2ecc71', t0: now }); }
          Sfx.play('splat', 1);
          if (ev.to === myId) { app.classList.remove('shake'); void app.offsetWidth; app.classList.add('shake'); Sfx.play('bonk'); } else if (ev.by === myId) Sfx.play('mine');
        } else if (ev.ev === 'pfsync') {
          Object.assign(score, ev.sc); pies.clear(); ev.pies.forEach((p) => pies.set(p.id, { x: p.x, y: p.y, dx: p.dx, dy: p.dy, sp: p.sp, t0: now })); hud();
        }
      },
      stop() { cancelAnimationFrame(raf); window.removeEventListener('resize', size); document.removeEventListener('keydown', kd); document.removeEventListener('keyup', ku); if (lastD) send({ action: 'pfmove', d: 0 }); },
    };
  }

  // ---- Hot Potato: players stand in a ring; the holder taps someone to throw them the bomb; whoever holds it when it blows is out ----
  function renderBomb() {
    const g = S.mini, me = S.you.name, cars = g.cars, n = cars.length, mine = cars.find((c) => c.name === me), myId = mine ? mine.i : -1;
    let holder = g.holder, alive = new Set(g.alive), from = -1, hot = false, gotAt = 0, tickT = 0;
    const hs = n <= 6 ? 78 : n <= 9 ? 64 : n <= 14 ? 50 : 38;
    const posOf = (k) => { const a = (k / n) * Math.PI * 2 - Math.PI / 2; return [50 + 38 * Math.cos(a), 50 + 38 * Math.sin(a)]; };
    app.innerHTML = `<div class="hud rchud"><span id="bstat"></span><span id="bleft"></span></div>
      <div class="ring" id="ring" style="--hs:${hs}px">${cars.map((c, k) => { const [x, y] = posOf(k); return `<button class="bh" data-i="${c.i}" style="left:${x}%;top:${y}%">${faceImg(c.av, 'bface')}<span class="bn">${esc(c.name)}</span></button>`; }).join('')}
        <div class="bomb gone" id="bomb">💣</div><div class="rmsg" id="rmsg"></div></div>`;
    const ring = document.getElementById('ring'), bomb = document.getElementById('bomb'), heads = [...ring.querySelectorAll('.bh')];
    const idxPos = new Map(cars.map((c, k) => [c.i, posOf(k)]));
    const nameOf = (i) => (cars.find((c) => c.i === i) || {}).name || '?';
    const sync = () => {
      heads.forEach((h) => { const i = +h.dataset.i; h.classList.toggle('out', !alive.has(i)); h.classList.toggle('me', i === myId); h.classList.toggle('has', i === holder);
        h.classList.toggle('target', holder === myId && alive.has(i) && i !== myId && !(i === from && alive.size > 2)); });
      const pos = idxPos.get(holder);
      if (pos) { bomb.style.left = pos[0] + '%'; bomb.style.top = pos[1] + '%'; bomb.classList.remove('gone'); } else bomb.classList.add('gone');
      bomb.classList.toggle('hot', hot && holder !== -1);
      const st = document.getElementById('bstat');
      st.textContent = !alive.has(myId) ? '💀 You\'re out — watch!' : holder === myId ? '💣 YOU have the bomb! Tap someone!' : holder === -1 ? '…' : `💣 ${nameOf(holder)} has the bomb`;
      st.classList.toggle('mine', holder === myId && alive.has(myId));
      document.getElementById('bleft').textContent = `${alive.size} left`;
    };
    const tick = () => { if (holder !== -1) Sfx.play('tick'); tickT = setTimeout(tick, hot ? 170 : 520); };    // faster ticking once the fuse is nearly gone
    sync(); tick();
    ring.addEventListener('click', (e) => {
      const h = e.target.closest('.bh'); if (!h || holder !== myId || !alive.has(myId)) return;
      const i = +h.dataset.i; if (i === myId || !alive.has(i) || Date.now() - gotAt < 360) return;
      if (i === from && alive.size > 2) { document.getElementById('rmsg').textContent = "Can't throw it straight back!"; setTimeout(() => { document.getElementById('rmsg').textContent = ''; }, 900); return; }
      send({ action: 'bpass', to: i });
    });
    live = {
      onEvent(ev) {
        if (ev.ev === 'bstate') { holder = ev.holder; alive = new Set(ev.alive); from = -1; hot = false; gotAt = Date.now(); clearTimeout(tickT); tick(); sync(); if (holder === myId) { Sfx.play('pop'); try { navigator.vibrate && navigator.vibrate(60); } catch (e) { } } }
        else if (ev.ev === 'bpass') { holder = ev.to; from = ev.from; gotAt = Date.now(); Sfx.play('whoosh'); sync(); if (holder === myId) { Sfx.play('pop'); try { navigator.vibrate && navigator.vibrate(60); } catch (e) { } } }
        else if (ev.ev === 'bwarn') { hot = true; clearTimeout(tickT); tick(); sync(); }
        else if (ev.ev === 'bboom') {
          alive.delete(ev.i); holder = -1; hot = false; Sfx.play('crash'); clearTimeout(tickT);
          const h = heads.find((x) => +x.dataset.i === ev.i); if (h) { h.classList.add('boom'); setTimeout(() => h.classList.remove('boom'), 1100); }
          if (ev.i === myId) bigX("💥 BOOM! You're out"); else app.classList.add('shake'), setTimeout(() => app.classList.remove('shake'), 460);
          sync(); document.getElementById('rmsg').textContent = ev.left > 1 ? `${nameOf(ev.i)} is out!` : '';
          setTimeout(() => { const r = document.getElementById('rmsg'); if (r) r.textContent = ''; }, 1700);
        }
      },
      stop() { clearTimeout(tickT); },
    };
  }

  // ---- Copy Cat: watch the pads light up in order, then tap the same pattern; the pattern grows every round ----
  function renderCopy() {
    const g = S.mini, me = S.you.name, cars = g.cars, mine = cars.find((c) => c.name === me), myId = mine ? mine.i : -1;
    const ICONS = ['▲', '●', '■', '★'], ROW = 46;
    let alive = new Set(g.alive), phase = 'wait', round = 0, seq = [], got = 0, done = false, raf = 0, limitAt = 0, limitMs = 1;
    const timers = [], total = {}, fin = {}, lastPos = {};               // total = points this match; fin = who has finished THIS round (rank + points)
    cars.forEach((c) => { total[c.i] = 0; });
    app.innerHTML = `<div class="timer"><div id="bar"></div></div>
      <div class="hud rchud"><span id="ccstat">Get ready…</span><span id="ccinfo"></span></div>
      <div class="pads" id="pads">${[0, 1, 2, 3].map((i) => `<button class="pad p${i}" data-p="${i}" disabled><span>${ICONS[i]}</span></button>`).join('')}</div>
      <div class="cclb-h"><span>Leaderboard</span><span class="muted">this match</span></div>
      <div class="cclb" id="cclb" style="height:${cars.length * ROW}px">${cars.map((c) => `<div class="srow cc" data-i="${c.i}">
          <div class="rk"><span class="rkn">–</span></div>${faceImg(c.av, 'cwface')}<div class="nm">${esc(c.name)}${c.i === myId ? ' <small>(you)</small>' : ''}</div>
          <div class="ccs"></div><div class="pts"><span class="sc">0</span></div></div>`).join('')}</div>
      <div class="ccmsg" id="ccmsg"></div>`;
    const pads = [...document.querySelectorAll('.pad')], bar = document.getElementById('bar'), lb = document.getElementById('cclb');
    const rowEl = new Map([...lb.querySelectorAll('.srow')].map((e) => [+e.dataset.i, e]));
    const stat = (t, cls = '') => { const el = document.getElementById('ccstat'); el.textContent = t; el.className = cls; };
    const canTap = () => phase === 'input' && alive.has(myId) && !done;
    const setPads = () => pads.forEach((b) => { b.disabled = !canTap(); });
    // ---- leaderboard: sorted by points this match; rows glide to their new place whenever the scores change
    function board(first) {
      const order = [...cars].sort((a, b) => (total[b.i] - total[a.i]) || (a.i - b.i));
      order.forEach((c, pos) => {
        const el = rowEl.get(c.i), prev = lastPos[c.i];
        el.style.transform = `translateY(${pos * ROW}px)`;
        const rk = el.querySelector('.rkn');
        if (prev !== pos) {
          rk.textContent = pos + 1;
          if (prev !== undefined && !first) {                                        // moved: flip the rank number up or down and flash the row
            const dir = pos < prev ? 'up' : 'down';
            rk.classList.remove('flip-up', 'flip-down'); void rk.offsetWidth; rk.classList.add('flip-' + dir);
            el.classList.remove('moved-up', 'moved-down'); void el.offsetWidth; el.classList.add('moved-' + dir);
            el.style.zIndex = dir === 'up' ? 3 : 1; setTimeout(() => { el.classList.remove('moved-up', 'moved-down'); el.style.zIndex = ''; }, 1100);
          }
          lastPos[c.i] = pos;
        }
        el.querySelector('.sc').textContent = total[c.i];
        el.classList.toggle('me', c.i === myId); el.classList.toggle('leader', pos === 0 && total[c.i] > 0);
        const s = el.querySelector('.ccs'), f = fin[c.i];
        if (!alive.has(c.i)) { s.className = 'ccs out'; s.textContent = '✕ out'; }
        else if (f) { s.className = 'ccs done'; s.innerHTML = `✓ ${ordinal(f.rank)} <b>+${f.pts}</b>`; }
        else if (phase === 'input') { s.className = 'ccs wait'; s.textContent = '⏳ playing…'; }
        else { s.className = 'ccs'; s.textContent = ''; }
        el.classList.toggle('isout', !alive.has(c.i));
      });
    }
    const applyScores = (sc) => { if (sc) cars.forEach((c) => { if (sc[c.i] !== undefined) total[c.i] = sc[c.i]; }); };
    const light = (i, ms) => { const b = pads[i]; if (!b) return; b.classList.add('lit'); Sfx.play('pad', i); timers.push(setTimeout(() => b.classList.remove('lit'), ms)); };
    pads.forEach((b) => b.addEventListener('pointerdown', (e) => {
      e.preventDefault(); if (!canTap()) return; const i = +b.dataset.p;
      light(i, 160); send({ action: 'cctap', pad: i });
    }));
    const frame = (now) => { raf = requestAnimationFrame(frame); bar.style.width = phase === 'input' ? Math.max(0, 100 - ((now - limitAt) / limitMs) * 100) + '%' : '100%'; };
    raf = requestAnimationFrame(frame);
    const startInput = (limit, startedAt) => { phase = 'input'; limitMs = limit; limitAt = startedAt || performance.now(); setPads(); if (alive.has(myId) && !done) stat(`Your turn! ${got}/${seq.length}`, 'mine'); board(); };
    board(true);
    live = {
      onEvent(ev) {
        if (ev.ev === 'ccround') {
          round = ev.r; seq = ev.seq; alive = new Set(ev.alive); got = 0; done = false; phase = 'show'; applyScores(ev.scores);
          Object.keys(fin).forEach((k) => delete fin[k]); setPads(); board();
          document.getElementById('ccinfo').textContent = `Round ${round}`; stat(alive.has(myId) ? '👀 Watch the pattern…' : '👀 You\'re out — watch!');
          ev.seq.forEach((pad, k) => timers.push(setTimeout(() => light(pad, ev.step * 0.72), ev.startIn + k * ev.step)));
        } else if (ev.ev === 'ccgo') { startInput(ev.limit); }
        else if (ev.ev === 'ccok') { got = ev.n; stat(`Your turn! ${got}/${seq.length}`, 'mine'); }
        else if (ev.ev === 'ccdone') { done = true; setPads(); stat(`✅ ${ordinal(ev.rank)} to finish! +${ev.pts}`, 'ok'); Sfx.play(ev.rank === 1 ? 'win' : 'correct'); }
        else if (ev.ev === 'ccprog') {                                               // someone finished: their points go up and the leaderboard re-sorts live
          fin[ev.i] = { rank: ev.rank, pts: ev.pts }; total[ev.i] = ev.total; board();
          if (ev.i !== myId) Sfx.play('pop');
        }
        else if (ev.ev === 'ccwrong') { Sfx.play('buzzer'); bigX('Wrong!'); }
        else if (ev.ev === 'ccout') {
          alive.delete(ev.i); board();
          if (ev.i === myId) { setPads(); stat("You're out — watch the others!"); if (ev.why === 'slow') { Sfx.play('buzzer'); bigX("Too slow!"); } }
        } else if (ev.ev === 'ccend') { phase = 'between'; alive = new Set(ev.alive); applyScores(ev.scores); setPads(); board(); }
        else if (ev.ev === 'ccsync') {                                    // we reconnected mid-game
          round = ev.r; seq = ev.seq; alive = new Set(ev.alive); done = ev.done; got = ev.i; phase = ev.phase; applyScores(ev.scores);
          Object.keys(fin).forEach((k) => delete fin[k]); (ev.finished || []).forEach((f) => { fin[f.i] = { rank: f.rank, pts: f.pts }; });
          document.getElementById('ccinfo').textContent = `Round ${round}`;
          if (ev.phase === 'input') startInput(5000); else { setPads(); board(); stat(alive.has(myId) ? '👀 Watch the pattern…' : "You're out — watch the others!"); }
        }
      },
      stop() { cancelAnimationFrame(raf); timers.forEach(clearTimeout); },
    };
  }

  // ---- Picture This: the drawer sketches on a shared white board; everyone else watches live and types guesses ----
  const PAL = ['#1b1b1b', '#e53935', '#fb8c00', '#fdd835', '#43a047', '#1e88e5', '#8e24aa', '#6d4c41', '#ffffff'];   // last one is the eraser
  const SIZES = [5, 12, 26];
  function renderPic() {
    const g = S.mini, pic = g.pic, me = S.you.name, drawer = S.players.find((x) => x.name === pic.drawer) || { name: pic.drawer }, isDrawer = pic.you;
    const crowd = S.players.filter((x) => x.name !== pic.drawer);
    const wob = () => `--t:${(2.2 + Math.random() * 2.4).toFixed(2)}s;--d:-${(Math.random() * 3).toFixed(2)}s;--r:${(1 + Math.random() * 2.5).toFixed(1)}deg;--x:${(2 + Math.random() * 4).toFixed(1)}px`;
    const artist = `<div class="artist" id="artist"><div class="toon-in">${faceImg(drawer.av, 'thead')}
        <svg class="tbody" viewBox="0 0 60 64" aria-hidden="true" style="--shirt:#ff9a0a">
          <g class="leg l"><line x1="25" y1="36" x2="25" y2="57"/><ellipse cx="26.5" cy="60" rx="6" ry="3.5"/></g><g class="leg r"><line x1="35" y1="36" x2="35" y2="57"/><ellipse cx="36.5" cy="60" rx="6" ry="3.5"/></g>
          <rect class="torso" x="17" y="4" width="26" height="36" rx="10"/>
          <g class="arm l"><line x1="18" y1="11" x2="18" y2="36"/><circle cx="18" cy="38" r="4.8"/></g>
          <g class="arm r" id="penarm"><line x1="42" y1="11" x2="42" y2="36"/><circle cx="42" cy="38" r="4.8"/><line class="marker" x1="42" y1="40" x2="42" y2="52"/></g>
        </svg></div></div>`;
    app.innerHTML = `<div class="timer"><div id="bar"></div></div>
      <div class="pichead">${isDrawer ? `<span class="muted">Draw this</span><b class="picword">${esc(pic.word.toUpperCase())}</b>` : '<div class="hint" id="hint"></div>'}</div>
      <div class="easel"><canvas id="pcv"></canvas></div>
      <div class="stagerow">${isDrawer ? '' : artist}<div class="audience" id="aud">${crowd.map((x) => `<div class="aud${x.name === me ? ' me' : ''}" data-name="${esc(x.name)}" style="${wob()}">${faceImg(x.av, 'audface')}<span class="chk">✓</span></div>`).join('')}</div></div>
      <div class="feed" id="feed"></div>
      <div id="picctl"></div>`;
    const cv = document.getElementById('pcv'), ctx = cv.getContext('2d'), bar = document.getElementById('bar'), feed = document.getElementById('feed'), ctl = document.getElementById('picctl');
    const strokes = [], byId = new Map(); let scale = 1, dpr = 1, raf = 0, got = false, tickAt = -1;
    const t0 = performance.now(), timers = [];
    const size = () => {
      dpr = Math.min(2, window.devicePixelRatio || 1);
      const w = Math.min(app.clientWidth, 560), h = Math.round(w * 0.8);
      cv.style.width = w + 'px'; cv.style.height = h + 'px'; cv.width = Math.round(w * dpr); cv.height = Math.round(h * dpr); scale = (w * dpr) / 1000; redraw();
    };
    const line = (st, from) => {
      ctx.strokeStyle = ctx.fillStyle = PAL[st.c] || PAL[0]; ctx.lineWidth = st.w * scale; ctx.lineCap = ctx.lineJoin = 'round';
      const pts = st.pts;
      if (pts.length === 2) { ctx.beginPath(); ctx.arc(pts[0] * scale, pts[1] * scale, st.w * scale / 2, 0, 7); ctx.fill(); return; }
      ctx.beginPath(); ctx.moveTo(pts[Math.max(0, from - 2)] * scale, pts[Math.max(0, from - 2) + 1] * scale);
      for (let i = Math.max(0, from - 2) + 2; i < pts.length; i += 2) ctx.lineTo(pts[i] * scale, pts[i + 1] * scale);
      ctx.stroke();
    };
    function redraw() { ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.fillStyle = '#fff'; ctx.fillRect(0, 0, cv.width, cv.height); strokes.forEach((st) => line(st, 0)); }
    size(); window.addEventListener('resize', size);
    const addFeed = (html, cls = '') => { const d = document.createElement('div'); d.className = 'fl ' + cls; d.innerHTML = html; feed.appendChild(d); while (feed.children.length > 4) feed.firstChild.remove(); };

    // ---- the artist slides under the pen and waves the marker while strokes arrive
    const artistEl = document.getElementById('artist'); let drawingUntil = 0;
    const penAt = (x) => { if (!artistEl) return; artistEl.style.left = Math.max(12, Math.min(88, x / 10)) + '%'; artistEl.classList.add('drawing'); drawingUntil = performance.now() + 380; };
    const penTimer = setInterval(() => { if (artistEl && performance.now() > drawingUntil) artistEl.classList.remove('drawing'); }, 150); timers.push(penTimer);

    // ---- drawer: tools + pointer drawing
    let color = 0, sizeIdx = 1, seq = 0;
    if (isDrawer) {
      ctl.innerHTML = `<div class="tools"><div class="pal">${PAL.map((c, i) => `<button class="sw${i === 0 ? ' on' : ''}${i === 8 ? ' erase' : ''}" data-c="${i}" style="background:${c}" aria-label="${i === 8 ? 'Eraser' : 'Colour'}">${i === 8 ? '⌫' : ''}</button>`).join('')}</div>
        <div class="pal2"><span class="sz">${SIZES.map((z, i) => `<button class="szb${i === 1 ? ' on' : ''}" data-z="${i}"><i style="width:${6 + i * 5}px;height:${6 + i * 5}px"></i></button>`).join('')}</span>
        <button class="tl" id="undo">↶ Undo</button><button class="tl" id="clr">🗑 Clear</button></div></div>`;
      ctl.querySelectorAll('.sw').forEach((b) => (b.onclick = () => { color = +b.dataset.c; ctl.querySelectorAll('.sw').forEach((x) => x.classList.toggle('on', x === b)); }));
      ctl.querySelectorAll('.szb').forEach((b) => (b.onclick = () => { sizeIdx = +b.dataset.z; ctl.querySelectorAll('.szb').forEach((x) => x.classList.toggle('on', x === b)); }));
      document.getElementById('undo').onclick = () => { if (strokes.length) { strokes.pop(); redraw(); send({ action: 'draw', op: 'undo' }); } };
      document.getElementById('clr').onclick = () => { if (strokes.length) { strokes.length = 0; redraw(); send({ action: 'draw', op: 'clear' }); } };
      let cur = null, pend = [], flushT = 0, lastX = -9, lastY = -9;
      const pos = (e) => { const r = cv.getBoundingClientRect(); return [Math.max(0, Math.min(1000, Math.round((e.clientX - r.left) / r.width * 1000))), Math.max(0, Math.min(800, Math.round((e.clientY - r.top) / r.height * 800)))]; };
      const flush = () => { flushT = 0; if (cur && pend.length) { send({ action: 'draw', op: 'seg', id: cur.id, c: cur.c, w: cur.w, pts: pend.splice(0, 160) }); } };
      cv.addEventListener('pointerdown', (e) => {
        e.preventDefault(); try { cv.setPointerCapture(e.pointerId); } catch (x) { }
        const [x, y] = pos(e); cur = { id: ++seq, c: color, w: color === 8 ? SIZES[sizeIdx] * 1.7 : SIZES[sizeIdx], pts: [x, y] }; strokes.push(cur); line(cur, 0);
        pend = [x, y]; lastX = x; lastY = y; flush();
      });
      cv.addEventListener('pointermove', (e) => {
        if (!cur) return; e.preventDefault();
        for (const ev of (e.getCoalescedEvents ? e.getCoalescedEvents() : [e])) {
          const [x, y] = pos(ev); if (Math.abs(x - lastX) + Math.abs(y - lastY) < 3) continue;
          const from = cur.pts.length; cur.pts.push(x, y); pend.push(x, y); lastX = x; lastY = y; line(cur, from);
        }
        if (!flushT) flushT = setTimeout(flush, 55);
      });
      const end = () => { if (cur) { flush(); cur = null; } };
      ['pointerup', 'pointercancel', 'lostpointercapture'].forEach((n) => cv.addEventListener(n, end));
      cv.addEventListener('contextmenu', (e) => e.preventDefault());
    } else {
      ctl.innerHTML = `<form class="guessbar" id="gform"><input id="gin" placeholder="Type your guess…" maxlength="30" autocomplete="off" autocapitalize="none" autocorrect="off" spellcheck="false"><button id="gsend">Guess</button></form>`;
      const form = document.getElementById('gform'), input = document.getElementById('gin');
      form.onsubmit = (e) => { e.preventDefault(); const t = input.value.trim(); if (!t) return; send({ action: 'guess', text: t }); input.value = ''; input.focus(); };
    }

    const setHint = (h) => { const el = document.getElementById('hint'); if (!el) return;
      el.innerHTML = `<div class="lts">${[...h].map((ch) => ch === ' ' ? '<i class="gap"></i>' : `<span class="lt${ch === '_' ? '' : ' shown'}">${ch === '_' ? '' : esc(ch.toUpperCase())}</span>`).join('')}</div><div class="muted small">${pic.len - (pic.hint.split(' ').length - 1)} letters${h.includes('_') ? '' : ''}</div>`; };
    if (!isDrawer) setHint(pic.hint);
    const frame = (now) => { raf = requestAnimationFrame(frame); bar.style.width = Math.max(0, 100 - ((now - t0) / g.ms) * 100) + '%';
      const left = Math.ceil((g.ms - (now - t0)) / 1000); if (!isDrawer && !got && left <= 5 && left > 0 && left !== tickAt) { tickAt = left; Sfx.play('tick'); } };
    raf = requestAnimationFrame(frame);

    live = {
      onEvent(ev) {
        if (ev.ev === 'pic' && !isDrawer) {
          if (ev.op === 'seg') {
            let st = byId.get(ev.id); if (!st) { st = { id: ev.id, c: ev.c, w: ev.w, pts: [] }; byId.set(ev.id, st); strokes.push(st); }
            const from = st.pts.length; st.pts.push(...ev.pts); line(st, from); penAt(ev.pts[ev.pts.length - 2]);
          } else if (ev.op === 'undo') { const st = strokes.pop(); if (st) byId.delete(st.id); redraw(); }
          else if (ev.op === 'clear') { strokes.length = 0; byId.clear(); redraw(); }
        } else if (ev.ev === 'picsync') {                      // we (re)connected mid-round: the server sends everything drawn so far
          strokes.length = 0; byId.clear();
          for (const st of ev.strokes) { const c = { id: st.id, c: st.c, w: st.w, pts: [...st.pts] }; strokes.push(c); byId.set(c.id, c); seq = Math.max(seq, c.id); }
          redraw();
        } else if (ev.ev === 'pichint') { if (!isDrawer) { setHint(ev.hint); addFeed('💡 A letter was revealed', 'sys'); } }
        else if (ev.ev === 'picguess') addFeed(`<b>${esc(ev.name)}</b>: ${esc(ev.text)}`);
        else if (ev.ev === 'picok') {
          addFeed(`🎉 <b>${esc(ev.name)}</b> got it!`, 'ok');
          const el = [...document.querySelectorAll('.aud')].find((e) => e.dataset.name === ev.name); if (el) { el.classList.add('got'); el.classList.remove('hop'); void el.offsetWidth; el.classList.add('hop'); }
          if (ev.name !== me) Sfx.play('pop');
        } else if (ev.ev === 'picmine') {
          got = true; Sfx.play('correct'); addFeed(`✅ You got it! <b>+${ev.pts}</b>`, 'ok');
          ctl.innerHTML = `<div class="gotit">✅ You got it! <b>+${ev.pts} points</b><div class="muted small">Keep watching the others…</div></div>`;
        } else if (ev.ev === 'picclose') addFeed('🔥 So close!', 'sys');
      },
      stop() { cancelAnimationFrame(raf); window.removeEventListener('resize', size); timers.forEach(clearInterval); try { window.__lastDrawing = cv.toDataURL('image/jpeg', 0.7); } catch (e) { window.__lastDrawing = null; } },
    };
    if (!isDrawer) setTimeout(() => { const i = document.getElementById('gin'); if (i) i.focus(); }, 100);
  }

  // ---- RC Mayhem: every player has their own lane on one canvas; the server runs the physics, we draw what it says ----
  const CAR_COLORS = ['#e53935', '#1e88e5', '#43a047', '#fb8c00', '#8e24aa', '#00acc1', '#f06292', '#6d4c41'];
  const ordinal = (n) => n + (['th', 'st', 'nd', 'rd'][(n % 100 > 10 && n % 100 < 14) ? 0 : n % 10 < 4 ? n % 10 : 0]);
  function renderRc() {
    const g = S.mini, rc = g.rc, me = S.you.name;
    app.innerHTML = `<div class="timer"><div id="bar"></div></div>
      <div class="hud rchud"><span id="rcpos"></span><span id="rcnote"></span></div>
      <canvas id="rcv"></canvas>
      <div class="rcpad"><button class="rcbtn go" id="gobtn">GO</button><button class="rcbtn jump" id="jumpbtn">JUMP</button></div>`;
    const cv = document.getElementById('rcv'), ctx = cv.getContext('2d'), bar = document.getElementById('bar');
    const cars = new Map(), imgs = {};
    rc.cars.forEach((c, k) => { cars.set(c.i, { ...c, color: CAR_COLORS[k % CAR_COLORS.length], x: 0, y: 0, v: 0, f: 0, st: 0, dx: 0, dy: 0, at: performance.now(), rank: 0 }); if (c.av) { const im = new Image(); im.src = `/avatar/${c.av}.jpg`; imgs[c.i] = im; } });
    const mine = rc.cars.find((c) => c.name === me), myId = mine ? mine.i : -1;
    let W = 0, H = 0, dpr = 1, raf = 0, clockOff = 0, haveClock = false, wasAir = false, wasStall = false, banner = null;
    const t0 = performance.now(), effects = [];
    const size = () => {
      dpr = Math.min(2, window.devicePixelRatio || 1);
      W = Math.min(app.clientWidth, 640); H = Math.max(240, Math.min(560, window.innerHeight - 255));
      cv.style.height = H + 'px'; cv.width = Math.round(W * dpr); cv.height = Math.round(H * dpr);
    };
    size(); window.addEventListener('resize', size);

    // ---- input: GO is held, JUMP is tapped (buttons or keyboard)
    let goDown = false;
    const setGo = (on) => { if (on !== goDown) { goDown = on; send({ action: 'rcgo', on }); document.getElementById('gobtn').classList.toggle('held', on); } };
    const jump = () => send({ action: 'rcjump' });
    const goB = document.getElementById('gobtn'), jB = document.getElementById('jumpbtn');
    [goB, jB].forEach((b) => { b.addEventListener('contextmenu', (e) => e.preventDefault()); });
    goB.addEventListener('pointerdown', (e) => { e.preventDefault(); try { goB.setPointerCapture(e.pointerId); } catch (x) { } setGo(true); });
    ['pointerup', 'pointercancel', 'lostpointercapture'].forEach((n) => goB.addEventListener(n, () => setGo(false)));
    jB.addEventListener('pointerdown', (e) => { e.preventDefault(); jB.classList.add('held'); jump(); });
    ['pointerup', 'pointercancel', 'pointerleave'].forEach((n) => jB.addEventListener(n, () => jB.classList.remove('held')));
    const kd = (e) => { if (e.repeat) return; if (['ArrowRight', 'KeyD', 'KeyL'].includes(e.code)) setGo(true); else if (['ArrowUp', 'Space', 'KeyW', 'KeyJ'].includes(e.code)) { e.preventDefault(); jump(); } };
    const ku = (e) => { if (['ArrowRight', 'KeyD', 'KeyL'].includes(e.code)) setGo(false); };
    document.addEventListener('keydown', kd); document.addEventListener('keyup', ku);

    const rcBall = (o, t) => { const p = (((t + o.ph) % o.per) + o.per) % o.per / o.per; return o.hm * 4 * p * (1 - p); };       // same bounce as the server
    const drawCar = (c, sx, gy, ppu, t, isMe) => {
      const L = 44 * ppu, Hh = 15 * ppu, wr = 7.5 * ppu, y = gy - c.dy * ppu;
      ctx.save(); ctx.translate(sx, y);
      if (c.dy > 2) { ctx.fillStyle = 'rgba(0,0,0,.22)'; ctx.beginPath(); ctx.ellipse(0, gy - y, L * 0.5, 3 * ppu, 0, 0, 7); ctx.fill(); }   // ground shadow
      ctx.rotate(c.tilt || 0);                         // nose follows the ramp slope / the flight path
      // wheels
      [-L * 0.3, L * 0.3].forEach((wx) => {
        ctx.fillStyle = '#1b1b1b'; ctx.beginPath(); ctx.arc(wx, -wr, wr, 0, 7); ctx.fill();
        ctx.strokeStyle = '#aaa'; ctx.lineWidth = Math.max(1, ppu); ctx.beginPath(); const a = c.dx * 0.12 / 1; ctx.moveTo(wx + Math.cos(a) * wr * 0.7, -wr + Math.sin(a) * wr * 0.7); ctx.lineTo(wx - Math.cos(a) * wr * 0.7, -wr - Math.sin(a) * wr * 0.7); ctx.stroke();
      });
      // body + cab
      ctx.fillStyle = c.color; ctx.beginPath(); ctx.roundRect(-L * 0.5, -wr * 2 - Hh * 0.55, L, Hh * 0.9, 4 * ppu); ctx.fill();
      ctx.fillStyle = 'rgba(255,255,255,.35)'; ctx.fillRect(-L * 0.45, -wr * 2 - Hh * 0.45, L * 0.9, 2 * ppu);
      ctx.fillStyle = '#222'; ctx.beginPath(); ctx.roundRect(-L * 0.2, -wr * 2 - Hh * 1.5, L * 0.46, Hh, 5 * ppu); ctx.fill();   // cab
      // driver's head
      const hr = 8.2 * ppu, hx = L * 0.03, hy = -wr * 2 - Hh * 1.02, im = imgs[c.i];
      ctx.save(); ctx.beginPath(); ctx.ellipse(hx, hy, hr * 0.8, hr, 0, 0, 7); ctx.clip();
      if (im && im.complete && im.naturalWidth) ctx.drawImage(im, hx - hr * 0.8, hy - hr, hr * 1.6, hr * 2); else { ctx.fillStyle = '#f2c9a0'; ctx.fillRect(hx - hr, hy - hr, hr * 2, hr * 2); }
      ctx.restore();
      ctx.strokeStyle = 'rgba(0,0,0,.35)'; ctx.lineWidth = Math.max(1, ppu * 0.8); ctx.beginPath(); ctx.ellipse(hx, hy, hr * 0.8, hr, 0, 0, 7); ctx.stroke();
      // antenna
      ctx.strokeStyle = '#333'; ctx.lineWidth = Math.max(1, ppu * 0.8); ctx.beginPath(); ctx.moveTo(-L * 0.42, -wr * 2 - Hh * 0.5); ctx.lineTo(-L * 0.5, -wr * 2 - Hh * 1.9); ctx.stroke();
      ctx.fillStyle = '#ffd400'; ctx.fillRect(-L * 0.5 - 1, -wr * 2 - Hh * 1.9, 8 * ppu, 4 * ppu);
      ctx.restore();
      // effects on the car
      if (c.f & 2) {                                   // engine off: smoke + countdown
        for (let k = 0; k < 4; k++) { const ph = ((t / 700) + k * 0.25) % 1; ctx.fillStyle = `rgba(70,70,70,${0.55 * (1 - ph)})`; ctx.beginPath(); ctx.arc(sx - L * 0.45 - ph * 14 * ppu, y - 12 * ppu - ph * 34 * ppu, (4 + ph * 8) * ppu, 0, 7); ctx.fill(); }
      } else if (c.f & 4) {                            // slowed: sparks
        ctx.fillStyle = '#ffb703'; for (let k = 0; k < 4; k++) { const ph = ((t / 200) + k * 0.25) % 1; ctx.fillRect(sx - L * 0.5 - ph * 16 * ppu, y - 6 * ppu - Math.sin(k * 7) * 6 * ppu, 2.5 * ppu, 2.5 * ppu); }
      } else if (c.v > 250) {                          // speed lines
        ctx.strokeStyle = 'rgba(255,255,255,.55)'; ctx.lineWidth = Math.max(1, ppu * .9); for (let k = 0; k < 3; k++) { const ly = y - (8 + k * 9) * ppu; ctx.beginPath(); ctx.moveTo(sx - L * 0.55, ly); ctx.lineTo(sx - L * 0.55 - (14 + k * 6) * ppu, ly); ctx.stroke(); }
      }
    };

    const drawLane = (c, y0, h, big, t) => {
      const ppu = big ? W / 540 : W / 720, gy = y0 + h * 0.8, camX = c.dx - (W * 0.24) / ppu;
      ctx.save(); ctx.beginPath(); ctx.rect(0, y0, W, h); ctx.clip();
      const sky = ctx.createLinearGradient(0, y0, 0, gy); sky.addColorStop(0, '#7cc8ff'); sky.addColorStop(1, '#dff3ff'); ctx.fillStyle = sky; ctx.fillRect(0, y0, W, h);
      ctx.fillStyle = '#9ad7a0';                                                           // far hills (parallax)
      for (let k = -1; k < 6; k++) { const hx = ((k * 260 - camX * 0.25) % 1560 + 1560) % 1560 - 260; ctx.beginPath(); ctx.moveTo(hx * ppu * 0.8, gy); ctx.quadraticCurveTo((hx + 130) * ppu * 0.8, gy - 50 * ppu, (hx + 260) * ppu * 0.8, gy); ctx.fill(); }
      ctx.fillStyle = '#9a6a3e'; ctx.fillRect(0, gy, W, y0 + h - gy);                      // dirt track
      ctx.fillStyle = '#7d5230'; ctx.fillRect(0, gy, W, 4 * ppu);
      ctx.fillStyle = 'rgba(0,0,0,.14)';
      for (let k = 0; k < 14; k++) { const dx = ((k * 90 - camX) % 1260 + 1260) % 1260; ctx.fillRect((dx - 90) * ppu, gy + (10 + (k % 3) * 9) * ppu, 30 * ppu, 3 * ppu); }
      const sxOf = (x) => (x - camX) * ppu;
      // start / finish
      if (sxOf(0) > -40 && sxOf(0) < W) { ctx.fillStyle = '#fff'; ctx.fillRect(sxOf(0), gy - 4 * ppu, 4 * ppu, 6 * ppu); }
      const fx = sxOf(rc.len);
      if (fx > -60 && fx < W + 60) {
        ctx.fillStyle = '#333'; ctx.fillRect(fx - 2, gy - 90 * ppu, 4, 90 * ppu);
        for (let r = 0; r < 4; r++) for (let q = 0; q < 6; q++) { ctx.fillStyle = (r + q) % 2 ? '#111' : '#fff'; ctx.fillRect(fx + q * 6 * ppu, gy - 90 * ppu + r * 6 * ppu, 6 * ppu, 6 * ppu); }
        for (let q = 0; q < 10; q++) { ctx.fillStyle = q % 2 ? '#111' : '#fff'; ctx.fillRect(fx - 3 * ppu + q * 3 * ppu, gy + 2, 3 * ppu, 8 * ppu); }
      }
      // obstacles
      for (const o of rc.track) {
        const sx = sxOf(o.x), sw = o.w * ppu; if (sx > W + 20 || sx + sw < -20) continue;
        if (o.k === 'log') {
          const lh = o.h * ppu; ctx.fillStyle = '#7b4a22'; ctx.beginPath(); ctx.roundRect(sx, gy - lh, sw, lh, lh * 0.45); ctx.fill();
          ctx.fillStyle = '#c99a63'; ctx.beginPath(); ctx.ellipse(sx + sw - lh * 0.3, gy - lh / 2, lh * 0.28, lh * 0.42, 0, 0, 7); ctx.fill();
          ctx.strokeStyle = '#5a3515'; ctx.lineWidth = Math.max(1, ppu); ctx.beginPath(); ctx.moveTo(sx + sw * 0.25, gy - lh * 0.8); ctx.lineTo(sx + sw * 0.5, gy - lh * 0.2); ctx.stroke();
        } else if (o.k === 'rock') {
          const rh = o.h * ppu; ctx.fillStyle = '#7d8590'; ctx.beginPath(); ctx.moveTo(sx, gy); ctx.lineTo(sx + sw * 0.12, gy - rh * 0.7); ctx.lineTo(sx + sw * 0.4, gy - rh); ctx.lineTo(sx + sw * 0.78, gy - rh * 0.8); ctx.lineTo(sx + sw, gy); ctx.closePath(); ctx.fill();
          ctx.fillStyle = 'rgba(255,255,255,.22)'; ctx.beginPath(); ctx.moveTo(sx + sw * 0.4, gy - rh); ctx.lineTo(sx + sw * 0.78, gy - rh * 0.8); ctx.lineTo(sx + sw * 0.55, gy - rh * 0.5); ctx.closePath(); ctx.fill();
          ctx.strokeStyle = '#4c525a'; ctx.lineWidth = Math.max(1, ppu); ctx.beginPath(); ctx.moveTo(sx + sw * 0.3, gy - rh * 0.4); ctx.lineTo(sx + sw * 0.45, gy - rh * 0.1); ctx.stroke();
        } else if (o.k === 'ramp') {                                                                                      // wedge: drive up it, fly off the high end
          const rh = o.h * ppu; ctx.fillStyle = '#5b6ee1'; ctx.beginPath(); ctx.moveTo(sx, gy); ctx.lineTo(sx + sw, gy - rh); ctx.lineTo(sx + sw, gy); ctx.closePath(); ctx.fill();
          ctx.strokeStyle = '#ffd23f'; ctx.lineWidth = Math.max(1.5, ppu * 2); ctx.beginPath(); ctx.moveTo(sx, gy); ctx.lineTo(sx + sw, gy - rh); ctx.stroke();
          ctx.strokeStyle = 'rgba(255,255,255,.35)'; ctx.lineWidth = Math.max(1, ppu); for (let q = 1; q < 5; q++) { const qx = sx + sw * q / 5; ctx.beginPath(); ctx.moveTo(qx, gy); ctx.lineTo(qx, gy - rh * q / 5); ctx.stroke(); }
        } else if (o.k === 'ball') {                                                                                      // bouncing ball: go under it or jump it
          const d = o.w * ppu, yb = rcBall(o, t) * ppu, bx = sx + d / 2, by = gy - yb - d / 2;
          ctx.fillStyle = `rgba(0,0,0,${0.25 * (1 - Math.min(1, yb / (110 * ppu)))})`; ctx.beginPath(); ctx.ellipse(bx, gy - ppu, d * 0.45, 3 * ppu, 0, 0, 7); ctx.fill();
          ctx.save(); ctx.beginPath(); ctx.arc(bx, by, d / 2, 0, 7); ctx.clip(); ctx.fillStyle = '#fff'; ctx.fillRect(bx - d / 2, by - d / 2, d, d);
          ctx.translate(bx, by); ctx.rotate((t / 300) % 6.283); ctx.fillStyle = '#e53935'; for (let q = 0; q < 3; q++) { ctx.rotate(2.094); ctx.beginPath(); ctx.moveTo(0, 0); ctx.arc(0, 0, d, -0.5, 0.1); ctx.closePath(); ctx.fill(); }
          ctx.restore(); ctx.strokeStyle = '#7a1c18'; ctx.lineWidth = Math.max(1, ppu); ctx.beginPath(); ctx.arc(bx, by, d / 2, 0, 7); ctx.stroke();
        } else if (o.k === 'spike') {                                                                                     // spike trap
          const n = Math.max(3, Math.round(o.w / 12)), tw = sw / n; ctx.fillStyle = '#8a8f98'; ctx.fillRect(sx, gy - 3 * ppu, sw, 3 * ppu);
          for (let q = 0; q < n; q++) { ctx.fillStyle = '#c9ced6'; ctx.beginPath(); ctx.moveTo(sx + q * tw, gy - 3 * ppu); ctx.lineTo(sx + (q + 0.5) * tw, gy - o.h * ppu - 3 * ppu); ctx.lineTo(sx + (q + 1) * tw, gy - 3 * ppu); ctx.closePath(); ctx.fill(); ctx.strokeStyle = '#555a63'; ctx.lineWidth = Math.max(1, ppu * 0.7); ctx.stroke(); }
        } else if (o.k === 'oil') {                                                                                       // oil slick
          const cxo = sx + sw / 2; ctx.fillStyle = '#14121b'; ctx.beginPath(); ctx.ellipse(cxo, gy + ppu, sw / 2, 4.5 * ppu, 0, 0, 7); ctx.fill();
          ctx.fillStyle = 'rgba(120,200,255,.4)'; ctx.beginPath(); ctx.ellipse(cxo - sw * 0.15, gy, sw * 0.18, 1.6 * ppu, 0, 0, 7); ctx.fill(); ctx.fillStyle = 'rgba(255,140,220,.35)'; ctx.beginPath(); ctx.ellipse(cxo + sw * 0.18, gy + 2 * ppu, sw * 0.14, 1.4 * ppu, 0, 0, 7); ctx.fill();
        }
      }
      { let tgt = 0; const rp = rc.track.find((o) => o.k === 'ramp' && c.dx > o.x && c.dx < o.x + o.w);   // car pitch: slope on a ramp, flight path in the air
        if (!(c.f & 1) && rp) tgt = -Math.atan(rp.h / rp.w); else if (c.f & 1) tgt = -Math.atan2(c.vy || 0, Math.max(120, c.v)) * 0.9; c.tilt = (c.tilt || 0) + (tgt - (c.tilt || 0)) * 0.3; }
      // car + labels
      drawCar(c, (c.dx - camX) * ppu, gy, ppu, t, c.i === myId);
      ctx.font = `700 ${Math.max(10, Math.round(big ? 13 : 10))}px system-ui,sans-serif`; ctx.textBaseline = 'top';
      ctx.fillStyle = 'rgba(0,0,0,.45)'; const label = c.name + (c.rank ? '  🏁 ' + ordinal(c.rank) : ''); const tw = ctx.measureText(label).width;
      ctx.beginPath(); ctx.roundRect(5, y0 + 5, tw + 12, big ? 20 : 16, 8); ctx.fill(); ctx.fillStyle = '#fff'; ctx.fillText(label, 11, y0 + (big ? 9 : 7));
      if (c.f & 2) { ctx.textAlign = 'center'; ctx.font = `900 ${big ? 17 : 11}px system-ui,sans-serif`; ctx.fillStyle = '#ff5a4f'; ctx.fillText(`ENGINE OFF  ${(c.st / 10).toFixed(1)}`, (c.dx - camX) * ppu, gy - 82 * ppu); ctx.textAlign = 'left'; }
      // progress to the line
      ctx.fillStyle = 'rgba(0,0,0,.25)'; ctx.fillRect(0, y0 + h - 4, W, 4); ctx.fillStyle = c.color; ctx.fillRect(0, y0 + h - 4, W * Math.min(1, c.dx / rc.len), 4);
      ctx.restore();
    };

    const frame = (now) => {
      raf = requestAnimationFrame(frame);
      const t = now + clockOff;
      cars.forEach((c) => {                                         // smooth between 30 Hz server snapshots
        const age = Math.min(150, now - c.at) / 1000, ex = c.x + (c.f & 8 ? 0 : c.v * age);
        c.dx += (ex - c.dx) * 0.45; c.dy += (c.y - c.dy) * 0.55;
      });
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0); ctx.clearRect(0, 0, W, H);
      const all = [...cars.values()], meC = cars.get(myId);
      const others = all.filter((c) => c !== meC).sort((a, b) => (b.rank ? 1e6 - b.rank : b.dx) - (a.rank ? 1e6 - a.rank : a.dx)).slice(0, 5);
      const k = others.length, hO = k ? Math.min(118, (H * 0.6) / k) : 0, hMe = H - k * hO;        // opponents share the top, my lane gets the rest
      let y = 0;
      others.forEach((c) => { drawLane(c, y, hO, false, t); y += hO; });
      const top = H - hMe; if (y < top) y = top;
      if (meC) drawLane(meC, y, H - y, true, t);
      ctx.fillStyle = 'rgba(255,255,255,.55)'; for (let q = 1; q <= k; q++) ctx.fillRect(0, q * hO - 1, W, 2);
      if (k < all.length - 1) { ctx.font = '700 10px system-ui'; ctx.fillStyle = '#fff'; ctx.fillText(`+${all.length - 1 - k} more racing`, W - 90, 6); }
      if (banner && now < banner.until) {                           // "ENGINE OFF" / finish banner over my lane
        ctx.textAlign = 'center'; ctx.font = '900 34px system-ui,sans-serif'; ctx.lineWidth = 5; ctx.strokeStyle = '#0a2a5e'; ctx.strokeText(banner.text, W / 2, H * 0.36); ctx.fillStyle = banner.color; ctx.fillText(banner.text, W / 2, H * 0.36); ctx.textAlign = 'left';
      }
      // HUD: my place, engine hint, timer bar, engine sound
      const order = [...all].sort((a, b) => (b.rank ? 1e6 - b.rank : b.dx) - (a.rank ? 1e6 - a.rank : a.dx));
      const place = order.indexOf(meC) + 1;
      document.getElementById('rcpos').textContent = meC ? `🏁 ${ordinal(place)} of ${all.length}` : '';
      document.getElementById('rcnote').textContent = !meC ? '' : meC.rank ? 'Finished!' : meC.f & 2 ? '🔧 Engine off' : meC.f & 16 ? '🛢️ Slippery — no braking!' : meC.f & 4 ? '🐢 Slowed' : '';
      bar.style.width = Math.max(0, 100 - ((now - t0) / g.ms) * 100) + '%';
      if (meC) Sfx.engine(Math.min(1, meC.v / 360), !(meC.f & 2) && !(meC.f & 8));
    };
    raf = requestAnimationFrame(frame);

    live = {
      onEvent(ev) {
        const now = performance.now();
        if (ev.ev === 'rc') {
          const off = ev.t - now; clockOff = haveClock ? clockOff + (off - clockOff) * 0.2 : off; haveClock = true;
          for (const [i, x, y, v, f, st, vy] of ev.c) {
            const c = cars.get(i); if (!c) continue;
            c.x = x; c.y = y; c.v = v; c.f = f; c.st = st; c.vy = vy || 0; c.at = now;
            if (c.dx === 0 && x > 0) c.dx = x;
            if (i === myId) {                                          // my sounds come from the server's state, so they match what really happened
              const air = !!(f & 1), stall = !!(f & 2);
              if (air && !wasAir) Sfx.play('jump');
              if (!stall && wasStall) Sfx.play('restart');
              wasAir = air; wasStall = stall;
            }
          }
        } else if (ev.ev === 'rchit') {
          const c = cars.get(ev.i); if (!c) return;
          if (ev.i === myId) {
            if (ev.k === 'big') { Sfx.play('crash'); banner = { text: 'ENGINE OFF!', color: '#ff5a4f', until: performance.now() + 1100 }; app.classList.remove('shake'); void app.offsetWidth; app.classList.add('shake'); }
            else if (ev.k === 'spike') { Sfx.play('wrong'); banner = { text: 'SPIKES! Slowed 3s', color: '#ff8a65', until: performance.now() + 1400 }; }
            else if (ev.k === 'oil') { Sfx.play('pop'); banner = { text: 'OIL! No braking', color: '#b39ddb', until: performance.now() + 1200 }; }
            else if (ev.k === 'ball') { Sfx.play('thunk'); banner = { text: 'BOINK! Ball in the way', color: '#ffd23f', until: performance.now() + 900 }; }
            else { Sfx.play('thunk'); banner = { text: 'BONK! Jump it!', color: '#ffd23f', until: performance.now() + 900 }; }
          }
        } else if (ev.ev === 'rcfinish') {
          const c = cars.get(ev.i); if (!c) return; c.rank = ev.rank;
          if (ev.i === myId) { Sfx.play(ev.rank === 1 ? 'win' : 'correct'); banner = { text: ev.rank === 1 ? '🏆 1st place!' : `🏁 ${ordinal(ev.rank)}`, color: '#ffe45a', until: performance.now() + 2500 }; }
        }
      },
      stop() { cancelAnimationFrame(raf); window.removeEventListener('resize', size); document.removeEventListener('keydown', kd); document.removeEventListener('keyup', ku); if (goDown) send({ action: 'rcgo', on: false }); Sfx.engineStop(); },
    };
  }

  // Number Sniper's end screen: every elimination in order, and who scored the most
  function nsLogCard() {
    const fmt = (ms) => `${Math.floor(ms / 60000)}:${String(Math.floor(ms / 1000) % 60).padStart(2, '0')}`;
    const rows = S.standings.map((r) => ({ name: r.name, pts: r.gained })), top = Math.max(0, ...rows.map((r) => r.pts)), tops = rows.filter((r) => r.pts === top && top > 0);
    return `<div class="card nslog"><b>🎯 Who eliminated who</b>
      ${S.nsLog.length ? `<ol>${S.nsLog.map((e) => `<li><span class="nt">${fmt(e.at)}</span> ${e.self ? `<b>${esc(e.victim)}</b> eliminated themselves 🤦` : `<b>${esc(e.by)}</b> <span class="nx">🎯</span> <b>${esc(e.victim)}</b> <span class="np">+1</span>`}</li>`).join('')}</ol>` : '<p class="muted">Nobody was eliminated.</p>'}
      <div class="nstop">${tops.length ? `🏆 Most points: <b>${tops.map((t) => esc(t.name)).join(' & ')}</b> (${top})` : 'No points this round'}</div></div>`;
  }

  function stopAnim() { if (anim) { anim.stop(); anim = null; } }

  // Between-round screen: rows start in last round's order with last round's scores, the scores count up,
  // then rows glide to their new positions; rank numbers flip up (moved up) or down (moved down).
  function renderStandings() {
    const ROW = 60, rows = S.standings;
    app.innerHTML = `${brand}
      <div class="muted">Round ${S.round.index + 1} / ${S.round.total}</div>
      <h2 class="st-title">${S.isLast ? '🏁 Final standings' : '📊 Standings'}</h2>
      ${S.nsLog ? nsLogCard() : ''}
      ${S.reveal ? `<div class="card reveal"><div class="muted">The word was</div><div class="revword">${esc(S.reveal.toUpperCase())}</div>${window.__lastDrawing ? `<img src="${window.__lastDrawing}" alt="">` : ''}</div>` : ''}
      <div class="board" style="height:${rows.length * ROW}px">${rows.map((r) => `
        <div class="srow ${r.you ? 'me' : ''}" data-name="${esc(r.name)}" style="transform:translateY(${r.from * ROW}px)">
          <div class="rk"><span class="rkn">${r.from + 1}</span></div>
          ${faceImg(r.av)}
          <div class="nm">${esc(r.name)}${r.you ? ' <small>(you)</small>' : ''}</div>
          <span class="rdy" title="Ready">✓</span>
          <div class="pts"><span class="sc">${r.prev}</span>${r.gained ? `<span class="gain${r.gained < 0 ? ' neg' : ''}">${r.gained > 0 ? '+' : ''}${r.gained}</span>` : ''}</div>
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
        const st = Math.floor(p * 24); if (st !== lastStep && p < 1 && rows.some((r) => r.gained)) { lastStep = st; Sfx.play('count', p); }
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
    const away = new Set(S.players.filter((x) => x.away).map((x) => x.name));
    app.querySelectorAll('.srow').forEach((el) => { el.classList.toggle('isready', ready.has(el.dataset.name)); el.classList.toggle('away', away.has(el.dataset.name)); });
    const c = document.getElementById('rdycount'); if (c) c.textContent = `${S.ready.length} of ${S.standings.filter((x) => !away.has(x.name)).length} ready${away.size ? ` · ${away.size} away 💤` : ''}`;
    const b = document.getElementById('ready');
    if (b) { b.disabled = me || !standingsGate(); b.textContent = me ? '✓ Ready — waiting for others…' : 'Ready'; b.classList.toggle('waiting', me); }
  }

  // Host-only "Exit game": hold for 5 seconds to end the game for everyone (lives outside #app so it survives every screen and live game)
  const exitBtn = document.createElement('button'); exitBtn.id = 'hostexit'; exitBtn.hidden = true;
  exitBtn.innerHTML = '<i></i><span>Hold 5s: back to lobby</span>'; document.body.appendChild(exitBtn);
  (function () {
    let t0 = 0, raf = 0; const bar = exitBtn.firstChild;
    const stop = () => { t0 = 0; cancelAnimationFrame(raf); bar.style.width = '0'; exitBtn.classList.remove('hold'); };
    const tick = () => { if (!t0) return; const f = Math.min(1, (Date.now() - t0) / 5000); bar.style.width = f * 100 + '%'; if (f >= 1) { stop(); send({ action: 'tolobby' }); } else raf = requestAnimationFrame(tick); };
    exitBtn.addEventListener('pointerdown', (e) => { e.preventDefault(); if (t0) return; t0 = Date.now(); exitBtn.classList.add('hold'); raf = requestAnimationFrame(tick); });
    ['pointerup', 'pointerleave', 'pointercancel'].forEach((n) => exitBtn.addEventListener(n, stop));
    exitBtn.addEventListener('contextmenu', (e) => e.preventDefault());
  })();
  function render() {
    exitBtn.hidden = !(S && S.isHost && S.state !== 'lobby');
    clearInterval(timerId);
    if (S && (S.state === 'countdown' || S.state === 'play')) {     // set up once; ignore re-broadcasts while it runs
      const key = S.state + ':' + S.code + ':' + S.mini.index;
      if (key === liveKey) return;
      liveKey = key; stopLive(); stopAnim(); standKey = null;
      return S.state === 'countdown' ? renderCountdown() : S.mini.game === 'rc' ? renderRc() : S.mini.game === 'pic' ? renderPic() : S.mini.game === 'bomb' ? renderBomb() : S.mini.game === 'copy' ? renderCopy() : S.mini.game === 'pf' ? renderPf() : S.mini.game === 'ns' ? renderNs() : S.mini.game === 'bb' ? renderBb() : renderPlay();
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
    if (!S && reconnecting) { app.innerHTML = `${brand}<div class="card"><p class="muted">📡 Getting you back into your game…</p></div>`; return; }
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
      const m = S.mini, sel = new Set(m.selected), here = S.players.filter((x) => !x.away).length;
      const usable = m.games.filter((g) => sel.has(g.id) && g.min <= here);
      const n = m.rounds || usable.length;
      const ROUNDS = [[0, 'Each once'], [1, '1'], [3, '3'], [5, '5']];
      let pick;
      if (S.isHost) {
        pick = `<div class="card"><b>🎮 Games to play</b> <span class="muted">(${sel.size} picked)</span>
          <div class="chips">${m.games.map((g) => { const lock = g.min > here; return `<button class="chip ${sel.has(g.id) ? 'on' : ''}" data-game="${g.id}" ${lock && !sel.has(g.id) ? 'disabled' : ''}>${g.icon} ${esc(g.name)}${g.min > 1 ? ` <small>(${g.min}+ players)</small>` : ''}</button>`; }).join('')}</div>
          <b>Rounds</b>
          <div class="chips">${ROUNDS.map(([v, l]) => `<button class="chip ${m.rounds === v ? 'on' : ''}" data-rounds="${v}">${l}</button>`).join('')}</div>
          <div class="chips"><button class="chip small" id="allgames">Select all</button><button class="chip small" id="nogames">Clear</button></div></div>`;
      } else {
        const picked = m.games.filter((g) => sel.has(g.id));
        pick = `<div class="card"><b>🎮 Mini Games</b> <span class="muted">${m.rounds ? `· ${m.rounds} round${m.rounds > 1 ? 's' : ''}` : '· each game once'}</span>
          <div class="muted" style="margin-top:6px">${picked.length ? picked.map((g) => `${g.icon} ${esc(g.name)}`).join(' · ') : 'Host is picking games…'}</div></div>`;
      }
      h += `${lobbyHead()}${pick}
        <div class="card"><b>Players (${S.players.length})</b>${board(S.players)}</div>
        ${S.isHost ? `<button id="start" ${usable.length ? '' : 'disabled'}>Start game${usable.length ? ` · ${n} round${n > 1 ? 's' : ''}` : ''}</button>${usable.length ? '' : `<p class="muted">${sel.size ? 'Not enough players for the games you picked' : 'Pick at least one game to start'}</p>`}` : '<p class="muted">Waiting for host to start…</p>'}`;
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
    if (S.state === 'lobby') h += '<button class="secondary small" id="leave">Leave game</button>';
    h += `<div class="err">${esc(err)}</div>`;
    app.innerHTML = h;

    document.querySelectorAll('.choice').forEach((b) => (b.onclick = () => send({ action: 'answer', choice: +b.dataset.i })));
    const on = (id, a) => { const el = document.getElementById(id); if (el) el.onclick = () => send({ action: a }); };
    on('start', 'start'); on('next', 'next'); on('again', 'again'); on('leave', 'leave');
    document.querySelectorAll('[data-setmode]').forEach((b) => (b.onclick = () => { if (b.dataset.setmode !== S.mode) send({ action: 'mode', mode: b.dataset.setmode }); }));
    document.querySelectorAll('[data-game]').forEach((b) => (b.onclick = () => {
      const set = new Set(S.mini.selected); set.has(b.dataset.game) ? set.delete(b.dataset.game) : set.add(b.dataset.game);
      send({ action: 'config', games: [...set] });
    }));
    document.querySelectorAll('[data-rounds]').forEach((b) => (b.onclick = () => send({ action: 'config', rounds: +b.dataset.rounds })));
    const allg = document.getElementById('allgames'); if (allg) allg.onclick = () => send({ action: 'config', games: S.mini.games.filter((g) => g.min <= S.players.filter((x) => !x.away).length).map((g) => g.id) });
    const nog = document.getElementById('nogames'); if (nog) nog.onclick = () => send({ action: 'config', games: [] });
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
