"""Retrieve the fixed #188 pool and extract text; never invokes CAL or judges claims.

Owner/authority: CAL issue #188. Raw bytes are append-only private-local custody.
HTML text is BeautifulSoup 4.14.3 get_text(' ', strip=False); PDF uses pdftotext
-layout. The raw bytes, extractor, DOM ordinals and extraction hashes are retained.
One GET per fixed locator; unavailable locators are retained, never substituted.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import subprocess
import urllib.error
import urllib.request
from pathlib import Path

from bs4 import BeautifulSoup

POOL = [
    ('Statistics Canada firearms 2023', 'https://www150.statcan.gc.ca/n1/pub/85-002-x/2025001/article/00002-eng.htm'),
    ('Statistics Canada rural crime 2023', 'https://www150.statcan.gc.ca/n1/pub/85-002-x/2025001/article/00005-eng.htm'),
    ('Statistics Canada mothers and fathers 2023', 'https://www150.statcan.gc.ca/n1/pub/14-28-0001/2024001/article/00006-eng.htm'),
    ('Statistics Canada Indigenous custody', 'https://www150.statcan.gc.ca/n1/daily-quotidien/230712/dq230712a-eng.htm'),
    ('Statistics Canada COPD 2009', 'https://www150.statcan.gc.ca/n1/pub/82-625-x/2010002/article/11273-eng.htm'),
    ('CDC NIOSH truck crash', 'https://stacks.cdc.gov/view/cdc/181173'),
    ('CDC NCHS contraception DB188', 'https://www.cdc.gov/nchs/products/databriefs/db188.htm'),
    ('CDC EID Rift Valley fever figure', 'https://wwwnc.cdc.gov/eid/article/14/8/08-0082-f4'),
    ('FDA West Coast Laboratories', 'https://www.fda.gov/inspections-compliance-enforcement-and-criminal-investigations/warning-letters/west-coast-laboratories-inc-672954-06122024'),
    ('FDA Diamond Wipes International', 'https://www.fda.gov/inspections-compliance-enforcement-and-criminal-investigations/warning-letters/diamond-wipes-international-inc-534290-03072018'),
    ('FDA Somalabs', 'https://www.fda.gov/inspections-compliance-enforcement-and-criminal-investigations/warning-letters/somalabs-inc-573299-05312019'),
    ('NASA OIG IG-18-015', 'https://oig.nasa.gov/docs/IG-18-015.pdf'),
]


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    sources = []
    for i, (title, url) in enumerate(POOL, 1):
        folder = args.output / f'{i:02d}'
        folder.mkdir()
        record = {'source_id': f'S{i:02d}', 'title': title, 'fixed_url': url,
                  'retrieved_at_utc': dt.datetime.now(dt.timezone.utc).isoformat()}
        request = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 CAL-188 frozen-source research',
            'Accept': '*/*', 'Accept-Encoding': 'identity'})
        try:
            response = urllib.request.urlopen(request, timeout=60)
        except urllib.error.HTTPError as exc:
            response = exc
        except Exception as exc:
            record.update(status='SOURCE_UNAVAILABLE', error=repr(exc))
            (folder / 'custody.json').write_text(json.dumps(record, indent=2) + '\n')
            sources.append(record)
            print(json.dumps(record), flush=True)
            continue
        with response:
            raw = response.read(64 * 1024 * 1024 + 1)
            if len(raw) > 64 * 1024 * 1024:
                raise RuntimeError('Bounded source-size limit exceeded')
            record.update(http_status=response.status, final_url=response.geturl(),
                          media_type=response.headers.get('Content-Type'),
                          headers=dict(response.headers), raw_sha256=sha(raw), raw_bytes=len(raw))
        (folder / 'raw.bin').write_bytes(raw)
        record['status'] = 'AVAILABLE' if record['http_status'] == 200 else 'SOURCE_UNAVAILABLE'
        if record['status'] == 'AVAILABLE' and raw.startswith(b'%PDF'):
            subprocess.run(['pdftotext', '-layout', str(folder / 'raw.bin'),
                            str(folder / 'extracted.txt')], check=True)
            record['extraction_method'] = 'pdftotext -layout; original page/form-feed/line text retained'
            record['extractor_version'] = subprocess.run(['pdftotext', '-v'], capture_output=True, text=True).stderr
            record['extraction_sha256'] = sha((folder / 'extracted.txt').read_bytes())
        elif record['status'] == 'AVAILABLE':
            soup = BeautifulSoup(raw, 'html.parser')
            body = soup.find('main') or soup.body or soup
            blocks = []
            for ordinal, node in enumerate(body.find_all(['h1', 'h2', 'h3', 'h4', 'p', 'li', 'figcaption'])):
                text = node.get_text(' ', strip=False)
                blocks.append({'ordinal': ordinal, 'tag': node.name, 'id': node.get('id'),
                               'text': text, 'text_sha256': sha(text.encode()),
                               'element_serialization_sha256': sha(str(node).encode())})
            (folder / 'blocks.json').write_text(json.dumps(blocks, ensure_ascii=False, indent=2) + '\n')
            (folder / 'extracted.txt').write_text('\n\n'.join(b['text'] for b in blocks))
            record['extraction_method'] = "BeautifulSoup 4.14.3 html.parser; document-order main/body h1-h4,p,li,figcaption; get_text(' ', strip=False); evidence keeps exact extracted block text"
            record['extraction_sha256'] = sha((folder / 'extracted.txt').read_bytes())
            record['blocks_sha256'] = sha((folder / 'blocks.json').read_bytes())
            record['block_count'] = len(blocks)
            # Preserve links for same-document attached-file navigation if needed.
            (folder / 'links.json').write_text(json.dumps([
                {'text': a.get_text(' ', strip=False), 'href': a.get('href')}
                for a in soup.find_all('a', href=True)], ensure_ascii=False, indent=2) + '\n')
        (folder / 'custody.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n')
        sources.append(record)
        print(json.dumps({k: record.get(k) for k in ['source_id', 'status', 'http_status',
                         'raw_sha256', 'raw_bytes', 'block_count']}), flush=True)
    manifest = {'schema': 'cal188-fixed-source-custody-v1', 'cal_calls': 0,
                'source_substitutions': 0, 'pool_order_preserved': True, 'sources': sources}
    (args.output / 'SOURCE_CUSTODY.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')


if __name__ == '__main__':
    main()
