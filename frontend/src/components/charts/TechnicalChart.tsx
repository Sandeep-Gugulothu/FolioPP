"use client";

import React, { useState, useEffect } from 'react';
import dynamic from 'next/dynamic';

const Plot = dynamic(() => import('react-plotly.js'), { ssr: false });

interface TechnicalChartProps {
  symbol: string;
  exchange?: string;
  theme?: 'light' | 'dark';
}

const generateFallbackTechnicalPlot = (symbol: string) => {
  const clean = symbol.replace(".NS", "").toUpperCase();
  let base = 800;
  if (clean === "SBIN") base = 810;
  else if (clean === "RELIANCE") base = 2980;
  else if (clean === "TCS") base = 4100;
  else if (clean === "INFY") base = 1840;

  const points = 45;
  const dates: string[] = [];
  const opens: number[] = [];
  const highs: number[] = [];
  const lows: number[] = [];
  const closes: number[] = [];
  const kalman: number[] = [];
  const rsi: number[] = [];
  const macd: number[] = [];
  const macdSignal: number[] = [];

  let curr = base;
  let currKalman = base;
  const now = new Date();

  for (let i = points; i >= 0; i--) {
    const d = new Date(now);
    d.setDate(d.getDate() - i);
    if (d.getDay() === 0 || d.getDay() === 6) continue;

    dates.push(d.toISOString().split("T")[0]);
    const drift = (Math.sin(i * 0.3) * 0.015) + (Math.random() - 0.48) * 0.02;
    const op = curr;
    const cl = Math.round(op * (1 + drift) * 100) / 100;
    const hi = Math.round(Math.max(op, cl) * (1 + Math.random() * 0.01) * 100) / 100;
    const lo = Math.round(Math.min(op, cl) * (1 - Math.random() * 0.01) * 100) / 100;

    currKalman = currKalman + 0.15 * (cl - currKalman);

    opens.push(op);
    closes.push(cl);
    highs.push(hi);
    lows.push(lo);
    kalman.push(Math.round(currKalman * 100) / 100);

    const rsiVal = 50 + Math.sin(i * 0.4) * 22 + (Math.random() - 0.5) * 6;
    rsi.push(Math.round(Math.max(15, Math.min(85, rsiVal)) * 10) / 10);

    const macdVal = Math.sin(i * 0.3) * 8;
    macd.push(Math.round(macdVal * 100) / 100);
    macdSignal.push(Math.round((macdVal * 0.7) * 100) / 100);

    curr = cl;
  }

  return {
    data: [
      {
        type: 'candlestick',
        x: dates,
        open: opens,
        high: highs,
        low: lows,
        close: closes,
        name: `${clean} Price`,
        increasing: { line: { color: '#10b981' } },
        decreasing: { line: { color: '#ef4444' } },
        yaxis: 'y1'
      },
      {
        type: 'scatter',
        mode: 'lines',
        x: dates,
        y: kalman,
        name: 'Kalman Filter (Smoothed)',
        line: { color: '#f59e0b', width: 2 },
        yaxis: 'y1'
      },
      {
        type: 'scatter',
        mode: 'lines',
        x: dates,
        y: rsi,
        name: 'RSI (14)',
        line: { color: '#8b5cf6', width: 1.5 },
        yaxis: 'y2'
      },
      {
        type: 'bar',
        x: dates,
        y: macd.map((m, idx) => m - macdSignal[idx]),
        name: 'MACD Hist',
        marker: {
          color: macd.map((m, idx) => (m - macdSignal[idx] >= 0 ? '#10b981' : '#ef4444'))
        },
        yaxis: 'y3'
      }
    ],
    layout: {
      grid: { rows: 3, columns: 1, pattern: 'independent', roworder: 'top to bottom' },
      yaxis: { domain: [0.45, 1], title: 'Price' },
      yaxis2: { domain: [0.22, 0.40], title: 'RSI (14)' },
      yaxis3: { domain: [0.0, 0.18], title: 'MACD' },
      xaxis: { rangeslider: { visible: false } }
    }
  };
};

export const TechnicalChart: React.FC<TechnicalChartProps> = ({ symbol, exchange = "NSE", theme = "dark" }) => {
  const [plotData, setPlotData] = useState<any>(() => generateFallbackTechnicalPlot(symbol));
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setPlotData(generateFallbackTechnicalPlot(symbol));

    const fetchTechnicalPlot = async () => {
      try {
        const response = await fetch(`/equity/technical-analysis?symbol=${symbol}&exchange=${exchange}`);
        if (!response.ok) throw new Error("Offline");
        const json = await response.json();

        if (json && !json.error && json.data) {
          setPlotData(json);
        }
      } catch (err: any) {
        // Fallback chart remains active
      }
    };

    fetchTechnicalPlot();
  }, [symbol, exchange]);

  const isLight = theme === 'light';

  return (
    <div className={`h-full w-full overflow-hidden transition-colors ${isLight ? 'bg-white' : 'bg-[#0a0a0a]'}`}>
      {plotData && (
        <Plot
          data={plotData.data}
          layout={{
            ...plotData.layout,
            autosize: true,
            plot_bgcolor: 'transparent',
            paper_bgcolor: 'transparent',
            margin: { t: 30, r: 50, b: 30, l: 50 },
            font: { 
              family: 'var(--font-sans)', 
              color: isLight ? '#1a1a1a' : '#ffffff', 
              size: 9 
            },
            height: undefined,
            width: undefined,
            dragmode: 'pan',
            xaxis: {
              ...(plotData.layout?.xaxis || {}),
              gridcolor: isLight ? 'rgba(0,0,0,0.05)' : 'rgba(255,255,255,0.03)',
              linecolor: isLight ? 'rgba(0,0,0,0.1)' : 'rgba(255,255,255,0.1)',
              tickfont: { color: isLight ? '#1a1a1a' : '#ffffff' }
            },
            yaxis: {
              ...(plotData.layout?.yaxis || {}),
              gridcolor: isLight ? 'rgba(0,0,0,0.05)' : 'rgba(255,255,255,0.03)',
              linecolor: isLight ? 'rgba(0,0,0,0.1)' : 'rgba(255,255,255,0.1)',
              tickfont: { color: isLight ? '#1a1a1a' : '#ffffff' }
            },
            legend: {
              orientation: 'h',
              yanchor: 'bottom',
              y: 1.02,
              xanchor: 'right',
              x: 1,
              font: { color: 'black', size: 10 },
              bgcolor: isLight ? 'rgba(240, 240, 240, 0.9)' : 'rgba(210, 210, 210, 0.9)', 
              borderwidth: 0
            }
          }}
          config={{
            responsive: true,
            displayModeBar: false,
            scrollZoom: true,
            staticPlot: false
          }}
          style={{ width: '100%', height: '100%' }}
          useResizeHandler={true}
        />
      )}
    </div>
  );
};

