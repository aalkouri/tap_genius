(() => {
  const app = document.getElementById('app');
  let ws, S = null, err = '', timerId = null, revealSent = -1;

  function connect(then) {
    if (ws && ws.readyState === 1) return then();
    ws = new WebSocket(window.TAP_GENIUS_WS);
    ws.onopen = then;
    ws.onmessage = (e) => {
      const m = JSON.parse(e.data);
      if (m.type === 'error') { err = m.message; } else { S = m; err = ''; }
      render();
    };
    ws.onclose = () => { err = 'Disconnected. Reload to rejoin.'; render(); };
  }
  const send = (o) => ws && ws.readyState === 1 && ws.send(JSON.stringify(o));
  const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;' }[c]));
  const board = (players) => `<ol>${players.map((p) => `<li>${esc(p.name)}<span>${p.score}</span></li>`).join('')}</ol>`;

  function render() {
    clearInterval(timerId);
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
      h += `<div class="card"><div class="muted">Room code</div><div class="code">${S.code}</div></div>
        <div class="card"><b>Players (${S.players.length})</b>${board(S.players)}</div>
        ${S.isHost ? '<button id="start">Start game</button>' : '<p class="muted">Waiting for host to start…</p>'}`;
    } else if (S.state === 'question' || S.state === 'reveal') {
      const q = S.question, rev = S.state === 'reveal';
      h += `<div class="muted">Question ${q.index + 1} / ${q.total}</div>
        <div class="timer"><div id="bar"></div></div>
        <div class="card"><h2>${esc(q.text)}</h2></div>
        <div class="choices">${q.choices.map((c, i) => {
          const cls = ['choice', S.myChoice === i ? 'picked' : '', rev && S.correct === i ? 'right' : '', rev && S.correct !== i ? 'dim' : ''].join(' ');
          return `<button class="${cls}" data-i="${i}" ${rev || S.myChoice !== null ? 'disabled' : ''}>${esc(c)}</button>`;
        }).join('')}</div>`;
      if (rev) {
        h += `<div class="card"><b>${S.gained > 0 ? `+${S.gained} points!` : 'No points this round'}</b>${board(S.players)}</div>
          ${S.isHost ? '<button id="next">Next</button>' : '<p class="muted">Waiting for host…</p>'}`;
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

    if (S.state === 'question') {
      const bar = document.getElementById('bar');
      const total = 15000;
      timerId = setInterval(() => {
        const left = S.question.endsAt - Date.now();
        bar.style.width = Math.max(0, (left / total) * 100) + '%';
        if (left <= 0 && S.isHost && revealSent !== S.question.index) { revealSent = S.question.index; send({ action: 'reveal' }); }
        if (left <= -2000 && revealSent !== S.question.index) { revealSent = S.question.index; send({ action: 'reveal' }); }
      }, 100);
    }
  }
  render();
})();
