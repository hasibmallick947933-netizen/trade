"""
Forex AI Context-Grounded Conversational Analyst
Provides natural language reasoning grounded in current quantitative analysis,
market structure, macro surprises, and risk factors, avoiding market hallucinations.
"""

from typing import Dict, Any, List
import re

from backend.app.services.prediction_engine import PredictionEngine
from backend.app.services.currency_heatmap import CurrencyHeatmapEngine


class ForexAIChatAssistant:
    """Conversational agent grounded strictly on real-time platform metrics."""

    def __init__(self, pred_engine: PredictionEngine, heatmap_engine: CurrencyHeatmapEngine):
        self.pred_engine = pred_engine
        self.heatmap_engine = heatmap_engine

    async def respond(self, query: str, active_pair: str = "EUR/USD", timeframe: str = "1H") -> Dict[str, Any]:
        """
        Synthesizes an intelligent, structured financial response to the trader's query.
        """
        q = query.lower()
        pred = await self.pred_engine.generate_prediction(active_pair, timeframe)
        heatmap = await self.heatmap_engine.calculate_strength(timeframe)
        macro = self.pred_engine.macro_engine.get_pair_macro_bias(active_pair)
        yields = self.pred_engine.macro_engine.get_bond_yields_and_cross_assets()

        response_text = ""
        citations = []

        # 1. "Why is [PAIR] bullish/bearish?" or "Why buy/sell?"
        if any(w in q for w in ["why", "reason", "bullish", "bearish", "rationale", "conclusion"]):
            factors_s = "\n".join([f"  • {f}" for f in pred["factors_supporting"]])
            factors_o = "\n".join([f"  • {f}" for f in pred["factors_opposing"]])

            response_text = (
                f"### Analysis for **{active_pair} ({timeframe})**\n\n"
                f"**Directional State**: `{pred['signal_state']}` (Confidence: **{pred['confidence']}%**)\n"
                f"**Probabilities**: BUY **{pred['prob_buy']}%** | SELL **{pred['prob_sell']}%** | HOLD **{pred['prob_hold']}%**\n\n"
                f"**Market Regime**: {pred['market_regime']}\n\n"
                f"#### Core Factors Supporting Prediction:\n{factors_s}\n\n"
                f"#### Risk / Counter-Factors:\n{factors_o}\n\n"
                f"**Summary Conclusion**: {pred['explanation_summary']}"
            )
            citations = ["Technical Indicators", "Market Structure (BOS/CHOCH)", "Macro Bias", "Multi-Timeframe Confluence"]

        # 2. "Why should I avoid this trade?" or "risks"
        elif any(w in q for w in ["avoid", "risk", "danger", "caution", "downside"]):
            factors_o = "\n".join([f"  • {f}" for f in pred["factors_opposing"]])
            response_text = (
                f"### Trade Risk Breakdown for **{active_pair}**\n\n"
                f"Before executing, take note of the following critical hazards:\n\n"
                f"{factors_o}\n\n"
                f"• **Volatility Factor**: Expected volatility is **{pred['expected_volatility_pct']}%**.\n"
                f"• **Hard Stop Loss**: Position invalidation level is strictly at **{pred['stop_loss']}**.\n"
                f"• **Sizing Ceiling**: Do not exceed **{pred['suggested_lot_size']} lots** to keep risk capped at 1% of equity."
            )
            citations = ["Risk Engine", "ATR Volatility Matrix", "Order Book Liquidity"]

        # 3. "What are the strongest currencies today?" or "currency strength" / "heatmap"
        elif any(w in q for w in ["strongest", "weakest", "currency strength", "heatmap", "strong", "weak"]):
            ranked_str = "\n".join([f"  {i+1}. **{r['currency']}**: `{r['score']:+0.2f}`" for i, r in enumerate(heatmap["rankings"])])
            response_text = (
                f"### Currency Relative Strength Matrix ({timeframe})\n\n"
                f"{ranked_str}\n\n"
                f"• **Top Gainer / Strongest Currency**: **{heatmap['strongest']}**\n"
                f"• **Underperformer / Weakest Currency**: **{heatmap['weakest']}**\n"
                f"• **Optimal Pair Divergence**: Consider **{heatmap['best_long_opportunity']}** for maximum relative directional momentum."
            )
            citations = ["Currency Strength Engine", "Cross-Pair Basket Analysis"]

        # 4. "Compare EUR/USD and GBP/USD"
        elif "compare" in q or ("eur/usd" in q and "gbp/usd" in q):
            pred_gbp = await self.pred_engine.generate_prediction("GBP/USD", timeframe)
            response_text = (
                f"### Comparative Overview: EUR/USD vs GBP/USD ({timeframe})\n\n"
                f"| Metric | **EUR/USD** | **GBP/USD** |\n"
                f"| :--- | :--- | :--- |\n"
                f"| Current Price | {pred['current_price']} | {pred_gbp['current_price']} |\n"
                f"| Signal State | `{pred['signal_state']}` | `{pred_gbp['signal_state']}` |\n"
                f"| BUY Probability | **{pred['prob_buy']}%** | **{pred_gbp['prob_buy']}%** |\n"
                f"| SELL Probability | **{pred['prob_sell']}%** | **{pred_gbp['prob_sell']}%** |\n"
                f"| Confidence | {pred['confidence']}% | {pred_gbp['confidence']}% |\n"
                f"| Market Regime | {pred['market_regime']} | {pred_gbp['market_regime']} |\n"
                f"| Risk/Reward | {pred['risk_reward_ratio']} | {pred_gbp['risk_reward_ratio']} |\n\n"
                f"**Synthesis**: {'EUR/USD' if pred['confidence'] > pred_gbp['confidence'] else 'GBP/USD'} displays cleaner structural conviction currently."
            )
            citations = ["Cross-Pair Signal Engine", "Comparative Risk Model"]

        # 5. Default General Intelligence Query
        else:
            response_text = (
                f"### Quantitative Summary for **{active_pair}**\n\n"
                f"Current stance is **{pred['signal_state']}** at {pred['current_price']}.\n"
                f"• Probabilities: BUY **{pred['prob_buy']}%**, SELL **{pred['prob_sell']}%**, HOLD **{pred['prob_hold']}%**.\n"
                f"• Nearest Support: **{pred['support_levels'][-1] if pred['support_levels'] else 'N/A'}** | Nearest Resistance: **{pred['resistance_levels'][0] if pred['resistance_levels'] else 'N/A'}**.\n"
                f"• Multi-Timeframe Confluence: **{pred['multi_timeframe']['alignment']}**.\n\n"
                f"Feel free to ask me:\n"
                f"- *'Why is this pair bullish/bearish?'*\n"
                f"- *'What are the main trade risks?'*\n"
                f"- *'What are the strongest currencies right now?'*\n"
                f"- *'Compare EUR/USD and GBP/USD'*."
            )
            citations = ["Live Model State", "Forex AI Core Engine"]

        return {
            "query": query,
            "pair": active_pair,
            "timeframe": timeframe,
            "response": response_text,
            "citations": citations,
        }
