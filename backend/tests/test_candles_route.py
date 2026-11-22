from __future__ import annotations

from collections.abc import Iterator

import pytest
from app.api.routes import candles as candles_route
from app.db.session import get_db_session
from app.main import app
from app.services.candles import CandleRecord, UnsupportedTimeframeError
from fastapi.testclient import TestClient
from sqlalchemy.dialects.postgresql import psycopg

FROZEN_NOW_MS = 1_763_800_000_000
SEVEN_DAYS_MS = 7 * 24 * 60 * 60 * 1000


@pytest.fixture(autouse=True)
def _reset_series_cache() -> Iterator[None]:
    candles_route._clear_series_cache()
    yield
    candles_route._clear_series_cache()
    app.dependency_overrides.clear()


class _FakeExecuteResult:
    def __init__(self, items: list[object]) -> None:
        self._items = items

    def __iter__(self):
        return iter(self._items)


class _FakeSession:
    def __init__(self) -> None:
        self.queries: list[object] = []

    def execute(self, query) -> _FakeExecuteResult:
        self.queries.append(query)
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


class _FailingSession:
    def __init__(self) -> None:
        self.calls = 0

    def execute(self, _query) -> _FakeExecuteResult:
        self.calls += 1
        raise RuntimeError("canceling statement due to statement timeout")

    def close(self) -> None:
        return None


def _use_session(session: object) -> None:
    def _override() -> Iterator[object]:
        yield session

    app.dependency_overrides[get_db_session] = _override


def _set_clocks(monkeypatch, monotonic_value: list[float]) -> None:
    monkeypatch.setattr(candles_route, "_now_ms", lambda: FROZEN_NOW_MS)
    monkeypatch.setattr(candles_route, "_monotonic", lambda: monotonic_value[0])


def test_list_candle_series_renders_lookback_bound_as_integer_literal(monkeypatch) -> None:
    _set_clocks(monkeypatch, [1000.0])
    session = _FakeSession()
    _use_session(session)

    response = TestClient(app).get("/api/candles/series")

    assert response.status_code == 200
    assert candles_route.SERIES_LOOKBACK_MS == SEVEN_DAYS_MS
    assert len(session.queries) == 1
    sql = str(
        session.queries[0].compile(
            dialect=psycopg.dialect(),
            compile_kwargs={"render_postcompile": True},
        )
    )
    expected_bound = FROZEN_NOW_MS - SEVEN_DAYS_MS
    assert f"c.timestamp >= {expected_bound}" in sql
    assert "%(since_ms)s" not in sql
    assert "max(c.timestamp) AS latest_timestamp" in sql
    assert "ORDER BY latest_timestamp DESC, c.exchange, c.symbol, c.timeframe" in sql
    assert "RECURSIVE" not in sql


def test_list_candle_series_cache_hit_within_ttl(monkeypatch) -> None:
    clock = [1000.0]
    _set_clocks(monkeypatch, clock)
    session = _FakeSession()
    _use_session(session)
    client = TestClient(app)

    first = client.get("/api/candles/series")
    clock[0] += candles_route.SERIES_CACHE_TTL_SECONDS - 1
    second = client.get("/api/candles/series")

    assert first.status_code == second.status_code == 200
    assert second.json() == first.json()
    assert len(session.queries) == 1


def test_list_candle_series_cache_expires_after_ttl(monkeypatch) -> None:
    clock = [1000.0]
    _set_clocks(monkeypatch, clock)
    session = _FakeSession()
    _use_session(session)
    client = TestClient(app)

    client.get("/api/candles/series")
    clock[0] += candles_route.SERIES_CACHE_TTL_SECONDS
    response = client.get("/api/candles/series")

    assert response.status_code == 200
    assert len(session.queries) == 2


def test_list_candle_series_does_not_cache_errors(monkeypatch) -> None:
    _set_clocks(monkeypatch, [1000.0])
    failing = _FailingSession()
    _use_session(failing)
    client = TestClient(app, raise_server_exceptions=False)

    first = client.get("/api/candles/series")
    second = client.get("/api/candles/series")

    assert first.status_code == second.status_code == 500
    assert failing.calls == 2

    session = _FakeSession()
    _use_session(session)
    recovered = client.get("/api/candles/series")

    assert recovered.status_code == 200
    assert len(recovered.json()) == 3
    assert len(session.queries) == 1
