# ============================================================

# 미국 매크로 · 유동성 현재상황 판정

# Google Colab용

#

# [기존 유지]

# Liquidity Score : 4점

#   1) 10Y 실질금리

#   2) 2Y 금리

#   3) 10Y-2Y Curve

#   4) Fed/TGA/RRP Liquidity Proxy

#

# [신규 추가]

# Private Credit Score : 2점

#   1) 미국 상업은행 대출

#   2) M2 광의통화

#

# [별도 경고등]

#   - 은행 지급준비금

#   - RRP 고갈 여부

#

# [별도 확인]

#   - 30Y

#   - 30Y-10Y

#

# [신규 별도 경고등]

# Labor / Unemployment Stress

#   - 실업률 추세

#   - Sahm Rule

#   - 신규 실업수당 청구

#   - 계속 실업수당 청구

#   - 비농업고용 3개월 평균

#   - 금리하락이 좋은 완화인지, 고용침체형 완화인지 구분

#

# [신규 별도 경고등]

# Yen Carry Trade Unwind Risk

#   - USD/JPY (엔화 강세)

#   - 미국 2Y 급락

#   - 미·일 단기금리차 축소(보조)

#   - VIX 급등

#   - Nikkei 급락

#   - Sahm Rule 상승

#   - 2024-08-05 엔캐리 청산 국면과 유사도 비교

#

# [신규 별도 경고등]

# Sudden Financial Shock Detector

#   - HY OAS : 기업 신용시장 스트레스

#   - SOFR-IORB : 레포/단기자금시장 스트레스

#   - STLFSI4 : 종합 금융시장 스트레스

#   - 기존 Liquidity Score에는 섞지 않고 별도 Shock Score(0~3)로 표시

# ============================================================

import sys

import subprocess

import pandas as pd

import numpy as np

from fred_source import download_series

START_DATE = "2023-01-01"

# ============================================================

# 1. FRED 데이터

# ============================================================

series = {

    # 금리

    "Real10Y": "DFII10",

    "Treasury2Y": "DGS2",

    "Treasury10Y": "DGS10",

    "Treasury30Y": "DGS30",

    # Fed / Treasury Liquidity

    "FedAssets": "WALCL",

    "TGA": "WTREGEN",

    "RRP": "RRPONTSYD",

    # 신규 : 민간 신용 / 광의통화

    "BankLoans": "TOTLL",      # Loans & Leases, All Commercial Banks

    "Reserves": "WRESBAL",     # Reserve Balances with Federal Reserve Banks

    "M2": "M2SL",              # M2 Money Stock

    # 미국 고용 / 실업 스트레스

    "UNRATE": "UNRATE",        # 실업률, 월간

    "ICSA": "ICSA",            # 신규 실업수당 청구, 주간 SA

    "CCSA": "CCSA",            # 계속 실업수당 청구, 주간 SA

    "PAYEMS": "PAYEMS",        # 비농업고용 총량, 월간 SA

    # 엔캐리 트레이드 모니터

    # DEXJPUS = 1달러당 엔화. 하락하면 엔화 강세

    "USDJPY": "DEXJPUS",

    "VIX": "VIXCLS",

    "Nikkei225": "NIKKEI225",

    "Sahm": "SAHMREALTIME",

    # 일본 단기금리. 월간 데이터라 실시간 판정보다는 보조지표로 사용

    "JapanCall": "IRSTCI01JPM156N",

    # 갑작스러운 금융충격 감시

    "HYOAS": "BAMLH0A0HYM2",   # ICE BofA US High Yield OAS, %

    "SOFR": "SOFR",             # Secured Overnight Financing Rate, %

    "IORB": "IORB",             # Interest Rate on Reserve Balances, %

    "STLFSI": "STLFSI4",        # St. Louis Fed Financial Stress Index

}

downloaded = download_series(series, START_DATE)

# 중요:

# 각 시리즈의 날짜 빈도가 다르므로 concat으로 union index 생성

df = pd.concat(downloaded, axis=1).sort_index()

# 핵심 시리즈가 다운로드되지 않았으면 뒤에서 애매한 KeyError가 나지 않도록

# 여기서 명확하게 중단합니다.

required_base = [

    "Real10Y", "Treasury2Y", "Treasury10Y", "Treasury30Y",

    "FedAssets", "TGA", "RRP", "BankLoans", "Reserves", "M2"

]

required_labor = [

    "UNRATE", "ICSA", "CCSA", "PAYEMS", "Sahm"

]

required_carry = [

    "USDJPY", "VIX", "Nikkei225", "Sahm"

]

required_shock = [

    "HYOAS", "SOFR", "IORB", "STLFSI"

]

missing_base = [x for x in required_base if x not in df.columns]

missing_labor = [x for x in required_labor if x not in df.columns]

missing_carry = [x for x in required_carry if x not in df.columns]

missing_shock = [x for x in required_shock if x not in df.columns]

if missing_base:

    raise ValueError(

        f"필수 매크로 시리즈 다운로드 실패: {missing_base}"

    )

if missing_labor:

    raise ValueError(

        f"고용/실업 모니터 필수 시리즈 다운로드 실패: {missing_labor}"

    )

if missing_carry:

    raise ValueError(

        f"엔캐리 모니터 필수 시리즈 다운로드 실패: {missing_carry}"

    )

if missing_shock:

    raise ValueError(

        f"금융충격 모니터 필수 시리즈 다운로드 실패: {missing_shock}"

    )

# ============================================================

# 2. 단위 변환

# ============================================================

# WALCL / TGA / WRESBAL = Million USD

df["FedAssets_T"] = df["FedAssets"] / 1_000_000

df["TGA_T"] = df["TGA"] / 1_000_000

df["Reserves_T"] = df["Reserves"] / 1_000_000

# RRP / TOTLL / M2 = Billion USD

df["RRP_T"] = df["RRP"] / 1_000

df["BankLoans_T"] = df["BankLoans"] / 1_000

df["M2_T"] = df["M2"] / 1_000

# ============================================================

# 3. Yield Curve

# ============================================================

df["Spread10_2"] = df["Treasury10Y"] - df["Treasury2Y"]

df["Spread30_10"] = df["Treasury30Y"] - df["Treasury10Y"]

# ============================================================

# 4. 기존 Fed/Treasury Liquidity Proxy

#

# 기존 Net Liquidity 공식 유지

# 다만 RRP가 거의 0이 된 환경에서는

# "전체 유동성"이 아니라 Fed/Treasury Liquidity Proxy로 해석

# ============================================================

df["NetLiquidity"] = (

    df["FedAssets_T"]

    - df["TGA_T"]

    - df["RRP_T"]

)

