import streamlit as st
import sys
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.data_loader import load_data, get_categories, get_all_list_types, get_category_stats, get_top_books, filter_data, get_data_summary
from utils.charts import create_pie_chart, create_bar_chart
from streamlit_echarts import st_pyecharts

st.set_page_config(page_title="市场概览", page_icon="📊", layout="wide")

@st.cache_data
def get_data():
    return load_data()

df = get_data()
categories = get_categories(df)
list_types = get_all_list_types(df)

st.markdown("# 📊 市场概览分析")

summary = get_data_summary(df)

st.markdown("## 📈 数据概览")
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.metric("📚 书籍总数", f"{summary['total_books']:,}")
with col2:
    st.metric("📊 数据量总数", f"{summary['total_records']:,}")
with col3:
    st.metric("📂 分类数", f"{summary['total_categories']}")
with col4:
    st.metric("🏢 出版社数", f"{summary['total_publishers']}")
with col5:
    st.metric("✍️ 作者数", f"{summary['total_authors']}")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("💰 平均价格", f"¥{summary['avg_price']:.2f}")
with col2:
    st.metric("📉 平均折扣", f"{summary['avg_discount']:.1f}折")
with col3:
    st.metric("💬 总评论数", f"{summary['total_comments']:,}")
with col4:
    st.metric("⭐ 平均推荐率", f"{summary['avg_recommend_rate']:.1f}%")

st.markdown("---")

st.markdown("## 📋 榜单分布统计")
list_dist = summary['list_distribution']
col1, col2, col3, col4 = st.columns(4)
for i, (count, num) in enumerate(list_dist.items()):
    col = [col1, col2, col3, col4][i % 4]
    with col:
        st.metric(f"上榜{count}次", f"{num:,}本")

multi_list_pct = summary['multi_list_books'] / summary['total_books'] * 100
st.info(f"💡 有 {summary['multi_list_books']:,} 本书同时在多个榜单出现，占比 {multi_list_pct:.1f}%")

st.markdown("---")

st.sidebar.markdown("### 筛选条件")

selected_list_type = st.sidebar.multiselect(
    "选择榜单类型",
    list_types,
    default=list_types
)

price_range = st.sidebar.slider(
    "价格范围（元）",
    float(df['price'].min()),
    float(df['price'].max()),
    (0.0, float(df['price'].max())),
    step=1.0
)

comments_range = st.sidebar.slider(
    "评论数范围",
    int(df['comments'].min()),
    int(df['comments'].max()),
    (0, int(df['comments'].max())),
    step=1000
)

filtered_df = filter_data(
    df, 
    list_types=selected_list_type if selected_list_type else None,
    price_range=price_range,
    comments_range=comments_range
)

st.markdown(f"**当前筛选结果：{len(filtered_df):,} 条记录**")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("📚 书籍数量", f"{len(filtered_df):,}")
with col2:
    st.metric("💰 平均价格", f"¥{filtered_df['price'].mean():.2f}")
with col3:
    st.metric("💬 平均评论数", f"{filtered_df['comments'].mean():.0f}")
with col4:
    st.metric("⭐ 平均推荐率", f"{filtered_df['recommend_rate'].mean():.1f}%")

st.markdown("---")

st.markdown("## 📂 分类分析")

col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("### 分类分布")
    category_counts = filtered_df['category'].value_counts()
    if len(category_counts) > 0:
        pie = create_pie_chart(category_counts, title="各分类书籍占比", show_top=12)
        st_pyecharts(pie)
    else:
        st.info("暂无数据")

with col2:
    st.markdown("### 各分类书籍数量TOP15")
    if len(filtered_df) > 0:
        category_counts_top = category_counts.sort_values(ascending=True).tail(15)
        
        fig = px.bar(x=category_counts_top.values, y=category_counts_top.index, orientation='h',
                     color=category_counts_top.values, color_continuous_scale='Teal',
                     title='各分类书籍数量', height=450)
        fig.update_layout(margin=dict(t=30, b=20, l=20, r=20), xaxis_title="书籍数量", yaxis_title="", showlegend=False)
        fig.update_coloraxes(showscale=False)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("暂无数据")

st.markdown("---")

st.markdown("## 🔥 热门书籍 TOP 20")
top_books = get_top_books(filtered_df, by='comments', top_n=20)
if len(top_books) > 0:
    top_books_sorted = top_books.sort_values('comments', ascending=True)
    
    fig = px.bar(top_books_sorted, x='comments', y='title', orientation='h',
                 color='comments', color_continuous_scale='Oranges',
                 title='热门书籍评论数TOP20', height=600)
    fig.update_layout(margin=dict(t=30, b=20, l=20, r=20), yaxis_title="", showlegend=False)
    fig.update_coloraxes(showscale=False)
    fig.update_yaxes(tickfont_size=10)
    st.plotly_chart(fig, use_container_width=True)
    
    with st.expander("📋 查看详细数据"):
        top_books_display = top_books.copy()
        top_books_display['价格'] = top_books_display['price'].apply(lambda x: f"¥{x:.2f}")
        top_books_display['评论数'] = top_books_display['comments'].apply(lambda x: f"{x:,}")
        top_books_display['推荐率'] = top_books_display['recommend_rate'].apply(lambda x: f"{x:.1f}%")
        top_books_display['上榜榜单'] = top_books_display['list_types'].apply(lambda x: x.replace('|', ', ') if pd.notna(x) else '')
        top_books_display = top_books_display[['title', 'author', '价格', '评论数', '推荐率', 'category', '上榜榜单', 'list_count']]
        top_books_display.columns = ['书名', '作者', '价格', '评论数', '推荐率', '分类', '上榜榜单', '上榜次数']
        st.dataframe(top_books_display, use_container_width=True)
else:
    st.info("暂无数据")

st.markdown("---")

st.markdown("## 💰 价格分析")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 价格区间分布")
    if len(filtered_df) > 0:
        price_bins = [0, 20, 40, 60, 100, 200, 500, float('inf')]
        price_labels = ['0-20元', '20-40元', '40-60元', '60-100元', '100-200元', '200-500元', '500元以上']
        filtered_df_copy = filtered_df.copy()
        filtered_df_copy['价格区间'] = pd.cut(filtered_df_copy['price'], bins=price_bins, labels=price_labels, right=False)
        price_dist = filtered_df_copy['价格区间'].value_counts().sort_index()
        bar = create_bar_chart(
            price_dist.values.tolist(),
            price_dist.index.tolist(),
            title="各价格区间书籍数量",
            x_name="数量",
            y_name="价格区间",
            horizontal=True,
            height="400px"
        )
        st_pyecharts(bar)
    else:
        st.info("暂无数据")

with col2:
    st.markdown("### 榜单书籍数量")
    if len(filtered_df) > 0:
        list_type_data = []
        for _, row in filtered_df.iterrows():
            for lt in str(row['list_types']).split('|'):
                list_type_data.append(lt.strip())
        list_type_counts = pd.Series(list_type_data).value_counts()
        bar = create_bar_chart(
            list_type_counts.values.tolist(),
            list_type_counts.index.tolist(),
            title="各榜单书籍数量",
            x_name="数量",
            y_name="榜单",
            horizontal=True,
            height="400px"
        )
        st_pyecharts(bar)
    else:
        st.info("暂无数据")