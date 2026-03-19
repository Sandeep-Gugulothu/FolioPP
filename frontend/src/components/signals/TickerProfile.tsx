"use client";

import React from "react";

export const TickerProfile: React.FC<{ symbol: string }> = ({ symbol }) => (
  <div className="h-full bg-[#0c0c0c] p-6 font-mono overflow-y-auto no-scrollbar">
    <div className="space-y-4 mb-8">
      <div className="space-y-0.5 mb-4">
        <h3 className="text-[11px] font-black text-white">{symbol === 'AAPL' ? 'Apple Inc.' : 'Adobe Inc.'}</h3>
        <p className="text-[10px] text-white">345 Park Avenue</p>
        <p className="text-[10px] text-blue-500 hover:underline cursor-pointer">(408) 536 6000, https://www.adobe.com</p>
      </div>

      <div className="space-y-1.5 text-[10px] text-white">
        <p><span className="font-black">Sector:</span> Technology, <span className="font-black">Industry:</span> Software - Infrastructure</p>
        <p><span className="font-black">Full time employees:</span> 30709</p>
        <p><span className="font-black">CIK:</span> 0000796343, <span className="font-black">ISIN:</span> US00724F1012, <span className="font-black">CUSIP:</span> 00724F101</p>
        <p><span className="font-black">Exchange:</span> NASDAQ, <span className="font-black">IPO Date:</span> 1986-08-13</p>
      </div>
    </div>

    <div className="border-t border-white/5 pt-6">
      <h4 className="text-[11px] font-black text-white mb-4">Description</h4>
      <p className="text-[10px] leading-relaxed text-white text-justify">
        {symbol} operates as a diversified software company worldwide. It operates through three segments: Digital Media, Digital Experience, and Publishing and Advertising. The Digital Media segment offers products, services, and solutions that enable individuals, teams, and enterprises to create, publish, and promote content...
      </p>
    </div>
  </div>
);
