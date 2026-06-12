import os
os.environ["NO_PROXY"] ="gtimg.cn,qq.com,sina.com.cn,sinajs.cn,eastmoney.com"
import akshare as ak
from fastapi import FastAPI
from backtest import backtest_metrics
app = FastAPI()  #造一个web应用对象

@app.get("/indicators")
def indicators(symbol: str = "sh600519"):
    df = ak.stock_zh_a_hist_tx(symbol= symbol)
    df["MA5"] = df["close"].rolling(window=5).mean()
    df["pct_chg"] = df["close"].pct_change() * 100

    result = df[["date", "close", "MA5", "pct_chg"]].tail(10).to_dict(orient="records")
    return result


@app.get("/backtest")
def backtest(symbol: str = "sh600519"):
    return backtest_metrics(symbol)