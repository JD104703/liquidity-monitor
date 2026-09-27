# 미국 유동성 · 위험 모니터 자동 게시

원본 노트북의 계산식·점수 체계를 유지하고, FRED 공개 CSV 다운로드와 카드형 웹 출력으로 옮긴 버전입니다. KRX 승인이나 FRED API 키 없이 사용하는 공개 CSV 경로입니다. 외부 제공처의 응답 상태에 따라 수집이 실패할 수 있습니다.

## 처음 한 번 설정

1. GitHub에서 `liquidity-monitor`라는 저장소를 만듭니다. 기본 브랜치는 `main`으로 합니다. 공개 저장소에서는 코드와 계산 기준도 공개됩니다. 비공개 저장소의 Pages 사용 가능 여부는 계정 플랜을 확인하세요.
2. 이 폴더의 파일을 저장소 루트에 올립니다. ZIP 파일 자체가 아니라 압축을 푼 내용물을 올리세요. `.github/workflows/publish.yml`도 반드시 포함해야 합니다. 웹 업로드에서 빠지면 **Add file → Create new file**로 해당 경로를 입력하고 파일 내용을 붙여 넣습니다.
3. 저장소의 **Settings → Pages → Build and deployment → Source**에서 **GitHub Actions**를 선택합니다.
4. **Actions → Update liquidity dashboard → Run workflow**를 눌러 최초 실행합니다. 성공하면 **Settings → Pages** 또는 실행의 `github-pages` 환경에 공유 주소가 표시됩니다.

새 설정 이전에 자동 push 실행이 실패했더라도 Pages 설정 후 다시 실행하면 됩니다. 이 패키지만으로 저장소 생성이나 실제 웹 게시가 완료되는 것은 아닙니다.

## 운영 방식

- 매일 **한국시간 오전 9시 17분** 예약 실행: `17 0 * * *` (UTC).
- 모든 계산과 렌더링이 성공한 경우에만 Pages에 게시합니다.
- 수집·계산·검산이 실패하면 새 게시를 하지 않아 기존 정상 페이지가 유지됩니다.
- 화면에는 마지막 정상 생성 시각과 모든 원본 지표의 마지막 관측일을 표시합니다.
- 마지막 생성 후 36시간이 지나면 웹페이지에 갱신 지연 표시가 나타납니다. 이는 작업 실행의 신선도를 확인하는 기능이며 월간·주간 데이터 자체가 최신임을 보장하는 검사는 아닙니다.
- 일본 단기금리 보조지표가 없으면 기존 계산의 선택 지표 처리는 유지하고, 엔캐리 카드에서 자료 불완전을 표시합니다.
- GitHub 예약 실행은 정시에 시작된다는 보장이 없으며, 공개 저장소에 60일 동안 활동이 없으면 예약 실행이 비활성화될 수 있습니다. 비활성화 시 Actions에서 다시 활성화하고 실행합니다.

## 로컬 실행

Python 3.12 권장:

```bash
python -m pip install -r requirements.txt
python build.py
```

생성된 `public/index.html`을 브라우저로 열 수 있습니다. 인터넷 연결이 필요합니다. 실행 도중 오류가 나면 모의 데이터로 대체하지 않습니다.

## 구성

- `calculate.py`: 원본 1~21번 지표 계산 (데이터 다운로드 연결 부분만 변경)
- `fred_source.py`: FRED CSV 다운로드, 재시도, 기본 구조 확인
- `dashboard.py`: 카드형 대시보드와 점수 검산
- `detail_output.py`: 원본 세부 출력
- `build.py`: HTML 생성, 생성 시각·관측일 표시
- `.github/workflows/publish.yml`: 예약 실행과 Pages 배포

이 코드의 점수·임계값은 원본 사용자 모델이며, 계산 방법론을 새로 검증하거나 변경한 것이 아닙니다. 서로 다른 주기의 최신 관측값과 과거 비교 방식도 원본 기준입니다.

공식 설정 자료:
- https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages
- https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows
