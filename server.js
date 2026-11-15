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
  clearTimeout(room.timer); clearTimeout(room.spawnTimer); clearInterval(room.tick); miniCleanup(room);
  room.avIds.forEach((id) => AVATARS.delete(id));
  rooms.delete(room.code);
}

// ---------- mini games (room.mode === 'mini'): countdown -> play -> standings, repeated ----------
const MINI = {
  whack: { id: 'whack', name: 'Whack-a-Mole', icon: '🔨', how: 'Tap the head before anyone else does!', ms: 30000 },
  pf:    { id: 'pf', name: 'Pie Fight', icon: '🥧', how: 'Run around the edge, then throw pies at faces across the arena. Hit = +1, get hit = -1!', ms: 50000, min: 2 },
  bomb:  { id: 'bomb', name: 'Hot Potato', icon: '💣', how: 'Tap a player to throw them the bomb before it blows!', ms: 90000, min: 3 },
  copy:  { id: 'copy', name: 'Copy Cat', icon: '🎵', how: 'Watch the pattern, then tap it back. The fastest to finish each round scores the most. One mistake and you are out!', ms: 80000, min: 1 },
  pic:   { id: 'pic', name: 'Picture This', icon: '🎨', how: 'One player draws a secret word. Everyone else types guesses — fast guesses score more!', ms: 75000, min: 2 },
  rc:    { id: 'rc', name: 'RC Mayhem', icon: '🏎️', how: 'Hold GO to drive. Tap JUMP over logs. Wait for the bridges!', ms: 70000 },
};
const WORDS = JSON.parse(fs.readFileSync(path.join(__dirname, 'words.json'), 'utf8'));   // things that are fun to draw
const COUNTDOWN_MS = 4000, CELLS = 9;   // 3-2-1-GO takes 4s; whack-a-mole is a 3x3 grid
const MISS_LOCK_MS = 1000, MISS_GRACE_MS = 500;   // empty-square penalty: 1s lockout; only squares with no mole for 0.5s count as empty
const HOLE_REST_MS = 1500;   // after a mole leaves a hole (whacked or not), that hole stays empty this long
const GRACE_MS = +process.env.GRACE_MS || 3 * 60 * 1000;   // a player whose connection drops (phone locked, app switched) keeps their seat this long
const TOKENS = new Map();         // secret session token -> player, so a returning phone can take its seat back
const here = (room) => room.players.filter((p) => !p.away);
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
    .map((x) => ({ name: x.name, score: x.score, answered: x.choice !== null, av: x.av, away: !!x.away }));
  const v = { type: 'state', state: room.state, code: room.code, isHost: p === room.host, players, you: { name: p.name, score: p.score, av: p.av } };
  v.mode = room.mode; v.host = room.host.name;
  v.config = { band: room.band, cats: room.cats };
  if (room.state === 'lobby') {
    if (room.mode === 'mini') v.mini = { games: Object.values(MINI).map(({ id, name, icon, min }) => ({ id, name, icon, min: min || 1 })), selected: room.miniGames, rounds: room.miniRounds };      // rounds 0 = each picked game once
    else v.catalog = { bands: BANDS.map((id) => ({ id, label: BAND_LABEL[id] })), cats: CATS };
  }
  if (room.state === 'countdown' || room.state === 'play') {
    const g = MINI[room.order[room.qIndex]];
    v.mini = { game: g.id, name: g.name, icon: g.icon, how: g.how, index: room.qIndex, total: room.order.length, ms: room.state === 'countdown' ? COUNTDOWN_MS : g.ms, cells: CELLS };
    if (g.id === 'pic' && room.pic) {   // the word itself only ever goes to the drawer
      const me = p === room.pic.drawer;
      v.mini.pic = { drawer: room.pic.drawer.name, you: me, hint: picPattern(room.pic), len: room.pic.word.length };
      if (me) v.mini.pic.word = room.pic.word;
    }
    if (g.id === 'pf') v.mini.cars = room.players.map((x) => ({ i: x.idx, name: x.name, av: x.av, t: x.pf ? Math.round(x.pf.t) : 0 }));
    if (g.id === 'bomb' || g.id === 'copy') {
      v.mini.cars = room.players.map((x) => ({ i: x.idx, name: x.name, av: x.av }));
      if (g.id === 'bomb') { v.mini.alive = (room.bomb ? [...room.bomb.alive] : room.players).map((x) => x.idx); v.mini.holder = room.bomb && room.bomb.holder ? room.bomb.holder.idx : -1; }
      else v.mini.alive = (room.copy ? [...room.copy.alive] : room.players).map((x) => x.idx);
    }
    if (g.id === 'rc' && room.rc) v.mini.rc = { len: RC.LEN, track: room.rc.track, cars: room.players.map((x) => ({ i: x.idx, name: x.name, av: x.av })) };
  }
  if (room.state === 'standings' && room.pic && room.pic.word) v.reveal = room.pic.word;   // round is over: show the answer
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
const openGames = () => [...rooms.values()].filter((r) => r.state === 'lobby' && r.players.length < MAX_PLAYERS && here(r).length)
  .sort((a, b) => b.created - a.created)
  .map((r) => ({ id: r.code, host: r.host.name, av: r.host.av, mode: r.mode, players: r.players.filter((p) => !p.away).length }));
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
  room.players.forEach((p, i) => { p.prev = p.score; p.gained = 0; p.idx = i; });
  if ((MINI[room.order[room.qIndex]].min || 1) > here(room).length) {                    // not enough players left for this game: use another game the host picked
    const alt = room.miniGames.filter((id) => (MINI[id].min || 1) <= here(room).length);
    room.order[room.qIndex] = alt.length ? alt[Math.floor(Math.random() * alt.length)] : 'whack';
  }
  const gid = room.order[room.qIndex];
  miniCleanup(room); room.bomb = null; room.copy = null; room.pf = null;
  room.rc = gid === 'rc' ? { track: makeTrack() } : null;      // RC: same track for every lane
  room.pic = gid === 'pic' ? picStart(room) : null;            // Picture This: choose the drawer and the word
  if (gid === 'pf') pfPlace(room);                              // Pie Fight: spread everyone around the edge
  broadcast(room);
  room.timer = setTimeout(() => playMini(room), COUNTDOWN_MS);
}
function playMini(room) {
  if (room.state !== 'countdown') return;
  const g = MINI[room.order[room.qIndex]];
  room.state = 'play'; room.playStart = Date.now(); room.moles = null;
  if (g.id === 'pic') picPrep(room);
  broadcast(room);
  if (g.id === 'whack') {
    room.moles = new Map(); room.moleSeq = 0;
    room.holeFree = Array(CELLS).fill(0);   // per hole: time from which a new mole may use it
    room.holeEnd = Array(CELLS).fill(0);    // per hole: when its last mole left (whacked or timed out)
    room.players.forEach((p) => { p.missUntil = 0; });
    room.spawnTimer = setTimeout(() => spawnMoles(room), 500);
  } else if (g.id === 'rc') rcInit(room);
  else if (g.id === 'pic') picHints(room);
  else if (g.id === 'bomb') bombInit(room);
  else if (g.id === 'copy') copyInit(room);
  else if (g.id === 'pf') pfInit(room);
  room.timer = setTimeout(() => endMini(room), g.ms);
}
// The order of mini games for a series: `n` rounds drawn from `ids`, every game once per lap (shuffled), never the same game twice in a row.
function buildMiniOrder(ids, n) {
  const order = [];
  while (order.length < n) {
    const lap = shuffle([...ids]);
    if (order.length && lap.length > 1 && lap[0] === order[order.length - 1]) lap.push(lap.shift());
    order.push(...lap);
  }
  return order.slice(0, n);
}
// Points for a finishing order: best place first, ties share the better place's points.
function awardPlaces(groups) {
  let pos = 0;
  for (const g of groups) { if (!g.length) continue; const pts = RC.POINTS[pos] !== undefined ? RC.POINTS[pos] : 1; g.forEach((p) => { p.score += pts; }); pos += g.length; }
}
function miniCleanup(room) {          // stop any timers a mini game left running
  const b = room.bomb; if (b) { clearTimeout(b.fuseTimer); clearTimeout(b.warnTimer); clearTimeout(b.rebomb); }
  const c = room.copy; if (c) clearTimeout(c.timer);
}

