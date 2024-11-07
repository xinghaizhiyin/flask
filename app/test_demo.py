import pytest
import allure
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

@pytest.fixture(scope="module")
def driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # 无头模式
    chrome_options.add_argument("--disable-gpu")
    service = Service('C:\\Users\\Administrator\\PycharmProjects\\flask\driver\\chromedriver.exe')  # 替换为实际路径
    driver = webdriver.Chrome(service=service, options=chrome_options)

    yield driver
    driver.quit()

@allure.feature("淘宝主页")
@allure.story("验证主页元素和标题")
def test_taobao_homepage(driver):
    with allure.step("打开淘宝主页"):
        driver.get("https://www.taobao.com/")
        time.sleep(3)  # 等待页面加载

    with allure.step("检查页面标题"):
        assert "淘宝网" in driver.title, "页面标题不包含'淘宝网'"

    with allure.step("检查搜索框是否存在"):
        search_box = driver.find_element(By.ID, "q")
        assert search_box is not None, "找不到搜索框"

    with allure.step("输出测试成功信息"):
        print("淘宝网主页测试成功")
