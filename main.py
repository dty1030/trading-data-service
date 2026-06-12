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

@app.get("/news")
def news(symbol: str, name: str):
    code = symbol[-6:] #取最后六位
    # 相当于List<Map>
    items = []
    try:
        df = ak.stock_news_em(symbol=code)
        for r in df.head(8).to_dict(orient="records"):
            items.append({"来源": "东财", "时间": r["发布时间"], "标题": r["新闻标题"]})
    except Exception as e:
        items.append({"来源": "东财", "错误":
            str(e)[:50]})

    try:
        #新浪只有 时间/内容
        df = ak.stock_info_global_sina()
        df = df[df["内容"].str.contains(name)].head(5)
        for r in df.to_dict(orient="records"):
            items.append({"来源": "新浪", "时间":
                r["时间"], "标题": r["内容"][:60]})
    except Exception as e:
        items.append({"来源": "新浪", "错误":
            str(e)[:50]})
    # 东财快讯
    try:
        df = ak.stock_info_global_em()
        df = df[df["摘要"].str.contains(name)].head(8)
        for r in df.head(8).to_dict(orient="records"):
            items.append({"来源": "东财快讯",
                          "标题": r["标题"],
                          "摘要": r["摘要"],
                          "时间": r["发布时间"], })
    except Exception as e:
        items.append({"来源": "东财快讯", "错误":
            str(e)[:50]})
    return items