"""Deterministic local corpus CLI; direct file reads are equally valid acquisition."""
import argparse
import json
import math
from pathlib import Path
import re


def tokens(text):
    return re.findall(r'[\w]+', text.lower())


def search(records, query, limit=6):
    terms = set(tokens(query))
    documents = [set(tokens(r['title'] + ' ' + r['text'])) for r in records]
    weights = {t: 1 + math.log((1 + len(records))/(1 + sum(t in d for d in documents))) for t in terms}
    ranked = []
    for record, words in zip(records, documents):
        score = sum(weights[t] for t in terms & words)
        if score:
            lines = record['text'].splitlines()
            snippet = max(lines, key=lambda line: len(terms & set(tokens(line))))[:320]
            ranked.append(dict(id=record['id'], title=record['title'], role=record['role'], version=record['version'], lineage=record['lineage'], score=round(score, 6), snippet=snippet))
    return sorted(ranked, key=lambda r: (-r['score'], r['id']))[:limit]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--log', type=Path, required=True, help='Explicit private output outside the fixture/source tree')
    sub = p.add_subparsers(dest='action', required=True)
    s = sub.add_parser('search'); s.add_argument('query'); s.add_argument('--limit', type=int, default=6)
    r = sub.add_parser('read'); r.add_argument('id')
    a = p.parse_args()
    root = Path(__file__).resolve().parent
    log = a.log.resolve()
    if log == root or root in log.parents:
        p.error('access log must be outside fixture/source tree')
    if any((ancestor/'.git').exists() for ancestor in (log.parent, *log.parent.parents)):
        p.error('access log must be outside Git')
    records = json.loads((root/'corpus.json').read_text())
    if a.action == 'search':
        if not 1 <= a.limit <= 50: p.error('limit must be 1..50')
        result = search(records, a.query, a.limit)
        event = dict(action='search', query=a.query, returned=[r['id'] for r in result])
    else:
        result = next((r for r in records if r['id'] == a.id), None)
        if result is None: p.error('unknown page id')
        event = dict(action='read', id=a.id)
    with log.open('a') as f: f.write(json.dumps(event)+'\n')
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == '__main__': main()
