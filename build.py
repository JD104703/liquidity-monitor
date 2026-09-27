"""Generate a self-contained static dashboard from live FRED data."""
from pathlib import Path
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from html import escape
import contextlib
import io
import json
import runpy
import os
from dashboard import render_dashboard

ROOT = Path(__file__).resolve().parent


def build():
    ns = runpy.run_path(str(ROOT / 'calculate.py'))
    with contextlib.redirect_stdout(io.StringIO()) as detail:
        exec(compile((ROOT/'detail_output.py').read_text(), 'detail_output.py', 'exec'), ns)
    content = render_dashboard(ns, detail.getvalue())
    generated = datetime.now(timezone.utc)
    freshness = []
    for name, code in ns['series'].items():
        data = ns['downloaded'].get(name)
        valid = data.dropna() if data is not None else None
        observed = str(valid.index[-1].date()) if valid is not None and len(valid) else None
        freshness.append({'name':name, 'fred_series':code, 'observation_date':observed})
    rows=''.join('<tr><td>'+escape(x['name'])+'</td><td>'+escape(x['fred_series'])+'</td><td>'+escape(x['observation_date'] or '자료 없음')+'</td></tr>' for x in freshness)
    stamp=generated.astimezone(ZoneInfo('Asia/Seoul')).strftime('%Y-%m-%d %H:%M KST')
    document='''<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>미국 유동성 · 위험 모니터</title><style>body{margin:0;background:#eaf0f6;padding:12px}.meta{max-width:1180px;margin:12px auto;font:13px/1.7 sans-serif;color:#435d72}.meta details{background:white;padding:16px;border-radius:12px}.meta table{width:100%;text-align:left}.meta td{padding:5px}.delay{padding:12px;background:#fff0d2;border-radius:8px}</style></head><body>'''
    document+=f'<div class="meta">마지막 정상 생성: <time id="generated" datetime="{generated.isoformat()}">{stamp}</time> · 매일 오전 9:17 KST 갱신 예정(실행 지연 가능)<div id="delay" class="delay" hidden>마지막 정상 생성 후 36시간이 지났습니다. 데이터 갱신 상태를 확인하세요.</div></div>'
    document+=content
    document+='<div class="meta"><details><summary>지표별 관측일 확인</summary><p>생성 시각과 데이터 관측일은 다릅니다. 일간·주간·월간 발표 주기가 혼재합니다.</p><table><tr><th>지표</th><th>FRED 코드</th><th>마지막 관측일</th></tr>'+rows+'</table></details></div>'
    document+='''<script>function checkAge(){const age=Date.now()-Date.parse(document.getElementById('generated').dateTime);document.getElementById('delay').hidden=age<=36*3600*1000;}checkAge();setInterval(checkAge,60000);</script></body></html>'''
    public=ROOT/'public';public.mkdir(exist_ok=True)
    temporary=public/'index.html.tmp';temporary.write_text(document,encoding='utf-8');temporary.replace(public/'index.html')
    (public/'.nojekyll').write_text('')
    (public/'status.json').write_text(json.dumps({'generated_at':generated.isoformat(), 'observations':freshness},ensure_ascii=False,indent=2))
    print(f'Built {public / "index.html"}',flush=True)
    return public/'index.html'

if __name__ == '__main__':
    build()
