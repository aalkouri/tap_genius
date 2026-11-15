// Tap Genius sound effects - synthesized with the Web Audio API (no audio files).
// Browsers only allow audio after a tap, so the context is unlocked on the first pointer event.
window.Sfx = (() => {
  const AC = window.AudioContext || window.webkitAudioContext;
  let ctx = null, master = null, muted = false;
  try { muted = localStorage.getItem('tg_mute') === '1'; } catch (e) { }
  window.__sfxLog = [];                                   // handy for tests/debugging

  function ensure() {
    if (!AC) return null;
    if (!ctx) { ctx = new AC(); master = ctx.createGain(); master.gain.value = 0.7; master.connect(ctx.destination); }
    if (ctx.state === 'suspended') ctx.resume();
    return ctx;
  }
  // one note: frequency f (optionally gliding to `to`), start offset t seconds from now
  function tone(f, t, dur, type = 'sine', vol = 0.2, to = null) {
    const c = ctx, t0 = c.currentTime + t;
    const o = c.createOscillator(), g = c.createGain();
    o.type = type; o.frequency.setValueAtTime(f, t0);
    if (to) o.frequency.exponentialRampToValueAtTime(to, t0 + dur);
    g.gain.setValueAtTime(0.0001, t0);
    g.gain.exponentialRampToValueAtTime(vol, t0 + 0.012);
    g.gain.exponentialRampToValueAtTime(0.0001, t0 + dur);
    o.connect(g); g.connect(master); o.start(t0); o.stop(t0 + dur + 0.03);
  }
  // ---- background music: one looping track, quiet under the effects; starts on the first tap ----
  const music = (() => {
    let el = null, wanted = false;
    const play = () => { if (muted || !wanted || document.hidden) return; if (!el) { el = new Audio('/audio/bgmusic.mp3'); el.loop = true; el.volume = 0.28; el.preload = 'auto'; window.__music = el; }
      const pr = el.play(); if (pr && pr.catch) pr.catch(() => { }); };
    return {
      start() { wanted = true; play(); },
      play, pause() { if (el) el.pause(); },
    };
  })();
  document.addEventListener('visibilitychange', () => (document.hidden ? music.pause() : music.play()));

  const N = { C4: 261.6, D4: 293.7, E4: 329.6, G4: 392, A4: 440, C5: 523.3, D5: 587.3, E5: 659.3, G5: 784, A5: 880, C6: 1046.5, E6: 1318.5 };

  const SOUNDS = {
    tap:      () => tone(660, 0, 0.07, 'triangle', 0.16),
    join:     () => { tone(520, 0, 0.09, 'sine', 0.18); tone(780, 0.07, 0.12, 'sine', 0.18); },
    start:    () => [N.C5, N.E5, N.G5, N.C6].forEach((f, i) => tone(f, i * 0.09, 0.16, 'square', 0.1)),
    question: () => { tone(N.G5, 0, 0.14, 'triangle', 0.18); tone(N.C6, 0.12, 0.2, 'triangle', 0.18); },
    tick:     () => tone(1100, 0, 0.04, 'square', 0.08),
    correct:  () => [N.C5, N.E5, N.G5, N.C6].forEach((f, i) => tone(f, i * 0.08, 0.2, 'triangle', 0.2)),
    wrong:    () => { tone(240, 0, 0.28, 'sawtooth', 0.13, 150); tone(180, 0.12, 0.3, 'sawtooth', 0.11, 110); },
    count:    (p = 0) => tone(500 + 700 * p, 0, 0.05, 'square', 0.06),   // p 0..1 rises as the score counts up
    up:       () => tone(280, 0, 0.32, 'sine', 0.2, 1000),
    down:     () => tone(900, 0, 0.32, 'sine', 0.18, 240),
    whoosh:   () => tone(400, 0, 0.18, 'sine', 0.08, 700),
    win:      () => { [N.C5, N.E5, N.G5, N.C6].forEach((f, i) => tone(f, i * 0.11, 0.22, 'triangle', 0.22)); [N.G5, N.C6, N.E6].forEach((f, i) => tone(f, 0.5 + i * 0.1, 0.5, 'triangle', 0.2)); },
    done:     () => [N.G4, N.C5, N.E5, N.G5].forEach((f, i) => tone(f, i * 0.12, 0.25, 'sine', 0.18)),
  };

  return {
    play(name, arg) {
      window.__sfxLog.push(name);
      if (muted || !SOUNDS[name] || !ensure()) return;
      try { SOUNDS[name](arg); } catch (e) { }
    },
    unlock() { ensure(); music.start(); },
    get muted() { return muted; },
    toggle() {
      muted = !muted;
      try { localStorage.setItem('tg_mute', muted ? '1' : '0'); } catch (e) { }
      if (muted) music.pause(); else { ensure(); music.start(); SOUNDS.tap(); }
      return muted;
    },
  };
})();
document.addEventListener('pointerdown', () => window.Sfx.unlock(), { passive: true });   // first tap unlocks audio + starts the music
