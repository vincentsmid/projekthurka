#!/usr/bin/env python3
"""Build script that reads concerts.md and injects concert data into HTML files."""

import re
from datetime import datetime, date

DAYS_CS = ['pondělí', 'úterý', 'středa', 'čtvrtek', 'pátek', 'sobota', 'neděle']
MONTHS_CS = [
    'ledna', 'února', 'března', 'dubna', 'května', 'června',
    'července', 'srpna', 'září', 'října', 'listopadu', 'prosince',
]

def format_date(d):
    return f"{DAYS_CS[d.weekday()]} {d.day}. {MONTHS_CS[d.month - 1]} {d.year}"

def parse_concerts(text):
    concerts = []
    blocks = re.split(r'^---$', text, flags=re.MULTILINE)
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        concert = {}
        for line in block.split('\n'):
            m = re.match(r'^(\w+):\s*(.+)$', line)
            if m:
                key = m.group(1).lower()
                val = m.group(2).strip()
                if key == 'date':
                    try:
                        concert['date'] = datetime.strptime(val, '%Y-%m-%d').date()
                    except ValueError:
                        pass
                elif key in ('title', 'název'):
                    concert['title'] = val
                elif key in ('venue', 'místo'):
                    concert['venue'] = val
                elif key in ('city', 'město'):
                    concert['city'] = val
                elif key in ('price', 'vstupné'):
                    concert['price'] = val
                elif key in ('time', 'čas'):
                    concert['time'] = val
                elif key in ('bands', 'kapely'):
                    concert['bands'] = val
                elif key in ('link', 'odkaz'):
                    concert['link'] = val
        if 'date' in concert and 'title' in concert:
            concerts.append(concert)
    concerts.sort(key=lambda c: c['date'])
    return concerts

def render_card(concert, is_next, is_past):
    classes = ['concert-card']
    if is_next:
        classes.append('next')
    if is_past:
        classes.append('past')

    badge = '<div class="next-badge">✦ příští koncert</div>' if is_next else ''
    date_str = format_date(concert['date'])
    venue = concert.get('venue', '')
    city = concert.get('city', '')
    venue_str = f"{venue}, {city}" if city else venue

    bands = ''
    if concert.get('bands'):
        bands = f'<div class="card-bands">♪ {concert["bands"]}</div>'

    meta_parts = []
    if concert.get('time'):
        meta_parts.append(f'<span>⏰ {concert["time"]}</span>')
    if concert.get('price'):
        meta_parts.append(f'<span>🍄 {concert["price"]}</span>')
    meta = f'<div class="card-meta">{"".join(meta_parts)}</div>' if meta_parts else ''

    link = ''
    if concert.get('link'):
        link = f'<a href="{concert["link"]}" target="_blank" class="card-link">→ více info</a>'

    return f"""    <div class="{' '.join(classes)}">
      <div class="concert-card-border"></div>
      {badge}
      <div class="card-date">{date_str}</div>
      <div class="card-title">{concert['title']}</div>
      <div class="card-venue">{venue_str}</div>
      {bands}
      {meta}
      {link}
    </div>"""

CARD_DIVIDER = """    <div class="card-divider">
      <svg width="60" height="30" viewBox="0 0 60 30">
        <path d="M5 15 Q15 3 30 15 Q45 27 55 15" fill="none" stroke="#ff6ef0" stroke-width="1" opacity="0.5"/>
        <circle cx="30" cy="15" r="3" fill="none" stroke="#00ffe0" stroke-width="0.8" opacity="0.4"/>
        <circle cx="30" cy="15" r="1.5" fill="#ffaa30" opacity="0.4"/>
      </svg>
    </div>"""

SECTION_VINE = """    <div class="section-vine">
      <svg width="140" height="50" viewBox="0 0 140 50">
        <path d="M10 25 Q35 5 70 25 Q105 45 130 25" fill="none" stroke="#6a3db8" stroke-width="1.5" opacity="0.6"/>
        <circle cx="70" cy="25" r="4" fill="none" stroke="#ff6ef0" stroke-width="0.8" opacity="0.4"/>
        <circle cx="70" cy="25" r="2" fill="#00ffe0" opacity="0.3"/>
        <circle cx="40" cy="15" r="1.5" fill="#ffaa30" opacity="0.3"/>
        <circle cx="100" cy="35" r="1.5" fill="#ff6ef0" opacity="0.3"/>
      </svg>
    </div>"""

