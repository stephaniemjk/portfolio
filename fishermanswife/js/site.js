/* Fisherman's Wife: loading screen, boil, scroll-triggered playback */
(function () {
  'use strict';

  var doc = document.documentElement;
  var reduceMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---------- Boil: step each filter's noise seed 8 times a second ---------- */
  var BOIL_OFFSETS = { 'boil-a': 0, 'boil-b': 1, 'boil-c': 2, 'boil-d': 0, 'boil-logo': 0, 'boil-hand': 1 };
  var boilers = [];
  Array.prototype.forEach.call(document.querySelectorAll('.filters filter'), function (f) {
    var turb = f.querySelector('feTurbulence');
    var seeds = (turb.getAttribute('data-seeds') || '').split(/\s+/).filter(Boolean);
    if (seeds.length) boilers.push({ el: turb, seeds: seeds, offset: BOIL_OFFSETS[f.id] || 0 });
  });
  var tick = 0, boilTimer = null;
  function stepBoil() {
    tick++;
    for (var i = 0; i < boilers.length; i++) {
      var b = boilers[i];
      b.el.setAttribute('seed', b.seeds[(tick + b.offset) % b.seeds.length]);
    }
  }
  function startBoil() { if (!reduceMotion && !boilTimer) boilTimer = setInterval(stepBoil, 125); }
  function stopBoil() { clearInterval(boilTimer); boilTimer = null; }
  startBoil();
  document.addEventListener('visibilitychange', function () {
    if (document.hidden) stopBoil(); else startBoil();
  });

  /* ---------- Pot: transparent WebM, or animated WebP where WebM alpha fails (Safari, all iOS) ---------- */
  var ua = navigator.userAgent;
  var isIOS = /iPad|iPhone|iPod/.test(ua) || (/Macintosh/.test(ua) && navigator.maxTouchPoints > 1);
  var isSafari = /^((?!chrome|chromium|android|crios|fxios|edg).)*safari/i.test(ua);
  var potVideo = document.getElementById('pot-video');
  var potReady;
  if (isIOS || isSafari || !potVideo.canPlayType('video/webm; codecs="vp9"')) {
    var potImg = new Image();
    potImg.className = 'pot-media';
    potImg.width = 1430; potImg.height = 1218;
    potImg.alt = potVideo.getAttribute('aria-label');
    potReady = new Promise(function (res) { potImg.onload = potImg.onerror = res; });
    potImg.src = 'video/pot.webp';
    potVideo.parentNode.replaceChild(potImg, potVideo);
    potVideo = null;
  } else {
    potReady = mediaReady(potVideo);
  }

  /* ---------- Loading screen ---------- */
  var loader = document.getElementById('loader');
  var go = document.getElementById('loader-go');
  var logo = document.querySelector('.logo');
  var firstScene = document.querySelector('.scene-video');

  function imgReady(img) {
    if (img.complete) return Promise.resolve();
    return new Promise(function (res) { img.addEventListener('load', res); img.addEventListener('error', res); });
  }
  function mediaReady(v) {
    // iOS often skips preloading, so metadata is enough; a timeout below covers the rest
    if (v.readyState >= 1) return Promise.resolve();
    return new Promise(function (res) {
      ['loadedmetadata', 'canplay', 'error'].forEach(function (e) { v.addEventListener(e, res, { once: true }); });
    });
  }
  function wait(ms) { return new Promise(function (res) { setTimeout(res, ms); }); }

  var assetsReady = Promise.all([
    imgReady(logo),
    potReady,
    mediaReady(firstScene),
    document.fonts ? document.fonts.ready : Promise.resolve()
  ]);
  Promise.all([Promise.race([assetsReady, wait(7000)]), wait(1000)]).then(function () {
    go.disabled = false;
    go.classList.add('is-ready');
  });

  var entered = false;
  function enter() {
    if (entered) return;
    entered = true;
    window.scrollTo(0, 0);
    doc.classList.remove('is-loading');
    loader.classList.add('is-leaving');
    var done = function () {
      if (!loader.parentNode) return;
      loader.parentNode.removeChild(loader);
      document.getElementById('story').focus({ preventScroll: true });
    };
    loader.addEventListener('transitionend', done, { once: true });
    setTimeout(done, 1000);
    startPlayback();
  }
  go.addEventListener('click', enter);

  /* ---------- Continue / go back / start from beginning ---------- */
  function visible(el) { return el.getClientRects().length > 0; }
  function sections() {
    return Array.prototype.filter.call(document.querySelectorAll('.step-section'), visible);
  }
  Array.prototype.forEach.call(document.querySelectorAll('.steps .step[data-step]'), function (a) {
    a.addEventListener('click', function (e) {
      var list = sections();
      var from = document.getElementById(a.parentNode.getAttribute('data-from'));
      var i = list.indexOf(from);
      var kind = a.getAttribute('data-step');
      var target = kind === 'begin' ? list[0] : kind === 'next' ? list[i + 1] : list[i - 1];
      if (!target) return;
      e.preventDefault();
      target.scrollIntoView({ behavior: reduceMotion ? 'auto' : 'smooth', block: 'start' });
    });
  });

  /* ---------- Back to top ---------- */
  var up = document.querySelector('.go-up');
  if (up) {
    var upTick = false;
    var upCheck = function () {
      upTick = false;
      up.classList.toggle('is-shown', window.scrollY > window.innerHeight * 0.9);
    };
    window.addEventListener('scroll', function () {
      if (!upTick) { upTick = true; requestAnimationFrame(upCheck); }
    }, { passive: true });
    upCheck();
    up.addEventListener('click', function (e) {
      e.preventDefault();
      window.scrollTo({ top: 0, behavior: reduceMotion ? 'auto' : 'smooth' });
    });
  }

  /* ---------- Playback on scroll ---------- */
  // If the browser blocks autoplay (iPhone Low Power Mode, data saver), show a play button instead
  function tapButton(v) {
    var box = v.parentNode;
    return box && box.querySelector ? box.querySelector('.tap-play') : null;
  }
  function play(v) {
    var p = v.play();
    if (p && p.catch) p.catch(function (err) {
      if (err && err.name === 'AbortError') return; // paused before it started (scrolled past): not blocked
      var b = tapButton(v);
      if (b) b.hidden = false;
    });
  }
  Array.prototype.forEach.call(document.querySelectorAll('.scene-video'), function (v) {
    var box = v.parentNode;
    var b = tapButton(v);
    var r = box.querySelector('.replay');
    if (b) {
      b.addEventListener('click', function () { b.hidden = true; play(v); });
      v.addEventListener('playing', function () { b.hidden = true; });
    }
    // Each scene plays once. When it ends the picture dims (scene 4 stays bright on La Fin)
    // and a replay button appears.
    if (r && v.getAttribute('data-end') === 'hold') r.classList.add('is-corner');
    v.addEventListener('ended', function () {
      box.classList.add('is-done');
      if (r) r.hidden = false;
    });
    if (r) r.addEventListener('click', function () {
      r.hidden = true;
      box.classList.remove('is-done');
      try { v.currentTime = 0; } catch (err) {}
      play(v);
    });
  });

  function startPlayback() {
    if (!('IntersectionObserver' in window)) {
      // Old browsers: just play everything, scene 4 included
      if (potVideo) play(potVideo);
      Array.prototype.forEach.call(document.querySelectorAll('.scene-video'), play);
      Array.prototype.forEach.call(document.querySelectorAll('.reveal'), function (el) { el.classList.add('is-in'); });
      return;
    }

    var videos = Array.prototype.slice.call(document.querySelectorAll('.scene-video'));
    if (potVideo) { potVideo.setAttribute('data-mode', 'loop'); videos.unshift(potVideo); }

    // The pot loops while at least a third is on screen. Each scene starts once at half visible,
    // pauses if scrolled away before it ends, and stays on its last frame when done.
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        var v = e.target;
        var once = v.getAttribute('data-mode') === 'once';
        var ratio = e.intersectionRatio;
        if (once) {
          if (v.ended) return;
          if (ratio >= 0.5) play(v);
          else if (ratio === 0 || !e.isIntersecting) v.pause();
        } else {
          if (ratio >= 0.33) play(v); else v.pause();
        }
      });
    }, { threshold: [0, 0.33, 0.5] });
    videos.forEach(function (v) { io.observe(v); });

    // Start buffering each scene well before it arrives
    var pre = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.preload = 'auto'; pre.unobserve(e.target); }
      });
    }, { rootMargin: '150% 0px' });
    videos.forEach(function (v) { pre.observe(v); });

    // Narration fades in
    var reveal = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add('is-in'); reveal.unobserve(e.target); }
      });
    }, { threshold: 0.15 });
    Array.prototype.forEach.call(document.querySelectorAll('.reveal'), function (el) { reveal.observe(el); });
  }
})();
