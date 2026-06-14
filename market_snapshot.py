import os
os.environ["NO_PROXY"] ="eastmoney.com,.eastmoney.com,82.push2.eastmoney.com"

import akshare as ak

def market_snapshot(symbol: str = "sh600519"):
    df = ak.stock_zh_a_spot()
    row = df[df["代码"] == symbol]

    records = row.head(1).to_dict(orient="records")
    if not records:
        return {
            "symbol": symbol,
            "error": "stock not found"
        }

    return records[0]