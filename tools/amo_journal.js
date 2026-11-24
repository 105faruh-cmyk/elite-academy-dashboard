// Запускать на вкладке https://eliteacademykg.amocrm.ru/leads/pipeline/9612890/ (javascript_tool).
// DAYS_BACK: сколько дней пересчитать (сегодня + вчера = 2). Результат: window._ZJ (JSON {Z,J}) и window._AG (строка токенов).
// Читать результат кусками по ~900 символов: window._ZJ.slice(0,900) ...
const DAYS_BACK = 2;
const KEYS = ['италия💙','сша🔥','китай🧡','китай🔥','магистр🔥','сша💙','сша🤍','сша🇺🇸','китай🤍','китай💙','акш💙','америка🔥','германия🔥','сша💜','магистр💙','германия💙','акш🔥','малайзия💙','сша💚','универ','акш💚','вуз💚','чп','пятница','акш🧡'];
const RK={80021038:1,89992782:1,76732738:1,76732742:1,76732866:1,76732870:2,76732874:3,76732878:4,76732882:4,76732886:5,142:6};
const BK=s=>{const d=new Date(s*1000+6*3600e3);return String(d.getUTCMonth()+1).padStart(2,'0')+'-'+String(d.getUTCDate()).padStart(2,'0')};
const now=new Date(Date.now()+6*3600e3);const F=Date.UTC(now.getUTCFullYear(),now.getUTCMonth(),now.getUTCDate()-(DAYS_BACK-1))/1000-6*3600;
let ev=[],p=1;while(p<80){const r=await fetch(`/api/v4/events?filter[type]=lead_status_changed&filter[created_at][from]=${F}&limit=100&page=${p}`);if(r.status!=200)break;const j=await r.json();ev.push(...j._embedded.events);if(!j._links||!j._links.next)break;p++}
ev=ev.filter(e=>{const v=e.value_after&&e.value_after[0]&&e.value_after[0].lead_status;return v&&v.pipeline_id==9612890}).map(e=>[e.entity_id,e.created_at,e.value_after[0].lead_status.id]).sort((a,b)=>a[1]-b[1]);
let leads=[];p=1;while(p<30){const r=await fetch(`/api/v4/leads?limit=250&page=${p}&filter[created_at][from]=${F}&filter[pipeline_id]=9612890`);if(r.status!=200)break;const j=await r.json();leads.push(...j._embedded.leads);if(!j._links.next)break;p++}
const L={};leads.forEach(l=>L[l.id]=l);
const need=[...new Set(ev.map(e=>e[0]))].filter(i=>!L[i]);
for(let i=0;i<need.length;i+=200){const q=need.slice(i,i+200).map(x=>'filter[id][]='+x).join('&');const r=await fetch('/api/v4/leads?limit=250&'+q);if(r.status!=200)continue;const j=await r.json();j._embedded.leads.forEach(l=>L[l.id]=l)}
// ранее достигнутый этап: по событиям до окна (последние 60 дней) для лидов из окна
const PRE={};const ids=[...new Set(ev.map(e=>e[0]))];
for(let i=0;i<ids.length;i+=50){const q=ids.slice(i,i+50).map(x=>'filter[entity_id][]='+x).join('&');let pg=1;while(pg<20){const r=await fetch(`/api/v4/events?filter[type]=lead_status_changed&filter[entity]=lead&${q}&filter[created_at][to]=${F-1}&limit=100&page=${pg}`);if(r.status!=200)break;const j=await r.json();j._embedded.events.forEach(e=>{const v=e.value_after&&e.value_after[0]&&e.value_after[0].lead_status;if(v&&v.pipeline_id==9612890){const rk=RK[v.id]||0;if(rk>(PRE[e.entity_id]||0))PRE[e.entity_id]=rk}});if(!j._links||!j._links.next)break;pg++}}
const typ=l=>{const t=(l._embedded&&l._embedded.tags||[]).map(x=>x.name.toLowerCase());if(t.some(x=>/tilda|тильда/.test(x)))return 'T';if(t.includes('таргет'))return 't';if(t.includes('органика'))return 'o';return ''};
const cvf=l=>{const c=(l.custom_fields_values||[]).find(c=>c.field_id==1148293);return c?String(c.values[0].value):''};
const EMO={'огонь':'🔥','синее':'💙','оранж':'🧡','белое':'🤍','флаг':'🇺🇸','фиолет':'💜','зеленое':'💚','зелёное':'💚'};
const cw=s=>{s=(s||'').toLowerCase().replace(/ё/g,'е').replace(/🇺🇲/g,'🇺🇸').replace(/\(флаг\)/g,'🇺🇸');for(const w in EMO)s=s.split(w).join(EMO[w]);s=s.replace(/cша/g,'сша');return s.replace(/[\s!.,?]/g,'')};
const Z={};leads.forEach(l=>{const k=BK(l.created_at)+'|'+typ(l);Z[k]=(Z[k]||0)+1});
const J={},AG={},cur={};
for(const [id,ts,st] of ev){const l=L[id];if(!l)continue;const r=RK[st]||0;if(cur[id]===undefined)cur[id]=PRE[id]||0;if(r<=cur[id])continue;const d=BK(ts),t=typ(l)||'u',c=cw(cvf(l)),cd=BK(l.created_at),pr=l.price||0;
 for(let i=cur[id]+1;i<=r;i++){J[d]=J[d]||{};J[d][t]=J[d][t]||[0,0,0,0,0,0,0,0,0];J[d][t][i]++;if(i==5&&pr){J[d][t][7]+=pr;J[d][t][8]++}
  const cc=c.includes('можноузнатьобэтомподробнее')?'TPL':(KEYS.includes(c)?c:null);
  if(i<=5&&cc){const k=d.slice(3)+i+cd.slice(3)+cc;AG[k]=AG[k]||[0,0];AG[k][0]++;if(i==5)AG[k][1]+=pr}}
 cur[id]=r}
window._ZJ=JSON.stringify({Z,J});window._AG=Object.entries(AG).map(([k,v])=>k+':'+v[0]+(v[1]?'/'+v[1]:'')).join(' ');
'ok ev '+ev.length+' leads '+leads.length+' ZJ '+window._ZJ.length+' AG '+window._AG.length
