"""FRED public CSV; no API key required. Failures are never replaced by sample data."""
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.request import Request, urlopen
from urllib.parse import urlencode
from urllib.error import URLError
from io import BytesIO
import time
import pandas as pd


def fetch_series(code, start):
    url = 'https://fred.stlouisfed.org/graph/fredgraph.csv?' + urlencode({'id':code, 'cosd':start})
    error = None
    for attempt in range(3):
        try:
            # 일반 윈도우 크롬 브라우저에서 접속하는 것처럼 User-Agent를 길게 변경합니다.
            request = Request(url, headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'})
            with urlopen(request, timeout=35) as response:
                data = pd.read_csv(BytesIO(response.read()), na_values=['.'])
            if code not in data or len(data.columns) < 2:
                raise ValueError(f'{code}: unexpected CSV columns')
            dates = pd.to_datetime(data.iloc[:,0], errors='raise')
            values = pd.to_numeric(data[code], errors='coerce')
            result = pd.Series(values.to_numpy(), index=dates, name=code).sort_index()
            result = result.loc[result.index >= pd.Timestamp(start)]
            if result.dropna().empty:
                raise ValueError(f'{code}: no numeric observations')
            if result.index.has_duplicates:
                raise ValueError(f'{code}: duplicate dates')
            return result
        except (URLError, TimeoutError, ValueError, OSError) as exc:
            error = exc
            if attempt < 2:
                time.sleep(attempt + 1)
    raise RuntimeError(f'{code} download failed: {error}')


def download_series(series, start):
    downloaded = {}
    # 한 번에 1개씩만 안전하게 다운로드하도록 변경합니다.
    with ThreadPoolExecutor(max_workers=1) as pool:
        pending = {pool.submit(fetch_series, code, start):name for name,code in series.items()}
        for task in as_completed(pending):
            name = pending[task]
            try:
                downloaded[name] = task.result()
                print(f'{name}: {len(downloaded[name].dropna())} observations', flush=True)
            except Exception as exc:
                print(f'{name}: {exc}', flush=True)
    # Required/optional series are checked by the original calculation code.
    if not downloaded:
        raise RuntimeError('No FRED series could be downloaded. Publication stopped.')
    return {name:downloaded[name] for name in series if name in downloaded}
