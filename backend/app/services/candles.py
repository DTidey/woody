from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.candle import Candle

_TIMEFRAME_MINUTES = {
    "1m": 1,
    "3m": 3,
    "5m": 5,
    "15m": 15,
    "30m": 30,
    "45m": 45,
    "1h": 60,
    "2h": 120,
    "3h": 180,
    "4h": 240,
    "6h": 360,
    "8h": 480,
    "12h": 720,
    "1d": 1440,
    "1D": 1440,
    "1w": 10080,
    "1W": 10080,
}


class CandleServiceError(RuntimeError):
    pass


class UnsupportedTimeframeError(CandleServiceError):
    pass


@dataclass(frozen=True, slots=True)
class CandleRecord:
    id: object | None
    timestamp: int
    open: float
    close: float
    high: float
    low: float
    volume: float
    exchange: str
    symbol: str
    timeframe: str


def list_candles(
    *,
    db: Session,
    exchange: str,
    symbol: str,
    timeframe: str,
    limit: int,
) -> list[CandleRecord]:
    timeframe_minutes = _timeframe_minutes(timeframe)
    source_candles = _load_source_candles(
        db=db,
        exchange=exchange,
        symbol=symbol,
        limit=_source_limit(limit=limit, timeframe_minutes=timeframe_minutes),
    )

    if timeframe_minutes == 1:
        return _normalize_one_minute_candles(source_candles[-limit:], timeframe=timeframe)

    return _aggregate_candles(
        candles=source_candles,
        exchange=exchange,
        symbol=symbol,
        timeframe=timeframe,
        timeframe_minutes=timeframe_minutes,
        limit=limit,
    )


def _timeframe_minutes(timeframe: str) -> int:
    minutes = _TIMEFRAME_MINUTES.get(timeframe)
    if minutes is None:
        raise UnsupportedTimeframeError(f"Unsupported timeframe: {timeframe}")
    return minutes


def _source_limit(*, limit: int, timeframe_minutes: int) -> int:
    if timeframe_minutes == 1:
        return limit
    return limit * timeframe_minutes + timeframe_minutes


def _load_source_candles(
    *,
    db: Session,
    exchange: str,
    symbol: str,
    limit: int,
) -> list[Candle]:
    query = (
        select(Candle)
        .where(
            Candle.exchange == exchange,
            Candle.symbol == symbol,
            Candle.timeframe == "1m",
        )
        .order_by(Candle.timestamp.desc())
        .limit(limit)
    )
    rows = list(db.scalars(query))
    rows.reverse()
    return rows


def _normalize_one_minute_candles(
    candles: Iterable[Candle], *, timeframe: str
) -> list[CandleRecord]:
    normalized = [
        CandleRecord(
            id=candle.id,
            timestamp=int(candle.timestamp),
            open=float(candle.open),
            close=float(candle.close),
            high=float(candle.high),
            low=float(candle.low),
            volume=float(candle.volume),
            exchange=candle.exchange,
            symbol=candle.symbol,
            timeframe=timeframe,
        )
        for candle in candles
    ]
    normalized.sort(key=lambda candle: candle.timestamp, reverse=True)
    return normalized


def _aggregate_candles(
    *,
    candles: Iterable[Candle],
    exchange: str,
    symbol: str,
    timeframe: str,
    timeframe_minutes: int,
    limit: int,
) -> list[CandleRecord]:
    timeframe_milliseconds = timeframe_minutes * 60_000
    expected_rows_per_bucket = timeframe_minutes
    buckets: dict[int, list[Candle]] = {}

    for candle in candles:
        bucket_timestamp = int(candle.timestamp) - (int(candle.timestamp) % timeframe_milliseconds)
        buckets.setdefault(bucket_timestamp, []).append(candle)

    aggregated: list[CandleRecord] = []
    for bucket_timestamp, bucket_rows in buckets.items():
        if len(bucket_rows) != expected_rows_per_bucket:
            continue

        first_row = bucket_rows[0]
        last_row = bucket_rows[-1]
        aggregated.append(
            CandleRecord(
                id=None,
                timestamp=bucket_timestamp,
                open=float(first_row.open),
                close=float(last_row.close),
                high=max(float(row.high) for row in bucket_rows),
                low=min(float(row.low) for row in bucket_rows),
                volume=sum(float(row.volume) for row in bucket_rows),
                exchange=exchange,
                symbol=symbol,
                timeframe=timeframe,
            )
        )

    aggregated.sort(key=lambda candle: candle.timestamp, reverse=True)
    return aggregated[:limit]
