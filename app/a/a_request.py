import akshare as ak
import pandas as pd
from datetime import datetime, timedelta

# 获取所有A股股票列表
stock_list = ak.stock_zh_a_spot_em()  # 获取实时股票列表
stock_codes = stock_list["代码"].tolist()  # 提取股票代码

# 时间设置
now = datetime.now()
start_date = "2020-01-01"  # 起始日期
end_date = now.strftime("%Y-%m-%d")
one_month_ago = now - timedelta(days=30)
three_months_ago = now - timedelta(days=90)
one_year_ago = now - timedelta(days=365)

# 初始化结果存储
summary_data = []

# 遍历所有股票
for stock_code in stock_codes:
    try:
        # 获取每只股票的历史数据
        data = ak.stock_zh_a_hist(symbol=stock_code, period="daily", start_date=start_date, end_date=end_date,
                                  adjust="qfq")
        if data is None or data.empty:
            continue

        # 数据预处理
        data.columns = ["日期", "开盘", "收盘", "最高", "最低", "成交量", "成交额", "振幅", "涨跌幅", "涨跌额",
                        "换手率"]
        data["日期"] = pd.to_datetime(data["日期"])
        data.set_index("日期", inplace=True)
        data["均价"] = (data["最高"] + data["最低"]) / 2

        # 打印该股票的历史数据
        print(f"\n股票代码: {stock_code}")
        print(data.head())  # 打印该股票的前5条历史数据

        # 计算均价
        one_month_avg = data.loc[data.index >= one_month_ago, "均价"].mean()
        three_month_avg = data.loc[data.index >= three_months_ago, "均价"].mean()
        one_year_avg = data.loc[data.index >= one_year_ago, "均价"].mean()

        # 打印均价
        print(f"最近一个月均价: {one_month_avg}")
        print(f"最近三个月均价: {three_month_avg}")
        print(f"最近一年均价: {one_year_avg}")

        # 存储汇总结果
        summary_data.append({
            "股票代码": stock_code,
            "最近一个月均价": one_month_avg,
            "最近三个月均价": three_month_avg,
            "最近一年均价": one_year_avg
        })
    except Exception as e:
        print(f"股票代码 {stock_code} 获取失败: {e}")

# 汇总结果打印
summary_df = pd.DataFrame(summary_data)
print("\n=== 全部股票均价汇总 ===")
print(summary_df)