EMPTY_STATE = """    <div class="empty-state">
      <svg width="80" height="80" viewBox="0 0 80 80" style="opacity:0.4; margin-bottom:20px;">
        <circle cx="40" cy="40" r="30" fill="none" stroke="#ff6ef0" stroke-width="1"/>
        <circle cx="40" cy="40" r="20" fill="none" stroke="#00ffe0" stroke-width="0.5" opacity="0.4"/>
        <path d="M25 48 Q40 40 55 48" fill="none" stroke="#b8e090" stroke-width="1.5"/>
        <circle cx="28" cy="32" r="3" fill="#ffaa30" opacity="0.5"/>
        <circle cx="52" cy="32" r="3" fill="#ff6ef0" opacity="0.5"/>
      </svg>
      <p>zatím žádné koncerty v plánu</p>
      <p style="margin-top: 8px; font-size: 1rem;">ale něco roste...</p>
    </div>"""

def build_concert_list(concerts, today):
    upcoming = [c for c in concerts if c['date'] >= today]
    past = [c for c in concerts if c['date'] < today]
    past.reverse()

    parts = []

    if upcoming:
        parts.append('    <div class="section-label">~ nadcházející ~</div>')
        for i, c in enumerate(upcoming):
            parts.append(render_card(c, is_next=(i == 0), is_past=False))
            if i < len(upcoming) - 1:
                parts.append(CARD_DIVIDER)
    else:
        parts.append(EMPTY_STATE)

    if past:
        parts.append(SECTION_VINE)
        parts.append('    <div class="section-label">~ proběhlo ~</div>')
        for c in past:
            parts.append(render_card(c, is_next=False, is_past=True))

    return '\n'.join(parts)

def main():
    with open('concerts.md', 'r', encoding='utf-8') as f:
        concerts_text = f.read()

    concerts = parse_concerts(concerts_text)
    today = date.today()
    upcoming = [c for c in concerts if c['date'] >= today]

    # --- index.html: inject next concert ---
    with open('index.html', 'r', encoding='utf-8') as f:
        index = f.read()

    if upcoming:
        nxt = upcoming[0]
        title = nxt['title']
        date_str = format_date(nxt['date'])
        venue = nxt.get('venue', '')
        city = nxt.get('city', '')
        venue_str = f"{venue}, {city}" if city else venue
    else:
        title = 'žádné koncerty'
        date_str = 'zatím...'
        venue_str = 'ale něco se chystá'

    index = re.sub(
        r'(<div class="concert-title" id="concertTitle">)(.*?)(</div>)',
        rf'\g<1>{title}\3', index
    )
    index = re.sub(
        r'(<div class="concert-date" id="concertDate">)(.*?)(</div>)',
        rf'\g<1>{date_str}\3', index
    )
    index = re.sub(
        r'(<div class="concert-venue" id="concertVenue">)(.*?)(</div>)',
        rf'\g<1>{venue_str}\3', index
    )

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(index)

    # --- concerts.html: inject full concert list ---
    with open('concerts.html', 'r', encoding='utf-8') as f:
        concerts_html = f.read()

    concert_list = build_concert_list(concerts, today)
    concerts_html = re.sub(
        r'(<!-- BEGIN_CONCERTS -->).*?(<!-- END_CONCERTS -->)',
        f'\\1\n  <div id="concertList">\n{concert_list}\n  </div>\n  \\2',
        concerts_html,
        flags=re.DOTALL,
    )

    with open('concerts.html', 'w', encoding='utf-8') as f:
        f.write(concerts_html)

    print(f"Built with {len(upcoming)} upcoming, {len(concerts) - len(upcoming)} past concerts.")

if __name__ == '__main__':
    main()
