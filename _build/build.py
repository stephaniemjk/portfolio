"""Builds every page of stephaniemkim.com except /fishermanswife.

Run from anywhere:  python3 _build/build.py
Edit content in _build/ (about.html, designs/, reviews/) or in the lists below,
then run this and commit the generated .html files.

When style.css changes, bump CSSV so returning visitors get the new CSS
(Cloudflare tells browsers to cache it for 4 hours).
"""
import html
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, '_build')
CSSV = '20'

# Film Writing is hidden for now. To bring it back: set this to True,
# delete the "Film Writing hidden" lines in _redirects, and rebuild.
SHOW_FILM_WRITING = False

NAV = [
    ('/', 'About', 'about'),
    ('/graphics', 'Graphics', 'graphics'),
    ('/animations', 'Animations', 'animations'),
    ('/interactive', 'Interactive Web', 'interactive'),
] + ([('/film-writing', 'Film Writing', 'film')] if SHOW_FILM_WRITING else [])
DESC = ("Stephanie M. Kim: illustration, animation, interactive web and film writing from New York."
        if SHOW_FILM_WRITING else
        "Stephanie M. Kim: illustration, animation and interactive web from New York.")


def read(*parts):
    with open(os.path.join(SRC, *parts), encoding='utf-8') as f:
        return f.read().strip()


def page(title, active, main, desc=DESC):
    nav = '\n        '.join(
        f'<a{" class=\"is-active\" aria-current=\"page\"" if key == active else ""} href="{href}">{name}</a>'
        for href, name, key in NAV)
    full = "Stephanie M. Kim" if title is None else f"{title} | Stephanie M. Kim"
    return f'''<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{html.escape(full)}</title>
    <meta name="description" content="{html.escape(desc)}" />
    <meta property="og:title" content="{html.escape(full)}" />
    <meta property="og:description" content="{html.escape(desc)}" />
    <meta property="og:image" content="https://stephaniemkim.com/fishermanswife/img/posters/scene-01.webp" />
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=DM+Mono:ital,wght@0,300;0,400;0,500;1,400;1,500&display=swap" />
    <link rel="stylesheet" href="/style.css?v={CSSV}" />
    <script>document.documentElement.classList.add('js');</script>
  </head>
  <body>
    <main class="page">
      <header class="site-header">
        <h1><a href="/">Stephanie M. Kim</a></h1>
        <nav class="nav-bar" aria-label="Primary">
        {nav}
        </nav>
      </header>
{main}
    </main>
  </body>
</html>
'''


def tile(href, img, alt, title, sub=None, badge=None):
    s = f'\n            <p>{sub}</p>' if sub else ''
    b = f'\n            <span class="tile-badge">{badge}</span>' if badge else ''
    return f'''        <a class="gallery-tile" href="{href}">
          <div class="tile-media">
            <img src="{img}" alt="{alt}" loading="lazy" />{b}
          </div>
          <div class="tile-text">
            <h2>{title}</h2>{s}
          </div>
        </a>'''


def video_media(slug, title, w, h, sound, shaped=False):
    """A self-hosted looping video shown like a plain asset (files in assets/video/).
    shaped=True keeps the video's own shape (carousel); otherwise it fills a standard tile."""
    btn = '<button type="button" class="vid-sound" aria-pressed="false">Sound on</button>' if sound else ''
    style = f' style="aspect-ratio: {w} / {h}"' if shaped else ''
    return (f'<div class="vid"{style}>'
            f'<video src="/assets/video/{slug}.mp4" poster="/assets/img/{slug}-poster.webp" '
            f'autoplay muted loop playsinline preload="metadata" aria-label="{title}"></video>'
            f'{btn}</div>')


def video(slug, title, w, h, sound):
    return f'''        <div class="gallery-tile">
          <div class="tile-media video">
            {video_media(slug, title, w, h, sound)}
          </div>
          <div class="tile-text">
            <h2>{title}</h2>
          </div>
        </div>'''


# ---------- Content ----------

