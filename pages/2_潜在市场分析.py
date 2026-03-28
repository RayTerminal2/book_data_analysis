import streamlit as st
import sys
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.data_loader import load_data, get_categories, filter_data

st.set_page_config(page_title="潜在市场分析", page_icon="🎯", layout="wide")

@st.cache_data
def get_data():
    return load_data()

df = get_data()
categories = get_categories(df)

st.markdown("# 🎯 图书行业潜在市场分析")

with st.sidebar:
    st.markdown("### 筛选条件")
    selected_categories = st.multiselect("选择分类", categories, default=categories)
    price_range = st.slider("价格范围", 0, 500, (0, 500))

filtered_df = filter_data(df, categories=selected_categories, price_range=price_range)

st.markdown("## 📊 榜单表现分析")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("📚 上榜书籍", f"{len(filtered_df):,}")
with col2:
    st.metric("💬 总评论数", f"{filtered_df['comments'].sum():,.0f}")
with col3:
    st.metric("💰 平均价格", f"¥{filtered_df['price'].mean():.2f}")
with col4:
    top_10_pct = max(1, int(len(filtered_df) * 0.1))
    top_share = filtered_df.nlargest(top_10_pct, 'comments')['comments'].sum() / filtered_df['comments'].sum() * 100
    st.metric("📈 头部10%占比", f"{top_share:.1f}%")

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### 各分类读者关注度分布")
    category_stats = filtered_df.groupby('category').agg({
        'comments': 'sum'
    }).reset_index()
    category_stats = category_stats.sort_values('comments', ascending=False)
    
    if len(category_stats) > 0:
        top_10 = category_stats.head(10)
        other_sum = category_stats.iloc[10:]['comments'].sum() if len(category_stats) > 10 else 0
        
        labels = top_10['category'].tolist()
        values = top_10['comments'].tolist()
        if other_sum > 0:
            labels.append('其他')
            values.append(other_sum)
        
        fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=0.4,
                                        marker_colors=px.colors.qualitative.Set2[:len(labels)])])
        fig.update_layout(height=400, showlegend=True, margin=dict(t=20, b=20, l=20, r=20))
        st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown("### 头部效应解读")
    if top_share > 80:
        st.warning("⚠️ 极强头部效应\n\n头部10%书籍占据80%以上评论，读者注意力高度集中")
    elif top_share > 60:
        st.info("ℹ️ 较强头部效应\n\n头部10%书籍占据60-80%评论，读者注意力较集中")
    else:
        st.success("✅ 相对均衡\n\n头部效应不明显，新书有较多曝光机会")

st.markdown("---")

st.markdown("## 🚀 榜单深度分析")

st.markdown("### 持续热度TOP15")
heat_stats = filtered_df.groupby('category').agg({
    'list_count': lambda x: (x >= 3).sum() / len(x) * 100,
    'comments': 'mean'
}).reset_index()
heat_stats.columns = ['分类', '多榜占比', '平均评论数']
heat_stats = heat_stats.sort_values('多榜占比', ascending=True).tail(15)

fig = px.bar(heat_stats, x='多榜占比', y='分类', orientation='h',
             color='多榜占比', color_continuous_scale='Blues',
             title='多榜占比(%)', height=450)
fig.update_layout(margin=dict(t=30, b=20, l=20, r=20), yaxis_title="", showlegend=False)
fig.update_coloraxes(showscale=False)
st.plotly_chart(fig, use_container_width=True)
st.caption("📊 多榜占比：同时出现在3个及以上榜单的书籍比例，反映持续热度")

st.markdown("---")

st.markdown("## 💰 价格与折扣分析")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 价格分布")
    fig = px.histogram(filtered_df, x='price', nbins=50, 
                       title='书籍价格分布', height=400,
                       color_discrete_sequence=['#636EFA'])
    fig.update_layout(margin=dict(t=30, b=20, l=20, r=20), xaxis_title="价格(元)", yaxis_title="书籍数量")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown("### 折扣分布")
    fig = px.histogram(filtered_df, x='discount', nbins=30, 
                       title='书籍折扣分布', height=400,
                       color_discrete_sequence=['#EF553B'])
    fig.update_layout(margin=dict(t=30, b=20, l=20, r=20), xaxis_title="折扣(折)", yaxis_title="书籍数量")
    st.plotly_chart(fig, use_container_width=True)

st.markdown("### 价格与评论数关系")
price_scatter = filtered_df[filtered_df['comments'] > 0].copy()
if len(price_scatter) > 0:
    fig = px.scatter(price_scatter, x='price', y='comments', color='category',
                     hover_data=['title'], title='价格与评论数散点图', height=400,
                     color_discrete_sequence=px.colors.qualitative.Set2)
    fig.update_layout(margin=dict(t=30, b=20, l=20, r=20), xaxis_title="价格(元)", yaxis_title="评论数")
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

