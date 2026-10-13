import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Folks Orchestrator Cockpit",
  description: "Autonomous multi-agent orchestration platform integrating Kanban, War Rooms, and Board of Advisors.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-zinc-950 text-zinc-100 antialiased min-h-screen">
        {children}
      </body>
    </html>
  );
}
