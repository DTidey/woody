from __future__ import annotations

from collections.abc import Iterator

from app.db.session import get_db_session
from app.main import app
from app.services.candles import CandleRecord, UnsupportedTimeframeError
from fastapi.testclient import TestClient


class _FakeExecuteResult:
    def __init__(self, items: list[object]) -> None:
        self._items = items

    def __iter__(self):
        return iter(self._items)


class _FakeSession:
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
                        "latest_timestamp": 1710000000000,
                    },
                )(),
                type(
                    "SeriesRow",
                    (),
                    {
                        "exchange": "coinbase",
                        "symbol": "BTC-USDT",
                        "timeframe": "1h",
                        "latest_timestamp": 1710000000000,
                    },
                )(),
                type(
                    "SeriesRow",
                    (),
                    {
                        "exchange": "binance",
                        "symbol": "ETH-USDT",
                        "timeframe": "4h",
                        "latest_timestamp": 1709990000000,
                    },
                )(),
            ]
        )

    def close(self) -> None:
        return None


def _override_db_session() -> Iterator[_FakeSession]:
    yield _FakeSession()


def test_list_candles_returns_locally_aggregated_rows(monkeypatch) -> None:
    def _override_single_session() -> Iterator[_FakeSession]:
        yield _FakeSession()

    def _fake_list_candles_from_store(**kwargs) -> list[CandleRecord]:
        assert kwargs["exchange"] == "binance"
        assert kwargs["symbol"] == "BTC-USDT"
        assert kwargs["timeframe"] == "1h"
        assert kwargs["limit"] == 1
        return [
            CandleRecord(
                id=None,
                timestamp=1710000000000,
                open=100.0,
                close=101.5,
                high=103.0,
                low=99.5,
                volume=2500.0,
                exchange="binance",
                symbol="BTC-USDT",
                timeframe="1h",
            )
        ]

    monkeypatch.setattr(
        "app.api.routes.candles.list_candles_from_store",
        _fake_list_candles_from_store,
    )
    app.dependency_overrides[get_db_session] = _override_single_session
    client = TestClient(app)

    response = client.get("/api/candles?limit=1&exchange=binance&symbol=BTC-USDT&timeframe=1h")

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": None,
            "timestamp": 1710000000000,
            "open": 100.0,
            "close": 101.5,
            "high": 103.0,
            "low": 99.5,
            "volume": 2500.0,
            "exchange": "binance",
            "symbol": "BTC-USDT",
            "timeframe": "1h",
        }
    ]


def test_list_candles_requires_series_filters() -> None:
    client = TestClient(app)

    response = client.get("/api/candles?limit=1")

    assert response.status_code == 422


def test_list_candles_rejects_unsupported_timeframe(monkeypatch) -> None:
    def _fake_list_candles_from_store(**_kwargs) -> list[CandleRecord]:
        raise UnsupportedTimeframeError("Unsupported timeframe: 2x")

    monkeypatch.setattr(
        "app.api.routes.candles.list_candles_from_store",
        _fake_list_candles_from_store,
    )
    client = TestClient(app)

    response = client.get("/api/candles?limit=1&exchange=binance&symbol=BTC-USDT&timeframe=2x")

    assert response.status_code == 400
    assert response.json() == {"detail": "Unsupported timeframe: 2x"}


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
            "latest_timestamp": 1710000000000,
        },
        {
            "exchange": "coinbase",
            "symbol": "BTC-USDT",
            "timeframe": "1h",
            "latest_timestamp": 1710000000000,
        },
        {
            "exchange": "binance",
            "symbol": "ETH-USDT",
            "timeframe": "4h",
            "latest_timestamp": 1709990000000,
        },
    ]
