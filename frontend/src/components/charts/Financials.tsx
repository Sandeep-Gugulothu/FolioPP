"use client";

import React, { useState, useEffect } from "react";

interface FinancialsProps {
  symbol: string;
  exchange?: string;
  initialTab?: "Income" | "Balance" | "Cash";
}

type TabType = "Income" | "Balance" | "Cash";

export const Financials: React.FC<FinancialsProps> = ({ symbol, exchange = "NSE", initialTab = "Income" }) => {
  const [activeTab, setActiveTab] = useState<TabType>(initialTab as TabType);
  const [data, setData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    let endpoint = "";
    if (activeTab === "Income") endpoint = "financials";
    else if (activeTab === "Balance") endpoint = "balance-sheet";
    else if (activeTab === "Cash") endpoint = "cash-flow";

    fetch(`http://localhost:8000/equity/${endpoint}?symbol=${symbol}&exchange=${exchange}`)
      .then(res => res.json())
      .then(d => {
        setData(Array.isArray(d) ? d : []);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, [symbol, exchange, activeTab]);

  const FinancialRow = ({ label, data, field, isRatio = false, isShares = false, className = "" }: any) => {
    const hasAnyValue = data.some((item: any) => item[field] !== null && item[field] !== undefined);
    if (!hasAnyValue) return null;
    return (
      <tr className="border-b border-primary-border hover:bg-primary-text/[0.03] transition-colors group">
        <td className={`py-3 pl-3 text-primary-text opacity-100 font-bold text-[13px] transition-colors ${className}`}>{label}</td>
        {data.map((item: any) => (
          <td key={item.period_ending} className={`py-3 pr-3 text-right text-primary-text opacity-90 font-mono text-[13px] transition-colors ${className}`}>
            {item[field] != null
              ? isShares
                ? (item[field] / 1e7).toFixed(2) + ' Cr'
                : isRatio
                  ? item[field].toFixed(4)
                  : '₹' + (item[field] / 1e7).toFixed(2) + ' Cr'
              : '---'}
          </td>
        ))}
      </tr>
    );
  };

  const SectionRow = ({ label }: { label: string }) => (
    <tr className="bg-primary-text/[0.02]">
      <td colSpan={100} className="py-2.5 px-3 text-[10px] font-black text-secondary-text uppercase tracking-[0.3em]">{label}</td>
    </tr>
  );

  const renderIncomeStatement = () => (
    <>
      <SectionRow label="Revenue" />
      <FinancialRow label="Total Revenue" data={data} field="total_revenue" />
      <FinancialRow label="Operating Revenue" data={data} field="operating_revenue" />
      <FinancialRow label="Net Interest Income" data={data} field="net_interest_income" />
      <SectionRow label="Expenses" />
      <FinancialRow label="Operating Expense" data={data} field="operating_expense" />
      <FinancialRow label="SG&A" data={data} field="sga_expense" />
      <FinancialRow label="D&A" data={data} field="depreciation_amortization" />
      <SectionRow label="Profitability" />
      <FinancialRow label="Gross Profit" data={data} field="gross_profit" />
      <FinancialRow label="Net Income" data={data} field="net_income" />
    </>
  );

  const renderBalanceSheet = () => (
    <>
      <SectionRow label="Current Assets" />
      <FinancialRow label="Cash & Equivalents" data={data} field="cash_and_cash_equivalents" />
      <FinancialRow label="Receivables" data={data} field="receivables" />
      <SectionRow label="Total Assets" />
      <FinancialRow label="Total Assets" data={data} field="total_assets" className="font-black text-primary-text underline underline-offset-4" />
      <SectionRow label="Liabilities" />
      <FinancialRow label="Total Liabilities" data={data} field="total_liabilities_net_minority_interest" />
      <SectionRow label="Equity" />
      <FinancialRow label="Total Equity" data={data} field="total_equity_gross_minority_interest" className="font-black text-primary-text" />
    </>
  );

  const renderCashFlow = () => (
    <>
      <SectionRow label="Operating Activities" />
      <FinancialRow label="Operating Cash Flow" data={data} field="operating_cash_flow" className="font-bold text-emerald-500" />
      <SectionRow label="Financing Activities" />
      <FinancialRow label="Dividends Paid" data={data} field="cash_dividends_paid" />
      <SectionRow label="Summary" />
      <FinancialRow label="Free Cash Flow" data={data} field="free_cash_flow" className="font-black text-primary-text" />
      <FinancialRow label="End Cash Position" data={data} field="end_cash_position" className="font-black text-primary-text underline" />
    </>
  );

  return (
    <div className="h-full bg-transparent flex flex-col p-6 overflow-y-auto no-scrollbar">
      <div className="flex gap-4 mb-8 border-b border-primary-border pb-4">
        {["Income", "Balance", "Cash"].map((t) => (
          <button
            key={t}
            onClick={() => setActiveTab(t as TabType)}
            className={`px-4 py-1.5 text-[11px] font-black uppercase tracking-[0.2em] transition-all rounded ${activeTab === t ? 'bg-primary-text/10 text-primary-text' : 'text-secondary-text hover:text-primary-text'}`}
          >
            {t === "Income" ? "Income Statement" : t === "Balance" ? "Balance Sheet" : "Cash Flow"}
          </button>
        ))}
      </div>

      {loading ? (
           <div className="p-20 text-center text-secondary-text uppercase font-black text-[10px] tracking-widest animate-pulse">Syncing Ledgers...</div>
      ) : (
        <div className="flex-1 overflow-x-auto">
            <table className="w-full text-left border-collapse">
            <thead>
                <tr className="border-b border-primary-border">
                <th className="py-3 text-[10px] font-black text-secondary-text uppercase tracking-widest pl-2">Metric</th>
                {data.map(item => (
                    <th key={item.period_ending} className="py-3 text-[10px] font-black text-secondary-text uppercase text-right tracking-widest pr-2">
                    {item.period_ending.split('-')[0]}
                    </th>
                ))}
                </tr>
            </thead>
            <tbody className="text-[13px]">
                {activeTab === "Income" && renderIncomeStatement()}
                {activeTab === "Balance" && renderBalanceSheet()}
                {activeTab === "Cash" && renderCashFlow()}
            </tbody>
            </table>
        </div>
      )}
    </div>
  );
};
