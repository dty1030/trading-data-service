import baostock as bs
import pandas as pd
import os
os.environ["NO_PROXY"] = "sina.com.cn,sinajs.cn,sina.com"
import akshare as ak
from datetime import date, timedelta


def get_kline(
        code_tx: str) -> pd.DataFrame:  # ① int → str (它是字符串,你还索引它)
    code = code_tx[
        -6:]  # ② 取后6位: "sh600519"→"600519", "600519"→"600519" 都行
    if code[0] in ('0', '3',
                   '2'):  # 0/3/2 开头 = 深市
        bs_code = "sz." + code
    else:  # 6 开头(含科创板688) = 沪市
        bs_code = "sh." + code
    bs.login()
    rs = bs.query_history_k_data_plus(
        bs_code,
        "date,open,high,low,close,amount,turn,pctChg",
        # 要哪些列
        start_date=(date.today() - timedelta(days=90)).isoformat(),
        end_date=date.today().isoformat(),
        frequency="d",
        adjustflag="2")  # d=日线; 2=前复权(技术分析常用)
    rows = []
    while rs.error_code == '0' and rs.next():
        rows.append(
            rs.get_row_data())  # 一行行取
    bs.logout()
    df = pd.DataFrame(rows, columns=rs.fields)
    # 坑3:全转 float
    for c in ["open", "high", "low", "close", "amount", "turn", "pctChg"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    return df


#用来获取行业/概念/板块指数
def getIndices():

    #Sina Data Source
    df = ak.stock_zh_index_spot_sina()
    df.columns = ["code", "name", "price", "chg", "pct", "open", "high", "low", "preclose", "vol", "amount"][
        :len(df.columns)]

    watchList = ["sh000001","sh000688","sh000680","sz399389","sh000682"]
    output = []
    for code in watchList:
        row = df[df["code"] == code]
        if row.empty: continue
        r = row.iloc[0]
        current_vol = float(r["vol"])
        if code.startswith("sh"):
            current_vol *= 100
        prev_vol = get_prev_vol(code)
        output.append({
            "name": r["name"], "price": float(r["price"]),
            "pct": float(r["pct"]), "vol": current_vol, "prevVol": prev_vol
        })
    return output

    # 获取指数(综合指数、规模指数、一级行业指数、二级行业指数、策略指数、成长指数、价值指数、主题指数)K线数据
    # 综合指数，例如：sh.000001 上证指数，sz.399106 深证综指 等；
    # 规模指数，例如：sh.000016 上证50，sh.000300 沪深300，sh.000905 中证500，sz.399001 深证成指等；
    # 一级行业指数，例如：sh.000037 上证医药，sz.399433 国证交运 等；
    # 二级行业指数，例如：sh.000952 300地产，sz.399951 300银行 等；
    # 策略指数，例如：sh.000050 50等权，sh.000982 500等权 等；
    # 成长指数，例如：sz.399376 小盘成长 等；
    # 价值指数，例如：sh.000029 180价值 等；
    # 主题指数，例如：sh.000015 红利指数，sh.000063 上证周期 等；

    # 详细指标参数，参见“历史行情指标参数”章节；“周月线”参数与“日线”参数不同。
    # 周月线指标：date,code,open,high,low,close,volume,amount,adjustflag,turn,pctChg
    rs = bs.query_history_k_data_plus("sh.000001",
                                      "date,code,open,high,low,close,preclose,volume,amount,pctChg",
                                      start_date='2017-01-01', end_date='2017-06-30', frequency="d")
    print('query_history_k_data_plus respond error_code:' + rs.error_code)
    print('query_history_k_data_plus respond  error_msg:' + rs.error_msg)

    # 打印结果集


    # 登出系统
    bs.logout()
#查新浪历史行情
def get_prev_vol(code):
    h = ak.stock_zh_index_daily(symbol=code)   # 新浪历史, 有 volume 列
    return float(h.iloc[-2]["volume"])         # 倒数第二行=昨天