# ============================================================

# 5. 주간 데이터

# ============================================================

weekly_cols = [

    "Real10Y",

    "Treasury2Y",

    "Treasury10Y",

    "Treasury30Y",

    "Spread10_2",

    "Spread30_10",

    "FedAssets_T",

    "TGA_T",

    "RRP_T",

    "NetLiquidity",

    "BankLoans_T",

    "Reserves_T"

]

weekly = (

    df[weekly_cols]

    .resample("W-FRI")

    .last()

    .ffill()

)

if len(weekly) < 53:

    raise ValueError("YoY 및 최근 4주 변화를 계산하기 위한 데이터가 부족합니다.")

now = weekly.iloc[-1]

prev4 = weekly.iloc[-5]

prev52 = weekly.iloc[-53]

# ============================================================

# 6. 최근 4주 금리 변화

# ============================================================

real_change = now["Real10Y"] - prev4["Real10Y"]

y2_change = now["Treasury2Y"] - prev4["Treasury2Y"]

y10_change = now["Treasury10Y"] - prev4["Treasury10Y"]

y30_change = now["Treasury30Y"] - prev4["Treasury30Y"]

spread10_2_change = (

    now["Spread10_2"] - prev4["Spread10_2"]

)

spread30_10_change = (

    now["Spread30_10"] - prev4["Spread30_10"]

)

liq_change = (

    now["NetLiquidity"] - prev4["NetLiquidity"]

)

# ============================================================

# 7. 은행 대출 / 지급준비금 변화

# ============================================================

bankloan_4w_pct = (

    now["BankLoans_T"] / prev4["BankLoans_T"] - 1

) * 100

bankloan_yoy = (

    now["BankLoans_T"] / prev52["BankLoans_T"] - 1

) * 100

reserve_4w_change = (

    now["Reserves_T"] - prev4["Reserves_T"]

)

reserve_4w_pct = (

    now["Reserves_T"] / prev4["Reserves_T"] - 1

) * 100

# ============================================================

# 8. M2

#

# M2는 월간 데이터이므로

# 최근 4주 변화가 아니라

#

# 1) 3개월 연율화

# 2) YoY

#

# 로 판단

# ============================================================

m2_monthly = (

    df["M2_T"]

    .dropna()

    .resample("ME")

    .last()

    .dropna()

)

if len(m2_monthly) < 13:

    raise ValueError("M2 YoY 계산을 위한 데이터가 부족합니다.")

m2_now = m2_monthly.iloc[-1]

m2_prev3 = m2_monthly.iloc[-4]

m2_prev12 = m2_monthly.iloc[-13]

m2_3m_ann = (

    (m2_now / m2_prev3) ** 4 - 1

) * 100

m2_yoy = (

    m2_now / m2_prev12 - 1

) * 100

m2_date = m2_monthly.index[-1]

# ============================================================

# 9. 기존 Liquidity Score (4점)

# ============================================================

score = 0

signals = []

# ① 10Y 실질금리

if real_change < 0:

    score += 1

    signals.append(

        "10Y 실질금리 하락 → 위험자산 할인율 부담 완화 (+)"

    )

else:

    signals.append(

        "10Y 실질금리 상승 → 위험자산 할인율 부담 (-)"

    )

# ② 2Y

if y2_change < 0:

    score += 1

    signals.append(

        "2Y 금리 하락 → Fed 완화 기대 강화 (+)"

    )

else:

    signals.append(

        "2Y 금리 상승 → Fed 긴축/고금리 기대 (-)"

    )

# ③ 좋은 Steepening

if spread10_2_change > 0 and y2_change < 0:

    score += 1

    signals.append(

        "2Y 하락형 10Y-2Y Steepening → 금융여건 완화 (+)"

    )

elif spread10_2_change > 0 and y10_change > 0:

    signals.append(

        "10Y 상승형 10Y-2Y Steepening "

        "→ 재정·Term Premium 부담 (-)"

    )

else:

    signals.append(

        "10Y-2Y → 뚜렷한 완화형 Steepening 없음"

    )

# ④ 기존 Net Liquidity

if liq_change > 0:

    score += 1

    signals.append(

        "Fed/Treasury Liquidity Proxy 증가 (+)"

    )

else:

    signals.append(

        "Fed/Treasury Liquidity Proxy 감소 (-)"

    )

# ============================================================

# 10. 기존 4점 판정

# ============================================================

if score == 4:

    regime = "★★★★★ 매우 우호적"

elif score == 3:

    regime = "★★★★☆ 우호적"

elif score == 2:

    regime = "★★★☆☆ 혼조"

elif score == 1:

    regime = "★★☆☆☆ 비우호적"

else:

    regime = "★☆☆☆☆ 긴축적"

# ============================================================

# 11. 신규 Private Credit Score (2점)

#

# 기존 4점 점수에는 섞지 않음.

# "Fed 유동성"과 "민간 신용"을 분리해서 보기 위함.

# ============================================================

credit_score = 0

credit_signals = []

# 은행 대출

if bankloan_4w_pct > 0 and bankloan_yoy > 0:

    credit_score += 1

    credit_signals.append(

        "은행대출 증가 → 민간 신용창출 확대 (+)"

    )

elif bankloan_4w_pct <= 0 and bankloan_yoy > 0:

    credit_signals.append(

        "은행대출 YoY는 증가하지만 최근 4주는 둔화 → 신용확장 모멘텀 점검"

    )

else:

    credit_signals.append(

        "은행대출 감소/부진 → 민간 신용창출 약화 (-)"

    )

# M2

if m2_3m_ann > 0 and m2_yoy > 0:

    credit_score += 1

    credit_signals.append(

        "M2 증가 → 광의통화 확장 (+)"

    )

elif m2_yoy > 0:

    credit_signals.append(

        "M2 YoY는 증가하지만 최근 3개월 모멘텀 둔화"

    )

else:

    credit_signals.append(

        "M2 YoY 감소 → 광의통화 위축 (-)"

    )

if credit_score == 2:

    credit_regime = "★★★★★ 민간 신용 강한 확장"

elif credit_score == 1:

    credit_regime = "★★★☆☆ 민간 신용 혼조"

else:

    credit_regime = "★☆☆☆☆ 민간 신용 위축"

# ============================================================

# 12. 지급준비금 경고등

#

# 준비금은 단순히 '증가=무조건 호재'가 아니므로

# 점수에는 넣지 않고 Stress Indicator로 사용

# ============================================================

if reserve_4w_pct <= -5:

    reserve_signal = (

        "⚠️ 경고 — 은행 지급준비금이 최근 4주 급감 "

        "→ 단기 자금시장 스트레스 점검 필요"

    )

