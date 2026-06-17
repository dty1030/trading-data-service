
import os
os.environ["NO_PROXY"] ="gtimg.cn,qq.com,sina.com.cn,sinajs.cn,eastmoney.com"
import pandas as pd
import akshare as ak
from typing import List, Optional


def getIndicators(
        symbol: str = "sh600519",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        ma: Optional[List[int]] = None,
        limit: int = 10
):
    if ma is None:
        ma = [5, 10, 20]
    # 1. 获取历史 K 线
    df = ak.stock_zh_a_hist_tx(symbol=symbol)

    # 2. 统一日期类型，方便后面按时间过滤
    df["date"] = pd.to_datetime(df["date"])

    # 3. 基础涨跌幅
    df["pct_chg"] = df["close"].pct_change() * 100

    # 4. K 线阴阳
    df["is_bullish"] = df["close"] > df["open"]
    df["is_bearish"] = df["close"] < df["open"]

    # 5. 量比：今天成交额 / 前一天成交额
    df["volume_ratio"] = df["amount"] / df["amount"].shift(1)

    # 6. 动态计算均线
    for n in ma:
        ma_col = f"MA{n}"
        above_col = f"above_MA{n}"

        df[ma_col] = df["close"].rolling(window=n).mean()
        df[above_col] = df["close"] > df[ma_col]

    # 7. 先算指标，再过滤时间段
    if start_date:
        df = df[df["date"] >= pd.to_datetime(start_date)]

    if end_date:
        df = df[df["date"] <= pd.to_datetime(end_date)]

    # 8. 如果没有传时间范围，就默认取最近 limit 条
    if not start_date and not end_date:
        df = df.tail(limit)

    # 9. 组织返回字段
    base_columns = [
        "date",
        "open",
        "high",
        "low",
        "close",
        "amount",
        "pct_chg",
        "volume_ratio",
        "is_bullish",
        "is_bearish",
    ]

    ma_columns = []
    for n in ma:
        ma_columns.append(f"MA{n}")
        ma_columns.append(f"above_MA{n}")

    columns = base_columns + ma_columns

    # 10. 日期转字符串
    result_df = df[columns].copy()
    result_df["date"] = result_df["date"].dt.strftime("%Y-%m-%d")

    # 11. 处理 NaN，否则 JSON 可能报错
    result_df = result_df.astype(object).where(pd.notna(result_df), None)

    return result_df.to_dict(orient="records")