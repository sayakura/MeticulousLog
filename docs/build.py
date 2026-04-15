#!/usr/bin/env python3
"""Generate docs/data.json from shot files and metadata."""
import json, glob, os, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'docs' / 'data.json'


def parse_shot_time(filename):
    m = re.search(r'shot_(\d{4}-\d{2}-\d{2})_(\d{2}-\d{2}-\d{2})', filename)
    if m:
        date, time = m.groups()
        return f"{date}T{time.replace('-', ':')}"
    return None


def main():
    with open(ROOT / 'meta' / 'shot-meta.json') as f:
        shot_meta = json.load(f)
    with open(ROOT / 'beans' / 'beans.json') as f:
        beans = {b['id']: b for b in json.load(f)}
    with open(ROOT / 'grinders' / 'grinders.json') as f:
        grinders = {g['id']: g for g in json.load(f)}
    with open(ROOT / 'baskets' / 'baskets.json') as f:
        baskets = {b['id']: b for b in json.load(f)}

    all_files = sorted(
        glob.glob(str(ROOT / 'shots' / '**' / '*.json'), recursive=True) +
        glob.glob(str(ROOT / 'logs' / '*.json'))
    )

    shots = []
    for filepath in all_files:
        with open(filepath) as f:
            raw = json.load(f)

        if 'id' not in raw or 'data' not in raw:
            continue

        uid = raw['id']
        data = raw['data']
        if not data:
            continue

        s_time, s_pressure, s_weight, s_flow = [], [], [], []
        for entry in data:
            t = entry.get('time', 0) / 1000
            s = entry.get('shot', {})
            s_time.append(round(t, 2))
            s_pressure.append(round(s.get('pressure', 0), 2))
            s_weight.append(round(s.get('weight', 0), 2))
            s_flow.append(round(s.get('flow', 0), 2))

        started_at = parse_shot_time(os.path.basename(filepath))

        shot_entry = {
            'id': uid,
            'startedAt': started_at,
            'profile': raw.get('name', ''),
            'duration': round(s_time[-1], 1) if s_time else 0,
            'series': {
                'time': s_time,
                'pressure': s_pressure,
                'weight': s_weight,
                'flow': s_flow,
            },
        }

        meta = shot_meta.get(uid)
        if meta:
            bean = beans.get(meta.get('beanId', ''))
            grinder = grinders.get(meta.get('grinderId', ''))
            basket = baskets.get(meta.get('basketId', ''))
            shot_entry['rating'] = meta.get('rating')
            shot_entry['note'] = meta.get('note', '')
            shot_entry['grindSetting'] = meta.get('grindSetting', '')
            if bean:
                shot_entry['bean'] = {
                    'name': bean['name'],
                    'roaster': bean['roaster'],
                    'roastLevel': bean.get('roastLevel', ''),
                }
            if grinder:
                shot_entry['grinder'] = {
                    'name': grinder['name'],
                    'brand': grinder['brand'],
                }
            if basket:
                shot_entry['basket'] = {'name': basket['name']}

        shots.append(shot_entry)

    shots.sort(key=lambda s: s.get('startedAt') or '', reverse=True)

    with open(OUT, 'w') as f:
        json.dump({'shots': shots}, f, separators=(',', ':'))

    size_kb = OUT.stat().st_size / 1024
    rated = sum(1 for s in shots if 'rating' in s)
    print(f'docs/data.json: {len(shots)} shots ({rated} rated), {size_kb:.0f} KB')


if __name__ == '__main__':
    main()