elif reserve_4w_pct < 0:

    reserve_signal = (

        "주의 — 지급준비금 감소 중 "

        "→ 아직 즉각적 위험 신호는 아니지만 추세 점검"

    )

else:

    reserve_signal = (

        "양호 — 지급준비금 안정/증가 "

        "→ 은행시스템 유동성 부담 제한적"

    )

# ============================================================

# 13. RRP 상태

#

# RRP가 거의 고갈되면 과거처럼

# RRP 감소가 QT를 흡수하는 효과가 사라짐

# ============================================================

if now["RRP_T"] < 0.05:

    rrp_signal = (

        "⚠️ RRP Buffer 거의 소진 "

        "→ 향후 유동성 판단에서 은행대출·M2·준비금 중요도 상승"

    )

elif now["RRP_T"] < 0.20:

    rrp_signal = (

        "RRP Buffer 낮음 "

        "→ 과거 대비 QT 완충 능력 크게 감소"

    )

else:

    rrp_signal = (

        "RRP Buffer 존재 "

        "→ 일부 유동성 완충 여력 존재"

    )

# ============================================================

# 14. Fed + Private Credit 종합판정

# ============================================================

if score >= 3 and credit_score == 2:

    total_liquidity_view = (

        "★★★★★ 매우 우호적 — "

        "금융여건과 민간 신용이 동시에 확장"

    )

elif score <= 1 and credit_score == 0:

    total_liquidity_view = (

        "★☆☆☆☆ 매우 비우호적 — "

        "Fed/Treasury 환경과 민간 신용이 동시에 약화"

    )

elif score <= 1 and credit_score == 2:

    total_liquidity_view = (

        "★★★☆☆ 체제 전환형 혼조 — "

        "Fed/Treasury 지표는 약하지만 은행 신용이 이를 보완"

    )

elif score >= 3 and credit_score == 0:

    total_liquidity_view = (

        "★★★☆☆ 정책완화 선행 — "

        "시장금리/Fed 환경은 좋아지지만 민간 신용 확산은 아직 미확인"

    )

elif score == 2 and credit_score == 2:

    total_liquidity_view = (

        "★★★★☆ 우호적 — "

        "기존 유동성은 혼조지만 민간 신용 확장이 강함"

    )

else:

    total_liquidity_view = (

        "★★★☆☆ 혼조 — "

        "Fed/Treasury와 민간 신용 신호가 완전히 일치하지 않음"

    )

# ============================================================

# 15. 기존 종합 매크로 해석

# ============================================================

if real_change < 0 and y2_change < 0 and liq_change > 0:

    macro_comment = (

        "금리환경과 Fed/Treasury 유동성 Proxy가 동시에 개선되고 있습니다. "

        "기존 유동성 기준으로 Risk-On 환경에 가깝습니다."

    )

elif real_change < 0 and y2_change < 0 and liq_change <= 0:

    macro_comment = (

        "Fed 완화 기대와 실질금리 하락은 나타나지만 "

        "Fed/Treasury Liquidity Proxy는 아직 증가하지 않습니다."

    )

elif real_change > 0 and liq_change < 0:

    macro_comment = (

        "실질금리가 오르고 Fed/Treasury Liquidity Proxy도 감소해 "

        "기존 프레임상 위험자산에 비우호적입니다."

    )

elif liq_change > 0 and real_change > 0:

    macro_comment = (

        "유동성 Proxy는 증가하지만 실질금리 상승이 이를 일부 상쇄합니다."

    )

else:

    macro_comment = (

        "금리와 Fed/Treasury 유동성 신호가 엇갈립니다."

    )

# ============================================================

# 16. 30Y / 30Y-10Y 판정

# ============================================================

if y30_change < 0 and spread30_10_change < 0:

    long_rate_signal = (

        "★★★★★ 매우 긍정적 — 30Y 하락 + 30Y-10Y 축소 "

        "→ 초장기 인플레·재정·Term Premium 부담 완화"

    )

elif y30_change < 0 and y10_change < 0:

    long_rate_signal = (

        "★★★★☆ 긍정적 — 10Y·30Y 동반 하락 "

        "→ 장기 금융여건 완화"

    )

elif y10_change < 0 and y30_change >= 0:

    long_rate_signal = (

        "★★☆☆☆ 주의 — 10Y는 하락하지만 30Y는 버팀/상승 "

        "→ Fed 완화 기대와 달리 초장기 재정 부담 지속"

    )

elif y30_change > 0 and spread30_10_change > 0:

    long_rate_signal = (

        "★☆☆☆☆ 부정적 — 30Y 상승 + 30Y-10Y 확대 "

        "→ 장기 인플레·재정·Term Premium 부담 증가"

    )

else:

    long_rate_signal = (

        "★★★☆☆ 중립 — 초장기금리 방향 추가 확인 필요"

    )

# ============================================================

# 17. 금리 구조 종합

# ============================================================

if (

    real_change < 0

    and y2_change < 0

    and y30_change < 0

    and spread30_10_change < 0

):

    rate_structure_comment = (

        "단기금리·실질금리·초장기금리가 함께 완화됩니다. "

        "Fed 완화 기대와 장기 위험 프리미엄 완화가 동시에 나타납니다."

    )

elif y2_change < 0 and y10_change < 0 and y30_change >= 0:

    rate_structure_comment = (

        "2Y와 10Y는 하락하지만 30Y가 따라오지 않습니다. "

        "통화정책 완화 기대는 있으나 초장기 재정/국채공급 부담이 남아 있습니다."

    )

elif y2_change < 0 and y30_change > 0 and spread30_10_change > 0:

    rate_structure_comment = (

        "Fed 완화 기대와 초장기 재정 부담이 동시에 나타나는 "

        "분화된 금리시장입니다."

    )

elif y2_change > 0 and real_change > 0 and y30_change > 0:

    rate_structure_comment = (

        "단기·실질·초장기금리가 모두 상승합니다. "

        "금융여건의 긴축 압력이 강합니다."

    )

else:

    rate_structure_comment = (

        "금리곡선 내부 신호가 혼재되어 있습니다."

    )

# ============================================================

# 18. 자산별 해석

# ============================================================

# Gold

if real_change < 0 and y30_change < 0:

    gold_view = (

        "매우 우호적 — 실질금리 하락 + 초장기금리 하락"

    )

elif real_change < 0:

    gold_view = (

        "우호적 — 실질금리 하락"

    )

else:

    gold_view = (

        "부담 — 실질금리 상승"

    )

# Bitcoin

