import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "FOREX AI — Institutional Quantitative Market Terminal",
  description: "AI-Powered Probabilistic Forex Market Analysis, Regime Detection, Explainable Signals, and Walk-Forward Backtesting",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="bg-background text-slate-100 min-h-screen antialiased selection:bg-accent/30 selection:text-white">
        {children}
      </body>
    </html>
  );
}