DESIGNS = [
    # slug, title, source fragment, image name, alt, width, height
    ('designs-grid-de-sac', 'Grid-de-Sac', 'grid-de-sac', 'grid-de-sac', 'Grid-de-Sac', 1920, 1080),
    ('designs-chezkim', 'Chez Kim', 'chez-kim', 'chez-kim', 'Chez Kim', 2000, 1600),
    ('designs-publicspace', 'Assembly at Radiant Square', 'public-space', 'public-space',
     'Digital collage of a public plaza inspired by Cité Radieuse', 2000, 1500),
]

VIDEOS = [
    # file slug (assets/video/<slug>.mp4, assets/img/<slug>-poster.webp), title, width, height,
    # has sound (shows the Sound on button)
    ('harmless-guests', 'Harmless Guests', 1920, 1080, True),
    ('nested-gloves', 'Nested Gloves in Scaffolding', 1080, 1440, False),
    ('puppet-karate', 'Puppet Karate', 1080, 1350, False),
    ('paint-strokes', 'Performance by the [Paint] Strokes', 1280, 720, False),
    ('le-train', 'Le Train', 1600, 1200, True),
    ('concrete-beach', 'Concrete Beach', 1600, 1200, True),
    ('vending-machine', 'Vending Machine', 1200, 1500, True),
]

LETTERBOXD = 'https://letterboxd.com/saucygarlicbaby/'

# (group name, show director on each entry, reviews)
REVIEW_GROUPS = [
    ('French New Wave', True, [
        dict(slug='film-writing-the-lovers', film='The Lovers', year='1958',
             director='Louis Malle', src='lovers.txt',
             lb='https://letterboxd.com/saucygarlicbaby/film/the-lovers/'),
        dict(slug='film-writing-vivre-sa-vie', film='Vivre Sa Vie', year='1962',
             director='Jean-Luc Godard', src='vivre.txt',
             lb='https://letterboxd.com/saucygarlicbaby/film/vivre-sa-vie/'),
        dict(slug='film-writing-masculin-feminin', film='Masculin Féminin', year='1966',
             director='Jean-Luc Godard', src='masculin.txt',
             lb='https://letterboxd.com/saucygarlicbaby/film/masculin-feminin/'),
    ]),
]

# Pulled from the site for now. Texts stay in _build/reviews/.
# To restore one, move it back into a group above, delete its line in
# _redirects, and rebuild.
PULLED = [
    dict(slug='film-writing-last-days-of-disco', film='The Last Days of Disco', year='1998',
         director='Whit Stillman', src='disco.txt',
         lb='https://letterboxd.com/saucygarlicbaby/film/the-last-days-of-disco/1/'),
    dict(slug='film-writing-barcelona', film='Barcelona', year='1994',
         director='Whit Stillman', src='barcelona.txt',
         lb='https://letterboxd.com/saucygarlicbaby/film/barcelona/reviews/'),
    dict(slug='film-writing-elevator-to-the-gallows', film='Elevator to the Gallows', year='1958',
         director='Louis Malle', src='elevator.txt',
         lb='https://letterboxd.com/saucygarlicbaby/film/elevator-to-the-gallows/'),
    dict(slug='film-writing-the-cousins', film='The Cousins', year='1959',
         director='Claude Chabrol', src='cousins.txt',
         lb='https://letterboxd.com/saucygarlicbaby/film/the-cousins-1959/'),
]

# ---------- Pages ----------

FILES = {}

FILES['index.html'] = page(None, 'about', '\n      ' + read('about.html'))

graphics = '\n'.join(
    tile('/' + slug, f'/assets/img/{img}-thumb.webp', alt, title)
    for slug, title, _, img, alt, _, _ in DESIGNS)
animations = '\n'.join(video(*v) for v in VIDEOS)


# Carousel view: one piece at a time, uncropped.
def slide(media, title, href=None):
    t = f'<a href="{href}">{title}</a>' if href else title
    return f'''          <li class="slide">
            <div class="slide-media">{media}</div>
            <p class="slide-caption">{t}</p>
          </li>'''


