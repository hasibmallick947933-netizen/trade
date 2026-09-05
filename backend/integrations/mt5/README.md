# Forex AI — MetaTrader 4 / MetaTrader 5 Bridge

This bridge connects your **MetaTrader 4 (MT4)** or **MetaTrader 5 (MT5)** terminal directly to the **Forex AI Python Backend**, streaming:
- **Calibrated Probabilities**: $P(\text{BUY}), P(\text{SELL}), P(\text{HOLD})$
- **Confidence Score & Market Regime**
- **Dynamic ATR Stop-Loss & Take-Profit Targets**
- **Automated or Manual Signal Execution**

---

## 3-Step Setup Instructions

### Step 1: Whitelist the Localhost API in MetaTrader
1. Open MT4 or MT5.
2. In the top menu, navigate to: `Tools` ➔ `Options` ➔ `Expert Advisors`.
3. Check the box: **"Allow WebRequest for listed URL:"**.
4. Click the green `+` icon and add:
   ```
   http://localhost:8000
   ```
5. Click **OK**.

---

### Step 2: Install the Expert Advisor in MetaTrader
1. In MT4/MT5, click `File` ➔ `Open Data Folder`.
2. Go to the directory:
   - For MT5: `MQL5/Experts/`
   - For MT4: `MQL4/Experts/`
3. Copy the file [`ForexAI_Bridge.mq5`](./ForexAI_Bridge.mq5) into that folder.
4. Open the **MetaEditor** (press `F4` in MetaTrader).
5. Open `ForexAI_Bridge.mq5` and press **Compile** (`F7`).
   - You should see `0 errors, 0 warnings`.

---

### Step 3: Attach to Chart
1. Return to your MetaTrader terminal.
2. In the **Navigator** panel (`Ctrl + N`), expand **Expert Advisors**.
3. Drag **`ForexAI_Bridge`** onto any active chart (e.g. `EURUSD`, `GBPUSD`).
4. In the settings pop-up:
   - `InpApiUrl`: `http://localhost:8000/api/v1`
   - `InpEnableAutoTrade`:
     - `false` = Visual dashboard & on-chart alerts only (Recommended initially).
     - `true` = Automatic trade placement using Forex AI signals and SL/TP.
   - `InpMinConfidence`: `70.0` (Only trigger trades if AI confidence $\ge 70\%$).
5. Click **OK**.

---

## How It Works in Real-Time
1. Every 5 seconds, the EA queries:
   ```http
   GET http://localhost:8000/api/v1/predictions/latest?pair=EUR/USD&timeframe=1H
   ```
2. The EA draws a live quantitative HUD directly on the chart:
   ```
   ========================================
             FOREX AI QUANTITATIVE BRIDGE   
   ========================================
   Symbol / TF:    EURUSD (1H)
   AI Signal:      STRONG BUY
   Probabilities:  BUY 67.4% | SELL 21.2% | HOLD 11.4%
   Confidence:     74.2%
   Regime:         Strong Trend / Medium Volatility
   Target SL:      1.08210
   Target TP1:     1.09150
   Risk / Reward:  1 : 2.10
   Auto-Trading:   DISABLED (Visual / Alert Mode)
   ========================================
   ```
3. If auto-trading is turned on and a high-confidence signal triggers, it automatically places the position with exact Stop-Loss and Take-Profit brackets.
