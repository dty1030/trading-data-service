import akshare as ak
import os

os.environ["NO_PROXY"] = "gtimg.cn,qq.com,sina.com.cn,sinajs.cn,eastmoney.com"


def run_backtest(symbol: str = "sh600519"):
    df = ak.stock_zh_a_hist_tx(symbol=symbol)

    # 1. 四条均线
    df["MA5"] = df["close"].rolling(window=5).mean()
    df["MA10"] = df["close"].rolling(window=10).mean()
    df["MA20"] = df["close"].rolling(window=20).mean()
    df["MA30"] = df["close"].rolling(window=30).mean()
    # 2. 信号:MA5>MA20 时 =1(该持有),否则=0(该空仓)
    df["signal"] = ((
        (df["MA5"] > df["MA10"]) &
        (df["MA10"] > df["MA20"]) &
        (df["MA20"] > df["MA30"]))
                    .astype(int))

    # 3. ⚠️躲未来函数:今天的仓位 =昨天的信号(往下挪一格)
    df["position"] = df["signal"].shift(1).fillna(0)
    # 4. 股票每日涨跌幅(小数)
    df["ret"] = df["close"].pct_change()
    # 5. 策略每日收益 = 仓位 ×当日涨跌(只有持有时才吃到涨跌)
    df["strat_ret"] = df["position"] * df["ret"]
    #
    df["bh_equity"] = (1 + df["ret"]).cumprod()
    df["strat_equity"] = (1 + df["strat_ret"]).cumprod()

    return df



def backtest_metrics(symbol: str = "sh600519"):
    df = run_backtest(symbol)

    strat_total = df["strat_equity"].iloc[-1] - 1
    bh_total = df["bh_equity"].iloc[-1] -1

    roll_max = df["strat_equity"].cummax()
    #最大回撤
    drawdown = df["strat_equity"] / roll_max - 1
    max_dd = drawdown.min()

    #仓位变化次数 = 交易次数
    trades = int((df["position"].diff() != 0).sum())

    return {
        "symbol": symbol,
        "策略总收益%": round(strat_total * 100,
                             2),
        "buyhold总收益%": round(bh_total * 100,
                                2),
        "最大回撤%": round(max_dd * 100, 2),
        "交易次数": trades,
        "持仓天数": int(df["position"].sum()),
        "总天数": len(df),
    }
