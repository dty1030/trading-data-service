import baostock as bs
import pandas as pd
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
