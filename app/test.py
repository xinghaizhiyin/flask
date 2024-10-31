from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# 配置ChromeDriver路径
driver_path = 'C:\\Users\\Administrator\\PycharmProjects\\flask\driver\\chromedriver.exe'  # 替换为你的chromedriver路径
service = Service(driver_path)
driver = webdriver.Chrome(service=service)

# 打开目标网站
driver.get("https://www.cupfox2025.com/vodshow/by/hits/id/fenlei1/lang/%E9%9F%A9%E8%AF%AD.html")  # 替换为登录页面的URL

try:
    # 输入用户名
    username_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "username"))  # 替换为实际用户名输入框的ID
    )
    username_field.clear()
    username_field.send_keys("your_username")  # 替换为实际用户名

    # 输入密码
    password_field = driver.find_element(By.ID, "password")  # 替换为实际密码输入框的ID
    password_field.clear()
    password_field.send_keys("your_password")  # 替换为实际密码

    # 点击登录按钮
    login_button = driver.find_element(By.ID, "login-button")  # 替换为实际登录按钮的ID
    login_button.click()

    # 可选择检查是否成功登录，比如等待某个元素出现
    success_message = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "welcome-message"))  # 替换为登录后显示的元素ID
    )
    print("登录成功！")

except Exception as e:
    print("登录失败：", e)

finally:
    # 关闭浏览器
    time.sleep(5)  # 等待一会儿以观察结果，实际应用中可视需求而定
    driver.quit()
