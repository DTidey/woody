from __future__ import annotations

from collections.abc import Iterator
from uuid import uuid4

from app.db.session import get_db_session
from app.main import app
from fastapi.testclient import TestClient


class _FakeScalarResult:
    def __init__(self, items: list[object]) -> None:
        self._items = items

    def __iter__(self):
        return iter(self._items)


class _FakeExecuteResult:
    def __init__(self, items: list[object]) -> None:
        self._items = items

    def __iter__(self):
        return iter(self._items)


class _FakeSession:
    def __init__(self) -> None:
        self.last_scalar_query = None

    def scalars(self, _query) -> _FakeScalarResult:
        self.last_scalar_query = _query
        return _FakeScalarResult(
            [
                type(
                    "CandleRow",
                    (),
                    {
                        "id": uuid4(),
                        "timestamp": 1710000000,
                        "open": 100.0,
                        "close": 101.5,
                        "high": 103.0,
                        "low": 99.5,
                        "volume": 2500.0,
                        "exchange": "binance",
                        "symbol": "BTC-USDT",
                        "timeframe": "1h",
                    },
                )()
            ]
        )

    def execute(self, _query) -> _FakeExecuteResult:
        return _FakeExecuteResult(
            [
                type(
                    "SeriesRow",
                    (),
                    {
                        "exchange": "binance",
                        "symbol": "BTC-USDT",
                        "timeframe": "1h",
                        "latest_timestamp": 1710000000,
                    },
                )(),
                type(
                    "SeriesRow",
                    (),
                    {
                        "exchange": "coinbase",
                        "symbol": "BTC-USDT",
                        "timeframe": "1h",
                        "latest_timestamp": 1710000000,
                    },
                )(),
                type(
                    "SeriesRow",
                    (),
                    {
                        "exchange": "binance",
                        "symbol": "ETH-USDT",
                        "timeframe": "4h",
                        "latest_timestamp": 1709990000,
                    },
                )(),
            ]
        )

    def close(self) -> None:
        return None


def _override_db_session() -> Iterator[_FakeSession]:
    yield _FakeSession()


def test_list_candles_returns_rows() -> None:
    fake_session = _FakeSession()

    def _override_single_session() -> Iterator[_FakeSession]:
        yield fake_session

    app.dependency_overrides[get_db_session] = _override_single_session
    client = TestClient(app)

    response = client.get("/api/candles?limit=1&exchange=binance&symbol=BTC-USDT&timeframe=1h")

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert "candle.exchange" in str(fake_session.last_scalar_query)
    assert response.json()[0]["symbol"] == "BTC-USDT"
    assert response.json()[0]["timeframe"] == "1h"
    assert response.json()[0]["exchange"] == "binance"


def test_list_candle_series_returns_distinct_pairs() -> None:
    app.dependency_overrides[get_db_session] = _override_db_session
    client = TestClient(app)

    response = client.get("/api/candles/series")

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == [
        {
            "exchange": "binance",
            "symbol": "BTC-USDT",
            "timeframe": "1h",
            "latest_timestamp": 1710000000,
        },
        {
            "exchange": "coinbase",
            "symbol": "BTC-USDT",
            "timeframe": "1h",
            "latest_timestamp": 1710000000,
        },
        {
            "exchange": "binance",
            "symbol": "ETH-USDT",
            "timeframe": "4h",
            "latest_timestamp": 1709990000,
        },
    ]
