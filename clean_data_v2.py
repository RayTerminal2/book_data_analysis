import pandas as pd
import re
import os

def clean_price(price_str):
    if pd.isna(price_str):
        return None
    price_str = str(price_str).replace(',', '')
    match = re.search(r'[\d.]+', price_str)
    return float(match.group()) if match else None

def clean_comments(comment_str):
    if pd.isna(comment_str):
        return 0
    match = re.search(r'(\d+)', str(comment_str))
    return int(match.group()) if match else 0

def clean_recommend(recommend_str):
    if pd.isna(recommend_str):
        return None
    match = re.search(r'([\d.]+)', str(recommend_str))
    return float(match.group()) if match else None

def main():
    data_dir = os.path.dirname(os.path.abspath(__file__))
    
    files = [
        'dangdang_books_24hours.csv',
        'dangdang_books_recent30.csv',
        'dangdang_books_recent7.csv',
        'dangdang_books_year-2025.csv'
    ]
    
    all_data = []
    
    for file in files:
        file_path = os.path.join(data_dir, file)
        if os.path.exists(file_path):
            df = pd.read_csv(file_path, encoding='utf-8')
            df.columns = ['rank', 'title', 'author', 'publisher', 'price_raw', 'original_price_raw', 
                          'comments_raw', 'recommend_raw', 'category', 'list_type']
            all_data.append(df)
            print(f"读取 {file}: {len(df)} 条记录")
    
    df = pd.concat(all_data, ignore_index=True)
    print(f"\n合并后总计: {len(df)} 条记录")
    
    df = df[~df['list_type'].str.contains('新书', na=False)]
    print(f"删除新书热卖榜后: {len(df)} 条记录")
    
    df['price'] = df['price_raw'].apply(clean_price)
    df['original_price'] = df['original_price_raw'].apply(clean_price)
    df['comments'] = df['comments_raw'].apply(clean_comments)
    df['recommend_rate'] = df['recommend_raw'].apply(clean_recommend)
    df['discount'] = (df['price'] / df['original_price'] * 10).round(1)
    
    book_stats = df.groupby(['title', 'author']).agg({
        'publisher': 'first',
        'price': 'first',
        'original_price': 'first',
        'comments': 'sum',
        'recommend_rate': 'mean',
        'category': 'first',
        'list_type': lambda x: list(x.unique()),
        'rank': 'count'
    }).reset_index()
    
    book_stats['list_types_str'] = book_stats['list_type'].apply(lambda x: '|'.join(x))
    book_stats['list_count'] = book_stats['rank']
    book_stats['recommend_rate'] = book_stats['recommend_rate'].round(1)
    book_stats['discount'] = (book_stats['price'] / book_stats['original_price'] * 10).round(1)
    
    final_df = book_stats[['title', 'author', 'publisher', 'price', 'original_price', 
                           'comments', 'recommend_rate', 'category', 'list_types_str', 
                           'list_count', 'discount']]
    
    final_df.columns = ['title', 'author', 'publisher', 'price', 'original_price', 
                        'comments', 'recommend_rate', 'category', 'list_types', 
                        'list_count', 'discount']
    
    output_path = os.path.join(data_dir, 'cleaned_all_books.csv')
    final_df.to_csv(output_path, index=False, encoding='utf-8')
    print(f"\n清洗后保存: {output_path}")
    print(f"最终书籍数量: {len(final_df)} 本")
    print(f"\n各榜单书籍数量:")
    for lt in df['list_type'].unique():
        count = len(df[df['list_type'] == lt])
        print(f"  {lt}: {count}")
    
    print(f"\n多榜单出现统计:")
    for i in range(1, 5):
        count = len(final_df[final_df['list_count'] == i])
        print(f"  出现{i}次: {count} 本")

if __name__ == '__main__':
    main()