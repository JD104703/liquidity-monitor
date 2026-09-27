from html import escape
import re
import numpy as np

def render_dashboard(g, original_text=''):
    def e(value): return escape(str(value))
    def clean(text): return re.sub(r'^[★☆🟢🟡🟠🔴⚠️\s]+', '', str(text)).strip()
    def tone(text):
        # 설명 전체가 아니라 판정 제목만 확인: '부담 제한적' 오인 방지
        text = str(text).split(' — ', 1)[0]
        for symbol, color in [('🔴','red'), ('🟠','orange'), ('🟡','amber'), ('🟢','green')]:
            if symbol in text: return color
        if any(t in text for t in ['양호','안정','완충 여력 존재']): return 'green'
        if any(t in text for t in ['비우호','긴축','부정','부담','위축','⚠️']): return 'red'
        if any(t in text for t in ['혼조','중립','주의','확인','정책완화 선행','체제 전환']): return 'amber'
        if any(t in text for t in ['우호','긍정','확장']): return 'green'
        return 'amber'
    def note(title, verdict, color=None):
        head, _, body = clean(verdict).partition(' — ')
        return f'<article><small>{e(title)}</small><strong class="{color or tone(verdict)}">● {e(head)}</strong><p>{e(body)}</p></article>'
    groups = [
        ('유동성','score',4,'regime', ['real_change','y2_change','spread10_2_change','liq_change'],
         [('실질금리 하락',g['real_change']<0),('2Y 하락',g['y2_change']<0),('완화형 스티프닝',g['spread10_2_change']>0 and g['y2_change']<0),('유동성 Proxy 증가',g['liq_change']>0)]),
        ('민간 신용','credit_score',2,'credit_regime',['bankloan_4w_pct','bankloan_yoy','m2_3m_ann','m2_yoy'],
         [('은행 대출 확장',g['bankloan_4w_pct']>0 and g['bankloan_yoy']>0),('M2 확장',g['m2_3m_ann']>0 and g['m2_yoy']>0)]),
        ('고용 스트레스','labor_score',5,'labor_regime',['sahm_now','unrate_6m_change','initial_claims_vs_low','continued_claims_vs_low','continued_claims_13w_change','payroll_3m_avg','payroll_12m_avg'],
         [('Sahm 조기경고',g['sahm_warning']),('실업률 상승',g['unrate_trigger']),('신규 청구 증가',g['initial_claims_trigger']),('계속 청구 증가',g['continued_claims_trigger']),('고용창출 둔화',g['payroll_trigger'])]),
        ('엔캐리 청산 위험','carry_score',6,'carry_regime',[],
         [('엔화 급등',g['yen_trigger']),('미국 2Y 급락',g['rate_trigger']),('금리차 축소(보조)',g['gap_trigger']),('VIX 급등',g['vol_trigger']),('일본 증시 급락',g['nikkei_trigger']),('Sahm 상승',g['growth_trigger'])]),
        ('금융충격','shock_score',3,'shock_regime',['hy_now','hy_5d_change','hy_4w_change','repo_3d_avg','repo_3d_vs_20d','stlfsi_now','stlfsi_4w_change'],
         [('HY OAS 경고',g['hy_trigger']),('레포 경고',g['repo_trigger']),('STLFSI 경고',g['stlfsi_trigger'])])]
    audit=[]
    def card(group, risk=False):
        title,key,maximum,reg,inputs,checks=group
        missing=[name for name in inputs if not np.isfinite(g[name])]
        if key=='carry_score':
            missing += [k for k in ['JPY_5D','JPY_4W','US2Y_4W','VIX','VIX_5D','Nikkei_5D','Sahm','CarryGapChange'] if not np.isfinite(g['carry_now'][k])]
        value=int(g[key]); count=sum(int(bool(flag)) for _,flag in checks)
        if not 0<=value<=maximum or value!=count:
            raise ValueError(f'{title}: 표시 점수 {value}와 조건 합계 {count} 불일치. 모든 셀을 다시 실행하세요.')
        verdict=g[reg]; color=tone(verdict)
        # 부분 데이터로 계산한 0을 정상/안정으로 표시하지 않음
        if missing: verdict='자료 불완전 — '+', '.join(missing); color='amber'
        head,_,body=clean(verdict).partition(' — ')
        bars=''.join(f'<i style="background:var(--{color})"></i>' if i<value and not missing else '<i></i>' for i in range(maximum))
        caption=(f'경고 조건 {value}개 발동 · 0은 경고 없음' if risk else '높을수록 우호적')
        if key=='carry_score': caption+=' · 엔화 강세가 판정의 필수 조건'
        if key=='shock_score': caption+=f' · 주의 이상 {g["shock_watch_count"]}개(경고 포함)'
        if missing: caption=f'유효한 입력 확인 필요 · 기존 계산 {value}/{maximum}'
        for label,flag in checks: audit.append(f'<tr><td>{e(title)}</td><td>{e(label)}</td><td>{"발동 (+1)" if flag else "미발동 (+0)"}</td></tr>')
        value_html=f'{value}<span> / {maximum}</span>' if not missing else '<span>확인 필요</span>'
        return f'<article style="border-top:4px solid var(--{color})"><small>{e(title)}</small><div class="score">{value_html}</div><div class="bar">{bars}</div><strong>{e(head)}</strong><p>{e(body)}</p><small>{e(caption)}</small></article>'
    css='''<style>
    .liq{--green:#16866b;--red:#c93650;--amber:#a77916;--orange:#c96b27;color:#19364d;background:#f1f6fb;font:14px/1.65 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;padding:26px;border-radius:18px;max-width:1180px;margin:12px auto}
    .liq *{box-sizing:border-box}.liq h2{margin:0;font-size:27px}.liq h3{margin:24px 0 12px;font-size:18px}.liq small{display:block;color:#657e92;font-size:12px}.liq p{margin:8px 0;color:#597186}.liq .hero{background:#17344c;color:white;padding:24px;border-radius:14px;margin:18px 0}.liq .hero p{color:#d8e7f1}.liq .hero small{color:#b6cede}.liq .hero strong{font-size:23px;display:block}
    .liq .grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:12px}.liq article{padding:21px;background:white;border:1px solid #dae5ee;border-radius:14px}.liq strong{display:block;margin-top:10px}.liq .score{font-size:40px;font-weight:750;line-height:1.4;margin-top:12px;font-variant-numeric:tabular-nums}.liq .score span{font-size:18px;color:#8197a8}.liq .bar{display:flex;gap:5px;margin:12px 0 16px}.liq .bar i{height:8px;flex:1;background:#e5edf3;border-radius:8px}
    .liq .green{color:var(--green)}.liq .red{color:var(--red)}.liq .amber{color:var(--amber)}.liq .orange{color:var(--orange)}.liq details{background:white;border:1px solid #dae5ee;border-radius:12px;padding:16px;margin-top:14px}.liq summary{cursor:pointer;font-weight:650}.liq .scroll{overflow:auto}.liq table{width:100%;border-collapse:collapse;text-align:left;white-space:nowrap}.liq td,.liq th{padding:10px;border-bottom:1px solid #e5edf3}.liq pre{white-space:pre-wrap;overflow-wrap:anywhere;font:12px/1.7 monospace;max-height:650px;overflow:auto}.liq ul{padding-left:20px}
    @media(max-width:600px){.liq{padding:14px}.liq .grid{grid-template-columns:1fr}}
    </style>'''
    html=[css,'<div class="liq"><small>US MACRO · LIQUIDITY MONITOR</small><h2>미국 유동성 · 위험 모니터</h2>',
          f'<small>주간 집계 기준 {e(g["weekly"].index[-1].date())} · 지표별 관측일은 다름</small>',
          f'<div class="hero"><small>종합 유동성 판정</small><strong>{e(clean(g["total_liquidity_view"]))}</strong><p>기존 금융여건 + 민간 신용 · 위험 경고는 아래에서 별도로 확인</p></div>',
          '<h3>01 · 유동성의 방향</h3><div class="grid">']
    html += [card(x) for x in groups[:2]]
    html += ['</div>',f'<p>{e(g["macro_comment"])}</p>','<h3>02 · 위험 경고등</h3><div class="grid">']
    html += [card(x,True) for x in groups[2:]]
    html += ['</div><div class="grid" style="margin-top:12px">',note('은행 지급준비금',g['reserve_signal'],'red' if g['reserve_4w_pct']<=-5 else 'amber' if g['reserve_4w_pct']<0 else 'green'),note('RRP 완충 여력',g['rrp_signal'],'red' if g['now']['RRP_T']<0.05 else 'amber' if g['now']['RRP_T']<0.2 else 'green'),note('초장기금리',g['long_rate_signal']),'</div>',
          '<h3>03 · 해석의 핵심</h3><div class="grid">',note('금리하락의 성격',g['easing_quality']),note('금리 구조',g['rate_structure_comment'],'amber'),note('2024년 엔캐리 비교',f'{g["carry_similarity"]:.0f}% 유사도 — {clean(g["carry_similarity_view"])}','amber'),'</div><small>유사도는 발생 확률이 아님. 엔캐리의 5일 변화는 원 코드에서 7일 전 관측값과 비교.</small>',
          '<h3>04 · 핵심 수치</h3><div class="scroll"><table><tr><th>지표</th><th>현재</th><th>비교</th><th>관측일</th></tr>']
    n=g['now']
    rows=[('10Y 실질금리',f'{n["Real10Y"]:.2f}%',f'4주 {g["real_change"]*100:+.0f}bp','Real10Y'),('2Y 금리',f'{n["Treasury2Y"]:.2f}%',f'4주 {g["y2_change"]*100:+.0f}bp','Treasury2Y'),('유동성 Proxy',f'${n["NetLiquidity"]:.3f}T',f'4주 {g["liq_change"]:+.3f}T','NetLiquidity'),('은행대출',f'${n["BankLoans_T"]:.2f}T',f'4주 {g["bankloan_4w_pct"]:+.2f}%','BankLoans_T'),('M2',f'${g["m2_now"]:.2f}T',f'3개월 연율 {g["m2_3m_ann"]:+.2f}%','M2'),('Sahm',f'{g["sahm_now"]:.2f}%p','원 코드 경고선 0.30 / 0.50%p','Sahm'),('HY OAS',f'{g["hy_now"]:.2f}%',f'4주 {g["hy_4w_change"]:+.2f}%p','HYOAS'),('SOFR-IORB',f'{g["repo_now"]:+.1f}bp',f'3일 평균 {g["repo_3d_avg"]:+.1f}bp',None),('STLFSI4',f'{g["stlfsi_now"]:+.2f}',f'4주 {g["stlfsi_4w_change"]:+.2f}','STLFSI')]
    for title,value,change,col in rows:
        date=g['repo_date'] if col is None else g['df'][col].dropna().index[-1]
        html.append('<tr>'+''.join(f'<td>{e(x)}</td>' for x in [title,value,change,date.date()])+'</tr>')
    html += ['</table></div><h3>05 · 자산별 해석</h3><div class="grid">',note('금 · Gold',g['gold_view']),note('비트코인 · Bitcoin',g['btc_view']),note('중소형주',g['smallcap_view']),'</div><small>자산별 판정은 기존 금리·유동성 조건 기준이며 별도 위험 점수를 통합한 판정은 아님.</small>',
          '<details><summary>점수 검산 · 조건별 발동 여부</summary><p>각 발동 조건은 +1점. 표시 점수와 조건 합계를 자동 대조하며, 불일치하면 실행을 중단합니다. 자료 불완전 표시가 있으면 미발동을 안전 신호로 해석하지 마세요.</p><div class="scroll"><table><tr><th>영역</th><th>조건</th><th>결과</th></tr>',''.join(audit),'</table></div></details>']
    for title,key in [('금융여건','signals'),('민간 신용','credit_signals'),('고용','labor_signals'),('엔캐리','carry_signals'),('금융충격','shock_signals')]:
        html.append(f'<details><summary>{title} · 판정 근거</summary><ul>'+''.join(f'<li>{e(s)}</li>' for s in g[key])+'</ul></details>')
    html.append(f'<details><summary>전체 세부 수치 · 기존 출력</summary><pre>{e(original_text)}</pre></details><small style="margin-top:16px">T = 조 달러 · bp = 0.01%p. 점수와 임계값은 기존 코드 기준. 관측일은 발표일과 다를 수 있음.</small></div>')
    return ''.join(html)
