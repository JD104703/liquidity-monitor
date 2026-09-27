# 22. 출력

# ============================================================



print()

print("=" * 90)

print("현재 미국 매크로 / 유동성 상황")

print("=" * 90)



print(f"기준일                    : {weekly.index[-1].date()}")



print()

print("[금리]")

print(f"10Y 실질금리              : {now['Real10Y']:.2f}%")

print(f"2Y 국채금리               : {now['Treasury2Y']:.2f}%")

print(f"10Y 국채금리              : {now['Treasury10Y']:.2f}%")

print(f"30Y 국채금리              : {now['Treasury30Y']:.2f}%")

print(f"10Y-2Y                    : {now['Spread10_2']:.2f}%p")

print(f"30Y-10Y                   : {now['Spread30_10']:.2f}%p")



print()

print("[Fed / Treasury]")

print(f"Fed Assets                : ${now['FedAssets_T']:.2f}T")

print(f"TGA                       : ${now['TGA_T']:.2f}T")

print(f"RRP                       : ${now['RRP_T']:.3f}T")

print(f"Liquidity Proxy           : ${now['NetLiquidity']:.2f}T")



print()

print("[은행 / 민간 신용]")

print(f"은행대출                  : ${now['BankLoans_T']:.2f}T")

print(f"은행 지급준비금           : ${now['Reserves_T']:.2f}T")

print(f"M2 ({m2_date.date()})     : ${m2_now:.2f}T")



# ============================================================



print()

print("=" * 90)

print("최근 4주 변화")

print("=" * 90)



print(f"10Y 실질금리              : {real_change:+.2f}%p")

print(f"2Y                        : {y2_change:+.2f}%p")

print(f"10Y                       : {y10_change:+.2f}%p")

print(f"30Y                       : {y30_change:+.2f}%p")

print(f"10Y-2Y                    : {spread10_2_change:+.2f}%p")

print(f"30Y-10Y                   : {spread30_10_change:+.2f}%p")

print(f"Liquidity Proxy           : {liq_change:+.3f}T")



print()

print(f"은행대출 4주              : {bankloan_4w_pct:+.2f}%")

print(f"은행대출 YoY              : {bankloan_yoy:+.2f}%")

print(f"지급준비금 4주            : {reserve_4w_change:+.3f}T")

print(f"지급준비금 4주 %          : {reserve_4w_pct:+.2f}%")



print()

print(f"M2 3개월 연율화           : {m2_3m_ann:+.2f}%")

print(f"M2 YoY                    : {m2_yoy:+.2f}%")



# ============================================================



print()

print("=" * 90)

print("기존 Liquidity Score")

print("=" * 90)



for signal in signals:

    print("•", signal)



print()

print(f"Liquidity Score           : {score} / 4")

print(f"판정                      : {regime}")

print()

print(macro_comment)



# ============================================================



print()

print("=" * 90)

print("신규 Private Credit / 광의통화")

print("=" * 90)



for signal in credit_signals:

    print("•", signal)



print()

print(f"Private Credit Score      : {credit_score} / 2")

print(f"판정                      : {credit_regime}")



print()

print("•", reserve_signal)

print("•", rrp_signal)



# ============================================================



print()

print("=" * 90)

print("Fed + 은행신용 종합 유동성 판정")

print("=" * 90)



print(total_liquidity_view)



# ============================================================



print()

print("=" * 90)

print("초장기금리 / 재정·Term Premium")

print("=" * 90)



print(long_rate_signal)

print()

print(rate_structure_comment)



# ============================================================



print()

print("=" * 90)

print("자산별 현재 해석")

print("=" * 90)



print(f"Gold                      : {gold_view}")

print(f"Bitcoin                   : {btc_view}")

print(f"중소형주                  : {smallcap_view}")



# ============================================================



print()

print("=" * 90)

print("미국 고용 / 실업 스트레스")

print("=" * 90)



print(f"실업률 ({unrate_date.date()})       : {unrate_now:.2f}%")

print(f"실업률 3개월 평균          : {unrate_3m_avg:.2f}%")

print(f"실업률 6개월 변화          : {unrate_6m_change:+.2f}%p")

print(f"실업률 YoY 변화            : {unrate_yoy_change:+.2f}%p")

print(f"Sahm Rule ({sahm_date.date()})      : {sahm_now:.2f}%p")



print()

print(f"신규 실업수당 4주평균      : {initial_claims_4w/1000:.0f}K")

print(f"신규청구 52주저점 대비     : {initial_claims_vs_low:+.1f}%")

print(f"신규청구 최근 13주 변화    : {initial_claims_13w_change:+.1f}%")

print(f"계속 실업수당 4주평균      : {continued_claims_4w/1_000_000:.2f}M")

print(f"계속청구 52주저점 대비     : {continued_claims_vs_low:+.1f}%")