if (

    (liq_change > 0 or credit_score == 2)

    and real_change < 0

    and y2_change < 0

):

    btc_view = (

        "매우 우호적 — 금리환경 개선 + 유동성/민간신용 확장"

    )

elif real_change < 0 and y2_change < 0:

    btc_view = (

        "우호적 — 금리환경 개선, 유동성 확산 추가 확인"

    )

elif liq_change < 0 and credit_score == 0:

    btc_view = (

        "주의 — Fed/Treasury 유동성과 민간신용 모두 약화"

    )

else:

    btc_view = (

        "중립 — 뚜렷한 방향 확인 필요"

    )

# 중소형주

if (

    y2_change < 0

    and credit_score == 2

    and y30_change < 0

):

    smallcap_view = (

        "매우 우호적 — 단기금리 하락 + 민간신용 확장 + 장기금리 안정"

    )

elif y2_change < 0 and credit_score == 2:

    smallcap_view = (

        "우호적 — 단기금리 하락 + 은행신용/M2 확장"

    )

elif y2_change < 0 and real_change < 0:

    smallcap_view = (

        "개선 가능 — 금융여건 완화 기대가 먼저 나타남"

    )

else:

    smallcap_view = (

        "아직 확인 필요"

    )

# ============================================================

# 19. 미국 고용 / 실업 스트레스

#

# 목적:

# 물가와 금리가 내려가는 국면에서 시장의 핵심 위험이

# "인플레이션"에서 "고용 둔화 / 경기침체"로 넘어가는지 점검합니다.

#

# 5개 신호를 별도로 확인합니다.

# 1) Sahm Rule

# 2) 실업률 상승 추세

# 3) 신규 실업수당 청구 증가

# 4) 계속 실업수당 청구 증가

# 5) 비농업고용 증가세 둔화

#

# 기존 Liquidity Score에는 섞지 않습니다.

# ============================================================

# ------------------------------------------------------------

# 19-1. 실업률 / Sahm Rule

# ------------------------------------------------------------

unrate_monthly = df["UNRATE"].dropna().sort_index()

sahm_monthly = df["Sahm"].dropna().sort_index()

if len(unrate_monthly) < 13:

    raise ValueError("실업률 추세 계산을 위한 데이터가 부족합니다.")

unrate_now = float(unrate_monthly.iloc[-1])

unrate_3m_avg = float(unrate_monthly.iloc[-3:].mean())

unrate_6m_change = float(

    unrate_monthly.iloc[-1] - unrate_monthly.iloc[-7]

)

unrate_yoy_change = float(

    unrate_monthly.iloc[-1] - unrate_monthly.iloc[-13]

)

unrate_date = unrate_monthly.index[-1]

sahm_now = float(sahm_monthly.iloc[-1])

sahm_date = sahm_monthly.index[-1]

# ------------------------------------------------------------

# 19-2. 신규 / 계속 실업수당 청구

#

# 단일 주 수치는 노이즈가 크므로 4주 이동평균 사용.

# 현재 4주 평균이 최근 52주 저점에서 얼마나 올라왔는지 확인합니다.

# 아래 임계값은 공식 recession rule이 아니라 조기경보용 경험적 기준입니다.

# ------------------------------------------------------------

icsa_weekly = df["ICSA"].dropna().sort_index()

ccsa_weekly = df["CCSA"].dropna().sort_index()

if len(icsa_weekly) < 56 or len(ccsa_weekly) < 56:

    raise ValueError("실업수당 청구 추세 계산을 위한 데이터가 부족합니다.")

icsa_ma4 = icsa_weekly.rolling(4).mean().dropna()

ccsa_ma4 = ccsa_weekly.rolling(4).mean().dropna()

initial_claims_4w = float(icsa_ma4.iloc[-1])

initial_claims_52w_low = float(icsa_ma4.iloc[-52:].min())

initial_claims_vs_low = (

    initial_claims_4w / initial_claims_52w_low - 1

) * 100

initial_claims_13w_change = (

    initial_claims_4w / float(icsa_ma4.iloc[-14]) - 1

) * 100

initial_claims_date = icsa_weekly.index[-1]

continued_claims_4w = float(ccsa_ma4.iloc[-1])

continued_claims_52w_low = float(ccsa_ma4.iloc[-52:].min())

continued_claims_vs_low = (

    continued_claims_4w / continued_claims_52w_low - 1

) * 100

continued_claims_13w_change = (

    continued_claims_4w / float(ccsa_ma4.iloc[-14]) - 1

) * 100

continued_claims_date = ccsa_weekly.index[-1]

# ------------------------------------------------------------

# 19-3. 비농업고용

#

# PAYEMS는 총 고용자 수(천 명) 수준이므로 월간 차분으로

# 월별 고용 증감을 만든 뒤 3개월 / 12개월 평균을 비교합니다.

# ------------------------------------------------------------

payems_monthly = df["PAYEMS"].dropna().sort_index()

payroll_change = payems_monthly.diff().dropna()

if len(payroll_change) < 12:

    raise ValueError("비농업고용 추세 계산을 위한 데이터가 부족합니다.")

payroll_latest = float(payroll_change.iloc[-1])

payroll_3m_avg = float(payroll_change.iloc[-3:].mean())

payroll_12m_avg = float(payroll_change.iloc[-12:].mean())

payroll_date = payems_monthly.index[-1]

# ------------------------------------------------------------

# 19-4. Labor Stress Trigger

# ------------------------------------------------------------

# ① Sahm Rule

# 공식 경기침체 신호는 0.50%p 이상.

# 0.30%p 이상은 그 전에 보는 조기 경고 구간으로 사용.

sahm_warning = sahm_now >= 0.30

sahm_recession_trigger = sahm_now >= 0.50

# ② 실업률 상승 추세

# 6개월 동안 +0.40%p 이상 상승하면 뚜렷한 악화로 판단.

unrate_trigger = unrate_6m_change >= 0.40

# ③ 신규 실업수당

# 4주 평균이 최근 52주 저점보다 20% 이상 높아졌을 때 조기경보.

initial_claims_trigger = initial_claims_vs_low >= 20.0

# ④ 계속 실업수당

# 신규 청구보다 "재취업이 어려운가"를 보는 지표.

# 52주 저점 대비 +15% 이상이면서 최근 13주도 증가하면 경고.

continued_claims_trigger = (

    continued_claims_vs_low >= 15.0

    and continued_claims_13w_change > 0

)

# ⑤ 비농업고용

# 최근 3개월 평균이 월 +7.5만 명 미만이고,

# 동시에 최근 12개월 평균의 60%에도 못 미치면 고용창출 급둔화.

