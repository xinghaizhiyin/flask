import akshare as ak
import pandas as pd

# 获取最近7天的日期范围
end_date = pd.to_datetime('today').strftime('%Y%m%d')
start_date = (pd.to_datetime('today') - pd.Timedelta(days=7)).strftime('%Y%m%d')

# 获取sh600654的最近7天的历史数据
stock_data = ak.stock_zh_a_hist(symbol="600654", period="daily", start_date=start_date, end_date=end_date)

# 打印数据
print(stock_data)

# 获取沪深市场所有A股的实时数据
stock_list = ak.stock_zh_a_spot()

# 提取股票代码
stock_codes = stock_list['代码'].apply(lambda x: str(x).zfill(6))  # 格式化股票代码为6位数字
print(stock_codes)
