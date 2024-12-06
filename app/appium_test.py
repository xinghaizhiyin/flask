import time
from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from mysql import MySQLDatabase

# 设置 Appium 的配置
desired_caps = {
    'platformName': 'Android',  # 移动平台类型
    'platformVersion': '14',  # 目标设备的操作系统版本
    'deviceName': '598c2fde',  # 测试设备的名称或唯一标识符
    'appPackage': 'com.xingin.xhs',  # 应用程序的包名（小红书）
    'appActivity': 'com.xingin.xhs.index.v2.IndexActivityV2',  # 应用程序的启动 Activity
    'automationName': 'UiAutomator2',  # 使用的自动化引擎
    "noReset": True,  # 保持 App 的状态
    "fullReset": False,  # 不完全重置设备
}

# 数据库配置
db_params = {
    'host': 'localhost',
    'user': 'root',
    'password': 'admin',
    'database': 'test'
}

# 初始化数据库操作类
processor = MySQLDatabase(**db_params)

# 创建 Appium 驱动
driver = webdriver.Remote('http://localhost:4723', desired_caps)

# 等待设备和应用启动
time.sleep(2)

try:
    # 已处理的内容，用于去重
    loaded_content = set()

    # 获取屏幕尺寸
    screen_size = driver.get_window_size()
    start_x = screen_size['width'] // 2
    start_y = screen_size['height'] * 3 // 4
    end_x = start_x
    end_y = screen_size['height'] // 4

    # 滑动 10 次加载更多内容
    for _ in range(10):
        # 查找所有 "android.widget.FrameLayout" 元素
        elements = driver.find_elements(by=AppiumBy.CLASS_NAME, value="android.widget.FrameLayout")

        # 遍历找到的元素并提取其 content-desc 属性
        for element in elements:
            content_desc = element.get_attribute("content-desc")

            # 处理非空且有效的 content-desc
            if content_desc and content_desc not in loaded_content:
                # 将 content-desc 拆分为数据列表
                data = content_desc.split()

                # 数据长度校验（确保有足够字段）
                if len(data) >= 4:
                    # 确保目标表存在（如果不存在则创建表）
                    processor.create_table_if_not_exists('xiaohongshu')

                    # 将数据插入到数据库中
                    processor.insert_data('xiaohongshu', data)
                    print(f"插入数据: {data}")

                # 将当前数据添加到已处理集合，避免重复处理
                loaded_content.add(content_desc)

        # 滑动屏幕加载更多内容
        driver.swipe(start_x, start_y, end_x, end_y, duration=1000)

        # 等待加载完成
        time.sleep(2)

finally:
    # 关闭 Appium 驱动
    driver.quit()

    # 关闭数据库连接
    processor.close()
