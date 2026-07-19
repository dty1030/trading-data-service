import baostock as bs
import pandas as pd
import os

os.environ["NO_PROXY"] = "sina.com.cn,sinajs.cn,sina.com"
import akshare as ak
from datetime import date, timedelta


def normalize_baostock_code(symbol: str) -> str:
    normalized = symbol.strip().lower().replace(".", "")
    code = normalized[-6:]
    prefix = normalized[:-6]
    if prefix not in ("", "sh", "sz"):
        raise ValueError("股票代码前缀错误：" + symbol)
    if len(code) != 6 or not code.isdigit():
        raise ValueError("股票代码格式错误：" + symbol)
    if code.startswith(("60", "68")):
        market = "sh"
    elif code.startswith(("00", "30", "20")):
        market = "sz"
    else:
        raise ValueError("暂不支持的股票代码：" + symbol)
    if prefix and prefix != market:
        raise ValueError("股票代码与市场前缀不匹配：" + symbol)

    return f"{market}.{code}"


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


# 用来获取行业/概念/板块指数
def getIndices():
    # Sina Data Source
    df = ak.stock_zh_index_spot_sina()
    df.columns = ["code", "name", "price", "chg", "pct", "open", "high", "low", "preclose", "vol", "amount"][
        :len(df.columns)]

    watchList = ["sh000001", "sh000688", "sh000680", "sz399389", "sh000682"]
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


# 查新浪历史行情
def get_prev_vol(code):
    h = ak.stock_zh_index_daily(symbol=code)  # 新浪历史, 有 volume 列
    return float(h.iloc[-2]["volume"])  # 倒数第二行=昨天


def query_baostock_records(query_func, **kwargs):
    lg = bs.login()
    if lg.error_code != "0":
        raise RuntimeError("BaoStock 登录失败：" + lg.error_msg)
    try:
        rs = query_func(**kwargs)
        if rs.error_code != "0":
            raise RuntimeError("BaoStock 查询失败：" + rs.error_msg)

        rows = []
        while rs.next():
            rows.append(rs.get_row_data())

        df = pd.DataFrame(rows, columns=rs.fields)
        return df.to_dict(orient="records")
    finally:
        bs.logout()


def collect_baostock_records(query_func, **kwargs):
    rs = query_func(**kwargs)
    if rs.error_code != "0":
        raise RuntimeError("BaoStock 查询失败：" + rs.error_msg)

    rows = []
    while rs.next():
        rows.append(rs.get_row_data())

    df = pd.DataFrame(rows, columns=rs.fields)
    return df.to_dict(orient="records")


def get_company_fundamentals(
        symbol: str,
        year: int,
        quarter: int,
        start_date: str,
        end_date: str
):
    code = normalize_baostock_code(symbol)

    lg = bs.login()
    if lg.error_code != "0":
        raise RuntimeError("BaoStock 登录失败：" + lg.error_msg)

    try:
        return {
            "code": code,
            "year": year,
            "quarter": quarter,
            "profit": collect_baostock_records(
                bs.query_profit_data,
                code=code,
                year=year,
                quarter=quarter
            ),
            "growth": collect_baostock_records(
                bs.query_growth_data,
                code=code,
                year=year,
                quarter=quarter
            ),
            "operation": collect_baostock_records(
                bs.query_operation_data,
                code=code,
                year=year,
                quarter=quarter
            ),
            "balance": collect_baostock_records(
                bs.query_balance_data,
                code=code,
                year=year,
                quarter=quarter
            ),
            "cashFlow": collect_baostock_records(
                bs.query_cash_flow_data,
                code=code,
                year=year,
                quarter=quarter
            ),
            "dupont": collect_baostock_records(
                bs.query_dupont_data,
                code=code,
                year=year,
                quarter=quarter
            ),
            "forecast": collect_baostock_records(
                bs.query_forecast_report,
                code=code,
                start_date=start_date,
                end_date=end_date
            ),
            "performanceExpress": collect_baostock_records(
                bs.query_performance_express_report,
                code=code,
                start_date=start_date,
                end_date=end_date
            )
        }
    finally:
        bs.logout()


def get_operation(code: str, year: int, quarter: int):
    return query_baostock_records(
        bs.query_operation_data,
        code=code,
        year=year,
        quarter=quarter
    )


def get_balance(code: str, year: int, quarter: int):
    return query_baostock_records(
        bs.query_balance_data,
        code=code,
        year=year,
        quarter=quarter
    )


def get_cash_flow(code: str, year: int, quarter: int):
    return query_baostock_records(
        bs.query_cash_flow_data,
        code=code,
        year=year,
        quarter=quarter
    )


def get_dupont(code: str, year: int, quarter: int):
    return query_baostock_records(
        bs.query_dupont_data,
        code=code,
        year=year,
        quarter=quarter
    )


def get_growth(code: str, year: int, quarter: int):
    return query_baostock_records(
        bs.query_growth_data,
        code=code,
        year=year,
        quarter=quarter
    )


def get_profit(code: str, year: int, quarter: int):
    return query_baostock_records(
        bs.query_profit_data,
        code=code,
        year=year,
        quarter=quarter
    )


def get_forecast_report(code: str, start_date: str, end_date: str):
    return query_baostock_records(
        bs.query_forecast_report,
        code=code,
        start_date=start_date,
        end_date=end_date
    )


def get_performance_express_report(code: str, start_date: str, end_date: str):
    return query_baostock_records(
        bs.query_performance_express_report,
        code=code,
        start_date=start_date,
        end_date=end_date
    )