graphic_slides = [slide(f'<a href="/{slug}"><img src="/assets/img/{img}.webp" alt="{alt}" loading="lazy" /></a>',
                        title, '/' + slug)
                  for slug, title, _, img, alt, _, _ in DESIGNS]
animation_slides = [slide(video_media(slug, t, w, h, snd, shaped=True), t)
                    for slug, t, w, h, snd in VIDEOS]

VIEW_SCRIPT = '''
      <script>
        (function () {
          var root = document.documentElement;
          var btns = document.querySelectorAll('.view-toggle button');
          var track = document.querySelector('.carousel-track');
          var slides = track.querySelectorAll('.slide');
          var count = document.querySelector('.carousel-count');
          var prev = document.querySelector('.carousel-prev');
          var next = document.querySelector('.carousel-next');
          var cur = 0;
          function setView(v) {
            root.setAttribute('data-view', v);
            btns.forEach(function (b) { b.setAttribute('aria-pressed', b.dataset.view === v); });
            try { localStorage.setItem('gallery-view', v); } catch (e) {}
          }
          function show() {
            count.textContent = (cur + 1) + ' / ' + slides.length;
            prev.disabled = cur === 0;
            next.disabled = cur === slides.length - 1;
          }
          function go(i) {
            cur = Math.max(0, Math.min(slides.length - 1, i));
            track.scrollTo({ left: slides[cur].offsetLeft - track.offsetLeft, behavior: 'smooth' });
            show();
          }
          btns.forEach(function (b) { b.addEventListener('click', function () { setView(b.dataset.view); }); });
          prev.addEventListener('click', function () { go(cur - 1); });
          next.addEventListener('click', function () { go(cur + 1); });
          track.addEventListener('scroll', function () {
            var i = Math.round(track.scrollLeft / track.clientWidth);
            if (i !== cur) { cur = i; show(); }
          }, { passive: true });
          document.addEventListener('keydown', function (e) {
            if (root.getAttribute('data-view') !== 'carousel') return;
            if (e.key === 'ArrowLeft') go(cur - 1);
            if (e.key === 'ArrowRight') go(cur + 1);
          });
          var saved = null;
          try { saved = localStorage.getItem('gallery-view'); } catch (e) {}
          setView(saved === 'carousel' ? 'carousel' : 'list');
          show();
        })();
      </script>'''

VIDEO_SCRIPT = '''
      <script>
        (function () {
          var boxes = [].slice.call(document.querySelectorAll('.vid'));
          boxes.forEach(function (box) {
            var v = box.querySelector('video'), b = box.querySelector('.vid-sound');
            if (!b) return;
            b.addEventListener('click', function () {
              v.muted = !v.muted;
              b.textContent = v.muted ? 'Sound on' : 'Sound off';
              b.setAttribute('aria-pressed', String(!v.muted));
              if (v.paused) v.play();
            });
          });
          if (!('IntersectionObserver' in window)) return;
          var io = new IntersectionObserver(function (entries) {
            entries.forEach(function (en) {
              var v = en.target;
              if (en.isIntersecting) { var p = v.play(); if (p && p.catch) p.catch(function () {}); }
              else v.pause();
            });
          }, { threshold: 0.25 });
          boxes.forEach(function (box) { io.observe(box.querySelector('video')); });
        })();
      </script>'''

def gallery_page(title, key, tiles, slides, scripts=''):
    """A gallery with a List (uniform tile grid) / Carousel toggle."""
    return page(title, key, f'''
      <div class="view-toggle" role="group" aria-label="View">
        <button type="button" data-view="list" aria-pressed="true">List</button>
        <button type="button" data-view="carousel" aria-pressed="false">Carousel</button>
      </div>
      <section class="gallery-grid view-list" aria-label="{title}">
{tiles}
      </section>
      <section class="carousel view-carousel" aria-label="{title}">
        <ul class="carousel-track">
{chr(10).join(slides)}
        </ul>
        <div class="carousel-controls">
          <button type="button" class="carousel-prev" aria-label="Previous">←</button>
          <span class="carousel-count" aria-live="polite"></span>
          <button type="button" class="carousel-next" aria-label="Next">→</button>
        </div>
      </section>{VIEW_SCRIPT}{scripts}''')


