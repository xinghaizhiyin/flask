import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# 模拟数据
data = pd.DataFrame({
    'Item': ['电影A', '电影B', '电影C', '电影D'],
    '审美评分': [85, 90, 75, 88],
    '热度指数': [1200, 1500, 800, 1100]
})

# 标题
st.title("审美与热度排行榜")

# 图表展示
st.subheader("热度与审美得分对比")
fig, ax = plt.subplots(figsize=(8, 6))  # 设置图表大小
ax.bar(data['Item'], data['热度指数'], color='orange', label='热度指数')
ax.plot(data['Item'], data['审美评分'], marker='o', color='blue', label='审美评分', linewidth=2)
plt.legend()
plt.xticks(rotation=45)  # 旋转x轴标签以避免重叠
plt.xlabel('电影')
plt.ylabel('分数/指数')
plt.title('热度与审美评分对比')

# 显示图表
st.pyplot(fig)

# 排行展示
st.subheader("排行榜")
data_sorted = data.sort_values(by=['热度指数', '审美评分'], ascending=False)
st.table(data_sorted)