// ---------- Pie Fight ----------
// Players ride a loop around the edge of a square arena (t = distance along the loop, clockwise from the top-left corner).
// Left = clockwise, right = counter-clockwise, so running off a corner carries you onto the next side. A throw pauses you for 1.5s;
// the pie leaves after a short wind-up and flies straight across the arena (perpendicular to your edge). Hit a face: +1 for you, -1 for them.
const PF = { P: 4000, S: 1000, SPEED: 520, PIE_SPEED: 1100, RELEASE_MS: 350, LOCK_MS: 1500, HIT_R: 60, STUN_MS: 1400, GRACE_MS: 700, TICK: 33 };
function pfPoint(t) {
  t = ((t % PF.P) + PF.P) % PF.P; const side = Math.floor(t / 1000), u = t - side * 1000;
  return side === 0 ? [u, 0] : side === 1 ? [1000, u] : side === 2 ? [1000 - u, 1000] : [0, 1000 - u];
}
const pfNormal = (t) => [[0, 1], [-1, 0], [0, -1], [1, 0]][Math.floor((((t % PF.P) + PF.P) % PF.P) / 1000)];      // straight in from the current edge
function pfPlace(room) {
  room.pf = { pies: [], seq: 0, live: false };
  const n = room.players.length;
  room.players.forEach((p, i) => { p.pf = { t: (2500 + (i * PF.P) / n) % PF.P, dir: 0, lockUntil: 0, releaseAt: 0, stunUntil: 0, score: 0 }; });
}
function pfInit(room) {
  room.pf.live = true; room.pfLast = Date.now();
  room.players.forEach((p) => { p.pf.dir = 0; p.pf.lockUntil = 0; p.pf.releaseAt = 0; p.pf.stunUntil = 0; p.pf.score = 0; });
  room.tick = setInterval(() => pfTick(room), PF.TICK);
}
const pfScores = (room) => Object.fromEntries(room.players.map((p) => [p.idx, p.pf ? p.pf.score : 0]));
function pfTick(room) {
  if (room.state !== 'play' || !room.pf) return;
  const now = Date.now(), dt = Math.min(0.1, (now - room.pfLast) / 1000), pf = room.pf; room.pfLast = now;
  const snap = [];
  for (const p of room.players) {
    const f = p.pf; if (!f) continue;
    if (!p.away && f.dir && now >= f.lockUntil) f.t = (f.t + f.dir * PF.SPEED * dt + PF.P) % PF.P;       // no running while throwing
    if (f.releaseAt && now >= f.releaseAt) {                                                              // the pie leaves the hand
      f.releaseAt = 0;
      const [ox, oy] = pfPoint(f.t), [nx, ny] = pfNormal(f.t), pie = { id: ++pf.seq, by: p, x: ox + nx * 25, y: oy + ny * 25, dx: nx, dy: ny };
      pf.pies.push(pie); emit(room, { ev: 'pfpie', id: pie.id, i: p.idx, x: Math.round(pie.x), y: Math.round(pie.y), dx: nx, dy: ny, sp: PF.PIE_SPEED });
    }
    snap.push([p.idx, Math.round(f.t), Math.max(0, Math.ceil((f.lockUntil - now) / 50)), Math.max(0, Math.ceil((f.stunUntil - now) / 50)), f.dir]);
  }
  for (const pie of [...pf.pies]) {                                                                       // fly, hit a face, or land on the far wall
    const ox = pie.x, oy = pie.y, step = PF.PIE_SPEED * dt; pie.x += pie.dx * step; pie.y += pie.dy * step;
    let best = null, bestD = 1e9;
    for (const q of room.players) {
      if (q === pie.by || !q.pf || q.away) continue;                                                       // away players are not targets
      const [hx, hy] = pfPoint(q.pf.t), vx = pie.x - ox, vy = pie.y - oy, L2 = vx * vx + vy * vy || 1;
      const u = Math.max(0, Math.min(1, ((hx - ox) * vx + (hy - oy) * vy) / L2)), cx = ox + vx * u, cy = oy + vy * u;
      if (Math.hypot(hx - cx, hy - cy) < PF.HIT_R) { const d = Math.hypot(hx - ox, hy - oy); if (d < bestD) { bestD = d; best = [q, hx, hy]; } }
    }
    if (best) {
      const [q, hx, hy] = best; pf.pies.splice(pf.pies.indexOf(pie), 1);
      pie.by.pf.score += 1; q.pf.score -= 1; q.pf.stunUntil = now + PF.STUN_MS;
      emit(room, { ev: 'pfhit', id: pie.id, by: pie.by.idx, to: q.idx, x: Math.round(hx), y: Math.round(hy), sc: pfScores(room) });
    } else if (pie.x < 0 || pie.x > PF.S || pie.y < 0 || pie.y > PF.S) {
      pf.pies.splice(pf.pies.indexOf(pie), 1);
      emit(room, { ev: 'pfland', id: pie.id, x: Math.round(Math.max(0, Math.min(PF.S, pie.x))), y: Math.round(Math.max(0, Math.min(PF.S, pie.y))) });
    }
  }
  emit(room, { ev: 'pf', t: now - room.playStart, c: snap });
}
function pfAward(room) { room.players.forEach((p) => { if (p.pf) p.score += p.pf.score; }); room.pf.live = false; }

