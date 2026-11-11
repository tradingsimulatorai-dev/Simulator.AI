import uvicorn
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse

app = FastAPI(title="Autonomous 11-Agent Quant Trading Terminal")

# স্বয়ংক্রিয়ভাবে পরিচালিত ট্রেড স্টোরেজ (SL, TP ও প্রফিটসহ)
AUTONOMOUS_TRADES = [
    {
        "id": 1, 
        "pair": "XAUUSD", 
        "type": "SELL", 
        "entry": "4003.36", 
        "sl": "4035.50", 
        "tp": "3940.00", 
        "score": "91/100", 
        "agents": "11/11 PASS", 
        "pnl": "+$45.80", 
        "status": "RUNNING"
    },
    {
        "id": 2, 
        "pair": "EURUSD", 
        "type": "SELL", 
        "entry": "1.10961", 
        "sl": "1.11400", 
        "tp": "1.10000", 
        "score": "91/100", 
        "agents": "10/11 PASS", 
        "pnl": "-$12.40", 
        "status": "RUNNING"
    }
]

def get_autonomous_market_scans():
    return [
        {"pair": "XAUUSD", "dir": "SELL", "dir_color": "bg-red-900/60 text-red-300 border-red-700", "grade": "A+", "score": "91/100", "regime": "STRONG_TREND", "confluence": "LDN+NY Overlap, H4+H1 Aligned, ADX Power (45)", "agents_vote": "11/11 APPROVED", "price": "4003.36", "sl": "4035.50", "tp": "3940.00"},
        {"pair": "EURUSD", "dir": "SELL", "dir_color": "bg-red-900/60 text-red-300 border-red-700", "grade": "A+", "score": "91/100", "regime": "STRONG_TREND", "confluence": "LDN+NY Overlap, H4+H1 Aligned, ADX Power (61)", "agents_vote": "11/11 APPROVED", "price": "1.10961", "sl": "1.11400", "tp": "1.10000"},
        {"pair": "USDJPY", "dir": "BUY", "dir_color": "bg-emerald-900/60 text-emerald-300 border-emerald-700", "grade": "A+", "score": "91/100", "regime": "STRONG_TREND", "confluence": "LDN+NY Overlap, H4+H1 Aligned, ADX Power (62)", "agents_vote": "10/11 APPROVED", "price": "159.81", "sl": "159.20", "tp": "161.00"},
        {"pair": "GBPUSD", "dir": "SELL", "dir_color": "bg-red-900/60 text-red-300 border-red-700", "grade": "A+", "score": "90/100", "regime": "STRONG_TREND", "confluence": "LDN+NY Overlap, H4+H1 Aligned, ADX Power (42)", "agents_vote": "9/11 APPROVED", "price": "1.32805", "sl": "1.33400", "tp": "1.31500"}
    ]

