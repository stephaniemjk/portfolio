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

  /* ---------- Playback on scroll ---------- */
  function play(v) {
    var p = v.play();
    if (p && p.catch) p.catch(function () {});
  }

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

    // Loops play while at least a third is on screen. Scene 4 starts once at half visible,
    // pauses if scrolled away before it ends, and holds on its last frame (La Fin).
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
