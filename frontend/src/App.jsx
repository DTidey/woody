import { useEffect, useState } from "react";
import { useQuery } from "@tanstack/react-query";

import CandleChart from "./components/CandleChart";
import { buildChartSeries } from "./lib/candles";
import { fetchCandles, fetchCandleSeriesOptions } from "./lib/api";

const SUPPORTED_TIMEFRAMES = [
  "1m",
  "3m",
  "5m",
  "15m",
  "30m",
  "45m",
  "1h",
  "2h",
  "3h",
  "4h",
  "6h",
  "8h",
  "12h",
  "1d",
  "1w",
];

export default function App() {
  const [selectedExchange, setSelectedExchange] = useState("");
  const [selectedSymbol, setSelectedSymbol] = useState("");
  const [selectedTimeframe, setSelectedTimeframe] = useState("");

  const {
    data: seriesOptionsData,
    error: seriesError,
    isLoading: isSeriesLoading,
  } = useQuery({
    queryKey: ["candle-series-options"],
    queryFn: fetchCandleSeriesOptions,
  });

  const seriesOptions = seriesOptionsData ?? [];
  const availableExchanges = [...new Set(seriesOptions.map((series) => series.exchange))];
  const exchangeSeries = seriesOptions.filter((series) => series.exchange === selectedExchange);
  const availableSymbols = [...new Set(exchangeSeries.map((series) => series.symbol))].sort(
    (left, right) => left.localeCompare(right),
  );
  const availableTimeframes =
    selectedExchange && selectedSymbol ? SUPPORTED_TIMEFRAMES : [];

  useEffect(() => {
    if (seriesOptions.length === 0) {
      setSelectedExchange("");
      setSelectedSymbol("");
      setSelectedTimeframe("");
      return;
    }

    if (
      !selectedExchange ||
      !seriesOptions.some((series) => series.exchange === selectedExchange)
    ) {
      setSelectedExchange(seriesOptions[0].exchange);
      setSelectedSymbol(seriesOptions[0].symbol);
      setSelectedTimeframe("1m");
      return;
    }

    const matchingExchangeSeries = seriesOptions.filter(
      (series) => series.exchange === selectedExchange,
    );

    if (
      !selectedSymbol ||
      !matchingExchangeSeries.some((series) => series.symbol === selectedSymbol)
    ) {
      const nextSymbol = [...new Set(matchingExchangeSeries.map((series) => series.symbol))].sort(
        (left, right) => left.localeCompare(right),
      )[0];
      setSelectedSymbol(nextSymbol ?? "");
      setSelectedTimeframe("1m");
      return;
    }

    if (!SUPPORTED_TIMEFRAMES.includes(selectedTimeframe)) {
      setSelectedTimeframe("1m");
    }
  }, [selectedExchange, selectedSymbol, selectedTimeframe, seriesOptions]);

  const {
    data,
    error,
    isLoading,
  } = useQuery({
    queryKey: [
      "candles",
      {
        exchange: selectedExchange,
        limit: 200,
        symbol: selectedSymbol,
        timeframe: selectedTimeframe,
      },
    ],
    queryFn: () =>
      fetchCandles({
        exchange: selectedExchange,
        limit: 200,
        symbol: selectedSymbol,
        timeframe: selectedTimeframe,
      }),
    enabled: Boolean(selectedExchange && selectedSymbol && selectedTimeframe),
  });

  const candles = data ?? [];
  const chartSeries = buildChartSeries(candles);
  const hasNoSeries = !isSeriesLoading && !seriesError && seriesOptions.length === 0;

  return (
    <main className="app-shell">
      <section className="dashboard">
        <div className="headline">
          <h1>woody</h1>
          <p className="lede">Choose a market, pick a timeframe, and chart the candles.</p>
        </div>

        <section className="controls-panel">
          <div className="panel-header">
            <div>
              <p className="panel-kicker">Series selection</p>
              <h2>Choose what to chart</h2>
            </div>
            {isSeriesLoading ? <span className="status-chip">Loading series...</span> : null}
            {seriesError ? <span className="status-chip error">Series error</span> : null}
          </div>

          {seriesError ? (
            <div className="panel-message">
              <p>The frontend could not load available candle series.</p>
              <code>{seriesError.message}</code>
            </div>
          ) : hasNoSeries ? (
            <div className="panel-message">
              <p>No candle series are available yet.</p>
            </div>
          ) : (
            <div className="series-controls">
              <label className="field">
                <span className="field-label">Exchange</span>
                <select
                  value={selectedExchange}
                  onChange={(event) => {
                    const nextExchange = event.target.value;
                    const nextSymbol = [
                      ...new Set(
                        seriesOptions
                          .filter((series) => series.exchange === nextExchange)
                          .map((series) => series.symbol),
                      ),
                    ].sort((left, right) => left.localeCompare(right))[0];

                    setSelectedExchange(nextExchange);
                    setSelectedSymbol(nextSymbol ?? "");
                    setSelectedTimeframe("1m");
                  }}
                >
                  {availableExchanges.map((exchange) => (
                    <option key={exchange} value={exchange}>
                      {exchange}
                    </option>
                  ))}
                </select>
              </label>

              <label className="field">
                <span className="field-label">Symbol</span>
                <select
                  value={selectedSymbol}
                  onChange={(event) => {
                    setSelectedSymbol(event.target.value);
                    setSelectedTimeframe("1m");
                  }}
                >
                  {availableSymbols.map((symbol) => (
                    <option key={symbol} value={symbol}>
                      {symbol}
                    </option>
                  ))}
                </select>
              </label>

              <label className="field">
                <span className="field-label">Timeframe</span>
                <select
                  value={selectedTimeframe}
                  onChange={(event) => setSelectedTimeframe(event.target.value)}
                >
                  {availableTimeframes.map((timeframe) => (
                    <option key={timeframe} value={timeframe}>
                      {timeframe}
                    </option>
                  ))}
                </select>
              </label>
            </div>
          )}
        </section>

        <section className="chart-panel">
          <div className="panel-header">
            <div>
              <p className="panel-kicker">Market view</p>
              <h2>Recent candles</h2>
            </div>
            {isLoading ? <span className="status-chip">Loading...</span> : null}
            {error ? <span className="status-chip error">API error</span> : null}
          </div>

          {hasNoSeries ? (
            <div className="panel-message">
              <p>Selectable candle series will appear here once data is available.</p>
            </div>
          ) : error ? (
            <div className="panel-message">
              <p>The frontend could not load candle data from the API.</p>
              <code>{error.message}</code>
            </div>
          ) : (
            <CandleChart candles={chartSeries.data} />
          )}
        </section>
      </section>
    </main>
  );
}