if payroll_12m_avg > 0:

    payroll_trigger = (

        payroll_3m_avg < 75

        and payroll_3m_avg < payroll_12m_avg * 0.60

    )

else:

    payroll_trigger = payroll_3m_avg < 0

labor_score = int(sum([

    sahm_warning,

    unrate_trigger,

    initial_claims_trigger,

    continued_claims_trigger,

    payroll_trigger,

]))

# ------------------------------------------------------------

# 19-5. 고용 스트레스 판정

# ------------------------------------------------------------

if sahm_recession_trigger:

    labor_regime = (

        "🔴 경기침체 경고 — Sahm Rule 0.50%p 이상"

    )

elif labor_score >= 4:

    labor_regime = (

        "🔴 매우 높음 — 고용 악화 신호가 광범위하게 동시 발생"

    )

elif labor_score == 3:

    labor_regime = (

        "🟠 높아지는 중 — 실업/청구/고용 증가세에서 복수 경고"

    )

elif labor_score == 2:

    labor_regime = (

        "🟡 둔화 확인 — 고용시장이 냉각되고 있으나 위기 확정은 아님"

    )

elif labor_score == 1:

    labor_regime = (

        "🟡 초기 냉각 — 일부 고용 지표 약화, 추세 확인 필요"

    )

else:

    labor_regime = (

        "🟢 안정 — 현재 고용/실업 스트레스 제한적"

    )

# ------------------------------------------------------------

# 19-6. 금리하락의 성격 판정

#

# 사용자 관점의 핵심:

# 2Y가 내려갈 때 고용이 멀쩡하면 Risk-On에 유리한 '좋은 완화',

# 고용까지 무너지면 경기침체를 반영하는 '나쁜 완화'일 수 있습니다.

# ------------------------------------------------------------

if y2_change < 0 and labor_score <= 1:

    easing_quality = (

        "🟢 좋은 금리하락 가능성 — 2Y는 하락하지만 고용 스트레스는 낮음"

    )

elif y2_change < 0 and labor_score == 2:

    easing_quality = (

        "🟡 혼합형 금리하락 — 완화 기대와 고용 둔화가 함께 나타남"

    )

elif y2_change < 0 and labor_score >= 3:

    easing_quality = (

        "🔴 나쁜 금리하락 위험 — 금리 하락이 고용/경기 악화를 반영할 가능성"

    )

elif y2_change >= 0 and labor_score >= 3:

    easing_quality = (

        "🔴 정책 딜레마 — 금리 부담이 남아 있는데 고용도 빠르게 약화"

    )

elif y2_change >= 0 and labor_score >= 1:

    easing_quality = (

        "🟡 금리 부담 + 고용 냉각 — 아직 완화 국면은 아니며 고용 추세 점검"

    )

else:

    easing_quality = (

        "🟢 현재는 고용보다 물가·금리 쪽이 더 중요한 국면"

    )

# ------------------------------------------------------------

# 19-7. 세부 신호 설명

# ------------------------------------------------------------

labor_signals = []

if sahm_recession_trigger:

    labor_signals.append(

        "Sahm Rule 0.50%p 이상 → 공식 정의상 경기침체 시작 신호 구간"

    )

elif sahm_warning:

    labor_signals.append(

        "Sahm Rule 0.30%p 이상 → 0.50%p 공식 트리거 접근 중"

    )

else:

    labor_signals.append(

        "Sahm Rule은 공식 경기침체 트리거와 거리가 있음"

    )

if unrate_trigger:

    labor_signals.append(

        f"실업률 6개월 {unrate_6m_change:+.2f}%p → 상승 추세 뚜렷"

    )

else:

    labor_signals.append(

        f"실업률 6개월 {unrate_6m_change:+.2f}%p → 급격한 악화 신호 없음"

    )

if initial_claims_trigger:

    labor_signals.append(

        f"신규 실업수당 4주평균이 52주 저점 대비 {initial_claims_vs_low:+.1f}% → 해고 증가 조기경보"

    )

else:

    labor_signals.append(

        f"신규 실업수당은 52주 저점 대비 {initial_claims_vs_low:+.1f}% → 급증 조건 미충족"

    )

if continued_claims_trigger:

    labor_signals.append(

        f"계속 실업수당이 52주 저점 대비 {continued_claims_vs_low:+.1f}% → 재취업 난이도 상승"

    )

else:

    labor_signals.append(

        f"계속 실업수당은 52주 저점 대비 {continued_claims_vs_low:+.1f}% → 심각한 장기실업 스트레스 미확인"

    )

if payroll_trigger:

    labor_signals.append(

        f"비농업고용 3개월 평균 {payroll_3m_avg:+.0f}K → 고용창출 급둔화"

    )

else:

    labor_signals.append(

        f"비농업고용 3개월 평균 {payroll_3m_avg:+.0f}K → 급격한 고용 붕괴 조건 미충족"

    )

# ============================================================

# 20. 엔캐리 트레이드 청산 위험

#

# 기준 사건 : 2024-08-05 전후 글로벌 엔캐리 청산

#

# 핵심 논리

# 1) 엔화 급등          : USDJPY 급락

# 2) 미국 단기금리 하락 : 미국 2Y 하락 → 미일 금리차 축소 압력

# 3) VIX 급등          : 위험회피 / 레버리지 청산 확인

# 4) Nikkei 급락       : 일본 위험자산 스트레스 확인

# 5) Sahm Rule 상승    : 미국 경기둔화 우려 확인

# 6) 일본 단기금리     : 월간 보조지표

#

# 주의:

# VIX 급등이나 Nikkei 급락만으로는 엔캐리 청산이라고 판정하지 않습니다.

# 반드시 '엔화 강세'가 먼저 확인되어야 합니다.

# ============================================================

def _clean_series(name):

    return df[name].dropna().sort_index()

def _latest_before(name, date=None):

    s = _clean_series(name)

    if date is not None:

        s = s[s.index <= pd.Timestamp(date)]

    if len(s) == 0:

        return np.nan

    return float(s.iloc[-1])

def _value_days_before(name, date=None, days=28):

    s = _clean_series(name)

    if len(s) == 0:

        return np.nan

    if date is None:

        end_date = s.index[-1]

    else:

        end_date = pd.Timestamp(date)

    target_date = end_date - pd.Timedelta(days=days)

    old = s[s.index <= target_date]

    if len(old) == 0:

        return np.nan

    return float(old.iloc[-1])

def _safe_pct_change(now_value, old_value):

    if pd.isna(now_value) or pd.isna(old_value) or old_value == 0:

        return np.nan

    return (now_value / old_value - 1) * 100