st.markdown("## 🏢 榜单竞争格局")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 出版社评论数TOP15")
    publisher_stats = filtered_df.groupby('publisher').agg({
        'comments': 'sum'
    }).reset_index()
    publisher_stats = publisher_stats.sort_values('comments', ascending=True).tail(15)
    
    fig = px.bar(publisher_stats, x='comments', y='publisher', orientation='h',
                 color='comments', color_continuous_scale='Teal',
                 title='出版社总评论数', height=450)
    fig.update_layout(margin=dict(t=30, b=20, l=20, r=20), yaxis_title="", showlegend=False)
    fig.update_coloraxes(showscale=False)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown("### 作者评论数TOP15")
    author_stats = filtered_df.groupby('author').agg({
        'comments': 'sum'
    }).reset_index()
    author_stats = author_stats.sort_values('comments', ascending=True).tail(15)
    
    fig = px.bar(author_stats, x='comments', y='author', orientation='h',
                 color='comments', color_continuous_scale='Purples',
                 title='作者总评论数', height=450)
    fig.update_layout(margin=dict(t=30, b=20, l=20, r=20), yaxis_title="", showlegend=False)
    fig.update_coloraxes(showscale=False)
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

st.markdown("## 💡 榜单机会识别")

st.markdown("### 分类机会矩阵")
opportunity_data = filtered_df.groupby('category').agg({
    'title': 'count',
    'comments': 'sum',
    'recommend_rate': 'mean'
}).reset_index()
opportunity_data.columns = ['分类', '书籍数量', '总评论数', '平均推荐率']

median_books = opportunity_data['书籍数量'].median()
median_comments = opportunity_data['总评论数'].median()

fig = px.scatter(opportunity_data, x='书籍数量', y='总评论数',
                 color='分类', title='分类机会矩阵', height=500,
                 color_discrete_sequence=px.colors.qualitative.Set2)
fig.update_traces(marker_size=12)
fig.add_hline(y=median_comments, line_dash="dash", line_color="gray", annotation_text="评论中位数")
fig.add_vline(x=median_books, line_dash="dash", line_color="gray", annotation_text="书籍中位数")
fig.update_layout(margin=dict(t=30, b=20, l=20, r=20), legend_orientation="h", legend_y=-0.2)
st.plotly_chart(fig, use_container_width=True)

st.markdown("**📊 图表解读：**")
st.markdown("- **左上区域**：高关注度低竞争领域，评论多但书籍少，市场机会大")
st.markdown("- **右上区域**：高关注度高竞争领域，评论多书籍也多，竞争激烈")
st.markdown("- **左下区域**：低关注度低竞争领域，评论少书籍少，市场待开发")
st.markdown("- **右下区域**：低关注度高竞争领域，评论少书籍多，需谨慎进入")

col1, col2 = st.columns(2)

with col1:
    opportunities = opportunity_data[
        (opportunity_data['书籍数量'] <= median_books) & 
        (opportunity_data['总评论数'] >= median_comments)
    ].sort_values('总评论数', ascending=False)
    
    st.markdown("### 🎯 高关注度低竞争领域")
    if len(opportunities) > 0:
        st.info(f"共发现 **{len(opportunities)}** 个领域，展示TOP5")
        for _, row in opportunities.head(5).iterrows():
            st.write(f"- **{row['分类']}**: {row['总评论数']:,.0f}条评论，{row['书籍数量']}本书")
    else:
        st.info("暂未发现高关注度低竞争领域")

with col2:
    quality_picks = opportunity_data[
        (opportunity_data['平均推荐率'] >= opportunity_data['平均推荐率'].median()) &
        (opportunity_data['总评论数'] >= median_comments)
    ].sort_values('平均推荐率', ascending=False)
    
    st.markdown("### 💰 高满意度高关注度分类")
    if len(quality_picks) > 0:
        st.success(f"共发现 **{len(quality_picks)}** 个分类，展示TOP5")
        for _, row in quality_picks.head(5).iterrows():
            st.write(f"- **{row['分类']}**: {row['平均推荐率']:.1f}%推荐率，{row['总评论数']:,.0f}条评论")
    else:
        st.success("暂未发现高满意度高关注度分类")

st.markdown("---")

st.markdown("## 📋 榜单洞察总结")

if len(filtered_df) > 0:
    total_books = len(filtered_df)
    total_comments = filtered_df['comments'].sum()
    avg_price = filtered_df['price'].mean()
    avg_discount = filtered_df['discount'].mean()
    
    top_category = category_stats.iloc[0]['category'] if len(category_stats) > 0 else 'N/A'
    top_publisher = publisher_stats.iloc[-1]['publisher'] if len(publisher_stats) > 0 else 'N/A'
    top_heat = heat_stats.iloc[-1]['分类'] if len(heat_stats) > 0 else 'N/A'
    
    st.markdown(f"""
    **榜单概况：**
    - 当前筛选范围内共有 **{total_books:,}** 本上榜书籍，累计 **{total_comments:,.0f}** 条评论
    - 平均价格 **¥{avg_price:.2f}**，平均折扣 **{avg_discount:.1f}折**
    
    **关键发现：**
    - 读者关注度最高的分类：**{top_category}**
    - 持续热度最高的分类：**{top_heat}**
    - 榜单表现最好的出版社：**{top_publisher}**
    - 发现 **{len(opportunities)}** 个高关注度低竞争领域
    - 发现 **{len(quality_picks)}** 个高满意度高关注度分类
    
    **注意：** 本分析基于当当网畅销榜数据，反映的是榜单表现而非真实市场份额。
    """)