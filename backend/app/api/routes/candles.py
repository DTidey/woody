from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy import text
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


def _load_candle_series(db: Session) -> list[CandleSeriesResponse]:
    # The obvious DISTINCT ON query times out on the live candle table because it scans and
    # sorts across the full history. This recursive/index-jump form enumerates one series key
    # at a time from the existing unique index, then looks up the latest timestamp per series.
    query = text(
        """
        WITH RECURSIVE series_keys AS (
            (
                SELECT c.exchange, c.symbol, c.timeframe
                FROM public.candle c
                ORDER BY c.exchange, c.symbol, c.timeframe
                LIMIT 1
            )
            UNION ALL
            SELECT next_key.exchange, next_key.symbol, next_key.timeframe
            FROM series_keys current_key
            CROSS JOIN LATERAL (
                SELECT c.exchange, c.symbol, c.timeframe
                FROM public.candle c
                WHERE (c.exchange, c.symbol, c.timeframe) > (
                    current_key.exchange,
                    current_key.symbol,
                    current_key.timeframe
                )
                ORDER BY c.exchange, c.symbol, c.timeframe
                LIMIT 1
            ) next_key
        )
        SELECT
            series_keys.exchange,
            series_keys.symbol,
            series_keys.timeframe,
            latest.latest_timestamp
        FROM series_keys
        CROSS JOIN LATERAL (
            SELECT c.timestamp AS latest_timestamp
            FROM public.candle c
            WHERE c.exchange = series_keys.exchange
              AND c.symbol = series_keys.symbol
              AND c.timeframe = series_keys.timeframe
            ORDER BY c.timestamp DESC
            LIMIT 1
        ) latest
        ORDER BY
        
            latest.latest_timestamp DESC,
            series_keys.exchange,
            series_keys.symbol,
            series_keys.timeframe
        """
    )
    return [
        CandleSeriesResponse(
            exchange=row.exchange,
            symbol=row.symbol,
            timeframe=row.timeframe,
            latest_timestamp=row.latest_timestamp,
        )
        for row in db.execute(query)
    ]


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
