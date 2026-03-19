from __future__ import annotations

from types import SimpleNamespace

from app.services.candles import _aggregate_candles, _source_limit, list_candles


class _FakeSession:
    def __init__(self, candles: list[object]) -> None:
        self._candles = candles

    def scalars(self, _query):
        return iter(self._candles)


def _one_minute_candle(
    timestamp: int,
    *,
    open: float,
    close: float,
    high: float,
    low: float,
    volume: float,
):
    return SimpleNamespace(
        id=f"c-{timestamp}",
        timestamp=timestamp,
        open=open,
        close=close,
        high=high,
        low=low,
        volume=volume,
        exchange="binance",
        symbol="BTC-USDT",
        timeframe="1m",
    )


def test_source_limit_adds_one_bucket_of_padding_for_higher_timeframes() -> None:
    assert _source_limit(limit=200, timeframe_minutes=60) == 12_060
    assert _source_limit(limit=200, timeframe_minutes=1) == 200


def test_aggregate_candles_builds_complete_bucket_and_drops_partial_one() -> None:
    candles = [
        _one_minute_candle(1_710_000_000_000, open=100, close=101, high=101, low=99, volume=1),
        _one_minute_candle(1_710_000_060_000, open=101, close=102, high=103, low=100, volume=2),
        _one_minute_candle(1_710_000_120_000, open=102, close=103, high=104, low=101, volume=3),
        _one_minute_candle(1_710_000_180_000, open=103, close=104, high=105, low=102, volume=4),
        _one_minute_candle(1_710_000_240_000, open=104, close=105, high=106, low=103, volume=5),
        _one_minute_candle(1_710_000_300_000, open=105, close=106, high=107, low=104, volume=6),
        _one_minute_candle(1_710_000_360_000, open=106, close=107, high=108, low=105, volume=7),
        _one_minute_candle(1_710_000_420_000, open=107, close=108, high=109, low=106, volume=8),
    ]

    result = _aggregate_candles(
        candles=candles,
        exchange="binance",
        symbol="BTC-USDT",
        timeframe="5m",
        timeframe_minutes=5,
        limit=2,
    )

    assert len(result) == 1
    assert result[0].timestamp == 1_710_000_000_000
    assert result[0].open == 100.0
    assert result[0].close == 105.0
    assert result[0].high == 106.0
    assert result[0].low == 99.0
    assert result[0].volume == 15.0
    assert result[0].id is None


def test_list_candles_returns_one_minute_rows_newest_first() -> None:
    result = list_candles(
        db=_FakeSession(
            candles=[
                _one_minute_candle(
                    1_710_000_120_000, open=102, close=103, high=104, low=101, volume=3
                ),
                _one_minute_candle(
                    1_710_000_060_000, open=101, close=102, high=103, low=100, volume=2
                ),
                _one_minute_candle(
                    1_710_000_000_000, open=100, close=101, high=101, low=99, volume=1
                ),
            ]
        ),
        exchange="binance",
        symbol="BTC-USDT",
        timeframe="1m",
        limit=2,
    )

    assert [candle.timestamp for candle in result] == [1_710_000_120_000, 1_710_000_060_000]
    assert result[0].id == "c-1710000120000"


def test_list_candles_aggregates_one_minute_rows_into_requested_timeframe() -> None:
    result = list_candles(
        db=_FakeSession(
            candles=[
                _one_minute_candle(
                    1_710_000_240_000, open=104, close=105, high=106, low=103, volume=5
                ),
                _one_minute_candle(
                    1_710_000_180_000, open=103, close=104, high=105, low=102, volume=4
                ),
                _one_minute_candle(
                    1_710_000_120_000, open=102, close=103, high=104, low=101, volume=3
                ),
                _one_minute_candle(
                    1_710_000_060_000, open=101, close=102, high=103, low=100, volume=2
                ),
                _one_minute_candle(
                    1_710_000_000_000, open=100, close=101, high=101, low=99, volume=1
                ),
            ]
        ),
        exchange="binance",
        symbol="BTC-USDT",
        timeframe="5m",
        limit=1,
    )

    assert len(result) == 1
    assert result[0].timestamp == 1_710_000_000_000
    assert result[0].timeframe == "5m"


def test_list_candles_returns_empty_when_no_one_minute_history() -> None:
    result = list_candles(
        db=_FakeSession(candles=[]),
        exchange="binance",
        symbol="BTC-USDT",
        timeframe="1h",
        limit=5,
    )

    assert result == []