FILES['graphics.html'] = gallery_page('Graphics', 'graphics', graphics, graphic_slides)
FILES['animations.html'] = gallery_page('Animations', 'animations', animations, animation_slides, VIDEO_SCRIPT)

FILES['interactive.html'] = page('Interactive Web', 'interactive', '''
      <section class="gallery-grid" aria-label="Interactive web projects">
''' + tile('/fishermanswife/', '/fishermanswife/img/posters/scene-01.webp',
           'A painted kitchen scene from Fisherman’s Wife', 'Fisherman’s Wife',
           'An interactive folk tale experience.') + '\n      </section>')

for slug, title, frag, img, alt, w, h in DESIGNS:
    FILES[slug + '.html'] = page(title, 'graphics', f'''
      <article class="detail">
        <div>
          <p class="kicker">Graphics</p>
          <h2>{title}</h2>
        </div>
        <img class="detail-image" src="/assets/img/{img}.webp" alt="{alt}" width="{w}" height="{h}" />
        <div class="detail-text">
          {read('designs', frag + '.html')}
        </div>
        <a class="back-link" href="/graphics">← Back to Graphics</a>
      </article>''')


def paragraphs(text):
    return [p.strip() for p in re.split(r'\n\s*\n', text) if p.strip()]


def review_item(r, show_director):
    d = f'\n              <p class="director">{r["director"]}</p>' if show_director else ''
    return f'''          <li>
            <a href="/{r['slug']}">
              <h3><cite>{r['film']}</cite> <span class="year">({r['year']})</span></h3>{d}
              <p>{html.escape(r['excerpt'], quote=False)}</p>
            </a>
          </li>'''


sections = []
for group, show_director, reviews in (REVIEW_GROUPS if SHOW_FILM_WRITING else []):
    if not reviews:
        continue
    for r in reviews:
        ps = paragraphs(read('reviews', r['src']))
        r['excerpt'] = re.split(r'(?<=[.!?”])\s', ps[0])[0]
        body = '\n          '.join(f'<p>{html.escape(p, quote=False)}</p>' for p in ps)
        kicker = f"{group} · {r['director']}" if show_director else r['director']
        FILES[r['slug'] + '.html'] = page(f"{r['film']} ({r['year']})", 'film', f'''
      <article class="detail">
        <div>
          <p class="kicker">{kicker}</p>
          <h2><cite>{r['film']}</cite> <span class="year">({r['year']})</span></h2>
        </div>
        <div class="detail-text">
          {body}
        </div>
        <p class="source">Also on <a href="{r['lb']}">Letterboxd</a></p>
        <a class="back-link" href="/film-writing">← Back to Film Writing</a>
      </article>''', desc=f"Stephanie M. Kim on {r['director']}’s {r['film']}.")
    items = '\n'.join(review_item(r, show_director) for r in reviews)
    sections.append(f'''        <div class="writing-section">
          <h2 class="writing-group">{group}</h2>
          <ul class="writing-list">
{items}
          </ul>
        </div>''')

if SHOW_FILM_WRITING:
  FILES['film-writing.html'] = page('Film Writing', 'film', f'''
      <section class="writing">
{chr(10).join(sections)}
        <p class="source">More on <a href="{LETTERBOXD}">Letterboxd</a></p>
      </section>''')

FILES['404.html'] = page('Page not found', None, '''
      <section class="about-wrap">
        <div class="about">
          <p>That page doesn’t exist.</p>
          <p><a href="/">Go to the homepage</a></p>
        </div>
      </section>''')

for name, content in FILES.items():
    with open(os.path.join(ROOT, name), 'w', encoding='utf-8') as f:
        f.write(content)
    print('wrote', name)
