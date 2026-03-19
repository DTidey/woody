import { render, screen } from "@testing-library/react";

import CandleChart from "./CandleChart";

const addSeries = vi.fn();
const remove = vi.fn();
const fitContent = vi.fn();
const setHeight = vi.fn();
const candleSetData = vi.fn();
const volumeSetData = vi.fn();

vi.mock("lightweight-charts", () => ({
  CandlestickSeries: "candlestick-series",
  HistogramSeries: "histogram-series",
  createChart: vi.fn(() => ({
    addSeries,
    panes: () => [undefined, { setHeight }],
    remove,
    timeScale: () => ({ fitContent }),
  })),
}));

describe("CandleChart", () => {
  beforeEach(() => {
    addSeries.mockReset();
    remove.mockReset();
    fitContent.mockReset();
    setHeight.mockReset();
    candleSetData.mockReset();
    volumeSetData.mockReset();

    addSeries
      .mockReturnValueOnce({ setData: candleSetData })
      .mockReturnValueOnce({ setData: volumeSetData });
  });

  it("renders an empty-state message when there are no candles", () => {
    render(<CandleChart candles={[]} />);

    expect(screen.getByText("No valid candle series is available to chart yet.")).toBeInTheDocument();
  });

  it("creates a separate volume histogram pane from candle data", () => {
    render(
      <CandleChart
        candles={[
          { time: 1_710_000_000, open: 100, high: 105, low: 99, close: 104, volume: 12 },
          { time: 1_710_000_300, open: 104, high: 106, low: 101, close: 102, volume: 8 },
        ]}
      />,
    );

    expect(addSeries).toHaveBeenNthCalledWith(
      1,
      "candlestick-series",
      expect.objectContaining({
        upColor: "#75c08f",
        downColor: "#de6b64",
      }),
    );
    expect(addSeries).toHaveBeenNthCalledWith(
      2,
      "histogram-series",
      expect.objectContaining({
        priceFormat: { type: "volume" },
      }),
      1,
    );
    expect(candleSetData).toHaveBeenCalledWith([
      { time: 1_710_000_000, open: 100, high: 105, low: 99, close: 104, volume: 12 },
      { time: 1_710_000_300, open: 104, high: 106, low: 101, close: 102, volume: 8 },
    ]);
    expect(volumeSetData).toHaveBeenCalledWith([
      { time: 1_710_000_000, value: 12, color: "#75c08f" },
      { time: 1_710_000_300, value: 8, color: "#de6b64" },
    ]);
    expect(setHeight).toHaveBeenCalledWith(140);
    expect(fitContent).toHaveBeenCalled();
  });
});
