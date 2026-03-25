"use client";

import React from "react";
import Image from "next/image";

interface ResearchChartProps {
  imageSrc: string;
}

export const ResearchChart: React.FC<ResearchChartProps> = ({ imageSrc }) => {
  if (!imageSrc) return <div className="h-full flex items-center justify-center opacity-20">Awaiting Signal...</div>;

  return (
    <div className="w-full h-full p-2 bg-black/40 flex flex-col items-center justify-center overflow-hidden">
      <div className="relative w-full h-full group">
        <img 
          src={imageSrc} 
          alt="Neural Research Plot" 
          className="w-full h-full object-contain filter drop-shadow-[0_0_30px_rgba(0,0,0,0.5)] transition-transform duration-500 group-hover:scale-[1.02]"
        />
        <div className="absolute top-2 right-2 flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
            <div className="px-2 py-1 bg-sky-500/20 text-sky-400 text-[8px] font-black uppercase tracking-widest border border-sky-500/30 rounded">HD RENDER</div>
            <div className="px-2 py-1 bg-emerald-500/20 text-emerald-500 text-[8px] font-black uppercase tracking-widest border border-emerald-500/30 rounded">PYTHON 3.10</div>
        </div>
      </div>
    </div>
  );
};