print(f"계속청구 최근 13주 변화    : {continued_claims_13w_change:+.1f}%")



print()

print(f"비농업고용 최근월          : {payroll_latest:+.0f}K")

print(f"비농업고용 3개월 평균      : {payroll_3m_avg:+.0f}K")

print(f"비농업고용 12개월 평균     : {payroll_12m_avg:+.0f}K")



print()

for signal in labor_signals:

    print("•", signal)



print()

print(f"Labor Stress Score        : {labor_score} / 5")

print(f"고용/실업 판정             : {labor_regime}")

print(f"금리하락의 성격            : {easing_quality}")



# ============================================================



print()

print("=" * 90)

print("엔캐리 트레이드 청산 위험")

print("=" * 90)



print(f"USDJPY                    : {carry_now['USDJPY']:.2f}")

print(f"엔화 5일 변화             : {carry_now['JPY_5D']:+.2f}%")

print(f"엔화 4주 변화             : {carry_now['JPY_4W']:+.2f}%")



print()

print(f"미국 2Y                   : {carry_now['US2Y']:.2f}%")

print(f"미국 2Y 4주 변화          : {carry_now['US2Y_4W']:+.2f}%p")



if not pd.isna(carry_now["JapanRate"]):

    print(f"일본 단기금리(보조)       : {carry_now['JapanRate']:.2f}%")



if not pd.isna(carry_now["CarryGap"]):

    print(f"미·일 단기금리차(보조)    : {carry_now['CarryGap']:+.2f}%p")



if not pd.isna(carry_now["CarryGapChange"]):

    print(f"금리차 4주 변화(보조)     : {carry_now['CarryGapChange']:+.2f}%p")



print()

print(f"VIX                       : {carry_now['VIX']:.2f}")

print(f"VIX 5일 변화              : {carry_now['VIX_5D']:+.1f}%")

print(f"Nikkei 5일 변화           : {carry_now['Nikkei_5D']:+.2f}%")

print(f"Sahm Rule                 : {carry_now['Sahm']:.2f}")



print()

for signal in carry_signals:

    print("•", signal)



print()

print(f"엔캐리 위험점수           : {carry_score} / 6")

print(f"현재 판정                 : {carry_regime}")

print(

    f"2024-08-05 유사도         : "

    f"{carry_similarity:.0f}%"

)

print(f"유사도 해석               : {carry_similarity_view}")



print()

print("[2024-08-05 기준 사건]")

print(f"엔화 4주 변화             : {carry_2024['JPY_4W']:+.2f}%")

print(f"미국 2Y 4주 변화          : {carry_2024['US2Y_4W']:+.2f}%p")

print(f"VIX                       : {carry_2024['VIX']:.2f}")

print(f"Nikkei 5일 변화           : {carry_2024['Nikkei_5D']:+.2f}%")

print(f"Sahm Rule                 : {carry_2024['Sahm']:.2f}")



# ============================================================



print()

print("=" * 90)

print("갑작스러운 금융충격 감시")

print("=" * 90)



print(f"HY OAS ({hy_date.date()})          : {hy_now:.2f}%")

print(f"HY OAS 1주 변화           : {hy_5d_change:+.2f}%p")

print(f"HY OAS 4주 변화           : {hy_4w_change:+.2f}%p")



print()

print(f"SOFR-IORB ({repo_date.date()})     : {repo_now:+.1f}bp")

print(f"SOFR-IORB 3일 평균        : {repo_3d_avg:+.1f}bp")

print(f"SOFR-IORB 20일 평균       : {repo_20d_avg:+.1f}bp")



print()

print(f"STLFSI4 ({stlfsi_date.date()})     : {stlfsi_now:+.2f}")

print(f"STLFSI4 4주 변화          : {stlfsi_4w_change:+.2f}")



print()

for signal in shock_signals:

    print("•", signal)



print()

print(f"Shock Score               : {shock_score} / 3")

print(f"판정                      : {shock_regime}")

print(shock_context)



# ============================================================



print()

print("=" * 90)

print("최종 한눈에 보기")

print("=" * 90)



print(f"기존 유동성               : {regime}")

print(f"민간 신용                 : {credit_regime}")

print(f"종합 유동성               : {total_liquidity_view}")

print(f"지급준비금                : {reserve_signal}")

print(f"RRP                       : {rrp_signal}")

print(f"초장기금리                : {long_rate_signal}")

print(f"고용/실업                 : {labor_regime}")

print(f"금리하락 성격             : {easing_quality}")

print(f"엔캐리 청산               : {carry_regime}")

print(f"2024 엔캐리 유사도        : {carry_similarity:.0f}% — {carry_similarity_view}")

print(f"갑작스러운 금융충격       : {shock_score} / 3 — {shock_regime}")



print()

print(f"Gold                      : {gold_view}")

print(f"Bitcoin                   : {btc_view}")

print(f"중소형주                  : {smallcap_view}")