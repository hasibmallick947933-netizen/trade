//+------------------------------------------------------------------+
//|                                              ForexAI_Bridge.mq5  |
//|                        Copyright 2026, FOREX AI Quantitative Lab |
//|                                             https://localhost:3000|
//+------------------------------------------------------------------+
#property copyright "FOREX AI Quantitative Lab"
#property link      "http://localhost:3000"
#property version   "1.00"
#property description "Bridges MT4/MT5 with Forex AI Python FastAPI Engine"
#property description "Streams calibrated probabilities, confidence, regimes & SL/TP"

#include <Trade\Trade.mqh>

//--- Input Parameters
input group "=== Forex AI API Configuration ==="
input string   InpApiUrl          = "https://trade-t1m8.onrender.com/api/v1"; // Forex AI API Base URL
input int      InpPollSeconds     = 5;                              // Polling Interval (seconds)

input group "=== Trading & Risk Filters ==="
input bool     InpEnableAutoTrade = false;                          // Enable Automated Execution (Default: Visual Only)
input double   InpMinConfidence   = 70.0;                           // Minimum Confidence Threshold (%)
input double   InpMinProb         = 60.0;                           // Minimum Directional Probability (%)
input double   InpLotSize         = 0.10;                           // Default Execution Lot Size
input ulong    InpMagicNumber     = 998811;                         // EA Magic Number

//--- Global Variables
CTrade         ExtTrade;
datetime       ExtLastPollTime = 0;
string         ExtSignalState = "INITIALIZING";
double         ExtProbBuy = 0.0;
double         ExtProbSell = 0.0;
double         ExtProbHold = 0.0;
double         ExtConfidence = 0.0;
string         ExtMarketRegime = "UNKNOWN";
double         ExtStopLoss = 0.0;
double         ExtTakeProfit = 0.0;
double         ExtSlPips = 20.0;
double         ExtTpPips = 40.0;
double         ExtRiskReward = 0.0;

//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit()
{
   ExtTrade.SetExpertMagicNumber(InpMagicNumber);
   EventSetTimer(InpPollSeconds);
   Print("Forex AI Bridge initialized for symbol: ", _Symbol);
   
   // Fetch first snapshot immediately
   FetchForexAISignal();
   DrawDashboard();
   return(INIT_SUCCEEDED);
}

//+------------------------------------------------------------------+
//| Expert deinitialization function                                 |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
   EventKillTimer();
   ObjectsDeleteAll(0, "ForexAI_");
   Comment("");
}

//+------------------------------------------------------------------+
//| Timer event handler                                              |
//+------------------------------------------------------------------+
void OnTimer()
{
   FetchForexAISignal();
   DrawDashboard();
   
   if(InpEnableAutoTrade)
   {
      CheckAndExecuteTrades();
   }
}

//+------------------------------------------------------------------+
//| Convert MT5 Symbol to Standard Pair (e.g. EURUSD -> EUR/USD)    |
//+------------------------------------------------------------------+
string FormatPairName(string rawSymbol)
{
   string clean = rawSymbol;
   StringReplace(clean, ".m", "");
   StringReplace(clean, ".pro", "");
   StringReplace(clean, ".raw", "");
   
   if(StringLen(clean) == 6)
   {
      return StringSubstr(clean, 0, 3) + "/" + StringSubstr(clean, 3, 3);
   }
   return "EUR/USD";
}

//+------------------------------------------------------------------+
//| Convert MT5 Timeframe to Forex AI string (1H, 4H, 1D, etc.)      |
//+------------------------------------------------------------------+
string FormatTimeframe(ENUM_TIMEFRAMES tf)
{
   switch(tf)
   {
      case PERIOD_M1:  return "1M";
      case PERIOD_M5:  return "5M";
      case PERIOD_M15: return "15M";
      case PERIOD_M30: return "30M";
      case PERIOD_H1:  return "1H";
      case PERIOD_H4:  return "4H";
      case PERIOD_D1:  return "1D";
      default:         return "1H";
   }
}

//+------------------------------------------------------------------+
//| Simple JSON Field Extractor                                      |
//+------------------------------------------------------------------+
string ExtractJsonString(string json, string field)
{
   string key = "\"" + field + "\":";
   int pos = StringFind(json, key);
   if(pos < 0) return "";
   
   int start = pos + StringLen(key);
   // Skip whitespace and quote
   while(start < StringLen(json) && (StringGetCharacter(json, start) == ' ' || StringGetCharacter(json, start) == '\"'))
      start++;
      
   int end = start;
   while(end < StringLen(json) && StringGetCharacter(json, end) != '\"' && StringGetCharacter(json, end) != ',' && StringGetCharacter(json, end) != '}')
      end++;
      
   return StringSubstr(json, start, end - start);
}