def _safe_diff(now_value, old_value):

    if pd.isna(now_value) or pd.isna(old_value):

        return np.nan

    return now_value - old_value

def carry_snapshot(date=None):

    # USD/JPY

    usd_now = _latest_before("USDJPY", date)

    usd_5d = _value_days_before("USDJPY", date, 7)

    usd_4w = _value_days_before("USDJPY", date, 28)

    # 미국 2Y

    us2_now = _latest_before("Treasury2Y", date)

    us2_4w = _value_days_before("Treasury2Y", date, 28)

    # VIX

    vix_now = _latest_before("VIX", date)

    vix_5d = _value_days_before("VIX", date, 7)

    # Nikkei

    nikkei_now = _latest_before("Nikkei225", date)

    nikkei_5d = _value_days_before("Nikkei225", date, 7)

    # Sahm Rule

    sahm_now = _latest_before("Sahm", date)

    # 일본 단기금리: 월간 데이터라 있으면 보조적으로만 사용

    if "JapanCall" in df.columns:

        japan_now = _latest_before("JapanCall", date)

        japan_4w = _value_days_before("JapanCall", date, 28)

    else:

        japan_now = np.nan

        japan_4w = np.nan

    jpy_5d_pct = _safe_pct_change(usd_now, usd_5d)

    jpy_4w_pct = _safe_pct_change(usd_now, usd_4w)

    us2_4w_change = _safe_diff(us2_now, us2_4w)

    vix_5d_pct = _safe_pct_change(vix_now, vix_5d)

    nikkei_5d_pct = _safe_pct_change(nikkei_now, nikkei_5d)

    # 단순 미일 단기금리 차이(미국 2Y - 일본 단기금리)

    # 일본 단기금리는 월간이라 보조지표입니다.

    if (

        not pd.isna(us2_now)

        and not pd.isna(japan_now)

    ):

        carry_gap_now = us2_now - japan_now

    else:

        carry_gap_now = np.nan

    if (

        not pd.isna(us2_4w)

        and not pd.isna(japan_4w)

    ):

        carry_gap_4w = us2_4w - japan_4w

    else:

        carry_gap_4w = np.nan

    carry_gap_change = _safe_diff(

        carry_gap_now,

        carry_gap_4w

    )

    return {

        "USDJPY": usd_now,

        "JPY_5D": jpy_5d_pct,

        "JPY_4W": jpy_4w_pct,

        "US2Y": us2_now,

        "US2Y_4W": us2_4w_change,

        "VIX": vix_now,

        "VIX_5D": vix_5d_pct,

        "Nikkei": nikkei_now,

        "Nikkei_5D": nikkei_5d_pct,

        "Sahm": sahm_now,

        "JapanRate": japan_now,

        "CarryGap": carry_gap_now,

        "CarryGapChange": carry_gap_change,

    }

carry_now = carry_snapshot()

carry_2024 = carry_snapshot("2024-08-05")

# ------------------------------------------------------------

# 20-1. 현재 엔캐리 청산 Trigger

# ------------------------------------------------------------

# ① 엔화 급등

# USDJPY가 내려가면 엔화 강세입니다.

yen_trigger = (

    (

        not pd.isna(carry_now["JPY_5D"])

        and carry_now["JPY_5D"] <= -2.5

    )

    or

    (

        not pd.isna(carry_now["JPY_4W"])

        and carry_now["JPY_4W"] <= -5.0

    )

)

# ② 미국 2Y 급락

# Fed 완화 기대 / 미국 성장 우려로 미일 금리차가 빠르게 좁아지는 경우

rate_trigger = (

    not pd.isna(carry_now["US2Y_4W"])

    and carry_now["US2Y_4W"] <= -0.30

)

# ③ 미일 단기금리차 축소

# 일본 데이터가 월간이므로 반드시 보조 신호로만 사용

gap_trigger = (

    not pd.isna(carry_now["CarryGapChange"])

    and carry_now["CarryGapChange"] <= -0.25

)

# ④ VIX 급등

vol_trigger = (

    (

        not pd.isna(carry_now["VIX"])

        and carry_now["VIX"] >= 25

    )

    or

    (

        not pd.isna(carry_now["VIX_5D"])

        and carry_now["VIX_5D"] >= 50

    )

)

# ⑤ Nikkei 급락

nikkei_trigger = (

    not pd.isna(carry_now["Nikkei_5D"])

    and carry_now["Nikkei_5D"] <= -7

)

# ⑥ 미국 경기둔화 경고

growth_trigger = (

    not pd.isna(carry_now["Sahm"])

    and carry_now["Sahm"] >= 0.40

)

carry_score = int(sum([

    yen_trigger,

    rate_trigger,

    gap_trigger,

    vol_trigger,

    nikkei_trigger,

    growth_trigger,

]))

# ------------------------------------------------------------

# 20-2. 엔캐리 위험 판정

# ------------------------------------------------------------

# 핵심 원칙:

# 엔화가 강해지지 않으면 VIX/Nikkei가 흔들려도

# '엔캐리 청산'이라고 부르지 않습니다.

if not yen_trigger:

    carry_regime = (

        "🟢 낮음 — 엔화 급등 신호 없음"

    )

elif (

    yen_trigger

    and (rate_trigger or gap_trigger)

    and vol_trigger

    and nikkei_trigger

):

    carry_regime = (

        "🔴 매우 높음 — 엔화 급등 + 금리차 축소 + "

        "VIX/일본증시 스트레스 동시 발생"

    )

elif (

    yen_trigger

    and (rate_trigger or gap_trigger)

    and (vol_trigger or nikkei_trigger)

):

    carry_regime = (

        "🔴 높음 — 엔화 강세 + 금리차 축소 + "

        "위험자산 스트레스 확인"

    )

elif (

    yen_trigger

    and (rate_trigger or gap_trigger)

):

    carry_regime = (

        "🟠 높아지는 중 — 엔화 강세와 "

        "Carry 금리차 축소가 동시 발생"

    )

else:

    carry_regime = (

        "🟡 관찰 — 엔화 강세는 있으나 "

        "금리차 축소/시장 스트레스 확인 필요"

    )

# ------------------------------------------------------------

# 20-3. 2024-08-05 엔캐리 청산 국면과 현재 유사도

# ------------------------------------------------------------

# 2024-08-05 당시와 현재를 절대 레벨 그대로 비교하면

# 시대별 금리/환율 레벨 차이 때문에 왜곡될 수 있으므로,

# '스트레스 방향의 변화폭'을 비교합니다.