// ---------- Hot Potato ----------
// One bomb with a hidden fuse. The holder taps another player to throw it; whoever holds it when it blows is out.
// A new bomb appears for the survivors until one player is left (or time runs out).
const BOMB = { FUSE_MIN: 4000, FUSE_MAX: 9000, HOLD_MS: 350, REBOMB_MS: 1800 };
const bombIdx = (room) => [...room.bomb.alive].map((p) => p.idx);
function bombInit(room) {
  room.bomb = { alive: new Set(room.players), out: [], holder: null, from: null, passedAt: 0, fuseTimer: null, warnTimer: null, rebomb: null };
  bombNew(room);
}
function bombNew(room) {
  const b = room.bomb, ok = [...b.alive].filter((p) => !p.away), pool = ok.length ? ok : [...b.alive];
  b.holder = pool[Math.floor(Math.random() * pool.length)]; b.from = null; b.passedAt = Date.now();
  const fuse = BOMB.FUSE_MIN + Math.random() * (BOMB.FUSE_MAX - BOMB.FUSE_MIN);
  clearTimeout(b.fuseTimer); clearTimeout(b.warnTimer);
  b.fuseTimer = setTimeout(() => bombBoom(room), fuse);
  b.warnTimer = setTimeout(() => emit(room, { ev: 'bwarn' }), Math.max(0, fuse - 1800));
  emit(room, { ev: 'bstate', holder: b.holder.idx, alive: bombIdx(room), n: b.out.length });
  bombAwayCheck(room);
}
function bombAwayCheck(room) {          // a holder whose phone is away cannot throw: the bomb bounces on for them
  const b = room.bomb; if (!b || !b.holder || !b.holder.away) return;
  setTimeout(() => {
    if (room.bomb !== b || room.state !== 'play' || !b.holder || !b.holder.away) return;
    const c = [...b.alive].filter((p) => p !== b.holder && !p.away); if (c.length) bombTransfer(room, b.holder, c[Math.floor(Math.random() * c.length)]);
  }, 600);
}
function bombTransfer(room, from, to) {
  const b = room.bomb; b.from = from; b.holder = to; b.passedAt = Date.now();
  emit(room, { ev: 'bpass', from: from.idx, to: to.idx }); bombAwayCheck(room);
}
function bombBoom(room) {
  const b = room.bomb; if (!b || room.state !== 'play' || !b.holder) return;
  const h = b.holder; b.alive.delete(h); b.out.push(h); b.holder = null; clearTimeout(b.warnTimer);
  emit(room, { ev: 'bboom', i: h.idx, left: b.alive.size });
  if (b.alive.size <= 1) { clearTimeout(room.timer); room.timer = setTimeout(() => endMini(room), 2400); return; }
  b.rebomb = setTimeout(() => { if (room.bomb === b && room.state === 'play') bombNew(room); }, BOMB.REBOMB_MS);
}
function bombLeft(room, p) {            // a player left for good while the bomb game was running
  const b = room.bomb; if (!b || !b.alive.has(p)) return;
  b.alive.delete(p);
  if (b.alive.size <= 1) { clearTimeout(b.fuseTimer); clearTimeout(b.warnTimer); clearTimeout(b.rebomb); b.holder = null; emit(room, { ev: 'bstate', holder: -1, alive: bombIdx(room), n: b.out.length }); clearTimeout(room.timer); room.timer = setTimeout(() => endMini(room), 1500); return; }
  if (b.holder === p) bombNew(room); else emit(room, { ev: 'bstate', holder: b.holder ? b.holder.idx : -1, alive: bombIdx(room), n: b.out.length });
}
function bombAward(room) { const b = room.bomb; awardPlaces([[...b.alive], ...[...b.out].reverse().map((p) => [p])]); }

