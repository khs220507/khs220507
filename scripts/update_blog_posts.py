"""Refresh the five latest public blog links; no credentials required."""
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.parse import urlparse
import xml.etree.ElementTree as ET
import re

def update():
    root = Path(__file__).resolve().parents[1]
    req = Request('https://khs220507.github.io/feed.xml', headers={'User-Agent': 'khs220507-profile'})
    with urlopen(req, timeout=30) as response:
        feed = ET.fromstring(response.read())
    ns = {'a': 'http://www.w3.org/2005/Atom'}
    rows = []
    for entry in feed.findall('a:entry', ns):
        link = next((node.get('href', '') for node in entry.findall('a:link', ns) if node.get('rel', 'alternate') == 'alternate'), '')
        if urlparse(link).netloc != 'khs220507.github.io':
            continue
        title = ' '.join((entry.findtext('a:title', '', ns)).split())
        title = title.replace('[', '\\[').replace(']', '\\]')
        rows.append(f'- [{title}]({link})')
        if len(rows) == 5: break
    if not rows: raise ValueError('No valid blog entries; README left unchanged')
    file = root / 'README.md'
    text = file.read_text(encoding='utf-8')
    pattern = r'<!-- BLOG-POSTS:START -->.*?<!-- BLOG-POSTS:END -->'
    assert len(re.findall(pattern, text, re.S)) == 1
    replacement = '<!-- BLOG-POSTS:START -->\n' + '\n'.join(rows) + '\n<!-- BLOG-POSTS:END -->'
    file.write_text(re.sub(pattern, lambda _: replacement, text, flags=re.S), encoding='utf-8')
    print(f'Updated {len(rows)} blog links')

if __name__ == '__main__': update()
