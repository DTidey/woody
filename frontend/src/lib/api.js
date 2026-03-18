const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api";

export async function fetchCandleSeriesOptions() {
  const response = await fetch(`${apiBaseUrl}/candles/series`);

  if (!response.ok) {
    throw new Error(`Unable to load candle series: ${response.status}`);
  }

  return response.json();
}

export async function fetchCandles({ exchange, limit = 200, symbol, timeframe }) {
  const params = new URLSearchParams({ limit: String(limit) });

  if (exchange) {
    params.set("exchange", exchange);
  }
  if (symbol) {
    params.set("symbol", symbol);
  }
  if (timeframe) {
    params.set("timeframe", timeframe);
  }

  const response = await fetch(`${apiBaseUrl}/candles?${params.toString()}`);

  if (!response.ok) {
    throw new Error(`Unable to load candles: ${response.status}`);
  }

  return response.json();
}

export { apiBaseUrl };
