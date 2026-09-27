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
            request = Request(url, headers={'User-Agent':'LiquidityMonitor/1.0'})
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
    with ThreadPoolExecutor(max_workers=4) as pool:
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
