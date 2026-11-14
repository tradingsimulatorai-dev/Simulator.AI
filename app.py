import hmac, os, threading
from flask import Flask, jsonify, request
from backtest import run_all

app = Flask(__name__)
DATA = os.environ.get("DATA_DIR", "data")
KEY = os.environ.get("API_KEY", "")
os.makedirs(DATA, exist_ok=True)
STATE = {"status": "idle", "results": [], "error": ""}


def authed():
    sent = request.headers.get("X-Key") or request.form.get("key") or ""
    return bool(KEY) and hmac.compare_digest(sent, KEY)


def clean(s):
    return "".join(ch for ch in s if ch.isalnum())


@app.post("/ingest")  # called by the MT4 EA
def ingest():
    if not authed():
        return "forbidden", 403
    sym = clean(request.args.get("symbol", ""))
    if not sym:
        return "no symbol", 400
    p = f"{DATA}/{sym}_M15.csv"
    mode = "w" if request.args.get("reset") == "1" or not os.path.exists(p) else "a"
    with open(p, mode) as f:
        if mode == "w":
            f.write("time,open,high,low,close,volume\n")
        f.write(request.get_data(as_text=True).strip() + "\n")
    return "ok"


@app.post("/upload")  # manual CSV upload from the page
def upload():
    if not authed():
        return "forbidden", 403
    n = 0
    for f in request.files.getlist("f"):
        sym = clean(f.filename.split("_")[0])
        if sym:
            f.save(f"{DATA}/{sym}_M15.csv")
            n += 1
    return f"{n} file(s) saved"


@app.post("/run")
def run():
    if not authed():
        return "forbidden", 403
    if STATE["status"] == "running":
        return "already running"

    def job():
        STATE.update(status="running", error="")
        try:
            STATE["results"] = run_all(DATA)
            STATE["status"] = "done"
        except Exception as e:
            STATE.update(status="error", error=str(e))

    threading.Thread(target=job, daemon=True).start()
    return "started"


@app.get("/state")
def state():
    return jsonify(STATE)


PAGE = """<!doctype html><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1"><title>Strategy backtests</title>
<style>
body{font:15px/1.5 system-ui,sans-serif;margin:0;padding:16px;background:#f6f7f9;color:#1d2433}
h1{font-size:20px;margin:0 0 12px}
.bar{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin-bottom:12px}
input,button{font:inherit;padding:8px 10px;border:1px solid #c5cad3;border-radius:6px;background:#fff}
button{background:#1d2433;color:#fff;border-color:#1d2433;cursor:pointer}
.w{overflow-x:auto}table{border-collapse:collapse;width:100%;min-width:560px;background:#fff}
th,td{padding:7px 9px;border-bottom:1px solid #e3e6ec;text-align:right;white-space:nowrap}
th:nth-child(-n+2),td:nth-child(-n+2){text-align:left}
.g{color:#0f7b3f;font-weight:600}.r{color:#b3261e}
</style>
<h1>Strategy backtests (15m, ATR stop and target)</h1>
<div class=bar>
<input id=k type=password placeholder="API key">
<input id=f type=file multiple accept=.csv>
<button onclick=up()>Upload CSV</button>
<button onclick=run()>Run backtest</button>
<span id=s></span></div>
<div class=w><table id=t></table></div>
<p>Win rate and PF are on unseen data (last third of the period). A check mark needs 30+ trades and PF above 1.1 there, and PF above 1 in the first part.</p>
<script>
const key=()=>document.getElementById('k').value;
async function post(u,fd){fd.append('key',key());return (await fetch(u,{method:'POST',body:fd})).text()}
async function up(){const fd=new FormData();for(const x of f.files)fd.append('f',x);s.textContent=await post('/upload',fd)}
async function run(){s.textContent=await post('/run',new FormData())}
async function load(){
 const d=await (await fetch('/state')).json();
 s.textContent=d.status+(d.error?': '+d.error:'');
 let h='<tr><th>Pair<th>Strategy<th>Trades<th>Win %<th>PF<th>Avg R<th>Max DD (R)<th>Earlier PF<th>Pass</tr>';
 for(const r of d.results){const o=r.oos;
  h+=`<tr><td>${r.sym}<td>${r.strat}<td>${o.n}<td>${o.wr??'-'}<td>${o.pf??'-'}<td>${o.exp??'-'}<td>${o.dd??'-'}<td>${r.is.pf??'-'}<td class=${r.ok?'g':'r'}>${r.ok?'yes':'no'}`}
 t.innerHTML=h}
setInterval(load,3000);load();
</script>"""


@app.get("/")
def home():
    return PAGE