// ---------- Copy Cat ----------
// A pattern of coloured pads plays; everyone taps it back. The pattern grows every round; a wrong tap (or being too slow) is out.
const COPY = { START_LEN: 2, MAX_LEN: 40 };
function copyInit(room) {
  room.players.forEach((p) => { p.ccTotal = 0; });                 // points earned in THIS match (added to the player's score when it ends)
  room.copy = { seq: Array.from({ length: COPY.MAX_LEN }, () => Math.floor(Math.random() * 4)), round: 0, phase: 'idle', alive: new Set(room.players), started: room.players.length, groups: [], roundOut: [], len: 0, timer: null, finished: 0 };
  copyRound(room);
}
const copyAliveIdx = (room) => [...room.copy.alive].map((p) => p.idx);
const copyScores = (room) => Object.fromEntries(room.players.map((p) => [p.idx, p.ccTotal || 0]));
function copyRound(room) {
  const c = room.copy; if (!c || room.state !== 'play') return;
  [...c.alive].filter((p) => p.away).forEach((p) => { c.alive.delete(p); c.roundOut.push(p); });          // phones that are away cannot play
  if (c.roundOut.length) { c.groups.push(c.roundOut); c.roundOut = []; }
  if (!c.alive.size || (c.started > 1 && c.alive.size <= 1)) return endMini(room);
  c.round++; c.len = COPY.START_LEN + c.round - 1; c.phase = 'show'; c.finished = 0;
  const step = Math.max(340, 720 - c.round * 28), startIn = 900;
  c.alive.forEach((p) => { p.cc = { i: 0, done: false }; });
  emit(room, { ev: 'ccround', r: c.round, seq: c.seq.slice(0, c.len), step, startIn, alive: copyAliveIdx(room), scores: copyScores(room) });
  c.timer = setTimeout(() => copyInput(room), startIn + c.len * step + 250);
}
function copyInput(room) {
  const c = room.copy; if (!c || room.state !== 'play' || c.phase !== 'show') return;
  c.phase = 'input'; const limit = 3500 + c.len * 1000;
  emit(room, { ev: 'ccgo', limit }); c.timer = setTimeout(() => copyEndInput(room), limit);
}
function copyEndInput(room) {
  const c = room.copy; if (!c || c.phase !== 'input') return;
  c.phase = 'between'; clearTimeout(c.timer);
  [...c.alive].filter((p) => !p.cc.done).forEach((p) => { c.alive.delete(p); c.roundOut.push(p); emit(room, { ev: 'ccout', i: p.idx, why: 'slow' }); });      // too slow
  if (c.roundOut.length) { c.groups.push(c.roundOut); c.roundOut = []; }
  emit(room, { ev: 'ccend', r: c.round, alive: copyAliveIdx(room), scores: copyScores(room) });
  c.timer = setTimeout(() => copyRound(room), 1700);
}
function copyAward(room) {
  const c = room.copy;
  if (c.started > 1 && c.alive.size === 1) [...c.alive][0].ccTotal += 5;      // last cat standing bonus
  room.players.forEach((p) => { p.score += p.ccTotal || 0; });
}

// ---------- Picture This ----------
// One player (the drawer) gets a secret word and draws it; strokes are relayed live to everyone else, who type guesses.
// Faster correct guesses earn more, and the drawer earns a share of every correct guess.
const PIC = { MIN: 3, SPAN: 7 };               // a correct guess is worth 3..10 points depending on how much time was left
function picStart(room) {
  room.drawn = room.drawn || new Set(); room.usedWords = room.usedWords || new Set();
  let pool = room.players.filter((p) => !room.drawn.has(p));
  if (!pool.length) { room.drawn.clear(); pool = room.players; }                 // everyone has drawn: start another lap
  const drawer = pool[Math.floor(Math.random() * pool.length)]; room.drawn.add(drawer);
  let words = WORDS.filter((w) => !room.usedWords.has(w)); if (!words.length) { room.usedWords.clear(); words = WORDS; }
  const word = words[Math.floor(Math.random() * words.length)]; room.usedWords.add(word);
  return { drawer, word, shown: new Set(), live: false, points: 0 };
}
const picPattern = (pic) => [...pic.word].map((ch, i) => (ch === ' ' ? ' ' : pic.shown.has(i) ? ch : '_')).join('');
function picPrep(room) {                                                          // called as the round starts
  if (!room.players.includes(room.pic.drawer)) room.pic.drawer = room.players[Math.floor(Math.random() * room.players.length)];   // drawer left during the countdown
  room.pic.live = true; room.pic.points = 0;
  room.players.forEach((p) => { p.guessed = false; p.lastGuess = 0; });
}
function picHints(room) {                                                         // reveal a few letters as time runs out
  const pic = room.pic, g = MINI.pic, n = pic.word.replace(/ /g, '').length >= 8 ? 2 : pic.word.length >= 4 ? 1 : 0;
  if (!n) return;
  const order = shuffle([...pic.word].map((c, i) => (c === ' ' ? -1 : i)).filter((i) => i >= 0));
  const reveal = (at, next) => { room.spawnTimer = setTimeout(() => { if (room.state !== 'play') return; order.splice(0, n).forEach((i) => pic.shown.add(i)); emit(room, { ev: 'pichint', hint: picPattern(pic) }); next && next(); }, g.ms * at - (Date.now() - room.playStart)); };
  reveal(0.42, () => reveal(0.68));
}
function picCheckDone(room) {
  const guessers = here(room).filter((p) => p !== room.pic.drawer);
  if (guessers.length && guessers.every((p) => p.guessed)) { clearTimeout(room.timer); room.timer = setTimeout(() => endMini(room), 1800); }
}
const lev1 = (a, b) => {                                                           // are the two words exactly one edit apart?
  if (Math.abs(a.length - b.length) > 1) return false;
  let i = 0; while (i < a.length && i < b.length && a[i] === b[i]) i++;
  if (a.length === b.length) return a.slice(i + 1) === b.slice(i + 1);
  return a.length > b.length ? a.slice(i + 1) === b.slice(i) : b.slice(i + 1) === a.slice(i);
};

