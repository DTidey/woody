function normalizeTime(timestamp) {
  if (!Number.isFinite(timestamp)) {
    return null;
  }

  if (timestamp > 1_000_000_000_000_000_000) {
    return Math.floor(timestamp / 1_000_000_000);
  }

  if (timestamp > 1_000_000_000_000_000) {
    return Math.floor(timestamp / 1_000_000);
  }

  if (timestamp > 1_000_000_000_000) {
    return Math.floor(timestamp / 1_000);
  }

  return Math.floor(timestamp);
}

function toFiniteNumber(value) {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : null;
}

export function buildChartSeries(candles) {
  if (!Array.isArray(candles) || candles.length === 0) {
    return {
      data: [],
      droppedRows: 0,
      selectedExchange: null,
      selectedSymbol: null,
      selectedTimeframe: null,
      totalRows: 0,
    };
  }

  const selectedExchange = candles[0]?.exchange ?? null;
  const selectedSymbol = candles[0]?.symbol ?? null;
  const selectedTimeframe = candles[0]?.timeframe ?? null;
  const filtered = candles.filter(
    (candle) =>
      candle?.exchange === selectedExchange &&
      candle?.symbol === selectedSymbol && candle?.timeframe === selectedTimeframe,
  );
  const dedupedByTime = new Map();

  for (const candle of filtered) {
    const time = normalizeTime(toFiniteNumber(candle?.timestamp));
    const open = toFiniteNumber(candle?.open);
    const high = toFiniteNumber(candle?.high);
    const low = toFiniteNumber(candle?.low);
    const close = toFiniteNumber(candle?.close);
    const volume = toFiniteNumber(candle?.volume);

    if ([time, open, high, low, close, volume].some((value) => value === null)) {
      continue;
    }

    if (high < Math.max(open, close) || low > Math.min(open, close) || low > high) {
      continue;
    }

    dedupedByTime.set(time, { time, open, high, low, close, volume });
  }

  const data = [...dedupedByTime.values()].sort((left, right) => left.time - right.time);

  return {
    data,
    droppedRows: candles.length - data.length,
    selectedExchange,
    selectedSymbol,
    selectedTimeframe,
    totalRows: candles.length,
  };
}
