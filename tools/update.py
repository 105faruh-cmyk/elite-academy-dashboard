"""Обновление data.enc.json без сырых данных в репозитории.
Запуск: PW=пароль python3 tools/update.py IN_DIR
IN_DIR содержит:
  meta.json  — ad-level Meta по дням (поля как ads_get_ad_entities: date_start,id,name,campaign_name,adset_name,
               effective_status,amount_spent,impressions,reach,clicks,actions:onsite_conversion.messaging_conversation_started_7d)
  ssp.json   — {"2026-11-01":[лиды таргет, лиды органика, квалы ОП, квалы AI, квалы таргет, квалы органика, назначено],...}
  amo.json   — {"Z":{"MM-DD|typ":n}, "J":{"MM-DD":{typ:[0,lid,q,naz,prov,pre,won,revKGS,priced]}}}  (typ: t/o/T/'' )
  ag.txt     — токены "DDsCCcode:n[/rev]" (DD день события, s этап 1-5, CC день создания, code кодовое слово или TPL)
Дни, которые есть во входных файлах, заменяются целиком; остальные остаются как были."""
import json, base64, hashlib, os, re, sys, datetime, collections
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

IN = sys.argv[1]; PW = os.environ['PW'].encode(); Y = '2026'; MON = os.environ.get('MON', '11')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); ENC = os.path.join(ROOT, 'data.enc.json')
b64 = base64.b64decode
e = json.load(open(ENC)); k = hashlib.pbkdf2_hmac('sha256', PW, b64(e['salt']), 300000, 32)
D = json.loads(AESGCM(k).decrypt(b64(e['iv']), b64(e['ct']), None))
P = lambda f: os.path.join(IN, f)

def short(n): return re.sub(r'^\s*"[^"]*"\s*', '', n or '').strip()
def key(n): return re.sub(r'[^a-zа-яё0-9]', '', short(n).lower().replace('ё', 'е'))

# Meta
if os.path.exists(P('meta.json')):
    M = [r for r in json.load(open(P('meta.json'))) if 'id' in r]
    aidx = {a[0]: i for i, a in enumerate(D['ads'])}
    days = collections.defaultdict(list)
    for r in M:
        if r['id'] not in aidx:
            aidx[r['id']] = len(D['ads']); D['ads'].append([r['id'], short(r['name']) or r['name'], r.get('campaign_name', ''), r.get('adset_name', ''), r.get('effective_status', '')])
        else:
            D['ads'][aidx[r['id']]][4] = r.get('effective_status', D['ads'][aidx[r['id']]][4])
        sp = float((r.get('amount_spent') or {}).get('value') or 0)
        cv = r.get('actions:onsite_conversion.messaging_conversation_started_7d')
        if isinstance(cv, dict): cv = (cv.get('values') or [{}])[0].get('value', 0)
        try: cv = int(cv or 0)
        except ValueError: cv = 0
        days[r['date_start']].append([aidx[r['id']], round(sp, 2), int(r.get('impressions') or 0), int(r.get('reach') or 0), int(r.get('clicks') or 0), cv])
    D['meta'].update(days)
if os.path.exists(P('ssp.json')):
    D['ssp'].update(json.load(open(P('ssp.json'))))

active = collections.defaultdict(set)
for d, rows in D['meta'].items():
    for row in rows:
        if row[1] > 0: active[d].add(key(D['ads'][row[0]][1]))
EMO = {'огонь': '🔥', 'синее': '💙', 'оранж': '🧡', 'белое': '🤍', 'флаг': '🇺🇸', 'фиолет': '💜', 'зеленое': '💚'}
def cw(s):
    s = (s or '').lower().replace('ё', 'е').replace('🇺🇲', '🇺🇸').replace('(флаг)', '🇺🇸')
    for w, em in EMO.items(): s = s.replace(w, em)
    return re.sub(r'[\s!.,?]', '', s.replace('cша', 'сша'))
MAP = json.load(open(os.path.join(ROOT, 'tools', 'codewords.json')))
MAP = {cw(c): [key(x) for x in v] for c, v in MAP.items()}
def prev(d): return (datetime.date.fromisoformat(d) - datetime.timedelta(days=1)).isoformat()
def attribute(code, d):
    c = cw(code); cands = MAP.get(c)
    if not cands: return None
    act = [x for x in cands if x in active.get(d, set()) or x in active.get(prev(d), set())]
    return act or cands

unattr = 0
if os.path.exists(P('amo.json')):
    A = json.load(open(P('amo.json')))
    nd = {f'{Y}-{md}' for md in A['J']} | {f'{Y}-{kk.split("|")[0]}' for kk in A['Z']}
    for d in nd: D['j'][d] = {}
    for kk, n in A['Z'].items():
        md, t = kk.split('|'); d = f'{Y}-{md}'; t = t or 'u'
        D['j'][d].setdefault(t, [0] * 9)[0] += n
    for md, m in A['J'].items():
        d = f'{Y}-{md}'
        for t, v in m.items():
            row = D['j'][d].setdefault(t or 'u', [0] * 9)
            for i in range(1, 9): row[i] += v[i]
if os.path.exists(P('ag.txt')):
    akeys = {key(a[1]): i for i, a in enumerate(D['ads'])}
    AJ = collections.defaultdict(lambda: collections.defaultdict(lambda: [0.0] * 6))
    for tok in open(P('ag.txt')).read().split():
        mm = re.match(r'(\d\d)(\d)(\d\d)(.+):(\d+)(?:/(\d+))?$', tok)
        if not mm: continue
        dd, st, cd, code, n, rv = mm.groups(); st, n, rv = int(st), int(n), float(rv or 0)
        d, c = f'{Y}-{MON}-{dd}', f'{Y}-{MON}-{cd}'
        tgt = ['__tpl'] if code == 'TPL' else attribute(code, c)
        if not tgt: unattr += n; continue
        w = 1.0 / len(tgt)
        for t in tgt:
            AJ[d][t][st - 1] += n * w
            if st == 5: AJ[d][t][5] += rv * w
    for d, m in AJ.items():
        D['aj'][d] = [[akeys.get(t, -1) if t != '__tpl' else -2] + [round(x, 2) for x in v] for t, v in m.items()]

D['updated'] = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%MZ')
pt = json.dumps(D, ensure_ascii=False, separators=(',', ':')).encode()
salt, iv = os.urandom(16), os.urandom(12); k = hashlib.pbkdf2_hmac('sha256', PW, salt, 300000, 32)
b = lambda x: base64.b64encode(x).decode()
json.dump({'v': 1, 'salt': b(salt), 'iv': b(iv), 'ct': b(AESGCM(k).encrypt(iv, pt, None))}, open(ENC, 'w'))
last = sorted(D['meta'])[-1]
print('ok updated', D['updated'], 'last day', last, 'spend', round(sum(r[1] for r in D['meta'][last]), 2), 'unattributed', unattr)