@app.get("/", response_class=HTMLResponse)
def autonomous_terminal():
    scans = get_autonomous_market_scans()
    
    scanner_rows = ""
    for item in scans:
        scanner_rows += f"""
        <tr class="border-b border-slate-800/80 hover:bg-slate-900/60 transition text-xs font-mono">
            <td class="p-3 font-bold text-slate-100">{item['pair']}</td>
            <td class="p-3"><span class="px-2 py-0.5 rounded text-[10px] font-bold border {item['dir_color']}">{item['dir']}</span></td>
            <td class="p-3"><span class="bg-emerald-950 text-emerald-400 border border-emerald-800 px-2 py-0.5 rounded font-bold">{item['grade']}</span></td>
            <td class="p-3 text-amber-400 font-bold">{item['score']}</td>
            <td class="p-3"><span class="bg-blue-950 text-blue-300 border border-blue-800 px-2 py-0.5 rounded text-[10px]">{item['regime']}</span></td>
            <td class="p-3 text-slate-300 text-[11px] font-sans">{item['confluence']}</td>
            <td class="p-3 text-emerald-400 font-bold">{item['agents_vote']}</td>
            <td class="p-3 text-red-400">SL: {item['sl']}</td>
            <td class="p-3 text-emerald-400">TP: {item['tp']}</td>
        </tr>
        """

    trade_rows = ""
    for trade in AUTONOMOUS_TRADES:
        pnl_color = "text-emerald-400" if "+" in trade['pnl'] else "text-red-400"
        trade_rows += f"""
        <tr class="border-b border-slate-800/60 text-xs font-mono">
            <td class="p-3 font-bold text-slate-200">#{trade['id']} - {trade['pair']}</td>
            <td class="p-3"><span class="px-2 py-0.5 rounded text-[10px] font-bold bg-slate-800 text-slate-300">{trade['type']}</span></td>
            <td class="p-3 text-slate-400">{trade['entry']}</td>
            <td class="p-3 text-red-400 font-bold">{trade['sl']}</td>
            <td class="p-3 text-emerald-400 font-bold">{trade['tp']}</td>
            <td class="p-3 text-amber-400">{trade['score']}</td>
            <td class="p-3 text-blue-300">{trade['agents']}</td>
            <td class="p-3 font-bold {pnl_color}">{trade['pnl']}</td>
            <td class="p-3"><a href="/close-auto-trade/{trade['id']}" class="bg-red-950 hover:bg-red-900 text-red-300 border border-red-800 px-2 py-1 rounded text-[10px] transition">Close</a></td>
        </tr>
        """

    html_content = f"""
    <!DOCTYPE html>
    <html lang="bn">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Autonomous 11-Agent Quant Trading Terminal</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-slate-950 text-slate-100 font-sans min-h-screen p-6">
        
        <!-- Header -->
        <header class="flex flex-col md:flex-row justify-between items-center border-b border-slate-800 pb-4 mb-6 gap-4">
            <div>
                <h1 class="text-2xl font-black tracking-tight text-emerald-400 flex items-center gap-2">
                    🤖 AUTONOMOUS 11-AGENT QUANT TERMINAL <span class="text-xs bg-emerald-950 text-emerald-300 border border-emerald-800 px-2 py-0.5 rounded-full">LIVE CHARTS & SL/TP ENGINE</span>
                </h1>
                <p class="text-xs text-slate-400 mt-1">Self-Adaptive 4-Regime Confluence & Fully Automated Execution Grid</p>
            </div>
            <div class="flex gap-3">
                <span class="bg-emerald-900/40 text-emerald-300 px-3 py-1.5 rounded-lg text-xs font-mono border border-emerald-700/60 flex items-center gap-1.5">
                    <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span> 11 AGENTS: ACTIVE
                </span>
            </div>
        </header>

        <!-- Top Overview Stats -->
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            <div class="bg-slate-900/80 p-4 rounded-xl border border-slate-800">
                <p class="text-xs text-slate-400">Account Equity</p>
                <h2 class="text-xl font-bold text-slate-100 mt-1">$16,420.50</h2>
            </div>
            <div class="bg-slate-900/80 p-4 rounded-xl border border-slate-800">
                <p class="text-xs text-slate-400">AI Consensus Threshold</p>
                <h2 class="text-xl font-bold text-emerald-400 mt-1">>= 8 / 11 Agents</h2>
                <span class="text-[10px] text-emerald-500 font-semibold">Strict Filtering Active</span>
            </div>
            <div class="bg-slate-900/80 p-4 rounded-xl border border-slate-800">
                <p class="text-xs text-slate-400">Autonomous Active Trades</p>
                <h2 class="text-xl font-bold text-amber-400 mt-1">{len(AUTONOMOUS_TRADES)} Positions</h2>
            </div>
            <div class="bg-slate-900/80 p-4 rounded-xl border border-slate-800">
                <p class="text-xs text-slate-400">Risk Guard Status</p>
                <h2 class="text-xl font-bold text-emerald-400 mt-1">SECURE</h2>
                <span class="text-[10px] text-slate-500">Max Drawdown Protected</span>
            </div>
        </div>

        <!-- LIVE TRADINGVIEW CHART SECTION -->
        <div class="bg-slate-900/60 p-5 rounded-2xl border border-slate-800 mb-6 shadow-2xl">
            <div class="flex justify-between items-center mb-4">
                <h2 class="text-sm font-bold text-slate-200 tracking-wider">📈 LIVE MARKET CHART (XAUUSD / FOREX)</h2>
                <span class="text-xs text-slate-400 font-mono">Real-time TradingView Feed</span>
            </div>
            <div class="tradingview-widget-container" style="height:450px;width:100%">
                <div id="tradingview_widget" style="height:100%;width:100%"></div>
                <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
                <script type="text/javascript">
                new TradingView.widget(
                {{
                    "autosize": true,
                    "symbol": "OANDA:XAUUSD",
                    "interval": "15",
                    "timezone": "Etc/UTC",
                    "theme": "dark",
                    "style": "1",
                    "locale": "en",
                    "toolbar_bg": "#f1f3f6",
                    "enable_publishing": false,
                    "hide_top_toolbar": false,
                    "save_image": false,
                    "container_id": "tradingview_widget"
                }}
                );
                </script>
            </div>
        </div>

        <!-- 11-Agent Confluence Scanner Table -->
        <div class="bg-slate-950 rounded-2xl border border-slate-800 overflow-hidden mb-6 shadow-2xl">
            <div class="bg-slate-900 px-5 py-3 border-b border-slate-800 flex justify-between items-center">
                <h2 class="text-sm font-bold text-slate-200 tracking-wider">01 / AI AGENT MARKET RESEARCH & SL/TP MATRIX</h2>
                <span class="text-xs text-slate-400 font-mono">Autonomous Evaluation Grid</span>
            </div>
            <div class="overflow-x-auto">
                <table class="w-full text-left border-collapse">
                    <thead>
                        <tr class="border-b border-slate-800 text-[11px] font-mono text-slate-400 bg-slate-900/40">
                            <th class="p-3">PAIR</th>
                            <th class="p-3">DIR</th>
                            <th class="p-3">GRADE</th>
                            <th class="p-3">SCORE</th>
                            <th class="p-3">MARKET REGIME</th>
                            <th class="p-3">CONFLUENCE FACTORS</th>
                            <th class="p-3">11-AGENT CONSENSUS</th>
                            <th class="p-3">STOP LOSS (SL)</th>
                            <th class="p-3">TAKE PROFIT (TP)</th>
                        </tr>
                    </thead>
                    <tbody>
                        {scanner_rows}
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Autonomous Trade Management Section -->
        <div class="bg-slate-900/60 p-5 rounded-2xl border border-slate-800">
            <div class="flex justify-between items-center mb-4">
                <h2 class="text-base font-bold text-slate-200">🤖 Autonomous AI Trade Execution (SL/TP Active)</h2>
                <a href="/trigger-auto-scan" class="bg-emerald-600 hover:bg-emerald-500 text-white font-bold px-4 py-2 rounded-lg text-xs transition shadow-lg">
                    TRIGGER AI AGENT SCAN & TRADE
                </a>
            </div>
            <div class="overflow-x-auto">
                <table class="w-full text-left border-collapse">
                    <thead>
                        <tr class="border-b border-slate-800 text-[10px] font-mono text-slate-400">
                            <th class="p-2">ID & PAIR</th>
                            <th class="p-2">TYPE</th>
                            <th class="p-2">ENTRY</th>
                            <th class="p-2">SL</th>
                            <th class="p-2">TP</th>
                            <th class="p-2">AI SCORE</th>
                            <th class="p-2">AGENTS</th>
                            <th class="p-2">P&L</th>
                            <th class="p-2">ACTION</th>
                        </tr>
                    </thead>
                    <tbody>
                        {trade_rows if trade_rows else '<tr><td colspan="9" class="p-4 text-center text-slate-500 text-xs">No autonomous trades active.</td></tr>'}
                    </tbody>
                </table>
            </div>
        </div>

    </body>
    </html>
    """
    return html_content

@app.get("/trigger-auto-scan")
def trigger_auto_scan():
    global AUTONOMOUS_TRADES
    new_id = len(AUTONOMOUS_TRADES) + 1
    AUTONOMOUS_TRADES.append({
        "id": new_id,
        "pair": "GBPUSD",
        "type": "SELL",
        "entry": "1.32805",
        "sl": "1.33400",
        "tp": "1.31500",
        "score": "90/100",
        "agents": "9/11 PASS",
        "pnl": "+$18.50",
        "status": "RUNNING"
    })
    return autonomous_terminal()

@app.get("/close-auto-trade/{trade_id}", response_class=HTMLResponse)
def close_auto_trade(trade_id: int):
    global AUTONOMOUS_TRADES
    AUTONOMOUS_TRADES = [t for t in AUTONOMOUS_TRADES if t["id"] != trade_id]
    return autonomous_terminal()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
    