double ExtractJsonDouble(string json, string field)
{
   string val = ExtractJsonString(json, field);
   return StringToDouble(val);
}

//+------------------------------------------------------------------+
//| Query Forex AI FastAPI REST Service                              |
//+------------------------------------------------------------------+
//+------------------------------------------------------------------+
//| Query Forex AI FastAPI REST Service                              |
//+------------------------------------------------------------------+
void FetchForexAISignal()
{
   string pair = FormatPairName(_Symbol);
   string tf = FormatTimeframe(Period());
   
   double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
   double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
   double mid = (bid > 0 && ask > 0) ? ((bid + ask) / 2.0) : 0.0;
   
   string url = InpApiUrl + "/predictions/latest?pair=" + pair + "&timeframe=" + tf;
   if(mid > 0)
   {
      url += "&current_price=" + DoubleToString(mid, _Digits);
   }
   
   char postData[];
   char resultData[];
   string resultHeaders;
   int timeout = 4000;
   
   ResetLastError();
   int res = WebRequest("GET", url, "", timeout, postData, resultData, resultHeaders);
   
   if(res == 200)
   {
      string response = CharArrayToString(resultData);
      ExtSignalState   = ExtractJsonString(response, "signal_state");
      ExtProbBuy       = ExtractJsonDouble(response, "prob_buy");
      ExtProbSell      = ExtractJsonDouble(response, "prob_sell");
      ExtProbHold      = ExtractJsonDouble(response, "prob_hold");
      ExtConfidence    = ExtractJsonDouble(response, "confidence");
      ExtMarketRegime  = ExtractJsonString(response, "market_regime");
      ExtRiskReward    = ExtractJsonDouble(response, "risk_reward_ratio");
      
      ExtSlPips        = ExtractJsonDouble(response, "sl_pips");
      ExtTpPips        = ExtractJsonDouble(response, "tp_pips");
      if(ExtSlPips <= 0) ExtSlPips = 20.0;
      if(ExtTpPips <= 0) ExtTpPips = 40.0;
      
      // Standard Pip Unit: 0.0001 for 4/5-digit pairs, 0.01 for 2/3-digit JPY pairs
      double pipUnit = (_Digits == 3 || _Digits == 5) ? _Point * 10 : _Point;
      if(pipUnit <= 0) pipUnit = 0.0001;
      
      // Anchor SL and TP directly to the broker's real-time chart prices
      if(ExtSignalState == "STRONG BUY" || ExtSignalState == "BUY" || ExtSignalState == "WEAK BUY")
      {
         // For BUY: Stop Loss is BELOW Ask, Take Profit is ABOVE Ask
         ExtStopLoss   = NormalizeDouble(ask - (ExtSlPips * pipUnit), _Digits);
         ExtTakeProfit = NormalizeDouble(ask + (ExtTpPips * pipUnit), _Digits);
      }
      else if(ExtSignalState == "STRONG SELL" || ExtSignalState == "SELL" || ExtSignalState == "WEAK SELL")
      {
         // For SELL: Stop Loss is ABOVE Bid, Take Profit is BELOW Bid
         ExtStopLoss   = NormalizeDouble(bid + (ExtSlPips * pipUnit), _Digits);
         ExtTakeProfit = NormalizeDouble(bid - (ExtTpPips * pipUnit), _Digits);
      }
      else // HOLD
      {
         ExtStopLoss   = NormalizeDouble(bid - (ExtSlPips * pipUnit), _Digits);
         ExtTakeProfit = NormalizeDouble(bid + (ExtTpPips * pipUnit), _Digits);
      }
      
      // Update on-chart visual levels
      UpdateChartPriceLines();
   }
   else
   {
      ExtSignalState = "DISCONNECTED";
      Print("WebRequest failed. Error code: ", GetLastError(), ". Check Options -> Allow WebRequest for: ", InpApiUrl);
   }
}

