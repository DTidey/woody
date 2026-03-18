import { useEffect, useState } from "react";
import { useQuery } from "@tanstack/react-query";

import CandleChart from "./components/CandleChart";
import { buildChartSeries } from "./lib/candles";
import { apiBaseUrl, fetchCandles, fetchCandleSeriesOptions } from "./lib/api";

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
  const availableSymbols = [...new Set(exchangeSeries.map((series) => series.symbol))];
  const timeframesForSymbol = seriesOptions
    .filter(
      (series) =>
        series.exchange === selectedExchange && series.symbol === selectedSymbol,
    )
    .map((series) => series.timeframe);

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
      setSelectedTimeframe(seriesOptions[0].timeframe);
      return;
    }

    const matchingExchangeSeries = seriesOptions.filter(
      (series) => series.exchange === selectedExchange,
    );
    if (
      !selectedSymbol ||
      !matchingExchangeSeries.some((series) => series.symbol === selectedSymbol)
    ) {
      setSelectedSymbol(matchingExchangeSeries[0]?.symbol ?? "");
      setSelectedTimeframe(matchingExchangeSeries[0]?.timeframe ?? "");
      return;
    }

    const matchingSeries = matchingExchangeSeries.filter(
      (series) => series.symbol === selectedSymbol,
    );
    if (
      matchingSeries.length > 0 &&
      !matchingSeries.some((series) => series.timeframe === selectedTimeframe)
    ) {
      setSelectedTimeframe(matchingSeries[0].timeframe);
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
  const latest = candles[0];
  const chartSeries = buildChartSeries(candles);
  const hasNoSeries = !isSeriesLoading && !seriesError && seriesOptions.length === 0;
  const debugSample = chartSeries.data.slice(0, 5);

  return (
    <main className="app-shell">
      <section className="dashboard">
        <div className="headline">
          <p className="eyebrow">TradingView Lightweight Charts</p>
          <h1>Candle data, wired end to end.</h1>
          <p className="lede">
            Your React frontend now fetches candle rows from FastAPI and renders
            them in a proper market chart.
          </p>
        </div>

        <div className="stats-grid">
          <article className="stat-card">
            <span className="stat-label">API</span>
            <code>{apiBaseUrl}</code>
          </article>
          <article className="stat-card">
            <span className="stat-label">Rows loaded</span>
            <strong>{candles.length}</strong>
          </article>
          <article className="stat-card">
            <span className="stat-label">Chart candles</span>
            <strong>{chartSeries.data.length}</strong>
          </article>
          <article className="stat-card">
            <span className="stat-label">Latest exchange</span>
            <strong>{chartSeries.selectedExchange ?? latest?.exchange ?? "Waiting for data"}</strong>
          </article>
          <article className="stat-card">
            <span className="stat-label">Latest symbol</span>
            <strong>{chartSeries.selectedSymbol ?? latest?.symbol ?? "Waiting for data"}</strong>
          </article>
          <article className="stat-card">
            <span className="stat-label">Latest timeframe</span>
            <strong>
              {chartSeries.selectedTimeframe ?? latest?.timeframe ?? "Waiting for data"}
            </strong>
          </article>
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
                    const nextSeries = seriesOptions.find(
                      (series) => series.exchange === nextExchange,
                    );
                    setSelectedExchange(nextExchange);
                    setSelectedSymbol(nextSeries?.symbol ?? "");
                    setSelectedTimeframe(nextSeries?.timeframe ?? "");
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
                    const nextSymbol = event.target.value;
                    const nextTimeframe = seriesOptions.find(
                      (series) =>
                        series.exchange === selectedExchange && series.symbol === nextSymbol,
                    )?.timeframe ?? "";
                    setSelectedSymbol(nextSymbol);
                    setSelectedTimeframe(nextTimeframe);
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
                  {timeframesForSymbol.map((timeframe) => (
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

          {chartSeries.droppedRows > 0 && !error ? (
            <div className="chart-note">
              Showing {chartSeries.data.length} clean candles for{" "}
              {chartSeries.selectedExchange ?? "the latest exchange"} /{" "}
              {chartSeries.selectedSymbol ?? "the latest symbol"} /{" "}
              {chartSeries.selectedTimeframe ?? "the latest timeframe"} after dropping{" "}
              {chartSeries.droppedRows} rows that did not fit one chartable series.
            </div>
          ) : null}

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

          {!hasNoSeries && !error ? (
            <div className="debug-panel">
              <div className="panel-header">
                <div>
                  <p className="panel-kicker">Chart debug</p>
                  <h2>Rows passed to the chart</h2>
                </div>
              </div>
              <div className="debug-meta">
                <span>
                  Series: {chartSeries.selectedExchange ?? selectedExchange ?? "N/A"} /{" "}
                  {chartSeries.selectedSymbol ?? selectedSymbol ?? "N/A"} /{" "}
                  {chartSeries.selectedTimeframe ?? selectedTimeframe ?? "N/A"}
                </span>
                <span>Showing {debugSample.length} of {chartSeries.data.length} rows</span>
              </div>
              <pre className="debug-json">{JSON.stringify(debugSample, null, 2)}</pre>
            </div>
          ) : null}
        </section>

        <section className="notes-panel">
          <div className="panel-header">
            <div>
              <p className="panel-kicker">Next step</p>
              <h2>Good follow-ups from here</h2>
            </div>
          </div>
          <ul className="todo-list">
            <li>Add symbol and timeframe selectors wired into the query.</li>
            <li>Show OHLC and volume for the hovered candle.</li>
            <li>Create separate views for watchlists or strategy sessions.</li>
          </ul>
        </section>
      </section>
    </main>
  );
}
