import { DynamoDBClient } from '@aws-sdk/client-dynamodb';
import { DynamoDBDocumentClient, PutCommand, GetCommand, UpdateCommand, DeleteCommand, QueryCommand } from '@aws-sdk/lib-dynamodb';
import { ApiGatewayManagementApiClient, PostToConnectionCommand } from '@aws-sdk/client-apigatewaymanagementapi';
import { readFileSync } from 'node:fs';

const QUESTIONS = JSON.parse(readFileSync(new URL('./questions.json', import.meta.url)));
const TABLE = process.env.TABLE;
const db = DynamoDBDocumentClient.from(new DynamoDBClient({}));
const ws = new ApiGatewayManagementApiClient({ endpoint: process.env.WS_ENDPOINT });

const QUESTION_MS = 15000;
const GRACE_MS = 1500;
const ROUNDS = 10;
const TTL_S = 4 * 60 * 60;
const ttl = () => Math.floor(Date.now() / 1000) + TTL_S;

export const handler = async (event) => {
  const { routeKey, connectionId } = event.requestContext;
  try {
    if (routeKey === '$connect') return { statusCode: 200 };
    if (routeKey === '$disconnect') { await leave(connectionId); return { statusCode: 200 }; }
    let msg;
    try { msg = JSON.parse(event.body || '{}'); } catch { await send(connectionId, { type: 'error', message: 'Bad JSON' }); return { statusCode: 400 }; }
    const fn = ACTIONS[msg.action];
    if (!fn) { await send(connectionId, { type: 'error', message: 'Unknown action' }); return { statusCode: 400 }; }
    await fn(connectionId, msg);
    return { statusCode: 200 };
  } catch (e) {
    console.error(e);
    await send(connectionId, { type: 'error', message: e.userMessage || 'Server error' });
    return { statusCode: 200 };
  }
};

const fail = (m) => Object.assign(new Error(m), { userMessage: m });
const roomKey = (code) => `ROOM#${code}`;
const cleanName = (n) => String(n || '').trim().replace(/\s+/g, ' ').slice(0, 20);

async function send(conn, data) {
  try {
    await ws.send(new PostToConnectionCommand({ ConnectionId: conn, Data: JSON.stringify(data) }));
    return true;
  } catch (e) {
    if (e.name === 'GoneException' || e.$metadata?.httpStatusCode === 410) return false;
    throw e;
  }
}

async function getRoom(code) {
  const r = await db.send(new GetCommand({ TableName: TABLE, Key: { pk: roomKey(code), sk: 'META' } }));
  if (!r.Item) throw fail('Room not found');
  return r.Item;
}
async function getPlayers(code) {
  const r = await db.send(new QueryCommand({
    TableName: TABLE, KeyConditionExpression: 'pk = :p AND begins_with(sk, :s)',
    ExpressionAttributeValues: { ':p': roomKey(code), ':s': 'PLAYER#' }, ConsistentRead: true,
  }));
  return r.Items;
}
async function connRoom(conn) {
  const r = await db.send(new GetCommand({ TableName: TABLE, Key: { pk: `CONN#${conn}`, sk: 'CONN' } }));
  if (!r.Item) throw fail('Join a room first');
  return r.Item.code;
}
async function addPlayer(conn, code, name) {
  await db.send(new PutCommand({ TableName: TABLE, Item: { pk: roomKey(code), sk: `PLAYER#${conn}`, conn, name, score: 0, ttl: ttl() } }));
  await db.send(new PutCommand({ TableName: TABLE, Item: { pk: `CONN#${conn}`, sk: 'CONN', code, ttl: ttl() } }));
}

const newCode = () => {
  const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ'; // no I/O
  return Array.from({ length: 4 }, () => chars[Math.floor(Math.random() * chars.length)]).join('');
};

// Build the view for one player. The correct answer is only revealed in reveal/done states.
function viewFor(room, players, me) {
  const q = QUESTIONS[room.order?.[room.qIndex]];
  const roster = players.map((p) => ({ name: p.name, score: p.score, answered: p.choice !== undefined && p.qIndex === room.qIndex }))
    .sort((a, b) => b.score - a.score);
  const view = { type: 'state', state: room.state, code: room.code, isHost: me.conn === room.hostConn, players: roster, you: { name: me.name, score: me.score } };
  if (room.state === 'question' || room.state === 'reveal') {
    view.question = { index: room.qIndex, total: room.order.length, text: q.q, choices: q.c, endsAt: room.endsAt };
    view.myChoice = me.qIndex === room.qIndex ? me.choice : null;
  }
  if (room.state === 'reveal') {
    view.correct = q.a;
    view.gained = me.qIndex === room.qIndex ? me.gained ?? 0 : 0;
  }
  return view;
}

