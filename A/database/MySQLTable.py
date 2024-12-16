# 实时数据表字段
real_time_columns = {
    'stock_code': 'VARCHAR(10) UNIQUE',  # 股票代码
    'stock_name': 'VARCHAR(100)',  # 股票名称
    'latest_price': 'FLOAT',  # 最新价
    'change_amt': 'FLOAT',  # 涨跌额
    'change_pct': 'FLOAT',  # 涨跌幅
    'buy_price': 'FLOAT',  # 买入价
    'sell_price': 'FLOAT',  # 卖出价
    'previous_close': 'FLOAT',  # 昨收
    'today_open': 'FLOAT',  # 今开
    'highest_price': 'FLOAT',  # 最高
    'lowest_price': 'FLOAT',  # 最低
    'volume': 'FLOAT',  # 成交量
    'amount': 'FLOAT',  # 成交额
    'timestamp': 'TIME',  # 时间戳
    'data_write_time': 'DATETIME'  # 数据写入时间
}

# 存储 7天数据表字段
seven_day_columns = {
    'stock_code': 'VARCHAR(10) UNIQUE',  # 股票代码（唯一）
    'stock_name': 'VARCHAR(100)',  # 股票名称
    'latest_price': 'FLOAT',  # 最新收盘价
    'latest_change_pct': 'FLOAT',  # 最新涨跌幅
    'latest_amplitude_pct': 'FLOAT',  # 最新振幅
    'avg_days': 'FLOAT',  # 7天收盘价平均值
    'change_pct': 'FLOAT',  # 7天涨跌幅平均值
    'amplitude_pct': 'FLOAT',  # 7天振幅平均值
    'min_days': 'FLOAT',  # 7天内最低价格
    'max_days': 'FLOAT',  # 7天内最高价格
    'down_count': 'INT',  # 7天中下跌次数
    'up_count': 'INT',  # 7天中上涨次数
    'data_write_time': 'DATETIME'  # 数据写入时间（当前时间）
}


# 存储 30天数据表字段
thirty_day_columns = {
    'stock_code': 'VARCHAR(10) UNIQUE',  # 股票代码（唯一）
    'stock_name': 'VARCHAR(100)',  # 股票名称
    'latest_price': 'FLOAT',  # 最新收盘价
    'latest_change_pct': 'FLOAT',  # 最新涨跌幅
    'latest_amplitude_pct': 'FLOAT',  # 最新振幅
    'avg_days': 'FLOAT',  # 7天收盘价平均值
    'change_pct': 'FLOAT',  # 7天涨跌幅平均值
    'amplitude_pct': 'FLOAT',  # 7天振幅平均值
    'min_days': 'FLOAT',  # 7天内最低价格
    'max_days': 'FLOAT',  # 7天内最高价格
    'down_count': 'INT',  # 7天中下跌次数
    'up_count': 'INT',  # 7天中上涨次数
    'data_write_time': 'DATETIME'  # 数据写入时间（当前时间）
}

# 存储 90天数据表字段
ninety_day_columns = {
    'stock_code': 'VARCHAR(10) UNIQUE',  # 股票代码（唯一）
    'stock_name': 'VARCHAR(100)',  # 股票名称
    'latest_price': 'FLOAT',  # 最新收盘价
    'latest_change_pct': 'FLOAT',  # 最新涨跌幅
    'latest_amplitude_pct': 'FLOAT',  # 最新振幅
    'avg_days': 'FLOAT',  # 7天收盘价平均值
    'change_pct': 'FLOAT',  # 7天涨跌幅平均值
    'amplitude_pct': 'FLOAT',  # 7天振幅平均值
    'min_days': 'FLOAT',  # 7天内最低价格
    'max_days': 'FLOAT',  # 7天内最高价格
    'down_count': 'INT',  # 7天中下跌次数
    'up_count': 'INT',  # 7天中上涨次数
    'data_write_time': 'DATETIME'  # 数据写入时间（当前时间）
}
stockcodes_columns = {
    'stock_code': 'VARCHAR(10) UNIQUE',  # 股票代码
    'data_write_time': 'DATETIME'  # 数据写入时间
}
merged_columns = {
    'stock_code': 'VARCHAR(10) UNIQUE',  # 股票代码（唯一）
    'stock_name': 'VARCHAR(100)',  # 股票名称
    'latest_price': 'FLOAT',  # 最新收盘价
    'latest_change_pct': 'FLOAT',  # 最新涨跌幅
    'latest_amplitude_pct': 'FLOAT',  # 最新振幅
    'avg_days_7': 'FLOAT',  # 7天收盘价平均值
    'change_pct_7': 'FLOAT',  # 7天涨跌幅平均值
    'amplitude_pct_7': 'FLOAT',  # 7天振幅平均值
    'min_days_7': 'FLOAT',  # 7天内最低价格
    'max_days_7': 'FLOAT',  # 7天内最高价格
    'down_count_7': 'INT',  # 7天中下跌次数
    'up_count_7': 'INT',  # 7天中上涨次数
    'avg_days_30': 'FLOAT',  # 30天收盘价平均值
    'change_pct_30': 'FLOAT',  # 30天涨跌幅平均值
    'amplitude_pct_30': 'FLOAT',  # 30天振幅平均值
    'min_days_30': 'FLOAT',  # 30天内最低价格
    'max_days_30': 'FLOAT',  # 30天内最高价格
    'down_count_30': 'INT',  # 30天中下跌次数
    'up_count_30': 'INT',  # 30天中上涨次数
    'avg_days_90': 'FLOAT',  # 90天收盘价平均值
    'change_pct_90': 'FLOAT',  # 90天涨跌幅平均值
    'amplitude_pct_90': 'FLOAT',  # 90天振幅平均值
    'min_days_90': 'FLOAT',  # 90天内最低价格
    'max_days_90': 'FLOAT',  # 90天内最高价格
    'down_count_90': 'INT',  # 90天中下跌次数
    'up_count_90': 'INT',  # 90天中上涨次数
    'data_write_time': 'DATETIME',  # 数据写入时间（当前时间）
    'is_favorite': 'INT',  # 收藏标记字段，1表示收藏，0或NULL表示未收藏
    'price_diff_7': 'FLOAT',  # 7天价差
    'price_diff_30': 'FLOAT',  # 30天价差
    'price_diff_90': 'FLOAT'  # 90天价差
}


