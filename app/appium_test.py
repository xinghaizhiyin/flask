from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 设置Appium的配置
desired_caps = {
    'platformName': 'Android',         # 运行测试的移动平台，iOS或Android。此处为Android。
    'platformVersion': '14',           # 移动设备的操作系统版本。此处为Android 14。
    'deviceName': '598c2fde',          # 测试设备的名称或唯一标识符。此处为设备ID。
    'app': '../driver/12.apk',         # 应用程序的路径（本地路径或URL），测试时会安装这个应用。此处为相对路径。
    'appPackage': 'uni.UNIAE84655',    # 应用程序包名，唯一标识该应用。此处为应用包名。
    'appActivity': 'io.dcloud.PandoraEntry',  # 应用程序启动时的主要Activity。此处为启动Activity的全名。
    'automationName': 'UiAutomator2'   # 使用的自动化引擎。Android推荐使用UiAutomator2。
}

# 创建Appium驱动
driver = webdriver.Remote('http://localhost:4723', desired_caps)

try:
    # 等待用户名输入框加载并输入用户名
    username = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((AppiumBy.ID, 'com.example.app:id/username'))  # 根据ID查找用户名输入框
    )
    username.send_keys('test_user')  # 输入用户名

    # 输入密码
    password = driver.find_element(by=AppiumBy.ID, value='com.example.app:id/password')  # 根据ID查找密码输入框
    password.send_keys('test_password')  # 输入密码

    # 点击登录按钮
    login_button = driver.find_element(by=AppiumBy.ID, value='com.example.app:id/login')  # 根据ID查找登录按钮
    login_button.click()  # 点击登录按钮

    # 验证登录是否成功
    success_message = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((AppiumBy.ID, 'com.example.app:id/success'))  # 根据ID查找成功消息
    )
    assert success_message.is_displayed()  # 断言成功消息是否显示

finally:
    # 退出Appium会话
    driver.quit()  # 关闭驱动并退出会话
