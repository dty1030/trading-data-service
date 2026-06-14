import os

os.environ["NO_PROXY"] = "gtimg.cn,qq.com,sina.com.cn, sinajs.cn, eastmoney.com"
import akshare as ak

def strategy_signals(symbol: str):

    df = ak.stock_zh_a_hist_tx(symbol)
    df["阳线"] = df["close"] > df["open"]
    df["阴线"] = df["close"] < df["open"]
    df["量比"] = df["amount"] / df["amount"].shift(1)
    df["倍量柱"] = df["阳线"] & (df["量比"] >= 1.45)

    last = df.iloc[-1]

    streak = 0
    for v in reversed(df["阴线"].tolist()):
        if v:
            streak += 1
        else:
            break

    return {
        "symbol": symbol,
        "日期": last["date"],
        "今日阳线": bool(last["阳线"]),
        "今日量比": round(float(last["量比"]), 2),
        "今日倍量柱": bool(last["倍量柱"]),
        "连续阴线天数": int(streak),
        "触发原则1_倍量柱重点关注": bool(last["倍量柱"]),
        "触发原则2_连续4阴谨慎看多": streak >= 4,
    }