async function broadcast(code, room) {
  room ??= await getRoom(code);
  const players = await getPlayers(code);
  await Promise.all(players.map(async (p) => {
    const ok = await send(p.conn, viewFor(room, players, p));
    if (!ok) await leave(p.conn, { silent: true });
  }));
}

async function leave(conn, { silent } = {}) {
  const r = await db.send(new GetCommand({ TableName: TABLE, Key: { pk: `CONN#${conn}`, sk: 'CONN' } }));
  if (!r.Item) return;
  const code = r.Item.code;
  await db.send(new DeleteCommand({ TableName: TABLE, Key: { pk: `CONN#${conn}`, sk: 'CONN' } }));
  await db.send(new DeleteCommand({ TableName: TABLE, Key: { pk: roomKey(code), sk: `PLAYER#${conn}` } }));
  const players = await getPlayers(code);
  if (!players.length) { await db.send(new DeleteCommand({ TableName: TABLE, Key: { pk: roomKey(code), sk: 'META' } })); return; }
  let room = await getRoom(code).catch(() => null);
  if (!room) return;
  if (room.hostConn === conn) {  // promote the next player to host
    await db.send(new UpdateCommand({ TableName: TABLE, Key: { pk: roomKey(code), sk: 'META' },
      UpdateExpression: 'SET hostConn = :h', ExpressionAttributeValues: { ':h': players[0].conn } }));
    room = { ...room, hostConn: players[0].conn };
  }
  if (!silent) await broadcast(code, room);
}

const ACTIONS = {
  async create(conn, { name }) {
    name = cleanName(name); if (!name) throw fail('Enter a name');
    let code;
    for (let i = 0; i < 10; i++) {
      code = newCode();
      try {
        await db.send(new PutCommand({ TableName: TABLE,
          Item: { pk: roomKey(code), sk: 'META', code, state: 'lobby', hostConn: conn, qIndex: -1, ttl: ttl() },
          ConditionExpression: 'attribute_not_exists(pk)' }));
        break;
      } catch (e) { if (e.name !== 'ConditionalCheckFailedException' || i === 9) throw e; }
    }
    await addPlayer(conn, code, name);
    await broadcast(code);
  },

  async join(conn, { code, name }) {
    code = String(code || '').toUpperCase().trim(); name = cleanName(name);
    if (!name) throw fail('Enter a name');
    const room = await getRoom(code);
    if (room.state !== 'lobby') throw fail('Game already started');
    const players = await getPlayers(code);
    if (players.length >= 50) throw fail('Room is full');
    if (players.some((p) => p.name.toLowerCase() === name.toLowerCase())) throw fail('Name already taken');
    await addPlayer(conn, code, name);
    await broadcast(code);
  },

  async start(conn) {
    const code = await connRoom(conn); const room = await getRoom(code);
    if (room.hostConn !== conn) throw fail('Only the host can do that');
    if (room.state !== 'lobby') return;
    const order = QUESTIONS.map((_, i) => i).sort(() => Math.random() - 0.5).slice(0, ROUNDS);
    await startQuestion(code, room, order, 0);
  },

  async answer(conn, { choice }) {
    const code = await connRoom(conn); const room = await getRoom(code);
    if (room.state !== 'question') return;
    if (Date.now() > room.endsAt + GRACE_MS) throw fail('Too late!');
    if (!Number.isInteger(choice) || choice < 0 || choice > 3) throw fail('Bad choice');
    try {
      await db.send(new UpdateCommand({ TableName: TABLE, Key: { pk: roomKey(code), sk: `PLAYER#${conn}` },
        UpdateExpression: 'SET choice = :c, qIndex = :q, answeredAt = :t',
        ConditionExpression: 'attribute_not_exists(qIndex) OR qIndex <> :q',  // first answer wins
        ExpressionAttributeValues: { ':c': choice, ':q': room.qIndex, ':t': Date.now() } }));
    } catch (e) { if (e.name === 'ConditionalCheckFailedException') return; throw e; }
    const players = await getPlayers(code);
    if (players.every((p) => p.qIndex === room.qIndex)) await reveal(code, room);
    else await broadcast(code, room);
  },

  // Host's client calls this when the timer expires (or early); idempotent.
  async reveal(conn) {
    const code = await connRoom(conn); const room = await getRoom(code);
    if (room.state !== 'question') return;
    if (room.hostConn !== conn && Date.now() < room.endsAt) throw fail('Not yet');
    await reveal(code, room);
  },

  async next(conn) {
    const code = await connRoom(conn); const room = await getRoom(code);
    if (room.hostConn !== conn) throw fail('Only the host can do that');
    if (room.state !== 'reveal') return;
    const nextIdx = room.qIndex + 1;
    if (nextIdx >= room.order.length) {
      await db.send(new UpdateCommand({ TableName: TABLE, Key: { pk: roomKey(code), sk: 'META' },
        UpdateExpression: 'SET #s = :d', ExpressionAttributeNames: { '#s': 'state' }, ExpressionAttributeValues: { ':d': 'done' } }));
      return broadcast(code, { ...room, state: 'done' });
    }
    await startQuestion(code, room, room.order, nextIdx);
  },

  async again(conn) {  // host resets finished game back to lobby, scores cleared
    const code = await connRoom(conn); const room = await getRoom(code);
    if (room.hostConn !== conn) throw fail('Only the host can do that');
    const players = await getPlayers(code);
    await Promise.all(players.map((p) => db.send(new UpdateCommand({ TableName: TABLE, Key: { pk: p.pk, sk: p.sk },
      UpdateExpression: 'SET score = :z REMOVE choice, qIndex, answeredAt, gained', ExpressionAttributeValues: { ':z': 0 } }))));
    await db.send(new UpdateCommand({ TableName: TABLE, Key: { pk: roomKey(code), sk: 'META' },
      UpdateExpression: 'SET #s = :l, qIndex = :n', ExpressionAttributeNames: { '#s': 'state' }, ExpressionAttributeValues: { ':l': 'lobby', ':n': -1 } }));
    await broadcast(code);
  },
};

