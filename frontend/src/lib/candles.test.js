import { buildChartSeries } from "./candles";

describe("buildChartSeries", () => {
  it("returns empty chart metadata for missing input", () => {
    expect(buildChartSeries()).toEqual({
      data: [],
      droppedRows: 0,
      selectedExchange: null,
      selectedSymbol: null,
      selectedTimeframe: null,
      totalRows: 0,
    });
  });

  it("drops invalid rows and deduplicates timestamps", () => {
    const result = buildChartSeries([
      {
        exchange: "binance",
        symbol: "BTC-USDT",
        timeframe: "1m",
        timestamp: 1_710_000_000_000,
        open: 100,
        high: 102,
        low: 99,
        close: 101,
        volume: 10,
      },
      {
        exchange: "binance",
        symbol: "BTC-USDT",
        timeframe: "1m",
        timestamp: 1_710_000_000_000,
        open: 101,
        high: 103,
        low: 100,
        close: 102,
        volume: 11,
      },
      {
        exchange: "binance",
        symbol: "BTC-USDT",
        timeframe: "1m",
        timestamp: 1_710_000_060_000,
        open: 103,
        high: 102,
        low: 101,
        close: 104,
        volume: 12,
      },
    ]);

    expect(result.data).toEqual([
      { time: 1_710_000_000, open: 101, high: 103, low: 100, close: 102, volume: 11 },
    ]);
    expect(result.droppedRows).toBe(2);
    expect(result.selectedExchange).toBe("binance");
    expect(result.selectedSymbol).toBe("BTC-USDT");
    expect(result.selectedTimeframe).toBe("1m");
  });

  it("normalizes millisecond timestamps to seconds and keeps series ordering ascending", () => {
    const result = buildChartSeries([
      {
        exchange: "binance",
        symbol: "BTC-USDT",
        timeframe: "5m",
        timestamp: 1_710_000_300_000,
        open: 105,
        high: 107,
        low: 104,
        close: 106,
        volume: 21,
      },
      {
        exchange: "binance",
        symbol: "BTC-USDT",
        timeframe: "5m",
        timestamp: 1_710_000_000_000,
        open: 100,
        high: 106,
        low: 99,
        close: 105,
        volume: 34,
      },
    ]);

    expect(result.data).toEqual([
      { time: 1_710_000_000, open: 100, high: 106, low: 99, close: 105, volume: 34 },
      { time: 1_710_000_300, open: 105, high: 107, low: 104, close: 106, volume: 21 },
    ]);
  });
});
