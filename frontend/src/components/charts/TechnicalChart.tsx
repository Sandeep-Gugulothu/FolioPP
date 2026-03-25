"use client";

import React, { useState, useEffect } from 'react';
import dynamic from 'next/dynamic';

// Dynamic import for Plotly to avoid SSR issues
const Plot = dynamic(() => import('react-plotly.js'), { ssr: false });

interface TechnicalChartProps {
  symbol: string;
  exchange?: string;
}

export const TechnicalChart: React.FC<TechnicalChartProps> = ({ symbol, exchange = "NSE" }) => {
  const [plotData, setPlotData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchTechnicalPlot = async () => {
      setLoading(true);
      setError(null);
      try {
        const response = await fetch(`http://localhost:8000/equity/technical-analysis?symbol=${symbol}&exchange=${exchange}`);
        if (!response.ok) throw new Error("Failed to synthesize technical chart");
        const json = await response.json();
        
        if (json && !json.error) {
          setPlotData(json);
        } else {
          setError(json.error || "No data for technical analysis");
        }
      } catch (err: any) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchTechnicalPlot();
  }, [symbol, exchange]);

  if (loading) {
    return (
      <div className="h-full w-full flex items-center justify-center bg-background">
        <div className="flex flex-col items-center gap-4">
          <div className="w-8 h-8 border-2 border-primary-border/20 border-t-primary-text rounded-full animate-spin" />
          <span className="text-[10px] font-black uppercase tracking-widest text-primary-text/40">Synthesizing Institutional Strategy...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="h-full w-full flex items-center justify-center bg-background p-8 text-center">
        <span className="text-rose-500/80 text-[10px] font-black uppercase tracking-widest leading-relaxed">
           Technical Analysis Failure: {error}
        </span>
      </div>
    );
  }

  return (
    <div className="h-full w-full bg-[#0a0a0a] overflow-hidden">
      {plotData && (
        <Plot
          data={plotData.data}
          layout={{
            ...plotData.layout,
            autosize: true,
            plot_bgcolor: 'transparent',
            paper_bgcolor: 'transparent',
            margin: { t: 30, r: 50, b: 30, l: 50 },
            font: { family: 'var(--outfit-font)', color: '#ffffff', size: 9 },
            height: undefined, 
            width: undefined,
            dragmode: 'pan',
            legend: {
              orientation: 'h',
              yanchor: 'bottom',
              y: 1.02,
              xanchor: 'right',
              x: 1,
              font: { color: 'black', size: 10 },
              bgcolor: 'rgba(210, 210, 210, 0.9)', // Light institutional grey
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
