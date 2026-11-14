import glob, os
import numpy as np
import pandas as pd


def ema(s, n):
    return s.ewm(span=n, adjust=False).mean()


def prep(df):
    c, h, l = df.close, df.high, df.low
    pc = c.shift()
    tr = pd.concat([h - l, (h - pc).abs(), (l - pc).abs()], axis=1).max(axis=1)
    w = lambda s: s.ewm(alpha=1 / 14, adjust=False).mean()
    df["atr"] = w(tr)
    up, dn = h.diff(), -l.diff()
    pdm = pd.Series(np.where((up > dn) & (up > 0), up, 0.0), index=df.index)
    mdm = pd.Series(np.where((dn > up) & (dn > 0), dn, 0.0), index=df.index)
    pdi, mdi = 100 * w(pdm) / df.atr, 100 * w(mdm) / df.atr
    df["adx"] = w(100 * (pdi - mdi).abs() / (pdi + mdi))
    d = c.diff()
    df["rsi"] = 100 - 100 / (1 + w(d.clip(lower=0)) / w(-d.clip(upper=0)))
    df["e20"], df["e50"], df["e200"] = ema(c, 20), ema(c, 50), ema(c, 200)
    m = ema(c, 12) - ema(c, 26)
    df["mh"] = m - ema(m, 9)
    ma, sd = c.rolling(20).mean(), c.rolling(20).std()
    df["bu"], df["bl"] = ma + 2 * sd, ma - 2 * sd
    df["hh"], df["ll"] = h.rolling(20).max().shift(), l.rolling(20).min().shift()
    df["atr50"] = df.atr.rolling(50).mean()
    return df


def strategies(df):
    c = df.close
    up, dn = df.e50 > df.e200, df.e50 < df.e200
    S = {}
    S["Trend Pullback"] = np.where(up & (df.adx > 20) & (df.rsi > 40) & (df.rsi.shift() <= 40), 1,
                          np.where(dn & (df.adx > 20) & (df.rsi < 60) & (df.rsi.shift() >= 60), -1, 0))
    L = (df.e20 > df.e50) & up & (df.mh > 0) & (df.adx > 25)
    Sh = (df.e20 < df.e50) & dn & (df.mh < 0) & (df.adx > 25)
    S["Trend Flow"] = np.where(L & ~L.shift(fill_value=False), 1,
                      np.where(Sh & ~Sh.shift(fill_value=False), -1, 0))
    ex = df.atr > 1.2 * df.atr50
    S["Vol Breakout"] = np.where(ex & (c > df.hh) & up, 1, np.where(ex & (c < df.ll) & dn, -1, 0))
    S["Range Sweep"] = np.where((df.low < df.bl) & (c > df.bl) & (df.rsi < 35), 1,
                       np.where((df.high > df.bu) & (c < df.bu) & (df.rsi > 65), -1, 0))
    return S


def spread_for(sym):
    # assumed average spread in price units (edit to match your broker)
    if "XAU" in sym:
        return 0.30
    if "JPY" in sym:
        return 0.015
    return 0.00012


def sim(df, sig, spread, k=1.5, m=3.0, maxbars=96):
    o, h, l, c, a = (df[x].values for x in ("open", "high", "low", "close", "atr"))
    t = df.time.values
    out, i, n = [], 210, len(df)
    while i < n - 2:
        d = sig[i]
        if d == 0 or not a[i] > 0:
            i += 1
            continue
        e, sl, tp = o[i + 1], k * a[i], m * a[i]
        R, j, end = None, i + 1, min(i + 1 + maxbars, n)
        while j < end:
            hit_sl = l[j] <= e - sl if d == 1 else h[j] >= e + sl
            hit_tp = h[j] >= e + tp if d == 1 else l[j] <= e - tp
            if hit_sl:  # SL first when both hit in one candle (conservative)
                R = -1.0
                break
            if hit_tp:
                R = m / k
                break
            j += 1
        if R is None:
            j = end - 1
            R = d * (c[j] - e) / sl
        R -= spread / sl
        out.append((t[i + 1], R))
        i = j + 1
    return out


def stats(R):
    R = np.array(R, dtype=float)
    if len(R) == 0:
        return {"n": 0}
    w, ls = R[R > 0].sum(), -R[R <= 0].sum()
    eq = np.cumsum(R)
    dd = (np.maximum.accumulate(eq) - eq).max()
    return {"n": int(len(R)), "wr": round(float(100 * (R > 0).mean()), 1),
            "pf": round(float(w / ls), 2) if ls > 0 else 99.0,
            "exp": round(float(R.mean()), 3), "tot": round(float(R.sum()), 1),
            "dd": round(float(dd), 1)}


def run_all(folder, k=1.5, m=3.0):
    res = []
    for f in sorted(glob.glob(folder + "/*.csv")):
        sym = os.path.basename(f).split("_")[0]
        df = pd.read_csv(f)
        df["time"] = pd.to_datetime(df.time.astype(str).str.replace(".", "-", regex=False))
        df = df.drop_duplicates("time").sort_values("time").reset_index(drop=True)
        if len(df) < 1500:
            continue
        df = prep(df)
        cut = df.time.iloc[int(len(df) * 2 / 3)]
        for name, sig in strategies(df).items():
            tr = sim(df, sig, spread_for(sym), k, m)
            ins = [r for t, r in tr if t < np.datetime64(cut)]
            oos = [r for t, r in tr if t >= np.datetime64(cut)]
            so, si = stats(oos), stats(ins)
            ok = bool(so["n"] >= 30 and so.get("pf", 0) > 1.1 and si.get("pf", 0) > 1.0)
            res.append({"sym": sym, "strat": name, "is": si, "oos": so, "ok": ok,
                        "bars": len(df), "from": str(df.time.iloc[0])[:10], "to": str(df.time.iloc[-1])[:10]})
    res.sort(key=lambda r: r["oos"].get("pf", 0), reverse=True)
    return res
