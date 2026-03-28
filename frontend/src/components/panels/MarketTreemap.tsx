"use client";

import React, { useState, useEffect } from "react";
import dynamic from "next/dynamic";

const Plot = dynamic(() => import("react-plotly.js"), { ssr: false });

const mockTreemapData = [
  { symbol: "RELIANCE", marketCap: 2000000, change: 1.24, sector: "Energy" },
  { symbol: "TCS", marketCap: 1500000, change: -0.52, sector: "Tech" },
  { symbol: "HDFCBANK", marketCap: 1200000, change: 0.85, sector: "Finance" },
  { symbol: "INFY", marketCap: 700000, change: 2.10, sector: "Tech" },
  { symbol: "ICICIBANK", marketCap: 850000, change: -1.15, sector: "Finance" },
  { symbol: "SBIN", marketCap: 920000, change: 0.55, sector: "Finance" },
  { symbol: "BHARTIARTL", marketCap: 650000, change: 1.52, sector: "Telecom" },
  { symbol: "ITC", marketCap: 580000, change: -0.25, sector: "FMCG" },
  { symbol: "LT", marketCap: 450000, change: 1.12, sector: "Eng" },
  { symbol: "HINDUNILVR", marketCap: 620000, change: -0.88, sector: "FMCG" },
  { symbol: "KOTAKBANK", marketCap: 380000, change: 0.42, sector: "Finance" },
  { symbol: "AXISBANK", marketCap: 350000, change: 1.20, sector: "Finance" },
  { symbol: "WIPRO", marketCap: 280000, change: -2.30, sector: "Tech" },
  { symbol: "HCLTECH", marketCap: 310000, change: 0.95, sector: "Tech" },
  { symbol: "ASIANPAINT", marketCap: 290000, change: -1.05, sector: "Paint" },
];

export const MarketTreemap: React.FC<{ theme?: 'light' | 'dark' }> = ({ theme = "dark" }) => {
  const [isClient, setIsClient] = useState(false);
  const [revision, setRevision] = useState(0);

  useEffect(() => {
    setIsClient(true);
    setTimeout(() => setRevision(prev => prev + 1), 500);
  }, []);

  if (!isClient) return <div className="h-full flex items-center justify-center text-secondary-text">Initialising Market Matrix...</div>;

  const labels = ["Market", ...mockTreemapData.map(d => d.symbol)];
  const parents = ["", ...mockTreemapData.map(d => "Market")];
  const values = [
    mockTreemapData.reduce((acc, d) => acc + d.marketCap, 0),
    ...mockTreemapData.map(d => d.marketCap)
  ];
  const isLight = theme === 'light';
  
  const colors = [isLight ? '#eee' : '#111', ...mockTreemapData.map(d => d.change >= 0 ? '#3D9970' : '#FF4136')];
  const customdata = [
    [0, 0], 
    ...mockTreemapData.map(d => [d.change, d.marketCap])
  ];

  return (
    <div className={`h-full w-full p-1 transition-colors ${isLight ? 'bg-white' : 'bg-[#050505]'}`}>
      <Plot
        data={[
          {
            type: "treemap",
            labels: labels,
            parents: parents,
            values: values,
            branchvalues: "total",
            textinfo: "label+value",
            marker: {
              colors: colors,
              line: { width: 1, color: isLight ? '#fff' : '#050505' }
            },
            customdata: customdata,
            hovertemplate: "<b>%{label}</b><br>Market Cap: ₹%{value:,.0f} Cr<br>Change: %{customdata[0]:.2f}%<extra></extra>",
          }
        ]}
        layout={{
          autosize: true,
          paper_bgcolor: 'transparent',
          plot_bgcolor: 'transparent',
          margin: { t: 30, l: 0, r: 0, b: 0 },
          font: { family: 'var(--font-sans)', size: 11, color: isLight ? '#1a1a1a' : '#fff' },
           annotations: [
            {
              x: 0.5, y: 1.05,
              xref: "paper", yref: "paper",
              text: "Color: <span style='color:#3D9970'>Positive</span> | <span style='color:#FF4136'>Negative</span>",
              showarrow: false,
              font: { size: 10, color: isLight ? '#1a1a1a' : '#888' }
            }
          ]
        }}
        useResizeHandler={true}
        revision={revision}
        className="w-full h-full"
        style={{ width: '100%', height: '100%' }}
        config={{ displayModeBar: false }}
      />
    </div>
  );
};
