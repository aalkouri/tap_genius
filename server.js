// Tap Genius - authoritative multiplayer trivia server (Node + ws). Rooms live in memory.
const http = require('http'), fs = require('fs'), path = require('path'), crypto = require('crypto');
const { WebSocketServer } = require('ws');
const PORT = process.env.PORT || 80;
const PUB = path.join(__dirname, 'public');
const MIME = { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css', '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.webp': 'image/webp', '.svg': 'image/svg+xml', '.m4a': 'audio/mp4', '.mp3': 'audio/mpeg' };

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
// ---------- player photos: every player takes a head shot before joining ----------
// Kept in memory only, under a random id, and deleted when the game room closes.
const AVATARS = new Map();    // id -> JPEG Buffer
const MAX_AVATAR_CHARS = 40000;
function saveAvatar(dataUrl) {
  if (typeof dataUrl !== 'string' || dataUrl.length > MAX_AVATAR_CHARS) return null;
  const m = /^data:image\/jpeg;base64,([A-Za-z0-9+/=]+)$/.exec(dataUrl);
  if (!m) return null;
  const buf = Buffer.from(m[1], 'base64');
  if (buf.length < 200 || buf[0] !== 0xff || buf[1] !== 0xd8 || buf[2] !== 0xff) return null;   // must really be a JPEG
  const id = crypto.randomBytes(8).toString('hex');
  AVATARS.set(id, buf);
  return id;
}
function closeRoom(room) {
  clearTimeout(room.timer); clearTimeout(room.spawnTimer);
  room.avIds.forEach((id) => AVATARS.delete(id));
  rooms.delete(room.code);
}

// ---------- mini games (room.mode === 'mini'): countdown -> play -> standings, repeated ----------
const MINI = {
  whack: { id: 'whack', name: 'Whack-a-Mole', icon: '🔨', how: 'Tap the head before anyone else does!', ms: 30000 },
};
const MINI_ROUNDS = 3, COUNTDOWN_MS = 4000, CELLS = 9;   // 3-2-1-GO takes 4s; whack-a-mole is a 3x3 grid
const HOLE_REST_MS = 1500;   // after a mole leaves a hole (whacked or not), that hole stays empty this long
const rooms = new Map(); // code -> room

const srv = http.createServer((req, res) => {
  if (req.url === '/healthz') { res.writeHead(200); return res.end('ok'); }
  let p; try { p = decodeURIComponent(req.url.split('?')[0]); } catch (e) { res.writeHead(400); return res.end(); }
  const am = /^\/avatar\/([0-9a-f]{16})\.jpg$/.exec(p);
  if (am) {
    const buf = AVATARS.get(am[1]);
    if (!buf) { res.writeHead(404); return res.end(); }
    res.writeHead(200, { 'Content-Type': 'image/jpeg', 'Content-Length': buf.length, 'Cache-Control': 'private, max-age=86400' });
    return res.end(buf);
  }
  if (p === '/') p = '/index.html';
  const f = path.join(PUB, path.normalize(p));
  if (!f.startsWith(PUB + path.sep)) { res.writeHead(403); return res.end(); }
  fs.stat(f, (e, st) => {
    if (e || !st.isFile()) { res.writeHead(404); return res.end('Not found'); }
    const ext = path.extname(f);
    const h = { 'Content-Type': MIME[ext] || 'application/octet-stream', 'Accept-Ranges': 'bytes',
      'Cache-Control': ext === '.m4a' || ext === '.mp3' ? 'public, max-age=86400' : /^\/(img\/|favicon)/.test(p) ? 'public, max-age=3600' : 'no-cache' };
    // Range support: iOS Safari will not play <audio> from a server that can't serve byte ranges
    const m = /^bytes=(\d*)-(\d*)$/.exec(req.headers.range || '');
    if (m && (m[1] || m[2])) {
      let start = m[1] ? +m[1] : Math.max(0, st.size - +m[2]), end = m[1] && m[2] ? Math.min(+m[2], st.size - 1) : st.size - 1;
      if (start > end || start >= st.size) { res.writeHead(416, { 'Content-Range': `bytes */${st.size}` }); return res.end(); }
      res.writeHead(206, { ...h, 'Content-Range': `bytes ${start}-${end}/${st.size}`, 'Content-Length': end - start + 1 });
      return fs.createReadStream(f, { start, end }).pipe(res);
    }
    res.writeHead(200, { ...h, 'Content-Length': st.size });
    fs.createReadStream(f).pipe(res);
  });
});

const wss = new WebSocketServer({ server: srv, maxPayload: 48 * 1024 });
const send = (ws, o) => { if (ws.readyState === 1) ws.send(JSON.stringify(o)); };
const cleanName = (n) => String(n || '').trim().replace(/\s+/g, ' ').slice(0, 20);
const newCode = () => {
  const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ';
  let c; do { c = Array.from({ length: 4 }, () => chars[Math.floor(Math.random() * chars.length)]).join(''); } while (rooms.has(c));
  return c;
};

function view(room, p) {
  const players = [...room.players].sort((a, b) => b.score - a.score)
    .map((x) => ({ name: x.name, score: x.score, answered: x.choice !== null, av: x.av }));
  const v = { type: 'state', state: room.state, code: room.code, isHost: p === room.host, players, you: { name: p.name, score: p.score, av: p.av } };
  v.mode = room.mode; v.host = room.host.name;
  v.config = { band: room.band, cats: room.cats };
  if (room.state === 'lobby') {
    if (room.mode === 'mini') v.mini = { games: Object.values(MINI).map(({ id, name, icon }) => ({ id, name, icon })), rounds: MINI_ROUNDS };
    else v.catalog = { bands: BANDS.map((id) => ({ id, label: BAND_LABEL[id] })), cats: CATS };
  }
  if (room.state === 'countdown' || room.state === 'play') {
    const g = MINI[room.order[room.qIndex]];
    v.mini = { game: g.id, name: g.name, icon: g.icon, how: g.how, index: room.qIndex, total: room.order.length, ms: room.state === 'countdown' ? COUNTDOWN_MS : g.ms, cells: CELLS };
  }
  if (room.state === 'standings') {
    v.standings = room.snap.map((r) => ({ ...r, you: r.name === p.name }));
    v.round = { index: room.qIndex, total: room.order.length };
    v.isLast = room.isLast;
    v.ready = room.players.filter((x) => x.ready).map((x) => x.name);
  }
  if (room.state === 'question' || room.state === 'reveal') {
    const q = BYID.get(room.order[room.qIndex]);
    v.question = { index: room.qIndex, total: room.order.length, text: q.q, choices: q.c, endsAt: room.endsAt, ms: room.ms, visual: q.v || null, ct: q.ct || 'text', band: room.band };
    v.myChoice = p.choice;
    if (room.state === 'reveal') { v.correct = q.a; v.gained = p.gained; }  // answer only revealed after the round
  }
  return v;
}
// ---------- game browser: players pick an open game from a live list (no room codes to type) ----------
const browsers = new Set();   // sockets currently looking at the list
const openGames = () => [...rooms.values()].filter((r) => r.state === 'lobby' && r.players.length < MAX_PLAYERS)
  .sort((a, b) => b.created - a.created)
  .map((r) => ({ id: r.code, host: r.host.name, av: r.host.av, mode: r.mode, players: r.players.length }));
let listTimer = null;
function listChanged() {      // debounced push whenever a lobby opens, fills, starts or closes
  if (listTimer || !browsers.size) return;
  listTimer = setTimeout(() => { listTimer = null; const msg = { type: 'list', games: openGames() }; browsers.forEach((ws) => send(ws, msg)); }, 80);
}
const broadcast = (room) => { room.players.forEach((p) => send(p.ws, view(room, p))); listChanged(); };

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
    p.prev = p.score;
    if (p.choice === correct) {
      const frac = Math.min(1, (p.answeredAt - room.startedAt) / room.ms);
      p.gained = 500 + Math.round(500 * (1 - frac)); // 500-1000, faster = more
      p.score += p.gained;
    }
  });
  broadcast(room);
}
// Between rounds: everyone sees who is winning (ranks before/after let clients animate the movement), then waits for
// every player to tap Ready. The host can override so one idle player can't hold the game up.
function enterStandings(room) {
  clearTimeout(room.timer);
  const rank = (key) => new Map([...room.players].sort((a, b) => b[key] - a[key]).map((p, i) => [p, i]));  // stable: ties keep join order
  const from = rank('prev'), to = rank('score');
  room.snap = room.players.map((p) => ({ name: p.name, av: p.av, prev: p.prev, score: p.score, gained: p.gained, from: from.get(p), to: to.get(p) }))
    .sort((a, b) => a.from - b.from);
  room.isLast = room.qIndex + 1 >= room.order.length;
  room.state = 'standings';
  room.players.forEach((p) => { p.ready = false; });   // everyone taps Ready before the next question
  broadcast(room);
}
// lightweight in-game events (no full state): { type:'ev', ev:'spawn'|'hit', ... }
const emit = (room, o) => room.players.forEach((p) => send(p.ws, { type: 'ev', ...o }));
function startMini(room) {             // every mini game opens with the same 3-2-1-GO countdown
  clearTimeout(room.timer); clearTimeout(room.spawnTimer);
  room.state = 'countdown';
  room.players.forEach((p) => { p.prev = p.score; p.gained = 0; });
  broadcast(room);
  room.timer = setTimeout(() => playMini(room), COUNTDOWN_MS);
}
function playMini(room) {
  if (room.state !== 'countdown') return;
  const g = MINI[room.order[room.qIndex]];
  room.state = 'play'; room.playStart = Date.now(); room.moles = new Map(); room.moleSeq = 0;
  room.holeFree = Array(CELLS).fill(0);   // per hole: time from which a new mole may use it
  broadcast(room);
  room.spawnTimer = setTimeout(() => spawnMoles(room), 500);
  room.timer = setTimeout(() => endMini(room), g.ms);
}
// Whack-a-mole: heads pop faster and stay up for less time as the game goes on; near the end several pop at once.
function spawnMoles(room) {
  if (room.state !== 'play') return;
  const g = MINI.whack, now = Date.now(), f = Math.min(1, (now - room.playStart) / g.ms);
  for (const [id, m] of room.moles) if (m.hit || now > m.exp + 500) room.moles.delete(id);
  const ttl = Math.round(1500 - 850 * f);                                   // visible 1.5s -> 0.65s
  const n = f > 0.85 ? 2 + (Math.random() < 0.5) : f > 0.65 ? 1 + (Math.random() < 0.6) : 1;
  const busy = new Set([...room.moles.values()].map((m) => m.cell));
  // Prefer holes that have rested. If the late-game rush needs more than are rested, take the ones empty the longest;
  // a hole that still has a mole in it is never reused.
  const open = [...Array(CELLS).keys()].filter((c) => !busy.has(c));
  const rested = shuffle(open.filter((c) => room.holeFree[c] <= now));
  const tired = open.filter((c) => room.holeFree[c] > now).sort((x, y) => room.holeFree[x] - room.holeFree[y]);
  const free = [...tired.reverse(), ...rested];        // pop() takes rested holes first, then the longest-empty tired one
  for (let i = 0; i < n && free.length; i++) {
    const id = ++room.moleSeq, cell = free.pop();
    room.holeFree[cell] = now + ttl + HOLE_REST_MS;
    room.moles.set(id, { cell, exp: now + ttl, hit: false });
    const who = room.players[Math.floor(Math.random() * room.players.length)];   // whose head pops up
    emit(room, { ev: 'spawn', id, cell, ttl, av: who.av });
  }
  const gap = Math.round(1050 - 600 * f);                                   // next pop after 1.05s -> 0.45s
  if (now + gap < room.playStart + g.ms - 200) room.spawnTimer = setTimeout(() => spawnMoles(room), gap);
}
function endMini(room) {
  if (room.state !== 'play') return;
  clearTimeout(room.spawnTimer);
  room.players.forEach((p) => { p.gained = p.score - p.prev; });
  enterStandings(room);
}
function checkAllReady(room) {
  if (room.state === 'standings' && room.players.length && room.players.every((p) => p.ready)) { advance(room); return true; }
  return false;
}
function advance(room) {
  if (room.state !== 'standings') return;
  clearTimeout(room.timer);
  if (room.isLast) { room.state = 'done'; return broadcast(room); }
  room.qIndex++;
  if (room.mode === 'mini') startMini(room); else startQuestion(room);
}
function removePlayer(ws) {
  const room = ws.room; if (!room) return;
  room.players = room.players.filter((p) => p.ws !== ws); ws.room = null;
  if (!room.players.length) { closeRoom(room); listChanged(); return; }
  if (room.host.ws === ws) room.host = room.players[0];
  if (room.state === 'question' && room.players.every((p) => p.choice !== null)) return reveal(room);
  if (checkAllReady(room)) return;       // the player we were waiting on left
  broadcast(room);
}

