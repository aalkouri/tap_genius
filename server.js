// Tap Genius - authoritative multiplayer trivia server (Node + ws). Rooms live in memory.
const http = require('http'), fs = require('fs'), path = require('path');
const { WebSocketServer } = require('ws');
const PORT = process.env.PORT || 80;
const PUB = path.join(__dirname, 'public');
const MIME = { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css', '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.webp': 'image/webp', '.svg': 'image/svg+xml' };

const BANDS = ['2-5', '6-10', '11+'];
const BAND_LABEL = { '2-5': 'Ages 2–5', '6-10': 'Ages 6–10', '11+': 'Ages 11+' };
const QUESTION_MS = { '2-5': 30000, '6-10': 20000, '11+': 20000 }; // little ones get more time
const ROUNDS = 10, MAX_PLAYERS = 50, ROOM_IDLE_MS = 2 * 3600e3;

// ---------- question bank: questions/<category>.json (built by tools/build_questions.py) ----------
// Questions whose picture is a file under public/img/ are skipped when that file is missing (e.g. Disney art not added yet).
const CATS = [];   // [{ id, name, icon, counts: {band: n} }] in display order
const BANK = {};   // BANK[cat][band] = [question]
const BYID = new Map();
(function loadBank() {
  const dir = path.join(__dirname, 'questions');
  const ORDER = ['disney', 'animals', 'shapes', 'colors', 'numbers', 'fruits_veg', 'dinosaurs', 'space', 'ocean', 'vehicles'];
  let files = []; try { files = fs.readdirSync(dir).filter((f) => f.endsWith('.json')); } catch (e) { }
  files.sort((a, b) => (ORDER.indexOf(a.slice(0, -5)) + 100) % 100 - (ORDER.indexOf(b.slice(0, -5)) + 100) % 100);
  for (const f of files) {
    let d; try { d = JSON.parse(fs.readFileSync(path.join(dir, f), 'utf8')); } catch (e) { console.error('bad question file', f, e.message); continue; }
    const cat = { id: d.id, name: d.name, icon: d.icon, counts: {} }; BANK[d.id] = {};
    for (const b of BANDS) {
      BANK[d.id][b] = (d.bands[b] || []).filter((q) => {
        if (!q.v || q.v.t !== 'img') return true;
        const f2 = path.normalize(path.join(PUB, 'img', q.v.v));
        return f2.startsWith(path.join(PUB, 'img') + path.sep) && fs.existsSync(f2);
      });
      BANK[d.id][b].forEach((q) => BYID.set(q.id, q));
      cat.counts[b] = BANK[d.id][b].length;
    }
    CATS.push(cat);
  }
  console.log('question bank:', CATS.map((c) => `${c.id}=${Object.values(c.counts).join('/')}`).join(' '));
})();
const shuffle = (a) => { for (let i = a.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; } return a; };
// pick `n` questions for a band, spread evenly across the chosen categories
function pickQuestions(band, cats, n) {
  const lists = cats.map((c) => shuffle([...(BANK[c] ? BANK[c][band] : [])])).filter((l) => l.length);
  const out = [];
  for (let i = 0; out.length < n && lists.some((l) => l.length); i++) { const l = lists[i % lists.length]; if (l.length) out.push(l.pop()); }
  return shuffle(out);
}
const rooms = new Map(); // code -> room

const srv = http.createServer((req, res) => {
  if (req.url === '/healthz') { res.writeHead(200); return res.end('ok'); }
  let p = decodeURIComponent(req.url.split('?')[0]);
  if (p === '/') p = '/index.html';
  const f = path.join(PUB, path.normalize(p));
  if (!f.startsWith(PUB + path.sep)) { res.writeHead(403); return res.end(); }
  fs.readFile(f, (e, d) => {
    if (e) { res.writeHead(404); return res.end('Not found'); }
    res.writeHead(200, { 'Content-Type': MIME[path.extname(f)] || 'application/octet-stream', 'Cache-Control': 'no-cache' });
    res.end(d);
  });
});

const wss = new WebSocketServer({ server: srv, maxPayload: 1024 });
const send = (ws, o) => { if (ws.readyState === 1) ws.send(JSON.stringify(o)); };
const cleanName = (n) => String(n || '').trim().replace(/\s+/g, ' ').slice(0, 20);
const newCode = () => {
  const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ';
  let c; do { c = Array.from({ length: 4 }, () => chars[Math.floor(Math.random() * chars.length)]).join(''); } while (rooms.has(c));
  return c;
};

function view(room, p) {
  const players = [...room.players].sort((a, b) => b.score - a.score)
    .map((x) => ({ name: x.name, score: x.score, answered: x.choice !== null }));
  const v = { type: 'state', state: room.state, code: room.code, isHost: p === room.host, players, you: { name: p.name, score: p.score } };
  v.config = { band: room.band, cats: room.cats };
  if (room.state === 'lobby') v.catalog = { bands: BANDS.map((id) => ({ id, label: BAND_LABEL[id] })), cats: CATS };
  if (room.state === 'question' || room.state === 'reveal') {
    const q = BYID.get(room.order[room.qIndex]);
    v.question = { index: room.qIndex, total: room.order.length, text: q.q, choices: q.c, endsAt: room.endsAt, ms: room.ms, visual: q.v || null, ct: q.ct || 'text', band: room.band };
    v.myChoice = p.choice;
    if (room.state === 'reveal') { v.correct = q.a; v.gained = p.gained; }  // answer only revealed after the round
  }
  return v;
}
const broadcast = (room) => room.players.forEach((p) => send(p.ws, view(room, p)));

function startQuestion(room) {
  room.state = 'question'; room.startedAt = Date.now(); room.endsAt = room.startedAt + room.ms;
  room.players.forEach((p) => { p.choice = null; p.gained = 0; });
  clearTimeout(room.timer); room.timer = setTimeout(() => reveal(room), room.ms);
  broadcast(room);
}
function reveal(room) {
  if (room.state !== 'question') return;
  clearTimeout(room.timer); room.state = 'reveal';
  const correct = BYID.get(room.order[room.qIndex]).a;
  room.players.forEach((p) => {
    if (p.choice === correct) {
      const frac = Math.min(1, (p.answeredAt - room.startedAt) / room.ms);
      p.gained = 500 + Math.round(500 * (1 - frac)); // 500-1000, faster = more
      p.score += p.gained;
    }
  });
  broadcast(room);
}
function removePlayer(ws) {
  const room = ws.room; if (!room) return;
  room.players = room.players.filter((p) => p.ws !== ws); ws.room = null;
  if (!room.players.length) { clearTimeout(room.timer); rooms.delete(room.code); return; }
  if (room.host.ws === ws) room.host = room.players[0];
  if (room.state === 'question' && room.players.every((p) => p.choice !== null)) return reveal(room);
  broadcast(room);
}

const ACTIONS = {
  create(ws, m) {
    const name = cleanName(m.name); if (!name) return err(ws, 'Enter a name');
    if (ws.room) return;
    if (rooms.size >= 500) return err(ws, 'Server busy, try again soon');
    const room = { code: newCode(), state: 'lobby', players: [], qIndex: -1, order: [], last: Date.now(), band: '6-10', cats: CATS.map((c) => c.id), ms: QUESTION_MS['6-10'] };
    const p = { ws, name, score: 0, choice: null, gained: 0 };
    room.players.push(p); room.host = p; ws.room = room; ws.player = p; rooms.set(room.code, room);
    broadcast(room);
  },
  join(ws, m) {
    const name = cleanName(m.name); if (!name) return err(ws, 'Enter a name');
    if (ws.room) return;
    const room = rooms.get(String(m.code || '').toUpperCase().trim());
    if (!room) return err(ws, 'Room not found');
    if (room.state !== 'lobby') return err(ws, 'Game already started');
    if (room.players.length >= MAX_PLAYERS) return err(ws, 'Room is full');
    if (room.players.some((x) => x.name.toLowerCase() === name.toLowerCase())) return err(ws, 'Name already taken');
    const p = { ws, name, score: 0, choice: null, gained: 0 };
    room.players.push(p); ws.room = room; ws.player = p; broadcast(room);
  },
  config(ws, m) {  // host picks the age range and which categories to play
    const room = hostRoom(ws); if (!room || room.state !== 'lobby') return;
    if (BANDS.includes(m.band)) room.band = m.band;
    if (Array.isArray(m.cats)) room.cats = CATS.map((c) => c.id).filter((id) => m.cats.includes(id));
    broadcast(room);
  },
  start(ws) {
    const room = hostRoom(ws); if (!room || room.state !== 'lobby') return;
    room.ms = QUESTION_MS[room.band];
    const qs = pickQuestions(room.band, room.cats, ROUNDS);
    if (!qs.length) return err(ws, 'Pick at least one category that has questions for this age range');
    room.order = qs.map((q) => q.id);
    room.qIndex = 0; startQuestion(room);
  },
  answer(ws, m) {
    const room = ws.room, p = ws.player; if (!room || room.state !== 'question' || p.choice !== null) return;
    if (!Number.isInteger(m.choice) || m.choice < 0 || m.choice > 3) return;
    p.choice = m.choice; p.answeredAt = Date.now();
    if (room.players.every((x) => x.choice !== null)) reveal(room); else broadcast(room);
  },
  next(ws) {
    const room = hostRoom(ws); if (!room || room.state !== 'reveal') return;
    if (++room.qIndex >= room.order.length) { room.state = 'done'; return broadcast(room); }
    startQuestion(room);
  },
  again(ws) {
    const room = hostRoom(ws); if (!room || room.state !== 'done') return;
    room.state = 'lobby'; room.qIndex = -1; room.players.forEach((p) => { p.score = 0; p.choice = null; p.gained = 0; });
    broadcast(room);
  },
};
const err = (ws, message) => send(ws, { type: 'error', message });
const hostRoom = (ws) => (ws.room && ws.room.host === ws.player ? ws.room : null);

wss.on('connection', (ws) => {
  ws.isAlive = true; ws.on('pong', () => (ws.isAlive = true));
  ws.on('message', (raw) => {
    let m; try { m = JSON.parse(raw); } catch { return; }
    const fn = Object.hasOwn(ACTIONS, m.action) && ACTIONS[m.action];
    if (fn) { if (ws.room) ws.room.last = Date.now(); fn(ws, m); }
  });
  ws.on('close', () => removePlayer(ws));
});
// Heartbeat (CloudFront drops idle sockets) + idle room cleanup
setInterval(() => {
  wss.clients.forEach((ws) => { if (!ws.isAlive) return ws.terminate(); ws.isAlive = false; ws.ping(); });
  rooms.forEach((r) => { if (Date.now() - r.last > ROOM_IDLE_MS) { r.players.forEach((p) => p.ws.terminate()); } });
}, 30000);

srv.listen(PORT, () => console.log('Tap Genius listening on', PORT));
