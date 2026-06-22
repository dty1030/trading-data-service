import os

os.environ[
    "NO_PROXY"] = "push2his.eastmoney.com,82.push2.eastmoney.com,push2.eastmoney.com,quote.eastmoney.com,.eastmoney.com,eastmoney.com"
import akshare as ak

df = ak.stock_zh_a_hist(symbol="603777", period="daily",
                        start_date="20260101", end_date="20260621", adjust="")
print("列名:", df.columns.tolist())
print(df.tail(3))