def _positive_stress(value, reverse=False, baseline=0.0):

    if pd.isna(value):

        return 0.0

    if reverse:

        return max(0.0, -(value - baseline))

    return max(0.0, value - baseline)

def _stress_ratio(current, reference):

    # 기준 사건에서 해당 신호가 거의 없었다면 유사도 계산에서 0 처리

    if pd.isna(reference) or reference <= 0:

        return 0.0

    if pd.isna(current):

        return 0.0

    # 2024 사건보다 더 심해도 유사도는 최대 100%로 제한

    return min(max(current / reference, 0.0), 1.0)

current_stress = {

    # USDJPY 하락폭: 마이너스가 위험 방향이므로 부호 반전

    "JPY": _positive_stress(

        carry_now["JPY_4W"],

        reverse=True

    ),

    # 미국 2Y 하락폭

    "US2Y": _positive_stress(

        carry_now["US2Y_4W"],

        reverse=True

    ),

    # VIX는 평시 15를 기준으로 초과분 사용

    "VIX": _positive_stress(

        carry_now["VIX"],

        baseline=15.0

    ),

    # Nikkei 5일 하락폭

    "Nikkei": _positive_stress(

        carry_now["Nikkei_5D"],

        reverse=True

    ),

    # Sahm Rule

    "Sahm": _positive_stress(

        carry_now["Sahm"]

    ),

}

event_stress = {

    "JPY": _positive_stress(

        carry_2024["JPY_4W"],

        reverse=True

    ),

    "US2Y": _positive_stress(

        carry_2024["US2Y_4W"],

        reverse=True

    ),

    "VIX": _positive_stress(

        carry_2024["VIX"],

        baseline=15.0

    ),

    "Nikkei": _positive_stress(

        carry_2024["Nikkei_5D"],

        reverse=True

    ),

    "Sahm": _positive_stress(

        carry_2024["Sahm"]

    ),

}

# 엔화 + 미국 단기금리를 가장 중요하게 둠

carry_weights = {

    "JPY": 0.30,

    "US2Y": 0.25,

    "VIX": 0.20,

    "Nikkei": 0.15,

    "Sahm": 0.10,

}

carry_similarity = 0.0

for key, weight in carry_weights.items():

    carry_similarity += (

        _stress_ratio(

            current_stress[key],

            event_stress[key]

        )

        * weight

    )

carry_similarity *= 100

# ------------------------------------------------------------

# 20-4. 유사도 레이블

# ------------------------------------------------------------

if carry_similarity >= 75:

    carry_similarity_view = (

        "🔴 2024년 8월 청산국면과 매우 유사"

    )

elif carry_similarity >= 50:

    carry_similarity_view = (

        "🟠 2024년 8월 청산국면과 유사성 상승"

    )

elif carry_similarity >= 25:

    carry_similarity_view = (

        "🟡 일부 유사 신호 존재"

    )

else:

    carry_similarity_view = (

        "🟢 2024년 8월과 유사성 낮음"

    )

# ------------------------------------------------------------

# 20-5. 현재 상황 설명

# ------------------------------------------------------------

carry_signals = []

carry_signals.append(

    f"엔화 5일 {carry_now['JPY_5D']:+.2f}%, "

    f"4주 {carry_now['JPY_4W']:+.2f}% "

    "(USDJPY 기준, 마이너스=엔화 강세)"

)

if yen_trigger:

    carry_signals.append(

        "엔화가 빠르게 강해져 Carry 포지션 청산 압력이 커지는 방향"

    )

else:

    carry_signals.append(

        "엔화 급등 조건은 아직 충족하지 않음"

    )

if rate_trigger:

    carry_signals.append(

        "미국 2Y가 빠르게 하락 → 미일 금리차 축소 압력 확대"

    )

else:

    carry_signals.append(

        "미국 2Y 급락 조건 없음 → 2024년 8월과 핵심 차이"

    )

if vol_trigger:

    carry_signals.append(

        "VIX 스트레스 확인 → 레버리지 축소/위험회피 동반"

    )

else:

    carry_signals.append(

        "VIX 급등 신호 없음"

    )

if nikkei_trigger:

    carry_signals.append(

        "Nikkei 급락 확인 → 일본 위험자산 청산 압력 동반"

    )

else:

    carry_signals.append(

        "Nikkei 급락 조건 없음"

    )

if growth_trigger:

    carry_signals.append(

        "Sahm Rule 상승 → 미국 경기둔화 우려가 Carry 청산을 자극할 수 있음"

    )

else:

    carry_signals.append(

        "Sahm Rule 기준 경기침체 스트레스 낮음"

    )

# ============================================================

# 21. 갑작스러운 금융충격 감시 (Sudden Shock Detector)

#

# 목적:

# 평소의 금리/유동성 환경이 아니라 "갑자기 금융시스템 내부에서

# 뭔가 터지고 있는가"를 빠르게 확인합니다.

#

# ① HY OAS

#    - 회사채 신용위험이 갑자기 확대되는지 확인

#    - 2024-08-05 엔캐리 스트레스 때도 단기간 급등

#

# ② SOFR - IORB

#    - 레포/단기자금시장의 자금조달 압력 확인

#    - 하루짜리 월말/분기말 노이즈를 줄이기 위해 3일 평균 사용

#

# ③ STLFSI4

#    - 금리/스프레드/변동성을 합친 종합 금융스트레스 지수

#    - 0 = 장기평균 수준의 스트레스

#    - 0보다 높을수록 평균 이상 스트레스

#

# 기존 Liquidity Score에는 섞지 않고 Shock Score 0~3으로 별도 표시.

# ============================================================

shock_today = pd.Timestamp.today().normalize()

# ------------------------------------------------------------

# 21-1. HY OAS

# ------------------------------------------------------------

hy_series = df["HYOAS"].dropna().sort_index()

hy_series = hy_series[hy_series.index <= shock_today]

if len(hy_series) < 25:

    raise ValueError("HY OAS 금융충격 판단을 위한 데이터가 부족합니다.")

hy_now = float(hy_series.iloc[-1])

hy_date = hy_series.index[-1]

hy_5d_old = _value_days_before("HYOAS", hy_date, 7)

hy_4w_old = _value_days_before("HYOAS", hy_date, 28)

hy_5d_change = _safe_diff(hy_now, hy_5d_old)

hy_4w_change = _safe_diff(hy_now, hy_4w_old)

# 경험적 조기경보 기준:

# - 1주 +50bp, 4주 +75bp 또는 레벨 5% 이상이면 강한 신용 스트레스

# - 그 절반 정도부터 Watch

hy_trigger = (

    (not pd.isna(hy_5d_change) and hy_5d_change >= 0.50)

    or (not pd.isna(hy_4w_change) and hy_4w_change >= 0.75)

    or hy_now >= 5.00

)

