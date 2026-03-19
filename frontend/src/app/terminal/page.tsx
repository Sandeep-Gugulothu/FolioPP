import TerminalDockWrapper from "@/components/TerminalDockWrapper";

export const metadata = {
  title: "AI Terminal - FolioPP",
  description: "Advanced Market Reasoning & Signal Telemetry",
};

export default function TerminalPage() {
  return (
    <div className="min-h-screen bg-[#050505] overflow-y-auto">
        <TerminalDockWrapper />
    </div>
  );
}
