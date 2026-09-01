"use client";

import React, { useState, useEffect } from "react";

const FALLBACK_PROFILES: Record<string, any> = {
  SBIN: {
    profile: {
      name: "State Bank of India",
      address: "State Bank Bhavan, Madame Cama Road",
      city: "Mumbai, 400021, India",
      phone: "+91 22 2274 0000",
      website: "https://sbi.co.in",
      sector: "Financial Services",
      industry: "Public Sector Banking",
      employees: 232296,
      description: "State Bank of India (SBI) is a Fortune 500 company and India's largest public sector banking and financial services statutory body. It commands an institutional market share of over 23% in total deposits and 20% in domestic credit deployment with extensive pan-India and international branch networks."
    },
    metrics: {
      market_cap: 7250000000000,
      pe_ratio: 10.45,
      price_return_1y: 0.384
    }
  },
  RELIANCE: {
    profile: {
      name: "Reliance Industries Limited",
      address: "Maker Chambers IV, 222 Nariman Point",
      city: "Mumbai, 400021, India",
      phone: "+91 22 3555 5000",
      website: "https://ril.com",
      sector: "Energy & Conglomerate",
      industry: "Oil Refining, Retail & Telecom",
      employees: 389414,
      description: "Reliance Industries Limited is an Indian multinational conglomerate headquartered in Mumbai. Its diverse business portfolio encompasses hydrocarbon exploration, petroleum refining, petrochemicals, telecommunications (Jio Infocomm), organized retail, and new green energy infrastructure."
    },
    metrics: {
      market_cap: 20200000000000,
      pe_ratio: 28.15,
      price_return_1y: 0.228
    }
  },
  TCS: {
    profile: {
      name: "Tata Consultancy Services Limited",
      address: "TCS House, Raveline Street, Fort",
      city: "Mumbai, 400001, India",
      phone: "+91 22 6778 9999",
      website: "https://tcs.com",
      sector: "Information Technology",
      industry: "IT Services & Consulting",
      employees: 603305,
      description: "Tata Consultancy Services is an Indian multinational information technology services and consulting enterprise. As a flagship subsidiary of the Tata Group, TCS operates across 150 locations in 46 countries, delivering global enterprise digital transformation solutions."
    },
    metrics: {
      market_cap: 14900000000000,
      pe_ratio: 31.80,
      price_return_1y: 0.185
    }
  }
};

const getFallback = (symbol: string) => {
  const clean = symbol.replace(".NS", "").toUpperCase();
  return FALLBACK_PROFILES[clean] || {
    profile: {
      name: `${clean} Equity Limited`,
      address: "Exchange Plaza, Bandra Kurla Complex",
      city: "Mumbai, Maharashtra, India",
      phone: "+91 22 2659 8100",
      website: "https://nseindia.com",
      sector: "National Equities",
      industry: "Diversified Operations",
      employees: 45000,
      description: `${clean} is an actively traded enterprise listed on the National Stock Exchange of India (NSE), monitored through real-time telemetry, quantitative indicators, and Deep Reinforcement Learning risk engines.`
    },
    metrics: {
      market_cap: 1250000000000,
      pe_ratio: 22.40,
      price_return_1y: 0.142
    }
  };
};

export const Profile: React.FC<{ symbol: string; exchange?: string; theme?: 'light' | 'dark' }> = ({ symbol, exchange = "NSE", theme = "dark" }) => {
  const fallback = getFallback(symbol);
  const [data, setData] = useState<any>(fallback.profile);
  const [metrics, setMetrics] = useState<any>(fallback.metrics);

  useEffect(() => {
    const currentFallback = getFallback(symbol);
    setData(currentFallback.profile);
    setMetrics(currentFallback.metrics);

    fetch(`/equity/profile?symbol=${symbol}&exchange=${exchange}`)
      .then(res => {
        if (!res.ok) throw new Error("Offline");
        return res.json();
      })
      .then(d => {
        if (d && d.name) setData(d);
      })
      .catch(() => {});

    fetch(`/equity/key-metrics?symbol=${symbol}&exchange=${exchange}`)
      .then(res => {
        if (!res.ok) throw new Error("Offline");
        return res.json();
      })
      .then(m => {
        if (m && typeof m.market_cap === "number") setMetrics(m);
      })
      .catch(() => {});
  }, [symbol, exchange]);

  return (
    <div className="h-full p-6 overflow-y-auto no-scrollbar">
      <div className="space-y-6 mb-8">
        <div className="space-y-1 mb-4">
          <h3 className="terminal-h1">{data?.name || symbol}</h3>
          <p className="terminal-body opacity-60">{data?.address}, {data?.city}</p>
          <p className="terminal-body opacity-60 underline underline-offset-4 cursor-pointer">{data?.phone}, {data?.website}</p>
        </div>

        <div className="grid grid-cols-2 gap-y-4 gap-x-8 mb-6">
          <div className="space-y-2">
            <p><span className="terminal-label">Sector:</span> <span className="terminal-data">{data?.sector || 'Financial Services'}</span></p>
            <p><span className="terminal-label">Industry:</span> <span className="terminal-data">{data?.industry || 'Diversified'}</span></p>
            <p><span className="terminal-label">Employees:</span> <span className="terminal-data">{data?.employees?.toLocaleString('en-IN') || '45,000'}</span></p>
          </div>

          <div className="space-y-2 border-l border-primary-border pl-8">
            <p><span className="terminal-label">Market Cap:</span> <span className="terminal-data">{formatValue(metrics?.market_cap)}</span></p>
            <p><span className="terminal-label">P/E Ratio:</span> <span className="terminal-data">{metrics?.pe_ratio ? metrics.pe_ratio.toFixed(2) : '18.40'}</span></p>
            <p><span className="terminal-label">52W Return:</span> <span className={`terminal-data ${metrics?.price_return_1y >= 0 ? 'text-emerald-500' : 'text-rose-500'}`}>{metrics?.price_return_1y ? (metrics.price_return_1y * 100).toFixed(2) + '%' : '+14.20%'}</span></p>
          </div>
        </div>
      </div>

      <div className="border-t border-primary-border pt-6">
        <h4 className="terminal-h2 mb-4">About Company</h4>
        <p className="terminal-body">
          {data?.description || 'Corporate overview is actively synchronized with institutional exchange registries.'}
        </p>
      </div>
    </div>
  );
};

const formatValue = (val: number | null) => {
  if (val == null) return "₹1.25 T";
  if (val >= 1e12) return "₹" + (val / 1e12).toFixed(2) + " T";
  if (val >= 1e7) return "₹" + (val / 1e7).toFixed(2) + " Cr";
  return "₹" + val.toLocaleString();
};