// ---------- RC Mayhem ----------
// Every player drives an identical lane. The server runs all the physics (30 Hz) so the race is fair:
//  - log (small): jump it, or it slows you      - rock (big): engine cuts out for a couple of seconds
//  - bridge / lift: rises and falls on a timer; driving into it while it is up cuts the engine and bumps you back
const RC = { LEN: 3600, MAXV: 360, ACC: 520, DECEL: 240, BRAKE: 700, G: 1500, JV: 470, CAR: 20, TICK: 33,
  STALL_MS: 2600, BRIDGE_STALL_MS: 2200, SLOW_MS: 900, AFTER_FIRST_MS: 15000, POINTS: [10, 7, 5, 4, 3, 2] };
function mulberry(seed) { return () => { seed = (seed + 0x6D2B79F5) | 0; let t = Math.imul(seed ^ (seed >>> 15), 1 | seed); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }
function makeTrack() {
  const r = mulberry(Math.floor(Math.random() * 1e9)), track = [];
  let x = 520;
  while (x < RC.LEN - 450) {
    const roll = r(); let o;
    if (roll < 0.36) o = { k: 'log', x, w: 26 + Math.floor(r() * 14), h: 24 };
    else if (roll < 0.52) o = { k: 'rock', x, w: 50 + Math.floor(r() * 30), h: 56 };
    else { o = { k: roll < 0.77 ? 'bridge' : 'lift', x, w: 120, per: 4200 + Math.floor(r() * 1800), ph: Math.floor(r() * 6000) }; o.up = Math.round(o.per * (0.42 + r() * 0.12)); }
    track.push(o); x += o.w + 110 + Math.floor(r() * 170);
  }
  track.forEach((o, i) => { o.i = i; });
  return track;
}
const rcUp = (o, t) => (((t + o.ph) % o.per) + o.per) % o.per < o.up;      // bridge / lift is raised (blocking)
function rcInit(room) {
  room.rc.live = true; room.rc.finished = 0; room.rcLast = Date.now(); room.rcAllDone = false;
  room.players.forEach((p) => { p.rc = { x: 0, y: 0, vy: 0, v: 0, go: false, jumpAt: -1e9, stallUntil: 0, slowUntil: 0, hit: new Set(), done: false, finT: 0, rank: 0 }; });
  room.tick = setInterval(() => rcTick(room), RC.TICK);
}
function rcTick(room) {
  if (room.state !== 'play' || !room.rc) return;
  const now = Date.now(), dt = Math.min(0.1, (now - room.rcLast) / 1000), t = now - room.playStart, g = MINI.rc; room.rcLast = now;
  const cars = [];
  for (const p of room.players) {
    const c = p.rc; if (!c) continue;
    const prevFront = c.x + RC.CAR, engine = now >= c.stallUntil;
    if (c.done) c.v = Math.max(0, c.v - 400 * dt);
    else if (!engine) c.v = Math.max(0, c.v - RC.BRAKE * dt);
    else {
      const maxv = now < c.slowUntil ? RC.MAXV * 0.55 : RC.MAXV;
      if (c.go) c.v = c.v > maxv ? Math.max(maxv, c.v - 900 * dt) : Math.min(maxv, c.v + RC.ACC * dt);
      else c.v = Math.max(0, c.v - RC.DECEL * dt);
    }
    c.x += c.v * dt;
    if (c.y > 0 || c.vy > 0) { c.vy -= RC.G * dt; c.y += c.vy * dt; if (c.y <= 0) { c.y = 0; c.vy = 0; } }
    if (c.y === 0 && engine && !c.done && now - c.jumpAt < 130) { c.vy = RC.JV; c.y = 0.01; c.jumpAt = -1e9; }   // jump (a press just before landing still counts)
    if (!c.done) {
      const front = c.x + RC.CAR, back = c.x - RC.CAR;
      for (const o of room.rc.track) {
        if (o.x > front + 40) break;
        if (o.x + o.w < back) continue;
        if (o.k === 'log' || o.k === 'rock') {
          if (front > o.x && back < o.x + o.w && c.y < o.h && !c.hit.has(o.i)) {
            c.hit.add(o.i);
            if (o.k === 'log') { c.v *= 0.35; c.slowUntil = now + RC.SLOW_MS; emit(room, { ev: 'rchit', i: p.idx, k: 'small' }); }
            else { c.v = 0; c.stallUntil = now + RC.STALL_MS; emit(room, { ev: 'rchit', i: p.idx, k: 'big' }); }
          }
        } else if (prevFront <= o.x && front > o.x && rcUp(o, t)) {         // drove into a raised bridge / lift
          c.x = o.x - RC.CAR - 4; c.v = 0; c.stallUntil = now + RC.BRIDGE_STALL_MS; emit(room, { ev: 'rchit', i: p.idx, k: 'big' });
        }
      }
      if (c.x >= RC.LEN) {
        c.done = true; c.finT = t; c.rank = ++room.rc.finished;
        emit(room, { ev: 'rcfinish', i: p.idx, rank: c.rank, t });
        if (c.rank === 1) { clearTimeout(room.timer); room.timer = setTimeout(() => endMini(room), Math.min(Math.max(1000, g.ms - t), RC.AFTER_FIRST_MS)); }
      }
    }
    cars.push([p.idx, Math.round(c.x), Math.round(c.y), Math.round(c.v), (c.y > 0 ? 1 : 0) | (now < c.stallUntil ? 2 : 0) | (now < c.slowUntil ? 4 : 0) | (c.done ? 8 : 0), Math.max(0, Math.round((c.stallUntil - now) / 100))]);
  }
  emit(room, { ev: 'rc', t, c: cars });
  if (!room.rcAllDone && here(room).length && here(room).every((p) => p.rc && p.rc.done)) { room.rcAllDone = true; clearTimeout(room.timer); room.timer = setTimeout(() => endMini(room), 1800); }
}
function rcAward(room) {            // points by finishing place; anyone who did not finish is ranked by distance
  const order = room.players.filter((p) => p.rc).sort((a, b) => (b.rc.done - a.rc.done) || (a.rc.done ? a.rc.finT - b.rc.finT : b.rc.x - a.rc.x));
  order.forEach((p, i) => { p.score += RC.POINTS[i] !== undefined ? RC.POINTS[i] : 1; });
  room.rc.live = false;
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
    room.holeEnd[cell] = now + ttl;
    room.moles.set(id, { cell, exp: now + ttl, hit: false });
    const who = room.players[Math.floor(Math.random() * room.players.length)];   // whose head pops up
    emit(room, { ev: 'spawn', id, cell, ttl, av: who.av });
  }
  const gap = Math.round(1050 - 600 * f);                                   // next pop after 1.05s -> 0.45s
  if (now + gap < room.playStart + g.ms - 200) room.spawnTimer = setTimeout(() => spawnMoles(room), gap);
}
function endMini(room) {
  if (room.state !== 'play') return;
  clearTimeout(room.spawnTimer); clearInterval(room.tick); room.tick = null;
  if (room.rc && room.rc.live) rcAward(room);
  if (room.pic) room.pic.live = false;
  if (room.bomb) bombAward(room);
  if (room.copy) copyAward(room);
  if (room.pf && room.pf.live) pfAward(room);
  miniCleanup(room);
  room.players.forEach((p) => { p.gained = p.score - p.prev; });
  enterStandings(room);
}
function checkAllReady(room) {
  if (room.state === 'standings' && here(room).length && here(room).every((p) => p.ready)) { advance(room); return true; }
  return false;
}
function advance(room) {
  if (room.state !== 'standings') return;
  clearTimeout(room.timer);
  if (room.isLast) { room.state = 'done'; return broadcast(room); }
  room.qIndex++;
  if (room.mode === 'mini') startMini(room); else startQuestion(room);
}
// A roster change (someone left or went away): can the game carry on without them?
function settle(room) {
  if (room.state === 'play' && room.pf && room.pf.live && here(room).length < 2) return endMini(room);
  if (room.state === 'play' && room.pic && room.pic.live) {
    if (!room.players.includes(room.pic.drawer) || here(room).length < 2) return endMini(room);   // drawer gone / nobody left to guess
    picCheckDone(room);
  }
  if (room.state === 'question' && here(room).length && here(room).every((p) => p.choice !== null)) return reveal(room);
  if (checkAllReady(room)) return;
  broadcast(room);
}
function dropPlayer(room, p) {       // remove a player for good (they left, or were away too long)
  clearTimeout(p.awayTimer); clearTimeout(p.hostTimer); clearTimeout(p.drawerTimer);
  TOKENS.delete(p.token);
  if (p.ws && p.ws.player === p) { p.ws.room = null; p.ws.player = null; }
  room.players = room.players.filter((x) => x !== p);
  if (!room.players.length) { closeRoom(room); listChanged(); return; }
  if (room.bomb && room.state === 'play') bombLeft(room, p);
  if (room.copy && room.copy.alive.delete(p)) room.copy.roundOut.push(p);
  if (room.host === p) room.host = here(room)[0] || room.players[0];
  settle(room);
}
// The connection dropped (phone locked, app switched, signal lost). Keep their seat so they can come straight back.
function goAway(ws) {
  const room = ws.room, p = ws.player; if (!room || !p || p.ws !== ws) return;
  p.away = true; if (p.rc) p.rc.go = false;
  clearTimeout(p.awayTimer); p.awayTimer = setTimeout(() => { if (p.away) dropPlayer(room, p); }, GRACE_MS);
  if (room.host === p) p.hostTimer = setTimeout(() => { const n = here(room)[0]; if (p.away && room.host === p && n) { room.host = n; broadcast(room); } }, 20000);   // host gone a while: someone else takes over
  if (room.pic && room.pic.live && room.pic.drawer === p) p.drawerTimer = setTimeout(() => { if (p.away && room.state === 'play' && room.pic && room.pic.live && room.pic.drawer === p) endMini(room); }, 12000);
  settle(room);
}
// Bring a returning player up to date with things that are not part of the normal state message.
function resync(room, p) {
  if (room.state === 'play' && room.pf && room.pf.live) send(p.ws, { type: 'ev', ev: 'pfsync', sc: pfScores(room), pies: room.pf.pies.map((x) => ({ id: x.id, x: Math.round(x.x), y: Math.round(x.y), dx: x.dx, dy: x.dy, sp: PF.PIE_SPEED })) });
  if (room.state === 'play' && room.bomb) send(p.ws, { type: 'ev', ev: 'bstate', holder: room.bomb.holder ? room.bomb.holder.idx : -1, alive: bombIdx(room), n: room.bomb.out.length });
  if (room.state === 'play' && room.copy && room.copy.phase !== 'idle') { const c = room.copy; send(p.ws, { type: 'ev', ev: 'ccsync', r: c.round, phase: c.phase, seq: c.seq.slice(0, c.len), i: p.cc ? p.cc.i : 0, done: !!(p.cc && p.cc.done), alive: copyAliveIdx(room), scores: copyScores(room), finished: room.players.filter((q) => q.cc && q.cc.done).map((q) => ({ i: q.idx, rank: q.cc.rank, pts: q.cc.pts })) }); }
  if (room.state === 'play' && room.pic && room.pic.live) send(p.ws, { type: 'ev', ev: 'picsync', strokes: room.pic.strokes || [] });
}

