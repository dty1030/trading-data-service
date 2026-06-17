
from strategy import strategy_signals

import akshare as ak
from fastapi import FastAPI
from backtest import backtest_metrics
from market_snapshot import market_snapshot
from technical_facts import technical_facts
from indicators import getIndicators
from fastapi import Query
from typing import List, Optional

app = FastAPI()  #造一个web应用对象
#最新价、今开、最高、最低、成交量、成交额、涨跌幅...
@app.get("/indicators")
def indicators(
        symbol: str = "sh600519",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        ma: List[int] = Query(default=[5, 10, 20]),
        limit: int = 10
):
    return getIndicators(symbol, start_date, end_date, ma, limit)


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


@app.get("/strategy")
def strategy(symbol: str):
    return strategy_signals(symbol)
#实时行情, 包含  最新价， 涨跌幅， 成交量， 成交额， 今开， 最高， 最低， 时间戳
@app.get("/market-snapshot")
def market_snapshot_api(symbol: str ="sh600519"):
      return market_snapshot(symbol)

@app.get("/technical-facts")
def technical_facts_api(symbol: str ="sh600519"):
      return technical_facts(symbol)


