"use client";

import { AdminDashboard } from "@/components/panels/AdminDashboard";
import "@/assets/styles/globals.css";

export default function AdminPage() {
  return (
    <div className="w-screen h-screen bg-[#09090b]">
       <AdminDashboard />
    </div>
  );
}
