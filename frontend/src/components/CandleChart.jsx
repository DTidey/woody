import { CandlestickSeries, HistogramSeries, createChart } from "lightweight-charts";
import { useEffect, useRef, useState } from "react";

export default function CandleChart({ candles }) {
  const containerRef = useRef(null);
  const [chartError, setChartError] = useState(null);

  useEffect(() => {
    if (!containerRef.current) {
      return undefined;
    }

    setChartError(null);

    try {
      const chart = createChart(containerRef.current, {
        autoSize: true,
        layout: {
          background: { color: "transparent" },
          panes: {
            enableResize: true,
            separatorColor: "rgba(244, 239, 230, 0.08)",
            separatorHoverColor: "rgba(139, 198, 193, 0.2)",
          },
          textColor: "#f4efe6",
        },
        grid: {
          vertLines: { color: "rgba(244, 239, 230, 0.08)" },
          horzLines: { color: "rgba(244, 239, 230, 0.08)" },
        },
        crosshair: {
          vertLine: { color: "rgba(168, 214, 186, 0.35)" },
          horzLine: { color: "rgba(168, 214, 186, 0.35)" },
        },
        rightPriceScale: {
          borderColor: "rgba(244, 239, 230, 0.12)",
        },
        timeScale: {
          borderColor: "rgba(244, 239, 230, 0.12)",
          timeVisible: true,
          secondsVisible: false,
        },
      });

      const candleSeries = chart.addSeries(CandlestickSeries, {
        upColor: "#75c08f",
        downColor: "#de6b64",
        wickUpColor: "#75c08f",
        wickDownColor: "#de6b64",
        borderVisible: false,
      });

      const volumeSeries = chart.addSeries(
        HistogramSeries,
        {
          priceFormat: {
            type: "volume",
          },
        },
        1,
      );

      candleSeries.setData(candles);
      volumeSeries.setData(
        candles.map((candle) => ({
          time: candle.time,
          value: candle.volume ?? 0,
          color: candle.close >= candle.open ? "#75c08f" : "#de6b64",
        })),
      );

      chart.panes()?.[1]?.setHeight(140);
      chart.timeScale().fitContent();

      return () => {
        chart.remove();
      };
    } catch (error) {
      setChartError(error instanceof Error ? error.message : "Unknown chart error");
      return undefined;
    }
  }, [candles]);

  if (chartError) {
    return (
      <div className="panel-message">
        <p>The chart could not render the returned candle data.</p>
        <code>{chartError}</code>
      </div>
    );
  }

  if (candles.length === 0) {
    return (
      <div className="panel-message">
        <p>No valid candle series is available to chart yet.</p>
      </div>
    );
  }

  return <div className="chart-frame" ref={containerRef} />;
}