async function startQuestion(code, room, order, idx) {
  const endsAt = Date.now() + QUESTION_MS;
  await db.send(new UpdateCommand({ TableName: TABLE, Key: { pk: roomKey(code), sk: 'META' },
    UpdateExpression: 'SET #s = :q, qIndex = :i, #o = :o, endsAt = :e, startedAt = :b',
    ExpressionAttributeNames: { '#s': 'state', '#o': 'order' },
    ExpressionAttributeValues: { ':q': 'question', ':i': idx, ':o': order, ':e': endsAt, ':b': Date.now() } }));
  await broadcast(code, { ...room, state: 'question', qIndex: idx, order, endsAt, startedAt: Date.now() });
}

async function reveal(code, room) {
  // Atomically flip question -> reveal so scoring happens exactly once.
  try {
    await db.send(new UpdateCommand({ TableName: TABLE, Key: { pk: roomKey(code), sk: 'META' },
      UpdateExpression: 'SET #s = :r', ConditionExpression: '#s = :q',
      ExpressionAttributeNames: { '#s': 'state' }, ExpressionAttributeValues: { ':r': 'reveal', ':q': 'question' } }));
  } catch (e) { if (e.name === 'ConditionalCheckFailedException') return; throw e; }
  const correct = QUESTIONS[room.order[room.qIndex]].a;
  const players = await getPlayers(code);
  await Promise.all(players.map(async (p) => {
    let gained = 0;
    if (p.qIndex === room.qIndex && p.choice === correct) {
      const frac = Math.min(1, Math.max(0, (p.answeredAt - room.startedAt) / QUESTION_MS));
      gained = 500 + Math.round(500 * (1 - frac));  // 500-1000, faster = more
    }
    p.gained = gained; p.score += gained;
    await db.send(new UpdateCommand({ TableName: TABLE, Key: { pk: p.pk, sk: p.sk },
      UpdateExpression: 'SET score = :s, gained = :g', ExpressionAttributeValues: { ':s': p.score, ':g': gained } }));
  }));
  await broadcast(code, { ...room, state: 'reveal' });
}
