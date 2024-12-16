import akshare as ak
import pandas as pd
from concurrent.futures import ThreadPoolExecutor

# 获取所有 a 股股票的实时数据
stock_zh_a_spot = ak.stock_zh_a_spot()

# 筛选掉北交所的股票代码
stock_list = stock_zh_a_spot[~stock_zh_a_spot['代码'].str.startswith('bj')]['代码'].tolist()
stock_names = stock_zh_a_spot.set_index('代码')['名称'].to_dict()

# 处理每只股票的数据
def process_stock(stock_code):
    try:
        # 获取股票最近 5 天的历史数据
        stock_zh_a_daily = ak.stock_zh_a_daily(symbol=stock_code, adjust="qfq")
        if stock_zh_a_daily.empty:
            return None  # 如果数据为空，跳过该股票

        stock_zh_a_daily.reset_index(inplace=True)
        stock_zh_a_daily['date'] = pd.to_datetime(stock_zh_a_daily['date'])

        # 获取最近 5 天的数据
        recent_five_days = stock_zh_a_daily.tail(5)

        # 检查数据是否足够
        if len(recent_five_days) < 5:
            return None

        # 计算跌的次数
        recent_five_days = recent_five_days.copy()  # 创建副本以避免 SettingWithCopyWarning
        recent_five_days['close_shift'] = recent_five_days['close'].shift(1)  # 前一天的收盘价
        recent_five_days['is_down'] = recent_five_days['close'] < recent_five_days['close_shift']  # 判断是否下跌
        down_count = recent_five_days['is_down'].sum()  # 统计下跌次数

        # 计算最近 5 天的平均价格
        avg_price_5days = recent_five_days['close'].mean()

        # 获取最新价格
        latest_price = stock_zh_a_spot.loc[stock_zh_a_spot['代码'] == stock_code, '最新价'].values[0]
        stock_name = stock_names.get(stock_code, "未知名称")

        # 返回结果
        return {
            '股票代码': stock_code,
            '股票名称': stock_name,
            '最新价格': round(latest_price, 2),
            '最近五天均价': round(avg_price_5days, 2),
            '跌的次数': int(down_count),
        }
    except Exception as e:
        print(f"处理股票 {stock_code} 时出错: {e}")
        return None

# 处理所有股票数据并返回排序后的结果
def process_all_stocks():
    with ThreadPoolExecutor(max_workers=20) as executor:
        results = list(executor.map(process_stock, stock_list))

    # 过滤掉处理失败的数据
    result_list = [result for result in results if result is not None]

    # 转换为 DataFrame
    result_df = pd.DataFrame(result_list)

    # 按跌的次数排序，降序排列
    ranked_df = result_df.sort_values(by='跌的次数', ascending=False)
    return ranked_df

# 主程序
if __name__ == '__main__':
    # 配置 Pandas 显示设置，避免截断
    pd.set_option('display.max_rows', None)  # 显示所有行
    pd.set_option('display.max_columns', None)  # 显示所有列
    pd.set_option('display.width', 1000)  # 设置显示宽度

    print("正在处理所有股票数据，请稍候...")
    result_df = process_all_stocks()

    # 打印完整结果
    print(result_df)

    # 如果需要保存到文件，启用以下代码
    # result_df.to_csv('stock_analysis.csv', index=False, encoding='utf-8-sig')
    # result_df.to_excel('stock_analysis.xlsx', index=False, engine='openpyxl')