const ACTIONS = {
  create(ws, m) {
    const name = cleanName(m.name); if (!name) return err(ws, 'Enter a name');
    if (ws.room) return;
    if (rooms.size >= 500) return err(ws, 'Server busy, try again soon');
    const av = saveAvatar(m.avatar); if (!av) return err(ws, 'Take your picture first');
    const room = { code: newCode(), state: 'lobby', players: [], qIndex: -1, order: [], last: Date.now(), band: '6-10', cats: [], miniGames: [], miniRounds: 0, ms: QUESTION_MS['6-10'], mode: m.mode === 'mini' ? 'mini' : 'trivia', created: Date.now(), avIds: [av] };
    const p = { ws, name, av, room, score: 0, prev: 0, choice: null, gained: 0, token: crypto.randomBytes(12).toString('hex') };
    TOKENS.set(p.token, p);
    room.players.push(p); room.host = p; ws.room = room; ws.player = p; rooms.set(room.code, room); browsers.delete(ws);
    send(ws, { type: 'session', token: p.token });
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
    const p = { ws, name, av, room, score: 0, prev: 0, choice: null, gained: 0, token: crypto.randomBytes(12).toString('hex') };
    TOKENS.set(p.token, p);
    room.players.push(p); ws.room = room; ws.player = p; browsers.delete(ws);
    send(ws, { type: 'session', token: p.token });
    broadcast(room);
  },
  resume(ws, m) {  // a phone that lost its connection takes its seat back using its secret token
    if (ws.room) return;
    const p = TOKENS.get(String(m.token || '')), room = p && p.room;
    if (!p || !room || !rooms.has(room.code) || !room.players.includes(p)) return send(ws, { type: 'session', expired: true });
    if (p.ws && p.ws !== ws) { const old = p.ws; old.player = null; old.room = null; try { old.terminate(); } catch (e) { } }   // same player on a stale socket
    ws.room = room; ws.player = p; p.ws = ws; p.away = false;
    clearTimeout(p.awayTimer); clearTimeout(p.hostTimer); clearTimeout(p.drawerTimer);
    browsers.delete(ws); room.last = Date.now();
    send(ws, { type: 'session', token: p.token });
    broadcast(room); resync(room, p);
  },
  ping(ws) { send(ws, { type: 'pong' }); },     // lets a phone that just woke up check that its connection is really alive
  leave(ws) {    // the player chose to leave: free their seat straight away
    const room = ws.room, p = ws.player; if (!room || !p) return;
    dropPlayer(room, p); send(ws, { type: 'left' });
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
    if (Array.isArray(m.games)) room.miniGames = Object.keys(MINI).filter((id) => m.games.includes(id));       // Mini Games: which games to play (one is enough)
    if ([0, 1, 3, 5].includes(m.rounds)) room.miniRounds = m.rounds;                                            // ... and how many rounds
    broadcast(room);
  },
  start(ws) {
    const room = hostRoom(ws); if (!room || room.state !== 'lobby') return;
    if (room.mode === 'mini') {
      // FORCE_MINI=<id> is for automated tests only (always plays that game)
      const forced = process.env.FORCE_MINI && MINI[process.env.FORCE_MINI] ? process.env.FORCE_MINI : null;
      const eligible = forced ? [forced] : room.miniGames.filter((id) => MINI[id] && (MINI[id].min || 1) <= here(room).length);
      if (!eligible.length) return err(ws, room.miniGames.length ? 'Not enough players for the games you picked' : 'Pick at least one game');
      room.order = buildMiniOrder(eligible, room.miniRounds || (forced ? 3 : eligible.length));
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
    if (here(room).every((x) => x.choice !== null)) reveal(room); else broadcast(room);
  },
  whack(ws, m) {   // whack-a-mole: the first tap on a head scores; later taps on the same head do nothing
    const room = ws.room, p = ws.player; if (!room || room.state !== 'play' || !room.moles) return;
    const mole = room.moles.get(m.id);
    if (!mole || mole.hit || Date.now() > mole.exp + 150) return;
    mole.hit = true; p.score += 1;                      // exactly one point per mole: `hit` can only be set once
    room.holeFree[mole.cell] = Date.now() + HOLE_REST_MS;
    room.holeEnd[mole.cell] = Date.now();
    emit(room, { ev: 'hit', id: m.id, by: p.name, n: p.score - p.prev });   // n = that player's points this round (authoritative)
  },
  miss(ws, m) {    // whack-a-mole: tapping an empty square costs a point and locks out more empty taps for a second
    const room = ws.room, p = ws.player; if (!room || room.state !== 'play' || !room.moles) return;
    const cell = m.cell, now = Date.now();
    if (!Number.isInteger(cell) || cell < 0 || cell >= CELLS || now < (p.missUntil || 0)) return;
    for (const mo of room.moles.values()) if (mo.cell === cell && !mo.hit && now <= mo.exp) return;   // a mole is up there: not empty
    if (now < room.holeEnd[cell] + MISS_GRACE_MS) return;                                              // a mole only just left: near miss, no penalty
    p.missUntil = now + MISS_LOCK_MS; p.score -= 1;
    emit(room, { ev: 'miss', by: p.name, cell, n: p.score - p.prev });
  },
  draw(ws, m) {     // Picture This: the drawer's pen strokes, relayed to everyone else
    const room = ws.room, p = ws.player; if (!room || room.state !== 'play' || !room.pic || !room.pic.live || p !== room.pic.drawer) return;
    let msg;
    if (m.op === 'seg') {
      const raw = Array.isArray(m.pts) ? m.pts.slice(0, 160) : [], pts = [];
      for (let i = 0; i + 1 < raw.length; i += 2) pts.push(Math.max(0, Math.min(1000, raw[i] | 0)), Math.max(0, Math.min(800, raw[i + 1] | 0)));
      if (!pts.length || room.pic.points + pts.length > 60000) return;
      room.pic.points += pts.length;
      const strokes = room.pic.strokes || (room.pic.strokes = []), sid = m.id | 0;
      let st = strokes.find((x) => x.id === sid); if (!st) { st = { id: sid, c: Math.max(0, Math.min(9, m.c | 0)), w: Math.max(2, Math.min(48, m.w | 0)), pts: [] }; strokes.push(st); }
      st.pts.push(...pts);
      msg = { ev: 'pic', op: 'seg', id: m.id | 0, c: Math.max(0, Math.min(9, m.c | 0)), w: Math.max(2, Math.min(48, m.w | 0)), pts };
    } else if (m.op === 'undo' || m.op === 'clear') { msg = { ev: 'pic', op: m.op }; if (m.op === 'clear') room.pic.strokes = []; else if (room.pic.strokes) room.pic.strokes.pop(); }
    else return;
    room.players.forEach((q) => { if (q !== p) send(q.ws, { type: 'ev', ...msg }); });
  },
  guess(ws, m) {    // Picture This: a guess typed by a non-drawer
    const room = ws.room, p = ws.player; if (!room || room.state !== 'play' || !room.pic || !room.pic.live || p === room.pic.drawer || p.guessed) return;
    const now = Date.now(); if (now - p.lastGuess < 450) return; p.lastGuess = now;
    const raw = String(m.text || '').replace(/\s+/g, ' ').trim().slice(0, 30); if (!raw) return;
    const g = raw.toLowerCase().replace(/[^a-z]/g, ''), w = room.pic.word.replace(/ /g, '');
    if (g && (g === w || (w.length > 3 && (g === w + 's' || g + 's' === w)))) {
      const frac = Math.max(0, 1 - (now - room.playStart) / MINI.pic.ms), pts = PIC.MIN + Math.round(PIC.SPAN * frac);
      p.guessed = true; p.score += pts; room.pic.drawer.score += Math.ceil(pts / 2);                  // faster guess -> more for both of you
      emit(room, { ev: 'picok', name: p.name });
      send(ws, { type: 'ev', ev: 'picmine', pts });
      picCheckDone(room);
    } else {
      emit(room, { ev: 'picguess', name: p.name, text: raw.slice(0, 24) });
      if (w.length >= 4 && g.length >= 3 && lev1(g, w)) send(ws, { type: 'ev', ev: 'picclose' });
    }
  },
  pfmove(ws, m) {   // Pie Fight: left (+1, clockwise) / right (-1) held, 0 = released
    const p = ws.player; if (!ws.room || ws.room.state !== 'play' || !ws.room.pf || !p.pf) return; p.pf.dir = m.d > 0 ? 1 : m.d < 0 ? -1 : 0;
  },
  pfthrow(ws) {     // Pie Fight: wind up and throw; you are frozen for 1.5s and cannot throw again until it ends
    const room = ws.room, p = ws.player; if (!room || room.state !== 'play' || !room.pf || !room.pf.live || !p.pf || p.away) return;
    const now = Date.now(); if (now < p.pf.lockUntil || now - room.playStart < PF.GRACE_MS) return;
    p.pf.lockUntil = now + PF.LOCK_MS; p.pf.releaseAt = now + PF.RELEASE_MS;
    emit(room, { ev: 'pfwind', i: p.idx });
  },
  bpass(ws, m) {    // Hot Potato: the holder throws the bomb to another player
    const room = ws.room, p = ws.player, b = room && room.bomb; if (!b || room.state !== 'play' || b.holder !== p) return;
    const to = room.players.find((x) => x.idx === (m.to | 0)); if (!to || to === p || !b.alive.has(to) || to.away) return;
    const now = Date.now(); if (now - b.passedAt < BOMB.HOLD_MS) return;           // the bomb is too hot to throw back instantly
    if (to === b.from && b.alive.size > 2) return;                                 // no immediate return to whoever just threw it
    bombTransfer(room, p, to);
  },
  cctap(ws, m) {    // Copy Cat: a pad tapped while the input window is open
    const room = ws.room, p = ws.player, c = room && room.copy; if (!c || room.state !== 'play' || c.phase !== 'input' || !c.alive.has(p) || p.cc.done) return;
    const pad = m.pad | 0; if (pad < 0 || pad > 3) return;
    if (pad === c.seq[p.cc.i]) {
      p.cc.i++;
      if (p.cc.i >= c.len) {
        p.cc.done = true; p.cc.rank = ++c.finished; p.cc.pts = Math.max(1, 6 - p.cc.rank); p.ccTotal += p.cc.pts;      // 1st to finish 5 pts, 2nd 4, ... everyone else 1
        send(ws, { type: 'ev', ev: 'ccdone', rank: p.cc.rank, pts: p.cc.pts });
        emit(room, { ev: 'ccprog', i: p.idx, rank: p.cc.rank, pts: p.cc.pts, total: p.ccTotal });
        if ([...c.alive].every((q) => q.cc.done)) copyEndInput(room);
      }
      else send(ws, { type: 'ev', ev: 'ccok', n: p.cc.i });
    } else {
      c.alive.delete(p); c.roundOut.push(p);
      send(ws, { type: 'ev', ev: 'ccwrong' }); emit(room, { ev: 'ccout', i: p.idx, why: 'wrong' });
      if ([...c.alive].every((q) => q.cc.done)) copyEndInput(room);
    }
  },
  rcgo(ws, m) {    // RC Mayhem: GO button held / released
    const p = ws.player; if (!ws.room || ws.room.state !== 'play' || !p.rc) return; p.rc.go = !!m.on;
  },
  rcjump(ws) {     // RC Mayhem: JUMP tapped
    const p = ws.player; if (!ws.room || ws.room.state !== 'play' || !p.rc) return; p.rc.jumpAt = Date.now();
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
    if (fn) { if (ws.room) ws.room.last = Date.now(); try { fn(ws, m); } catch (e) { console.error('action failed:', m.action, e.message); } }
  });
  ws.on('close', () => { browsers.delete(ws); goAway(ws); });
});
// Heartbeat (CloudFront drops idle sockets) + idle room cleanup
setInterval(() => {
  wss.clients.forEach((ws) => { if (!ws.isAlive) return ws.terminate(); ws.isAlive = false; ws.ping(); });
  rooms.forEach((r) => { if (Date.now() - r.last > ROOM_IDLE_MS) { r.players.forEach((p) => { clearTimeout(p.awayTimer); TOKENS.delete(p.token); send(p.ws, { type: 'left' }); if (p.ws.player === p) { p.ws.room = null; p.ws.player = null; } }); closeRoom(r); listChanged(); } });
}, 30000);

srv.listen(PORT, () => console.log('Tap Genius listening on', PORT));
