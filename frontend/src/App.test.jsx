import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import App from "./App";
import * as api from "./lib/api";

vi.mock("./components/CandleChart", () => ({
  default: ({ candles }) => (
    <div data-testid="chart-mock">chart:{candles.length}</div>
  ),
}));

function renderApp() {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  });

  return render(
    <QueryClientProvider client={queryClient}>
      <App />
    </QueryClientProvider>,
  );
}

describe("App", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("defaults to the first exchange, sorts symbols ascending, and fetches candles", async () => {
    const fetchSeriesSpy = vi.spyOn(api, "fetchCandleSeriesOptions").mockResolvedValue([
      { exchange: "binance", symbol: "ETH-USDT", timeframe: "1m" },
      { exchange: "binance", symbol: "BTC-USDT", timeframe: "1m" },
      { exchange: "coinbase", symbol: "SOL-USD", timeframe: "1m" },
    ]);
    const fetchCandlesSpy = vi.spyOn(api, "fetchCandles").mockResolvedValue([
      {
        exchange: "binance",
        symbol: "ETH-USDT",
        timeframe: "1m",
        timestamp: 1_710_000_000_000,
        open: 100,
        high: 101,
        low: 99,
        close: 100.5,
      },
    ]);

    renderApp();

    await waitFor(() => expect(fetchSeriesSpy).toHaveBeenCalled());
    await waitFor(() =>
      expect(fetchCandlesSpy).toHaveBeenCalledWith({
        exchange: "binance",
        symbol: "ETH-USDT",
        timeframe: "1m",
        limit: 200,
      }),
    );

    const symbolSelect = screen.getByLabelText("Symbol");
    const symbolOptions = [...symbolSelect.querySelectorAll("option")].map((option) => option.value);
    expect(symbolOptions).toEqual(["BTC-USDT", "ETH-USDT"]);
    expect(symbolSelect).toHaveValue("ETH-USDT");

    expect(screen.getByLabelText("Timeframe")).toHaveValue("1m");
    expect(screen.getByTestId("chart-mock")).toHaveTextContent("chart:1");
    expect(screen.queryByText("Rows loaded")).not.toBeInTheDocument();
    expect(screen.queryByText("Chart debug")).not.toBeInTheDocument();
  });

  it("offers higher timeframe options and refetches when the timeframe changes", async () => {
    vi.spyOn(api, "fetchCandleSeriesOptions").mockResolvedValue([
      { exchange: "binance", symbol: "BTC-USDT", timeframe: "1m" },
    ]);
    const fetchCandlesSpy = vi.spyOn(api, "fetchCandles").mockResolvedValue([]);

    renderApp();

    const timeframeSelect = await screen.findByLabelText("Timeframe");
    await waitFor(() =>
      expect(
        [...timeframeSelect.querySelectorAll("option")].map((option) => option.value),
      ).toContain("4h"),
    );
    const timeframeOptions = [...timeframeSelect.querySelectorAll("option")].map((option) => option.value);

    expect(timeframeOptions).toContain("4h");
    expect(timeframeOptions).toContain("1d");

    await userEvent.selectOptions(timeframeSelect, "4h");

    await waitFor(() =>
      expect(fetchCandlesSpy).toHaveBeenLastCalledWith({
        exchange: "binance",
        symbol: "BTC-USDT",
        timeframe: "4h",
        limit: 200,
      }),
    );
  });

  it("shows an empty state when no series are available", async () => {
    vi.spyOn(api, "fetchCandleSeriesOptions").mockResolvedValue([]);
    const fetchCandlesSpy = vi.spyOn(api, "fetchCandles").mockResolvedValue([]);

    renderApp();

    expect(await screen.findByText("No candle series are available yet.")).toBeInTheDocument();
    expect(fetchCandlesSpy).not.toHaveBeenCalled();
  });

  it("shows an API error message when candle loading fails", async () => {
    vi.spyOn(api, "fetchCandleSeriesOptions").mockResolvedValue([
      { exchange: "binance", symbol: "BTC-USDT", timeframe: "1m" },
    ]);
    vi.spyOn(api, "fetchCandles").mockRejectedValue(new Error("Unable to load candles: 503"));

    renderApp();

    expect(
      await screen.findByText("The frontend could not load candle data from the API."),
    ).toBeInTheDocument();
    expect(screen.getByText("Unable to load candles: 503")).toBeInTheDocument();
  });
});
