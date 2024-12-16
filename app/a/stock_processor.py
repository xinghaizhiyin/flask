import akshare as ak
import pandas as pd
from concurrent.futures import ThreadPoolExecutor

# 获取所有 a 股股票的实时数据
stock_zh_a_spot = ak.stock_zh_a_spot()
stock_list = stock_zh_a_spot['代码'].tolist()  # 提取股票代码列表
stock_names = stock_zh_a_spot.set_index('代码')['名称'].to_dict()  # 提取股票代码与名称的对应关系

# 处理每只股票的数据
def process_stock(stock_code):
    try:
        # 获取每只股票的日K线数据，使用前复权数据
        stock_zh_a_daily = ak.stock_zh_a_daily(symbol=stock_code, adjust="qfq")
        if stock_zh_a_daily.empty:
            return None  # 如果数据为空，则跳过该股票

        stock_zh_a_daily.reset_index(inplace=True)  # 重置索引
        stock_zh_a_daily['date'] = pd.to_datetime(stock_zh_a_daily['date'])  # 转换日期为日期时间格式

        today = pd.to_datetime('today')  # 获取今天的日期
        one_month_ago = today - pd.DateOffset(months=1)  # 一个月前的日期
        three_months_ago = today - pd.DateOffset(months=3)  # 三个月前的日期
        one_year_ago = today - pd.DateOffset(years=1)  # 一年前的日期

        # 筛选出近一个月、近三个月、近一年的数据
        recent_one_month = stock_zh_a_daily[stock_zh_a_daily['date'] >= one_month_ago]
        recent_three_months = stock_zh_a_daily[stock_zh_a_daily['date'] >= three_months_ago]
        recent_one_year = stock_zh_a_daily[stock_zh_a_daily['date'] >= one_year_ago]
        # 获取最近 5 天的数据
        recent_five_days = stock_zh_a_daily.tail(6)

        # 计算指定时间段的平均价格
        def calculate_avg_price(data):
            if data.empty:
                return None  # 如果数据为空，返回 None
            return (data['open'].mean() + data['close'].mean() + data['high'].mean() + data['low'].mean()) / 4

        # 计算近一个月、近三个月、近一年的平均价格
        avg_one_month = calculate_avg_price(recent_one_month)
        avg_three_months = calculate_avg_price(recent_three_months)
        avg_one_year = calculate_avg_price(recent_one_year)
        avg_five_days = calculate_avg_price(recent_five_days)  # 计算最近五天的平均价格

        def count_down_days(data):
            # 排序数据，确保按照日期升序排列（从最旧到最新）
            data = data.sort_values(by='date', ascending=True)
            # 去除含有NaN值的行
            data = data.dropna(subset=['close'])
            # 计算收盘价低于前一日的次数
            down_days = (data['close'] < data['close'].shift(1)).sum()  # 计算收盘价低于前一日的次数
            return down_days

        # 使用修正后的方法计算最近五天的下跌次数
        down_days_count = count_down_days(recent_five_days)  # 计算最近五天的下跌次数

        # 获取股票的最新价格
        latest_price = stock_zh_a_spot.loc[stock_zh_a_spot['代码'] == stock_code, '最新价'].values[0]
        # 获取股票的名称
        stock_name = stock_names.get(stock_code, "未知名称")

        # 计算涨跌幅 (最新收盘价与开盘价的百分比变化)
        def calculate_percentage_change(latest_price, avg_price):
            if avg_price is not None and avg_price != 0:
                return round(((latest_price - avg_price) / avg_price) * 100, 2)  # 计算百分比变化
            return None

        # 计算近一个月、三个月、一年的涨跌幅
        month_change = calculate_percentage_change(latest_price, avg_one_month)
        three_month_change = calculate_percentage_change(latest_price, avg_three_months)
        year_change = calculate_percentage_change(latest_price, avg_one_year)

        # 获取昨日收盘价，作为计算涨跌幅的基准
        yesterday_close_price = stock_zh_a_daily['close'].iloc[-2] if len(stock_zh_a_daily) > 1 else None

        # 计算实时涨跌幅 (最新成交价与昨日收盘价的百分比变化)
        def calculate_percentage_change(latest_price, reference_price):
            if reference_price is not None and reference_price != 0:
                return round(((latest_price - reference_price) / reference_price) * 100, 2)  # 计算百分比变化
            return None

        # 计算实时的涨跌幅
        change_percentage = calculate_percentage_change(latest_price, yesterday_close_price)

        # 获取股票今天的最高价和最低价
        today_high_price = stock_zh_a_daily['high'].iloc[-1]  # 今日最高价
        today_low_price = stock_zh_a_daily['low'].iloc[-1]    # 今日最低价

        # 计算振幅 (今天最高价 - 最低价) / 昨日收盘价 * 100
        def calculate_amplitude(today_high, today_low, yesterday_close):
            if yesterday_close is not None and yesterday_close != 0:
                return round(((today_high - today_low) / yesterday_close) * 100, 2)
            return None

        # 计算实时的振幅
        amplitude = calculate_amplitude(today_high_price, today_low_price, yesterday_close_price)

        # 返回每只股票的各项数据
        return {
            '股票代码': stock_code,
            '股票名称': stock_name,
            '最新价格': round(latest_price, 2),
            '近一个月均价': round(avg_one_month, 2) if avg_one_month is not None else None,
            '近三个月均价': round(avg_three_months, 2) if avg_three_months is not None else None,
            '近一年均价': round(avg_one_year, 2) if avg_one_year is not None else None,
            '近五天均价': round(avg_five_days, 2) if avg_five_days is not None else None,  # 最近五天均价
            '五天下跌次数': down_days_count,  # 最近五天下跌次数
            '一个月涨跌幅(%)': month_change,
            '三个月涨跌幅(%)': three_month_change,
            '一年涨跌幅(%)': year_change,
            '涨跌幅(%)': change_percentage,  # 最新涨跌幅
            '振幅(%)': amplitude  # 最新振幅
        }
    except Exception as e:
        print(f"处理股票 {stock_code} 时出错: {e}")  # 捕获异常，打印错误信息
        return None


# 处理所有股票数据并返回排序后的结果
def process_all_stocks():
    # 使用线程池并发处理所有股票
    with ThreadPoolExecutor(max_workers=20) as executor:
        results = list(executor.map(process_stock, stock_list))

    # 过滤掉处理失败的股票（返回 None 的股票）
    result_list = [result for result in results if result is not None]
    # 将结果转换为 DataFrame
    result_df = pd.DataFrame(result_list)
    # 按照“一个月涨跌幅”排序，降序排列
    ranked_df = result_df.sort_values(by='一个月涨跌幅(%)', ascending=False)
    return ranked_df  # 返回排序后的 DataFrame
