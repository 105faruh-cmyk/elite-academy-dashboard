"""Сквозная (values A3:P...) -> skv.json {date:[[ключ названия, заявки amo, лиды, квалы],...]}
Использование: python3 tools/skv.py values.json out.json  (values.json — массив строк из get_values)"""
import json, re, sys
def short(n): return re.sub(r'^\s*"[^"]*"\s*', '', n or '').strip()
def key(n): return re.sub(r'[^a-zа-яё0-9]', '', short(n).lower().replace('ё', 'е'))
def num(x):
    x = (x or '').replace('\xa0', '').replace(' ', '').replace(',', '.')
    try: return float(x)
    except ValueError: return 0.0
V = json.load(open(sys.argv[1]))
out = {}; cur = None
for r in V:
    r = r + [''] * (16 - len(r))
    m = re.match(r'(\d\d)\.(\d\d)\.(\d{4})', r[0] or '')
    if m: cur = f'{m.group(3)}-{m.group(2)}-{m.group(1)}'
    if not cur or not r[1].strip(): continue
    out.setdefault(cur, []).append([key(r[1]), num(r[10]), num(r[12]), num(r[15])])
json.dump(out, open(sys.argv[2], 'w'), ensure_ascii=False)
print({d: [len(v), sum(x[2] for x in v), sum(x[3] for x in v)] for d, v in out.items()})