const ACTIONS = {
  create(ws, m) {
    const name = cleanName(m.name); if (!name) return err(ws, 'Enter a name');
    if (ws.room) return;
    if (rooms.size >= 500) return err(ws, 'Server busy, try again soon');
    const av = saveAvatar(m.avatar); if (!av) return err(ws, 'Take your picture first');
    const room = { code: newCode(), state: 'lobby', players: [], qIndex: -1, order: [], last: Date.now(), band: '6-10', cats: [], ms: QUESTION_MS['6-10'], mode: m.mode === 'mini' ? 'mini' : 'trivia', created: Date.now(), avIds: [av] };
    const p = { ws, name, av, score: 0, prev: 0, choice: null, gained: 0 };
    room.players.push(p); room.host = p; ws.room = room; ws.player = p; rooms.set(room.code, room); browsers.delete(ws);
    broadcast(room);
  },
  join(ws, m) {
    const name = cleanName(m.name); if (!name) return err(ws, 'Enter a name');
    if (ws.room) return;
    const room = rooms.get(String(m.id || '').toUpperCase().trim());
    if (!room) return err(ws, 'That game is no longer open');
    if (room.state !== 'lobby') return err(ws, 'Game already started');
    if (room.players.length >= MAX_PLAYERS) return err(ws, 'Room is full');
    if (room.players.some((x) => x.name.toLowerCase() === name.toLowerCase())) return err(ws, 'Name already taken');
    const av = saveAvatar(m.avatar); if (!av) return err(ws, 'Take your picture first');
    room.avIds.push(av);
    const p = { ws, name, av, score: 0, prev: 0, choice: null, gained: 0 };
    room.players.push(p); ws.room = room; ws.player = p; browsers.delete(ws); broadcast(room);
  },
  list(ws) {     // start watching the list of open games
    if (ws.room) return;
    browsers.add(ws); send(ws, { type: 'list', games: openGames() });
  },
  unlist(ws) { browsers.delete(ws); },
  mode(ws, m) {  // host switches the lobby between Trivia and Mini Games
    const room = hostRoom(ws); if (!room || room.state !== 'lobby') return;
    if (m.mode !== 'trivia' && m.mode !== 'mini') return;
    room.mode = m.mode; broadcast(room);
  },
  config(ws, m) {  // host picks the age range and which categories to play
    const room = hostRoom(ws); if (!room || room.state !== 'lobby') return;
    if (BANDS.includes(m.band)) room.band = m.band;
    if (Array.isArray(m.cats)) room.cats = CATS.map((c) => c.id).filter((id) => m.cats.includes(id));
    broadcast(room);
  },
  start(ws) {
    const room = hostRoom(ws); if (!room || room.state !== 'lobby') return;
    if (room.mode === 'mini') {
      const ids = Object.keys(MINI);
      room.order = Array.from({ length: MINI_ROUNDS }, () => ids[Math.floor(Math.random() * ids.length)]);
      room.qIndex = 0; return startMini(room);
    }
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
  whack(ws, m) {   // whack-a-mole: the first tap on a head scores; later taps on the same head do nothing
    const room = ws.room, p = ws.player; if (!room || room.state !== 'play') return;
    const mole = room.moles.get(m.id);
    if (!mole || mole.hit || Date.now() > mole.exp + 150) return;
    mole.hit = true; p.score += 1;                      // exactly one point per mole: `hit` can only be set once
    room.holeFree[mole.cell] = Date.now() + HOLE_REST_MS;
    emit(room, { ev: 'hit', id: m.id, by: p.name, n: p.score - p.prev });   // n = that player's points this round (authoritative)
  },
  ready(ws) {  // standings: this player is ready; the last one to tap starts the next question
    const room = ws.room, p = ws.player; if (!room || room.state !== 'standings' || p.ready) return;
    p.ready = true;
    if (!checkAllReady(room)) broadcast(room);
  },
  next(ws) {   // reveal -> standings; on the standings screen the host can skip waiting
    const room = hostRoom(ws); if (!room) return;
    if (room.state === 'reveal') return enterStandings(room);
    if (room.state === 'standings') return advance(room);
  },
  again(ws) {
    const room = hostRoom(ws); if (!room || room.state !== 'done') return;
    room.state = 'lobby'; room.qIndex = -1; room.players.forEach((p) => { p.score = 0; p.prev = 0; p.choice = null; p.gained = 0; });
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
  ws.on('close', () => { browsers.delete(ws); removePlayer(ws); });
});
// Heartbeat (CloudFront drops idle sockets) + idle room cleanup
setInterval(() => {
  wss.clients.forEach((ws) => { if (!ws.isAlive) return ws.terminate(); ws.isAlive = false; ws.ping(); });
  rooms.forEach((r) => { if (Date.now() - r.last > ROOM_IDLE_MS) { r.players.forEach((p) => p.ws.terminate()); } });
}, 30000);

srv.listen(PORT, () => console.log('Tap Genius listening on', PORT));
