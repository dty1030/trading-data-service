import os

os.environ["NO_PROXY"] = "gtimg.cn,qq.com,sina.com.cn, sinajs.cn, eastmoney.com"
import akshare as ak


def strategy_signals(symbol: str):
    double_volume_threshold = 1.79

    df = ak.stock_zh_a_hist_tx(symbol)
    df["阳线"] = df["close"] > df["open"]
    df["阴线"] = df["close"] < df["open"]
    df["量比"] = df["amount"] / df["amount"].shift(1)
    df["倍量柱"] = df["阳线"] & (df["量比"] >= double_volume_threshold)

    last = df.iloc[-1]

    streak = 0
    for v in reversed(df["阴线"].tolist()):
        if v:
            streak += 1
        else:
            break

    #成交量/量比-----
    volume_ratio = float(last["量比"])
    double_volume_threshold = 1.79
    is_double_volume = volume_ratio >= double_volume_threshold
    is_mild_volume_expansion = 1.2 <= volume_ratio < double_volume_threshold
    is_volume_shrinking = volume_ratio < 0.8
    if is_double_volume:
        volume_conclusion = "明显放量，达到倍量柱观察阈值"
    elif is_mild_volume_expansion:
        volume_conclusion = "温和放量"
    elif is_volume_shrinking:
        volume_conclusion = "缩量"
    else:
        volume_conclusion = "量能接近前一交易日，不能称为明显放量"
    return {
        "symbol": symbol,
        "日期": last["date"],
        "今日阳线": bool(last["阳线"]),
        "今日量比": round(float(last["量比"]), 2),
        "今日倍量柱": bool(last["倍量柱"]),
        "倍量柱阈值": double_volume_threshold,
        "是否明显放量": bool(is_double_volume),
        "是否温和放量": bool(is_mild_volume_expansion),
        "是否缩量": bool(is_volume_shrinking),
        "成交量情况": volume_conclusion,
        "连续阴线天数": int(streak),
        "触发原则1_倍量柱重点关注": bool(last["倍量柱"]),
        "触发原则2_连续4阴谨慎看多": streak >= 4,
    }
