# 更新代码
git add .

git commit -m '更新内容'

git push flask master

# flask接口 和 性能测试


## JMETER工具链接
性能/jmeter

https://jmeter-plugins.org/downloads/old/

https://github.com/undera/perfmon-agent?tab=readme-ov-file

# python pytest测试及allure报告
allure 是一个命令行工具，需要去github上下载最新版https://github.com/allure-framework/allure2/releases

allure 命令行工具是需要依赖jdk 环境，环境内容自己去搭建了
配置系统环境变量：C:\Users\Administrator\PycharmProjects\flask\allure-2.32.0\bin

pytest --alluredir ./report

allure serve ./report(注意全局)

allure generate report --clean -o allure-report（本地报告，其他设备可以打开）

# Appium 测试

下载 Appium Desktop定位

https://github.com/appium/appium-inspector/releases

您可以使用 npm 在全局范围内安装 Appium：

npm i -g appium

安装完成后，您应该可以从命令行运行 Appium：

appium

获取app信息

C:\Users\Administrator>aapt dump badging C:\Users\Administrator\PycharmProjects\flask\driver\12.apk

安装驱动本身¶
由于 UiAutomator2 驱动是由核心 Appium 团队维护的，它有一个官方的驱动名称，你可以通过 Appium 扩展 CLI 轻松安装：

appium driver install uiautomator2