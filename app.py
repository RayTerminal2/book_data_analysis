import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.data_loader import load_data, get_data_summary

st.set_page_config(
    page_title="当当网图书市场数据分析",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def get_data():
    return load_data()

df = get_data()
summary = get_data_summary(df)

st.markdown('<h1 class="main-header">📚 当当网图书市场数据分析平台</h1>', unsafe_allow_html=True)

st.sidebar.markdown("### 📊 导航")
st.sidebar.markdown("请从左侧页面列表选择分析模块")

st.markdown("## 欢迎使用图书市场数据分析平台")

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

st.markdown("---")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("💰 平均价格", f"¥{df['price'].mean():.2f}")
with col2:
    st.metric("📉 平均折扣", f"{df['discount'].mean():.1f}折")
with col3:
    st.metric("💬 总评论数", f"{df['comments'].sum():,}")
with col4:
    st.metric("⭐ 平均推荐率", f"{df['recommend_rate'].mean():.1f}%")

st.markdown("---")
st.markdown("### 📖 使用说明")
st.markdown("""
1. **市场概览** - 查看整体市场数据和分类分布
2. **分类分析** - 深入分析各分类特征
3. **出版社分析** - 了解出版社竞争格局
4. **作者分析** - 探索作者影响力
5. **价格策略** - 分析定价与折扣规律
6. **趋势对比** - 对比不同榜单变化
7. **畅销书画像** - 解析畅销书成功要素

请在左侧页面列表中选择相应模块开始分析。
""")