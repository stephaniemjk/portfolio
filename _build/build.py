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
CSSV = '6'

NAV = [
    ('/', 'About', 'about'),
    ('/visuals', 'Visuals', 'visuals'),
    ('/interactive', 'Interactive Web', 'interactive'),
    ('/film-writing', 'Film Writing', 'film'),
]
DESC = "Stephanie Kim: illustration, animation, interactive web and film writing from New York."


def read(*parts):
    with open(os.path.join(SRC, *parts), encoding='utf-8') as f:
        return f.read().strip()


def page(title, active, main, desc=DESC):
    nav = '\n        '.join(
        f'<a{" class=\"is-active\" aria-current=\"page\"" if key == active else ""} href="{href}">{name}</a>'
        for href, name, key in NAV)
    full = "Stephanie Kim" if title is None else f"{title} | Stephanie Kim"
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
    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap" />
    <link rel="stylesheet" href="/style.css?v={CSSV}" />
  </head>
  <body>
    <main class="page">
      <header class="site-header">
        <h1><a href="/">Stephanie Kim</a></h1>
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


def video(yt_id, title):
    return f'''        <div class="gallery-tile">
          <div class="tile-media">
            <iframe src="https://www.youtube-nocookie.com/embed/{yt_id}" title="{title}" loading="lazy" allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>
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
    ('oGl9cEbhAxA', 'Harmless Guests'),
    ('mzmz8qlgKCY', 'Le Train'),
]

LETTERBOXD = 'https://letterboxd.com/saucygarlicbaby/'

# (group name, show director on each entry, reviews)
REVIEW_GROUPS = [
    ('Whit Stillman', False, [
        dict(slug='film-writing-last-days-of-disco', film='The Last Days of Disco', year='1998',
             director='Whit Stillman', src='disco.txt',
             lb='https://letterboxd.com/saucygarlicbaby/film/the-last-days-of-disco/1/'),
        dict(slug='film-writing-barcelona', film='Barcelona', year='1994',
             director='Whit Stillman', src='barcelona.txt',
             lb='https://letterboxd.com/saucygarlicbaby/film/barcelona/reviews/'),
    ]),
    ('French New Wave', True, [
        dict(slug='film-writing-elevator-to-the-gallows', film='Elevator to the Gallows', year='1958',
             director='Louis Malle', src='elevator.txt',
             lb='https://letterboxd.com/saucygarlicbaby/film/elevator-to-the-gallows/'),
        dict(slug='film-writing-the-lovers', film='The Lovers', year='1958',
             director='Louis Malle', src='lovers.txt',
             lb='https://letterboxd.com/saucygarlicbaby/film/the-lovers/'),
        dict(slug='film-writing-the-cousins', film='The Cousins', year='1959',
             director='Claude Chabrol', src='cousins.txt',
             lb='https://letterboxd.com/saucygarlicbaby/film/the-cousins-1959/'),
        dict(slug='film-writing-vivre-sa-vie', film='Vivre Sa Vie', year='1962',
             director='Jean-Luc Godard', src='vivre.txt',
             lb='https://letterboxd.com/saucygarlicbaby/film/vivre-sa-vie/'),
        dict(slug='film-writing-masculin-feminin', film='Masculin Féminin', year='1966',
             director='Jean-Luc Godard', src='masculin.txt',
             lb='https://letterboxd.com/saucygarlicbaby/film/masculin-feminin/'),
    ]),
]

# ---------- Pages ----------

FILES = {}

FILES['index.html'] = page(None, 'about', '\n      ' + read('about.html'))

FILES['visuals.html'] = page('Visuals', 'visuals', '''
      <section class="gallery-grid" aria-label="Visual work">
''' + '\n'.join(
    [tile('/' + slug, f'/assets/img/{img}-thumb.webp', alt if img != 'public-space' else 'Digital collage of a public plaza', title)
     for slug, title, _, img, alt, _, _ in DESIGNS]
    + [video(i, t) for i, t in VIDEOS]) + '\n      </section>')

FILES['interactive.html'] = page('Interactive Web', 'interactive', '''
      <section class="gallery-grid" aria-label="Interactive web projects">
''' + tile('/fishermanswife/', '/fishermanswife/img/posters/scene-01.webp',
           'A painted kitchen scene from Fisherman’s Wife', 'Fisherman’s Wife',
           'An interactive folk tale experience.') + '\n      </section>')

for slug, title, frag, img, alt, w, h in DESIGNS:
    FILES[slug + '.html'] = page(title, 'visuals', f'''
      <article class="detail">
        <h2>{title}</h2>
        <img class="detail-image" src="/assets/img/{img}.webp" alt="{alt}" width="{w}" height="{h}" />
        <div class="detail-text">
          {read('designs', frag + '.html')}
        </div>
        <a class="back-link" href="/visuals">← Back to Visuals</a>
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
for group, show_director, reviews in REVIEW_GROUPS:
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
      </article>''', desc=f"Stephanie Kim on {r['director']}’s {r['film']}.")
    items = '\n'.join(review_item(r, show_director) for r in reviews)
    sections.append(f'''        <div class="writing-section">
          <h2 class="writing-group">{group}</h2>
          <ul class="writing-list">
{items}
          </ul>
        </div>''')

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
