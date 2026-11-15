// Tap Genius sound effects - synthesized with the Web Audio API (no audio files).
// Browsers only allow audio after a tap, so the context is unlocked on the first pointer event.
window.Sfx = (() => {
  const AC = window.AudioContext || window.webkitAudioContext;
  let ctx = null, master = null, muted = false, primed = false, eng = null;
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

  // crowd-like noise swell (filtered white noise) for the podium cheer
  function noise(t, dur, vol = 0.15, freq = 1400) {
    const c = ctx, t0 = c.currentTime + t, len = Math.floor(c.sampleRate * dur);
    const buf = c.createBuffer(1, len, c.sampleRate), d = buf.getChannelData(0);
    for (let i = 0; i < len; i++) d[i] = Math.random() * 2 - 1;
    const src = c.createBufferSource(), f = c.createBiquadFilter(), g = c.createGain();
    src.buffer = buf; f.type = 'bandpass'; f.frequency.value = freq; f.Q.value = 0.6;
    g.gain.setValueAtTime(0.0001, t0); g.gain.exponentialRampToValueAtTime(vol, t0 + dur * 0.25); g.gain.exponentialRampToValueAtTime(0.0001, t0 + dur);
    src.connect(f); f.connect(g); g.connect(master); src.start(t0); src.stop(t0 + dur);
  }
  const N = { C4: 261.6, D4: 293.7, E4: 329.6, G4: 392, A4: 440, C5: 523.3, D5: 587.3, E5: 659.3, G5: 784, A5: 880, C6: 1046.5, E6: 1318.5 };

  const SOUNDS = {
    tap:      () => tone(660, 0, 0.07, 'triangle', 0.16),
    join:     () => { tone(520, 0, 0.09, 'sine', 0.18); tone(780, 0.07, 0.12, 'sine', 0.18); },
    start:    () => [N.C5, N.E5, N.G5, N.C6].forEach((f, i) => tone(f, i * 0.09, 0.16, 'square', 0.1)),
    question: () => { tone(N.G5, 0, 0.14, 'triangle', 0.18); tone(N.C6, 0.12, 0.2, 'triangle', 0.18); },
    tick:     () => tone(1100, 0, 0.04, 'square', 0.08),
    correct:  () => [N.C5, N.E5, N.G5, N.C6].forEach((f, i) => tone(f, i * 0.08, 0.2, 'triangle', 0.2)),
    wrong:    () => { tone(240, 0, 0.28, 'sawtooth', 0.13, 150); tone(180, 0.12, 0.3, 'sawtooth', 0.11, 110); },
    buzzer:   () => { [0, 0.01].forEach((t) => { tone(140, t, 0.65, 'sawtooth', 0.2); tone(147, t, 0.65, 'square', 0.12); tone(70, t, 0.65, 'sawtooth', 0.16); }); },  // game-show wrong-answer buzzer
    count:    (p = 0) => tone(500 + 700 * p, 0, 0.05, 'square', 0.06),   // p 0..1 rises as the score counts up
    up:       () => tone(280, 0, 0.32, 'sine', 0.2, 1000),
    down:     () => tone(900, 0, 0.32, 'sine', 0.18, 240),
    whoosh:   () => tone(400, 0, 0.18, 'sine', 0.08, 700),
    win:      () => { [N.C5, N.E5, N.G5, N.C6].forEach((f, i) => tone(f, i * 0.11, 0.22, 'triangle', 0.22)); [N.G5, N.C6, N.E6].forEach((f, i) => tone(f, 0.5 + i * 0.1, 0.5, 'triangle', 0.2)); },
    beep:     () => tone(520, 0, 0.16, 'square', 0.13),                                   // 3.. 2.. 1..
    go:       () => { tone(N.C5, 0, 0.12, 'square', 0.13); tone(N.C6, 0.1, 0.45, 'square', 0.14); },   // GO!
    pop:      () => tone(320, 0, 0.09, 'sine', 0.12, 640),                                // a head pops up
    mine:     () => { tone(N.E5, 0, 0.08, 'triangle', 0.22); tone(N.C6, 0.07, 0.14, 'triangle', 0.22); },  // I got it
    bonk:     () => tone(210, 0, 0.12, 'square', 0.1, 95),                                // someone else got it
    jump:     () => tone(220, 0, 0.22, 'sine', 0.2, 760),                                  // RC: boing
    thunk:    () => { tone(120, 0, 0.12, 'square', 0.16, 60); noise(0, 0.08, 0.12, 500); },  // RC: clipped a log
    crash:    () => { noise(0, 0.5, 0.3, 700); tone(190, 0, 0.55, 'sawtooth', 0.2, 45); tone(95, 0.05, 0.5, 'square', 0.14, 40); },   // RC: engine cut out
    restart:  () => { [0, 0.16, 0.3].forEach((t, i) => tone(70 + i * 25, t, 0.12, 'sawtooth', 0.14, 120 + i * 40)); tone(90, 0.46, 0.35, 'sawtooth', 0.14, 260); },   // RC: engine coughs back to life
    pad:      (i = 0) => tone([392, 330, 494, 262][i] || 392, 0, 0.34, 'triangle', 0.26),          // Copy Cat: each coloured pad has its own note
    step:     () => tone(150, 0, 0.05, 'triangle', 0.09, 90),                             // footsteps in the podium cutscene
    land:     () => tone(260, 0, 0.1, 'sine', 0.16, 120),
    shutter:  () => { noise(0, 0.07, 0.2, 3000); noise(0.09, 0.05, 0.14, 2200); },         // camera click
    cheer:    () => { noise(0, 1.8, 0.2, 1300); noise(0.2, 1.6, 0.12, 2600); },
    done:     () => [N.G4, N.C5, N.E5, N.G5].forEach((f, i) => tone(f, i * 0.12, 0.25, 'sine', 0.18)),
  };

  return {
    play(name, arg) {
      window.__sfxLog.push(name);
      if (muted || !SOUNDS[name] || !ensure()) return;
      try { SOUNDS[name](arg); } catch (e) { }
    },
    // RC engine: one held note whose pitch follows the car's speed (0..1); call engineStop() when the race ends
    engine(speed, on) {
      if (muted || !ensure()) return this.engineStop();
      if (!eng) {
        const o = ctx.createOscillator(), f = ctx.createBiquadFilter(), g = ctx.createGain();
        o.type = 'sawtooth'; f.type = 'lowpass'; f.frequency.value = 700; g.gain.value = 0;
        o.connect(f); f.connect(g); g.connect(master); o.start(); eng = { o, g, f };
      }
      const t = ctx.currentTime;
      eng.o.frequency.setTargetAtTime(52 + speed * 120, t, 0.06);
      eng.f.frequency.setTargetAtTime(500 + speed * 900, t, 0.08);
      eng.g.gain.setTargetAtTime(on ? 0.05 + 0.06 * speed : 0, t, 0.08);
    },
    engineStop() { if (!eng) return; const e = eng; eng = null; try { e.g.gain.setTargetAtTime(0, ctx.currentTime, 0.05); e.o.stop(ctx.currentTime + 0.3); } catch (x) { } },
    unlock() {
      ensure(); music.start();
      if (!primed && window.speechSynthesis) {            // iOS only lets speech start from a tap: prime it silently once
        primed = true;
        try { const u = new SpeechSynthesisUtterance(' '); u.volume = 0; speechSynthesis.speak(u); } catch (e) { }
      }
    },
    say(text) {                                           // spoken countdown ("3", "2", "1", "Go!")
      window.__sfxLog.push('say:' + text);
      if (muted || !window.speechSynthesis) return;
      try { const u = new SpeechSynthesisUtterance(text); u.rate = 1.15; u.pitch = 1.2; u.volume = 1; speechSynthesis.cancel(); speechSynthesis.speak(u); } catch (e) { }
    },
    get muted() { return muted; },
    toggle() {
      muted = !muted;
      try { localStorage.setItem('tg_mute', muted ? '1' : '0'); } catch (e) { }
      if (muted) { music.pause(); this.engineStop(); } else { ensure(); music.start(); SOUNDS.tap(); }
      return muted;
    },
  };
})();
document.addEventListener('pointerdown', () => window.Sfx.unlock(), { passive: true });   // first tap unlocks audio + starts the music
