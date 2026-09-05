"use client";

import React, { useRef, useEffect, useState, useMemo } from "react";
import { Candle, Prediction } from "@/lib/api";

interface CandlestickChartProps {
  candles: Candle[];
  prediction: Prediction | null;
  pair: string;
  timeframe: string;
}

export const CandlestickChart: React.FC<CandlestickChartProps> = ({
  candles,
  prediction,
  pair,
  timeframe,
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [hoverIndex, setHoverIndex] = useState<number | null>(null);
  const [mousePos, setMousePos] = useState<{ x: number; y: number } | null>(null);

  // Compute EMA20 and EMA50 on candles
  const emaData = useMemo(() => {
    if (candles.length === 0) return { ema20: [], ema50: [] };

    const calcEMA = (span: number) => {
      const k = 2 / (span + 1);
      const res: (number | null)[] = [];
      let prevEma: number | null = null;

      for (let i = 0; i < candles.length; i++) {
        const c = candles[i].close;
        if (i === 0) {
          prevEma = c;
        } else if (prevEma !== null) {
          prevEma = c * k + prevEma * (1 - k);
        }
        res.push(prevEma);
      }
      return res;
    };

    return {
      ema20: calcEMA(20),
      ema50: calcEMA(50),
    };
  }, [candles]);

  // Render on canvas
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || candles.length === 0) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    // Handle high DPI
    const dpr = window.devicePixelRatio || 1;
    const width = canvas.parentElement?.clientWidth || 800;
    const height = canvas.parentElement?.clientHeight || 480;

    canvas.width = width * dpr;
    canvas.height = height * dpr;
    canvas.style.width = `${width}px`;
    canvas.style.height = `${height}px`;

    ctx.scale(dpr, dpr);

    // Padding
    const pTop = 20;
    const pBottom = 60;
    const pLeft = 10;
    const pRight = 75;

    const chartW = width - pLeft - pRight;
    const chartH = height - pTop - pBottom;
    const volH = 50;
    const priceH = chartH - volH - 10;

    // Find price min/max
    let minP = Infinity;
    let maxP = -Infinity;
    let maxVol = 0;

    candles.forEach((c) => {
      if (c.low < minP) minP = c.low;
      if (c.high > maxP) maxP = c.high;
      if (c.volume > maxVol) maxVol = c.volume;
    });

    // Also expand range to fit SL and TP if available
    if (prediction) {
      if (prediction.stop_loss) minP = Math.min(minP, prediction.stop_loss);
      if (prediction.take_profit_2) maxP = Math.max(maxP, prediction.take_profit_2);
      if (prediction.take_profit_1) maxP = Math.max(maxP, prediction.take_profit_1);
    }

    // Add 5% padding
    const pRange = maxP - minP || 1;
    minP -= pRange * 0.05;
    maxP += pRange * 0.05;

    const yPrice = (price: number) => {
      return pTop + priceH - ((price - minP) / (maxP - minP)) * priceH;
    };

    const candleCount = candles.length;
    const candleSlotW = chartW / candleCount;
    const candleW = Math.max(2, Math.min(14, candleSlotW * 0.7));

    // Clear background
    ctx.fillStyle = "#0c1018";
    ctx.fillRect(0, 0, width, height);

    // Draw grid lines
    ctx.strokeStyle = "rgba(35, 43, 62, 0.4)";
    ctx.lineWidth = 1;

    const gridSteps = 6;
    ctx.textAlign = "left";
    ctx.font = "10px JetBrains Mono, monospace";

    for (let i = 0; i <= gridSteps; i++) {
      const p = minP + (i / gridSteps) * (maxP - minP);
      const y = yPrice(p);

      ctx.beginPath();
      ctx.moveTo(pLeft, y);
      ctx.lineTo(width - pRight, y);
      ctx.stroke();

      // Price label on right
      ctx.fillStyle = "#64748b";
      ctx.fillText(p.toFixed(5), width - pRight + 8, y + 3);
    }

    // Draw Support & Resistance zones from prediction
    if (prediction) {
      // Support levels
      prediction.support_levels.forEach((lvl) => {
        const y = yPrice(lvl);
        ctx.strokeStyle = "rgba(16, 185, 129, 0.35)";
        ctx.setLineDash([4, 4]);
        ctx.beginPath();
        ctx.moveTo(pLeft, y);
        ctx.lineTo(width - pRight, y);
        ctx.stroke();
        ctx.fillStyle = "#10b981";
        ctx.fillText(`SUP ${lvl.toFixed(5)}`, width - pRight + 8, y + 3);
      });

      // Resistance levels
      prediction.resistance_levels.forEach((lvl) => {
        const y = yPrice(lvl);
        ctx.strokeStyle = "rgba(239, 68, 68, 0.35)";
        ctx.setLineDash([4, 4]);
        ctx.beginPath();
        ctx.moveTo(pLeft, y);
        ctx.lineTo(width - pRight, y);
        ctx.stroke();
        ctx.fillStyle = "#ef4444";
        ctx.fillText(`RES ${lvl.toFixed(5)}`, width - pRight + 8, y + 3);
      });

      // Stop Loss line
      const slY = yPrice(prediction.stop_loss);
      ctx.strokeStyle = "#ef4444";
      ctx.lineWidth = 1.5;
      ctx.setLineDash([2, 2]);
      ctx.beginPath();
      ctx.moveTo(pLeft, slY);
      ctx.lineTo(width - pRight, slY);
      ctx.stroke();
      ctx.fillStyle = "#ef4444";
      ctx.fillText(`SL ${prediction.stop_loss.toFixed(5)}`, width - pRight + 8, slY + 3);

      // Take Profit 1 line
      const tp1Y = yPrice(prediction.take_profit_1);
      ctx.strokeStyle = "#10b981";
      ctx.lineWidth = 1.5;
      ctx.setLineDash([2, 2]);
      ctx.beginPath();
      ctx.moveTo(pLeft, tp1Y);
      ctx.lineTo(width - pRight, tp1Y);
      ctx.stroke();
      ctx.fillStyle = "#10b981";
      ctx.fillText(`TP1 ${prediction.take_profit_1.toFixed(5)}`, width - pRight + 8, tp1Y + 3);

      ctx.setLineDash([]); // Reset line dash
    }

    // Draw Candlesticks & Volume
    candles.forEach((c, idx) => {
      const x = pLeft + idx * candleSlotW + candleSlotW / 2;
      const isUp = c.close >= c.open;
      const color = isUp ? "#10b981" : "#ef4444";

      // Volume bar
      const volBarH = (c.volume / (maxVol || 1)) * volH;
      const volY = pTop + priceH + 10 + volH - volBarH;
      ctx.fillStyle = isUp ? "rgba(16, 185, 129, 0.2)" : "rgba(239, 68, 68, 0.2)";
      ctx.fillRect(x - candleW / 2, volY, candleW, volBarH);

      // Wick
      ctx.strokeStyle = color;
      ctx.lineWidth = 1.2;
      ctx.beginPath();
      ctx.moveTo(x, yPrice(c.high));
      ctx.lineTo(x, yPrice(c.low));
      ctx.stroke();

      // Body
      const bodyTop = yPrice(Math.max(c.open, c.close));
      const bodyBottom = yPrice(Math.min(c.open, c.close));
      const bodyH = Math.max(1.5, bodyBottom - bodyTop);

      ctx.fillStyle = color;
      ctx.fillRect(x - candleW / 2, bodyTop, candleW, bodyH);
    });

    // Draw EMA 20 (Blue) & EMA 50 (Amber)
    const drawEma = (arr: (number | null)[], strokeColor: string) => {
      ctx.strokeStyle = strokeColor;
      ctx.lineWidth = 1.5;
      ctx.beginPath();
      let started = false;

      arr.forEach((val, idx) => {
        if (val !== null) {
          const x = pLeft + idx * candleSlotW + candleSlotW / 2;
          const y = yPrice(val);
          if (!started) {
            ctx.moveTo(x, y);
            started = true;
          } else {
            ctx.lineTo(x, y);
          }
        }
      });
      ctx.stroke();
    };

    drawEma(emaData.ema20, "#38bdf8"); // Sky blue for EMA 20
    drawEma(emaData.ema50, "#f59e0b"); // Amber for EMA 50

    // Draw Crosshair & Active Inspector
    if (mousePos && mousePos.x >= pLeft && mousePos.x <= width - pRight && mousePos.y >= pTop && mousePos.y <= pTop + priceH) {
      ctx.strokeStyle = "rgba(148, 163, 184, 0.4)";
      ctx.setLineDash([3, 3]);
      ctx.lineWidth = 1;

      // Vertical line
      ctx.beginPath();
      ctx.moveTo(mousePos.x, pTop);
      ctx.lineTo(mousePos.x, height - pBottom);
      ctx.stroke();

      // Horizontal line
      ctx.beginPath();
      ctx.moveTo(pLeft, mousePos.y);
      ctx.lineTo(width - pRight, mousePos.y);
      ctx.stroke();

      ctx.setLineDash([]);

      // Price badge on Y axis
      const hoveredPrice = maxP - ((mousePos.y - pTop) / priceH) * (maxP - minP);
      ctx.fillStyle = "#1e293b";
      ctx.fillRect(width - pRight, mousePos.y - 9, pRight - 5, 18);
      ctx.strokeStyle = "#475569";
      ctx.strokeRect(width - pRight, mousePos.y - 9, pRight - 5, 18);
      ctx.fillStyle = "#ffffff";
      ctx.fillText(hoveredPrice.toFixed(5), width - pRight + 6, mousePos.y + 3);
    }
  }, [candles, prediction, mousePos, emaData]);

  // Handle Mouse movement for tooltips
  const handleMouseMove = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    setMousePos({ x, y });

    const pLeft = 10;
    const pRight = 75;
    const chartW = rect.width - pLeft - pRight;
    const slotW = chartW / candles.length;
    const idx = Math.floor((x - pLeft) / slotW);

    if (idx >= 0 && idx < candles.length) {
      setHoverIndex(idx);
    } else {
      setHoverIndex(null);
    }
  };

  const handleMouseLeave = () => {
    setMousePos(null);
    setHoverIndex(null);
  };

  const activeCandle = hoverIndex !== null ? candles[hoverIndex] : candles[candles.length - 1];

  return (
    <div className="relative w-full h-full flex flex-col bg-surface border border-border rounded-xl overflow-hidden">
      {/* Top Bar Info */}
      <div className="flex flex-wrap items-center justify-between px-4 py-2 bg-surface-raised/60 border-b border-border text-xs">
        <div className="flex items-center gap-4">
          <div className="font-bold text-slate-100 flex items-center gap-1.5 font-mono text-sm">
            <span>{pair}</span>
            <span className="text-[10px] px-1.5 py-0.5 rounded bg-accent/20 text-accent font-semibold">
              {timeframe}
            </span>
          </div>

          {activeCandle && (
            <div className="hidden sm:flex items-center gap-3 font-mono text-[11px] text-slate-300">
              <span>O: <strong className="text-slate-100">{activeCandle.open.toFixed(5)}</strong></span>
              <span>H: <strong className="text-emerald-400">{activeCandle.high.toFixed(5)}</strong></span>
              <span>L: <strong className="text-red-400">{activeCandle.low.toFixed(5)}</strong></span>
              <span>C: <strong className={activeCandle.close >= activeCandle.open ? "text-emerald-400" : "text-red-400"}>
                {activeCandle.close.toFixed(5)}
              </strong></span>
              <span>Vol: <strong className="text-slate-400">{activeCandle.volume.toFixed(0)}</strong></span>
            </div>
          )}
        </div>

        {/* Legend */}
        <div className="flex items-center gap-3 text-[11px]">
          <span className="flex items-center gap-1 text-sky-400 font-mono">
            <span className="w-2 h-0.5 bg-sky-400"></span> EMA20
          </span>
          <span className="flex items-center gap-1 text-amber-400 font-mono">
            <span className="w-2 h-0.5 bg-amber-400"></span> EMA50
          </span>
          {prediction && (
            <>
              <span className="flex items-center gap-1 text-emerald-400 font-mono">
                <span className="w-2 h-0.5 border-t border-dashed border-emerald-400"></span> TP
              </span>
              <span className="flex items-center gap-1 text-red-400 font-mono">
                <span className="w-2 h-0.5 border-t border-dashed border-red-400"></span> SL
              </span>
            </>
          )}
        </div>
      </div>

      {/* Canvas container */}
      <div ref={containerRef} className="relative flex-1 w-full min-h-[420px]">
        <canvas
          ref={canvasRef}
          onMouseMove={handleMouseMove}
          onMouseLeave={handleMouseLeave}
          className="w-full h-full cursor-crosshair block"
        />
      </div>
    </div>
  );
};
