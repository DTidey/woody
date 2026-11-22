from __future__ import annotations

import threading
import time
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy import BigInteger, bindparam, text
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.services import CandleServiceError, UnsupportedTimeframeError
from app.services import list_candles as list_candles_from_store

router = APIRouter(prefix="/candles")
DbSession = Annotated[Session, Depends(get_db_session)]


class CandleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID | None
    timestamp: int
    open: float
    close: float
    high: float
    low: float
    volume: float
    exchange: str
    symbol: str
    timeframe: str


class CandleSeriesResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    exchange: str
    symbol: str
    timeframe: str
    latest_timestamp: int


# Production `public.candle` is a TimescaleDB hypertable with hundreds of weekly chunks, almost
# all compressed. Any query that walks the full history (DISTINCT ON, recursive index-jump)
# touches every chunk and exceeds the read-only role's statement timeout. Restricting to a recent
# window lets the planner exclude all but the newest chunks. Series without candles in the window
# (delisted symbols, stopped imports) are therefore not listed; /api/candles still serves them.
# 7 days so stock series survive weekends/holidays and a missed nightly import.
SERIES_LOOKBACK_MS = 7 * 24 * 60 * 60 * 1000
SERIES_CACHE_TTL_SECONDS = 600.0

# `since_ms` is rendered inline as an integer literal (literal_execute) rather than sent as a
# server-side bind parameter: with a bind parameter, psycopg's auto-prepared generic plan only
# gets runtime chunk exclusion (~1 s planning + ~3.4 s execution) instead of plan-time exclusion.
# The value is always an int computed from the server clock, never request input.
_SERIES_QUERY = text(
    """
    SELECT c.exchange, c.symbol, c.timeframe, max(c.timestamp) AS latest_timestamp
    FROM public.candle c
    WHERE c.timestamp >= :since_ms
    GROUP BY c.exchange, c.symbol, c.timeframe
    ORDER BY latest_timestamp DESC, c.exchange, c.symbol, c.timeframe
    """
).bindparams(bindparam("since_ms", type_=BigInteger, literal_execute=True))

# Successful results (including an empty list) are cached per process. The lock is held while
# querying so concurrent cold requests share one query. Exceptions are never cached.
_series_cache_lock = threading.Lock()
_series_cache: tuple[float, list[CandleSeriesResponse]] | None = None


def _now_ms() -> int:
    return time.time_ns() // 1_000_000


def _monotonic() -> float:
    return time.monotonic()


def _clear_series_cache() -> None:
    global _series_cache
    with _series_cache_lock:
        _series_cache = None


def _query_candle_series(db: Session) -> list[CandleSeriesResponse]:
    since_ms = int(_now_ms() - SERIES_LOOKBACK_MS)
    query = _SERIES_QUERY.bindparams(since_ms=since_ms)
    return [
        CandleSeriesResponse(
            exchange=row.exchange,
            symbol=row.symbol,
            timeframe=row.timeframe,
            latest_timestamp=row.latest_timestamp,
        )
        for row in db.execute(query)
    ]


def _load_candle_series(db: Session) -> list[CandleSeriesResponse]:
    global _series_cache
    with _series_cache_lock:
        now = _monotonic()
        if _series_cache is not None and now - _series_cache[0] < SERIES_CACHE_TTL_SECONDS:
            return list(_series_cache[1])
        series = _query_candle_series(db)
        _series_cache = (now, series)
        return list(series)


@router.get("", response_model=list[CandleResponse])
def list_candles(
    limit: int = Query(default=20, ge=1, le=500),
    exchange: str = Query(...),
    symbol: str = Query(...),
    timeframe: str = Query(...),
    db: DbSession = None,
) -> list[CandleResponse]:
    try:
        return list_candles_from_store(
            db=db,
            exchange=exchange,
            symbol=symbol,
            timeframe=timeframe,
            limit=limit,
        )
    except UnsupportedTimeframeError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except CandleServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc


@router.get("/series", response_model=list[CandleSeriesResponse])
def list_candle_series(db: DbSession = None) -> list[CandleSeriesResponse]:
    return _load_candle_series(db)