//+------------------------------------------------------------------+
//| Draw On-Chart Price Lines for SL and TP                          |
//+------------------------------------------------------------------+
void UpdateChartPriceLines()
{
   if(ExtStopLoss > 0)
   {
      if(ObjectFind(0, "ForexAI_SL") < 0)
      {
         ObjectCreate(0, "ForexAI_SL", OBJ_HLINE, 0, 0, ExtStopLoss);
         ObjectSetInteger(0, "ForexAI_SL", OBJPROP_COLOR, clrRed);
         ObjectSetInteger(0, "ForexAI_SL", OBJPROP_STYLE, STYLE_DASH);
         ObjectSetInteger(0, "ForexAI_SL", OBJPROP_WIDTH, 1);
         ObjectSetString(0, "ForexAI_SL", OBJPROP_TEXT, "Forex AI Target Stop Loss");
      }
      else
      {
         ObjectSetDouble(0, "ForexAI_SL", OBJPROP_PRICE, ExtStopLoss);
      }
   }
   
   if(ExtTakeProfit > 0)
   {
      if(ObjectFind(0, "ForexAI_TP") < 0)
      {
         ObjectCreate(0, "ForexAI_TP", OBJ_HLINE, 0, 0, ExtTakeProfit);
         ObjectSetInteger(0, "ForexAI_TP", OBJPROP_COLOR, clrLimeGreen);
         ObjectSetInteger(0, "ForexAI_TP", OBJPROP_STYLE, STYLE_DASH);
         ObjectSetInteger(0, "ForexAI_TP", OBJPROP_WIDTH, 1);
         ObjectSetString(0, "ForexAI_TP", OBJPROP_TEXT, "Forex AI Target Take Profit");
      }
      else
      {
         ObjectSetDouble(0, "ForexAI_TP", OBJPROP_PRICE, ExtTakeProfit);
      }
   }
}

//+------------------------------------------------------------------+
//| Draw On-Chart HUD Dashboard                                      |
//+------------------------------------------------------------------+
void DrawDashboard()
{
   double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
   double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);

   string text = "";
   text += "========================================\n";
   text += "          FOREX AI QUANTITATIVE BRIDGE   \n";
   text += "========================================\n";
   text += "Symbol / TF:    " + _Symbol + " (" + FormatTimeframe(Period()) + ")\n";
   text += "Live Market:    Bid: " + DoubleToString(bid, _Digits) + " | Ask: " + DoubleToString(ask, _Digits) + "\n";
   text += "AI Signal:      " + ExtSignalState + "\n";
   text += "Probabilities:  BUY " + DoubleToString(ExtProbBuy, 1) + "% | SELL " + DoubleToString(ExtProbSell, 1) + "% | HOLD " + DoubleToString(ExtProbHold, 1) + "%\n";
   text += "Confidence:     " + DoubleToString(ExtConfidence, 1) + "%\n";
   text += "Regime:         " + ExtMarketRegime + "\n";
   text += "Target SL:      " + DoubleToString(ExtStopLoss, _Digits) + "  [" + DoubleToString(ExtSlPips, 1) + " pips risk]\n";
   text += "Target TP1:     " + DoubleToString(ExtTakeProfit, _Digits) + "  [" + DoubleToString(ExtTpPips, 1) + " pips target]\n";
   text += "Risk / Reward:  1 : " + DoubleToString(ExtRiskReward, 2) + "\n";
   text += "Auto-Trading:   " + (InpEnableAutoTrade ? "ENABLED" : "DISABLED (Visual / Alert Mode)") + "\n";
   text += "========================================";

   Comment(text);
}

//+------------------------------------------------------------------+
//| Trade Execution Logic (When InpEnableAutoTrade is true)          |
//+------------------------------------------------------------------+
void CheckAndExecuteTrades()
{
   if(PositionsTotal() > 0) return; // Prevent multiple positions
   
   if(ExtConfidence < InpMinConfidence) return; // Confidence filter
   
   double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
   double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
   
   // Buy Trigger
   if((ExtSignalState == "STRONG BUY" || ExtSignalState == "BUY") && ExtProbBuy >= InpMinProb)
   {
      if(ExtStopLoss < ask && ExtTakeProfit > ask)
      {
         ExtTrade.Buy(InpLotSize, _Symbol, ask, ExtStopLoss, ExtTakeProfit, "Forex AI Buy Signal");
         Print("Forex AI executed BUY order at ", ask, " SL: ", ExtStopLoss, " TP: ", ExtTakeProfit);
      }
   }
   // Sell Trigger
   else if((ExtSignalState == "STRONG SELL" || ExtSignalState == "SELL") && ExtProbSell >= InpMinProb)
   {
      if(ExtStopLoss > bid && ExtTakeProfit < bid)
      {
         ExtTrade.Sell(InpLotSize, _Symbol, bid, ExtStopLoss, ExtTakeProfit, "Forex AI Sell Signal");
         Print("Forex AI executed SELL order at ", bid, " SL: ", ExtStopLoss, " TP: ", ExtTakeProfit);
      }
   }
}

//+------------------------------------------------------------------+
