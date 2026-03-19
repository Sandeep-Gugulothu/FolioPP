"use client";

import dynamic from "next/dynamic";

const DynamicTerminalDock = dynamic(
  () => import("./TerminalDock").then((mod) => mod.TerminalDock),
  { ssr: false }
);

export default function TerminalDockWrapper() {
  return <DynamicTerminalDock />;
}
