import streamlit as st
import sys
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.data_loader import load_data

st.set_page_config(page_title="竞品分析", page_icon="🔍", layout="wide")

@st.cache_data
def get_data():
    return load_data()

df = get_data()

st.markdown("# 🔍 《数字空间女性生存指南》竞品分析")

st.markdown("## 📊 市场概况")

psychology_df = df[df['category'] == '心理学'].copy()
female_keywords = ['女', '她', '女性', '妇女']
female_df = df[df['title'].str.contains('|'.join(female_keywords), case=False, na=False) |
                df['author'].str.contains('|'.join(female_keywords), case=False, na=False)].copy()

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("心理学类书籍", f"{len(psychology_df)}本")
with col2:
    st.metric("女性相关书籍", f"{len(female_df)}本")
with col3:
    st.metric("心理学平均价格", f"¥{psychology_df['price'].mean():.2f}")
with col4:
    st.metric("女性书籍平均价格", f"¥{female_df['price'].mean():.2f}")

st.markdown("### 价格分布对比")

fig = go.Figure()
fig.add_trace(go.Histogram(x=psychology_df['price'], name='心理学类', opacity=0.7, marker_color='#636EFA'))
fig.add_trace(go.Histogram(x=female_df['price'], name='女性相关', opacity=0.7, marker_color='#EF553B'))

fig.update_layout(
    title='心理学类 vs 女性相关书籍价格分布',
    xaxis_title='价格(元)',
    yaxis_title='书籍数量',
    barmode='overlay',
    height=400,
    margin=dict(t=30, b=20, l=20, r=20)
)
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

st.markdown("## 💰 定价策略分析")

st.markdown("### 价格-评论数关系")

fig = px.scatter(psychology_df, x='price', y='comments',
                 title='心理学类书籍价格与评论数关系', height=400,
                 color_discrete_sequence=['#636EFA'])
fig.update_layout(margin=dict(t=30, b=20, l=20, r=20), xaxis_title="价格(元)", yaxis_title="评论数")
st.plotly_chart(fig, use_container_width=True)

st.markdown("### 价格区间表现")

price_bins = [0, 30, 40, 50, 60, 80, 100, float('inf')]
price_labels = ['0-30元', '30-40元', '40-50元', '50-60元', '60-80元', '80-100元', '100元以上']

psychology_df_copy = psychology_df.copy()
psychology_df_copy['价格区间'] = pd.cut(psychology_df_copy['price'], bins=price_bins, labels=price_labels)

price_analysis = psychology_df_copy.groupby('价格区间').agg({
    'title': 'count',
    'comments': 'mean',
    'recommend_rate': 'mean'
}).reset_index()
price_analysis.columns = ['价格区间', '书籍数量', '平均评论数', '平均推荐率']

fig = px.bar(price_analysis, x='价格区间', y='书籍数量',
             title='各价格区间书籍数量', height=400,
             color='平均评论数', color_continuous_scale='Teal')
fig.update_layout(margin=dict(t=30, b=20, l=20, r=20))
st.plotly_chart(fig, use_container_width=True)

median_price = psychology_df['price'].median()
high_comment_price = psychology_df[psychology_df['comments'] > psychology_df['comments'].quantile(0.75)]['price'].median()

st.success(f"""
**定价建议：¥{median_price:.0f} - ¥{high_comment_price:.0f}**

- 心理学类书籍价格中位数：**¥{median_price:.2f}**
- 高评论数书籍价格中位数：**¥{high_comment_price:.2f}**
""")

st.markdown("---")

st.markdown("## 📖 内容定位分析")

st.markdown("### 高表现书籍特征")

top_books = psychology_df.nlargest(10, 'comments')[['title', 'author', 'price', 'comments', 'recommend_rate']]
top_books_display = top_books.copy()
top_books_display['价格'] = top_books_display['price'].apply(lambda x: f"¥{x:.2f}")
top_books_display['评论数'] = top_books_display['comments'].apply(lambda x: f"{x:,}")
top_books_display['推荐率'] = top_books_display['recommend_rate'].apply(lambda x: f"{x:.1f}%")
top_books_display = top_books_display[['title', 'author', '价格', '评论数', '推荐率']]
top_books_display.columns = ['书名', '作者', '价格', '评论数', '推荐率']

st.dataframe(top_books_display, use_container_width=True, height=350)

st.info("""
**差异化定位方向：**

1. **数字生活+女性主义**：现有心理学书籍多关注情绪管理、自我成长，缺乏针对数字时代女性生存策略的内容
2. **实操性强**：高评论数书籍多为工具书、实操手册，建议增加自查清单、话术模板等实用内容
3. **视觉友好**：畅销书多配有插图、图表，建议增加信息图、流程图等视觉元素
""")

st.markdown("---")

st.markdown("## 📋 综合建议")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 定价建议")
    st.success("""
    - **建议定价**：¥58-68
    - **建议折扣**：5-7折
    - **理由**：符合心理学类书籍价格中位数，且具有竞争力
    """)
    
    st.markdown("### 形式设计")
    st.warning("""
    - **开本**：32开或正16开
    - **装帧**：平装+护封
    - **视觉**：信息图+流程图+话术模板
    - **附加品**：可撕页、贴纸、提醒卡
    """)

with col2:
    st.markdown("### 内容定位")
    st.info("""
    - **核心定位**：数字时代女性自我保护实操指南
    - **差异化**：填补“数字生活+女性主义”市场空白
    - **目标读者**：18-28岁女性
    """)
    
    st.markdown("### 市场推广")
    st.error("""
    - **话题营销**：结合#容貌焦虑、#网暴等热门话题
    - **平台选择**：小红书、微博、B站
    - **KOL合作**：女性主义博主、心理博主
    """)