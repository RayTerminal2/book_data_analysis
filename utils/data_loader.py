import pandas as pd
import os

DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'cleaned_all_books.csv')

def load_data():
    df = pd.read_csv(DATA_PATH, encoding='utf-8')
    return df

def get_categories(df):
    return sorted(df['category'].unique().tolist())

def get_all_list_types(df):
    all_types = set()
    for types_str in df['list_types'].unique():
        for t in str(types_str).split('|'):
            all_types.add(t.strip())
    return sorted(list(all_types))

def get_category_stats(df):
    stats = df.groupby('category').agg({
        'title': 'count',
        'price': 'mean',
        'original_price': 'mean',
        'comments': 'sum',
        'recommend_rate': 'mean',
        'discount': 'mean',
        'list_count': 'mean'
    }).round(2)
    stats.columns = ['书籍数量', '平均价格', '平均原价', '总评论数', '平均推荐率', '平均折扣', '平均上榜次数']
    stats = stats.sort_values('书籍数量', ascending=False)
    return stats.reset_index()

def get_list_type_stats(df):
    list_type_data = []
    for _, row in df.iterrows():
        for lt in str(row['list_types']).split('|'):
            list_type_data.append({
                'list_type': lt.strip(),
                'price': row['price'],
                'comments': row['comments'],
                'recommend_rate': row['recommend_rate']
            })
    lt_df = pd.DataFrame(list_type_data)
    stats = lt_df.groupby('list_type').agg({
        'price': 'mean',
        'comments': 'mean',
        'recommend_rate': 'mean'
    }).round(2)
    stats['书籍数量'] = lt_df.groupby('list_type').size()
    stats = stats[['书籍数量', 'price', 'comments', 'recommend_rate']]
    stats.columns = ['书籍数量', '平均价格', '平均评论数', '平均推荐率']
    return stats.reset_index()

def get_top_books(df, by='comments', top_n=20):
    return df.nlargest(top_n, by)[['title', 'author', 'price', 'comments', 'recommend_rate', 'category', 'list_types', 'list_count']]

def get_data_summary(df):
    summary = {
        'total_books': len(df),
        'total_records': int(df['list_count'].sum()),
        'total_categories': df['category'].nunique(),
        'total_publishers': df['publisher'].nunique(),
        'total_authors': df['author'].nunique(),
        'avg_price': df['price'].mean(),
        'avg_discount': df['discount'].mean(),
        'total_comments': df['comments'].sum(),
        'avg_recommend_rate': df['recommend_rate'].mean(),
        'multi_list_books': len(df[df['list_count'] > 1]),
        'list_distribution': df['list_count'].value_counts().sort_index().to_dict()
    }
    return summary

def filter_data(df, categories=None, list_types=None, price_range=None, comments_range=None):
    filtered = df.copy()
    if categories:
        filtered = filtered[filtered['category'].isin(categories)]
    if list_types:
        mask = filtered['list_types'].apply(lambda x: any(lt in str(x) for lt in list_types))
        filtered = filtered[mask]
    if price_range:
        filtered = filtered[(filtered['price'] >= price_range[0]) & (filtered['price'] <= price_range[1])]
    if comments_range:
        filtered = filtered[(filtered['comments'] >= comments_range[0]) & (filtered['comments'] <= comments_range[1])]
    return filtered