hy_watch = (

    hy_trigger

    or (not pd.isna(hy_5d_change) and hy_5d_change >= 0.25)

    or (not pd.isna(hy_4w_change) and hy_4w_change >= 0.50)

    or hy_now >= 4.00

)

# ------------------------------------------------------------

# 21-2. SOFR - IORB

# ------------------------------------------------------------

repo = (

    df[["SOFR", "IORB"]]

    .dropna()

    .sort_index()

)

repo = repo[repo.index <= shock_today].copy()

if len(repo) < 20:

    raise ValueError("SOFR-IORB 금융충격 판단을 위한 데이터가 부족합니다.")

repo["SOFR_IORB_bp"] = (

    repo["SOFR"] - repo["IORB"]

) * 100

repo_now = float(repo["SOFR_IORB_bp"].iloc[-1])

repo_3d_avg = float(repo["SOFR_IORB_bp"].iloc[-3:].mean())

repo_20d_avg = float(repo["SOFR_IORB_bp"].iloc[-20:].mean())

repo_3d_vs_20d = repo_3d_avg - repo_20d_avg

repo_date = repo.index[-1]

# 단일 하루 튐보다 3일 평균을 중시.

# +10bp 이상이 며칠 지속되면 단기자금 조달 압력으로 경고.

repo_trigger = (

    repo_3d_avg >= 10.0

    or (repo_3d_avg >= 7.5 and repo_3d_vs_20d >= 7.5)

)

repo_watch = (

    repo_trigger

    or repo_3d_avg >= 5.0

    or repo_3d_vs_20d >= 5.0

)

# ------------------------------------------------------------

# 21-3. STLFSI4

# ------------------------------------------------------------

stlfsi_series = df["STLFSI"].dropna().sort_index()

stlfsi_series = stlfsi_series[stlfsi_series.index <= shock_today]

if len(stlfsi_series) < 8:

    raise ValueError("STLFSI4 금융충격 판단을 위한 데이터가 부족합니다.")

stlfsi_now = float(stlfsi_series.iloc[-1])

stlfsi_date = stlfsi_series.index[-1]

stlfsi_4w_old = _value_days_before("STLFSI", stlfsi_date, 28)

stlfsi_4w_change = _safe_diff(stlfsi_now, stlfsi_4w_old)

# STLFSI는 0이 장기 평균 수준의 스트레스.

# +0.50 이상 또는 4주 +0.75 이상 급등이면 강한 경고.

stlfsi_trigger = (

    stlfsi_now >= 0.50

    or (

        not pd.isna(stlfsi_4w_change)

        and stlfsi_4w_change >= 0.75

    )

)

stlfsi_watch = (

    stlfsi_trigger

    or stlfsi_now >= 0.00

    or (

        not pd.isna(stlfsi_4w_change)

        and stlfsi_4w_change >= 0.50

    )

)

# ------------------------------------------------------------

# 21-4. Shock Score

# ------------------------------------------------------------

shock_score = int(sum([

    hy_trigger,

    repo_trigger,

    stlfsi_trigger,

]))

shock_watch_count = int(sum([

    hy_watch,

    repo_watch,

    stlfsi_watch,

]))

if shock_score == 3:

    shock_regime = (

        "🔴 시스템 스트레스 — 신용·단기자금·종합금융 스트레스가 동시 발생"

    )

elif shock_score == 2:

    shock_regime = (

        "🟠 금융충격 확산 — 서로 다른 두 금융시장에 강한 스트레스 발생"

    )

elif shock_score == 1:

    shock_regime = (

        "🟡 국지적 충격 — 한 영역에서 강한 스트레스, 전염 여부 확인 필요"

    )

elif shock_watch_count >= 2:

    shock_regime = (

        "🟡 조기경보 — 강한 트리거는 없지만 복수 시장에서 스트레스 상승"

    )

elif shock_watch_count == 1:

    shock_regime = (

        "🟢 대체로 안정 — 한 지표만 주의 구간, 시스템 충격은 미확인"

    )

else:

    shock_regime = (

        "🟢 안정 — 기업신용·레포·종합 금융스트레스 모두 낮음"

    )

# ------------------------------------------------------------

# 21-5. 세부 신호

# ------------------------------------------------------------

shock_signals = []

if hy_trigger:

    shock_signals.append(

        f"🔴 HY OAS {hy_now:.2f}% / 1주 {hy_5d_change:+.2f}%p / 4주 {hy_4w_change:+.2f}%p → 기업 신용 스트레스 급증"

    )

elif hy_watch:

    shock_signals.append(

        f"🟡 HY OAS {hy_now:.2f}% / 1주 {hy_5d_change:+.2f}%p / 4주 {hy_4w_change:+.2f}%p → 신용스프레드 확대 관찰"

    )

else:

    shock_signals.append(

        f"🟢 HY OAS {hy_now:.2f}% / 4주 {hy_4w_change:+.2f}%p → 기업 신용시장 안정"

    )

if repo_trigger:

    shock_signals.append(

        f"🔴 SOFR-IORB 3일평균 {repo_3d_avg:+.1f}bp → 레포/단기자금 조달 스트레스"

    )

elif repo_watch:

    shock_signals.append(

        f"🟡 SOFR-IORB 3일평균 {repo_3d_avg:+.1f}bp → 단기자금시장 압력 관찰"

    )

else:

    shock_signals.append(

        f"🟢 SOFR-IORB 3일평균 {repo_3d_avg:+.1f}bp → 단기자금시장 안정"

    )

if stlfsi_trigger:

    shock_signals.append(

        f"🔴 STLFSI4 {stlfsi_now:+.2f} / 4주 {stlfsi_4w_change:+.2f} → 종합 금융스트레스 급증"

    )

elif stlfsi_watch:

    shock_signals.append(

        f"🟡 STLFSI4 {stlfsi_now:+.2f} / 4주 {stlfsi_4w_change:+.2f} → 평균 이상 스트레스 또는 빠른 상승"

    )

else:

    shock_signals.append(

        f"🟢 STLFSI4 {stlfsi_now:+.2f} / 4주 {stlfsi_4w_change:+.2f} → 평균 이하 금융스트레스"

    )

# VIX와 지급준비금은 Shock Score에 중복 반영하지 않고 맥락 확인용.

shock_context = (

    f"참고: VIX {carry_now['VIX']:.2f}, "

    f"지급준비금 4주 {reserve_4w_pct:+.2f}% — "

    "Shock Score에는 중복 반영하지 않음"

)

# ============================================================

