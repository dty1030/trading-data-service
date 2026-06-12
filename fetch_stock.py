import akshare as ak
import os

os.environ["NO_PROXY"] = "gtimg.cn,qq.com,sina.com.cn,sinajs.cn,eastmoney.com"

df = ak.stock_zh_a_hist_tx(symbol="sh600519")

print(df.tail())
print(df.columns.tolist())
df["MA5"]  = df["close"].rolling(window=5).mean()
df["涨跌幅"] = df["close"].pct_change() * 100
print(df[["date", "close", "MA5", "涨跌幅"]].tail(10))
print(df[["date", "close", "MA5"]].tail(10))