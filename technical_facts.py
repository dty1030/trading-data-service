import os

os.environ["NO_PROXY"] ="gtimg.cn,qq.com,sina.com.cn,sinajs.cn,eastmoney.com,.eastmoney.com"

import akshare as ak

def technical_facts(symbol: str):
    df = ak.stock_zh_a_hist_tx(symbol=symbol)
    df["MA5"] = df["close"].rolling(window=5).mean()
    df["MA10"] = df["close"].rolling(window=10).mean()
    df["MA20"] = df["close"].rolling(window=20).mean()
    df["MA30"] = df["close"].rolling(window=30).mean()
    df["MA60"] = df["close"].rolling(window=60).mean()
    df["MA120"] = df["close"].rolling(window=120).mean()
    df["MA240"] = df["close"].rolling(window=240).mean()

    # 取最后一行，也就是最新一个交易日。
    last = df.iloc[-1]

    #  从最后一行里拿收盘价和 均线，并转成 Python 浮点数。
    close = float(last["close"])
    ma5 = float(last["MA5"])
    ma10 = float(last["MA10"])
    ma20 = float(last["MA20"])
    ma30 = float(last["MA30"])
    ma60 = float(last["MA60"])
    ma120 = float(last["MA120"])
    ma240 = float(last["MA240"])

    close_ma5_gap_pct = (close - ma5) / ma5 * 100
    close_ma10_gap_pct = (close - ma10) / ma10 * 100
    close_ma20_gap_pct = (close - ma20) / ma20 * 100
    close_ma30_gap_pct = (close - ma30) / ma30 * 100
    close_ma60_gap_pct = (close - ma60) / ma60 * 100
    close_ma120_gap_pct = (close - ma120) / ma120 * 100
    close_ma240_gap_pct = (close - ma240) / ma240 * 100

    return {
        "symbol": symbol,
        "date": str(last["date"]),
        "close": round(close, 2),

        "ma5": round(ma5, 3),
        "above_ma5": close > ma5,
        "close_ma5_gap_pct": round(close_ma5_gap_pct,
                                   2),

        "ma10": round(ma10, 3),
        "above_ma10": close > ma10,
        "close_ma10_gap_pct":
            round(close_ma10_gap_pct, 2),

        "ma20": round(ma20, 3),
        "above_ma20": close > ma20,
        "close_ma20_gap_pct":
            round(close_ma20_gap_pct, 2),

        "ma30": round(ma30, 3),
        "above_ma30": close > ma30,
        "close_ma30_gap_pct":
            round(close_ma30_gap_pct, 2),

        "ma60": round(ma60, 3),
        "above_ma60": close > ma60,
        "close_ma60_gap_pct":
            round(close_ma60_gap_pct, 2),

        "ma120": round(ma120, 3),
        "above_ma120": close > ma120,
        "close_ma120_gap_pct":
            round(close_ma120_gap_pct, 2),

        "ma240": round(ma240, 3),
        "above_ma240": close > ma240,
        "close_ma240_gap_pct":
            round(close_ma240_gap_pct, 2),
    }

