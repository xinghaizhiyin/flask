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