import json
import os
import glob
from collections import Counter
import matplotlib.pyplot as plt
import pandas as pd
import re
from datetime import datetime
import seaborn as sns
from tqdm import tqdm
from wordcloud import WordCloud
import numpy as np
from pathlib import Path

# 英文停用词列表(内置)
ENGLISH_STOP_WORDS = {
    'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", 
    "you've", "you'll", "you'd", 'your', 'yours', 'yourself', 'yourselves', 
    'he', 'him', 'his', 'himself', 'she', "she's", 'her', 'hers', 'herself', 
    'it', "it's", 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 
    'what', 'which', 'who', 'whom', 'this', 'that', "that'll", 'these', 'those', 
    'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 
    'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 
    'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 
    'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after', 
    'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 
    'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 
    'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 
    'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 
    'very', 's', 't', 'can', 'will', 'just', 'don', "don't", 'should', "should've", 
    'now', 'd', 'll', 'm', 'o', 're', 've', 'y', 'ain', 'aren', "aren't", 'couldn', 
    "couldn't", 'didn', "didn't", 'doesn', "doesn't", 'hadn', "hadn't", 'hasn', 
    "hasn't", 'haven', "haven't", 'isn', "isn't", 'ma', 'mightn', "mightn't", 'mustn', 
    "mustn't", 'needn', "needn't", 'shan', "shan't", 'shouldn', "shouldn't", 'wasn', 
    "wasn't", 'weren', "weren't", 'won', "won't", 'wouldn', "wouldn't",
    # 行业特定停用词
    'said', 'says', 'will', 'new', 'also', 'one', 'two', 'may', 'now', 'use', 
    'using', 'used', 'can', 'could', 'would', 'should', 'get', 'many', 'much', 
    'year', 'month', 'day', 'time', 'way', 'week', 'need', 'make', 'see', 'look', 
    'even', 'first', 'last', 'still', 'going', 'however', 'including', 'according',
    'inc', 'ltd', 'co', 'com', 'org', 'net', 'www', 'that', 'well', 'still',
    'said', 'say', 'says', 'like', 'good', 'able', 'just', 'made', 'making',
    'let', 'know', 'take', 'going', 'put', 'set', 'thing', 'things'
}

def simple_tokenize(text):
    """简单的分词函数"""
    # 移除非字母字符并转为小写
    text = re.sub(r'[^a-zA-Z\s]', ' ', text.lower())
    # 分词
    return [word.strip() for word in text.split() if word.strip()]

class KeywordAnalyzer:
    def __init__(self, data_dir="output", top_n=30):
        """
        初始化关键词分析器
        
        Args:
            data_dir: 包含JSON文件的目录
            top_n: 要分析的前N个关键词
        """
        self.data_dir = data_dir
        self.top_n = top_n
        self.articles = []
        self.keywords_by_time = {}
        
        # 使用内置停用词列表
        self.stop_words = ENGLISH_STOP_WORDS.copy()
        
        # 添加一些旅游行业特定的停用词
        travel_stops = {
            'travel', 'company', 'business', 'market', 'service', 'services', 
            'industry', 'customers', 'customer', 'data', 'online', 'platform',
            'technology', 'app', 'product', 'experience', 'booking', 'bookings',
            'flight', 'flights', 'hotel', 'hotels', 'vacation', 'destination',
            'destinations', 'tour', 'tours', 'trip', 'trips', 'traveler', 'travelers',
            'agency', 'agencies', 'global', 'international'
        }
        self.stop_words.update(travel_stops)
        
        # 创建输出目录
        self.output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "analysis_results")
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
    
    def load_data(self):
        """从JSON文件加载文章数据"""
        json_files = glob.glob(os.path.join(self.data_dir, "phocuswire_page_*.json"))
        all_articles = []
        
        print(f"找到 {len(json_files)} 个JSON文件")
        
        for json_file in tqdm(json_files, desc="加载文章数据"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    articles = json.load(f)
                    all_articles.extend(articles)
            except Exception as e:
                print(f"读取文件 {json_file} 时出错: {e}")
        
        print(f"总共加载了 {len(all_articles)} 篇文章")
        self.articles = all_articles
        return all_articles
    
    def parse_date(self, date_str):
        """解析日期字符串为日期对象"""
        try:
            # 尝试各种可能的日期格式
            date_formats = [
                "%B %d, %Y",       # August 22, 2018
                "%d %B %Y",        # 22 August 2018
                "%B %Y",           # August 2018
                "%b %d, %Y",       # Aug 22, 2018
                "%d %b %Y",        # 22 Aug 2018
                "%d-%m-%Y",        # 22-08-2018
                "%Y-%m-%d",        # 2018-08-22
                "%m/%d/%Y",        # 08/22/2018
                "%d/%m/%Y"         # 22/08/2018
            ]
            
            for date_format in date_formats:
                try:
                    return datetime.strptime(date_str.strip(), date_format)
                except ValueError:
                    continue
                    
            # 如果只有年份
            if re.match(r"^\d{4}$", date_str.strip()):
                return datetime.strptime(date_str.strip(), "%Y")
                
            return None
        except:
            return None
    
    def preprocess_text(self, text):
        """预处理文本"""
        if not text:
            return []
            
        # 移除非字母字符
        text = re.sub(r'[^a-zA-Z\s]', ' ', text.lower())
        
        # 分词
        words = simple_tokenize(text)
        
        # 移除停用词和短词
        words = [word for word in words if word not in self.stop_words and len(word) > 2]
        
        return words

    def extract_keywords(self):
        """从所有文章中提取关键词"""
        all_words = []
        time_periods = {}
        
        for article in tqdm(self.articles, desc="提取关键词"):
            try:
                # 解析日期
                date_str = article.get('date')
                if not date_str:
                    continue
                    
                date_obj = self.parse_date(date_str)
                if not date_obj:
                    continue
                
                # 将日期转换为年月格式
                year_month = date_obj.strftime("%Y-%m")
                
                # 预处理文章内容
                content = article.get('content', '')
                words = self.preprocess_text(content)
                
                # 添加到所有词列表
                all_words.extend(words)
                
                # 按时间段组织关键词
                if year_month not in time_periods:
                    time_periods[year_month] = []
                time_periods[year_month].extend(words)
            except Exception as e:
                print(f"处理文章时出错: {e}")
        
        # 统计全局词频
        word_counts = Counter(all_words)
        
        # 获取前N个关键词
        top_keywords = [word for word, count in word_counts.most_common(self.top_n)]
        
        # 统计每个时间段的关键词频率
        keywords_by_time = {}
        for period, words in time_periods.items():
            period_counts = Counter(words)
            keywords_by_time[period] = {word: period_counts.get(word, 0) for word in top_keywords}
        
        self.top_keywords = top_keywords
        self.keywords_by_time = keywords_by_time
        self.all_word_counts = word_counts
        
        print(f"提取完成，识别出 {len(word_counts)} 个独特关键词")
        print(f"最常见的10个关键词: {word_counts.most_common(10)}")
        
        return top_keywords, keywords_by_time
    
    def create_time_series_df(self):
        """创建时间序列数据框"""
        if not self.keywords_by_time:
            print("请先运行 extract_keywords() 方法")
            return None
            
        # 转换为DataFrame
        data = []
        for period, keywords in self.keywords_by_time.items():
            for keyword, count in keywords.items():
                data.append({
                    'period': period,
                    'keyword': keyword,
                    'count': count
                })
        
        df = pd.DataFrame(data)
        
        # 转换为时间索引
        df['period'] = pd.to_datetime(df['period'])
        df = df.sort_values('period')
        
        return df
    
    def plot_keyword_trends(self, top_k=10):
        """绘制关键词趋势图"""
        df = self.create_time_series_df()
        if df is None or df.empty:
            print("没有足够的数据来生成趋势图")
            return
            
        # 计算每个关键词的总计数
        keyword_totals = df.groupby('keyword')['count'].sum().sort_values(ascending=False)
        top_keywords = keyword_totals.index[:top_k].tolist()
        
        if not top_keywords:
            print("没有足够的关键词数据来生成趋势图")
            return
            
        # 仅保留前K个关键词
        df_top = df[df['keyword'].isin(top_keywords)]
        
        # 创建透视表
        pivot_df = df_top.pivot(index='period', columns='keyword', values='count')
        
        # 填充缺失值
        pivot_df = pivot_df.fillna(0)
        
        # 平滑数据（可选）
        pivot_df_smooth = pivot_df.rolling(window=3, min_periods=1).mean()
        
        # 绘制趋势图
        plt.figure(figsize=(15, 8))
        ax = pivot_df_smooth.plot(figsize=(15, 8), linewidth=2.5)
        
        plt.title('Top Keywords Trends Over Time', fontsize=18)
        plt.xlabel('Time Period', fontsize=14)
        plt.ylabel('Keyword Frequency', fontsize=14)
        plt.legend(fontsize=12)
        plt.grid(True, alpha=0.3)
        
        # 保存图表
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, f'keyword_trends_top{top_k}.png'), dpi=300)
        plt.close()
        
        # 热图
        plt.figure(figsize=(15, 10))
        sns.heatmap(pivot_df.T, cmap='YlGnBu', linewidths=0.5, linecolor='gray')
        plt.title('Keyword Frequency Heatmap', fontsize=18)
        plt.xlabel('Time Period', fontsize=14)
        plt.ylabel('Keyword', fontsize=14)
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, f'keyword_heatmap_top{top_k}.png'), dpi=300)
        plt.close()
        
        print(f"已保存关键词趋势图至 {self.output_dir}")
    
    def plot_wordcloud(self):
        """生成词云图"""
        if not hasattr(self, 'all_word_counts') or not self.all_word_counts:
            print("请先运行 extract_keywords() 方法或确保有足够的关键词")
            return
        
        if len(self.all_word_counts) == 0:
            print("没有提取到任何关键词，无法生成词云")
            return
            
        wordcloud = WordCloud(
            width=1200, 
            height=800,
            background_color='white',
            max_words=200,
            contour_width=3,
            contour_color='steelblue',
            colormap='viridis'
        ).generate_from_frequencies(self.all_word_counts)
        
        plt.figure(figsize=(15, 10))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis("off")
        plt.tight_layout(pad=0)
        plt.savefig(os.path.join(self.output_dir, 'wordcloud.png'), dpi=300)
        plt.close()
        
        print(f"已保存词云图至 {self.output_dir}")
    
    def plot_yearly_keyword_comparison(self):
        """比较不同年份的关键词分布"""
        df = self.create_time_series_df()
        if df is None or df.empty:
            print("没有足够的数据来生成年度对比图")
            return
            
        # 添加年份列
        df['year'] = df['period'].dt.year
        
        # 每年的关键词频率
        yearly_data = []
        for year, group in df.groupby('year'):
            yearly_counts = group.groupby('keyword')['count'].sum()
            yearly_data.append({
                'year': year,
                'counts': yearly_counts
            })
        
        # 比较至少有两年数据的情况
        if len(yearly_data) < 2:
            print("数据不足以进行年度比较")
            return
            
        # 取最早和最晚的年份进行比较
        years = sorted([d['year'] for d in yearly_data])
        if len(years) > 1:
            earliest = years[0]
            latest = years[-1]
            
            earliest_data = next(d for d in yearly_data if d['year'] == earliest)
            latest_data = next(d for d in yearly_data if d['year'] == latest)
            
            # 找出共同的关键词
            common_keywords = set(earliest_data['counts'].keys()) & set(latest_data['counts'].keys())
            
            if not common_keywords:
                print("不同年份间没有共同的关键词")
                return
                
            # 构建对比数据
            compare_data = []
            for keyword in common_keywords:
                early_count = earliest_data['counts'].get(keyword, 0)
                late_count = latest_data['counts'].get(keyword, 0)
                
                # 计算变化百分比
                if early_count > 0:
                    change_pct = (late_count - early_count) / early_count * 100
                else:
                    change_pct = np.inf if late_count > 0 else 0
                
                compare_data.append({
                    'keyword': keyword,
                    f'{earliest}_count': early_count,
                    f'{latest}_count': late_count,
                    'change_pct': change_pct
                })
            
            # 转为DataFrame并排序
            compare_df = pd.DataFrame(compare_data)
            if compare_df.empty:
                print("没有足够的数据来生成年度对比图")
                return
                
            compare_df = compare_df.sort_values('change_pct', ascending=False)
            
            # 选择变化最大的关键词
            top_increased = compare_df.head(15)
            top_decreased = compare_df.tail(15).iloc[::-1]
            
            if not top_increased.empty:
                # 绘制增加最多的关键词
                plt.figure(figsize=(12, 8))
                plt.barh(top_increased['keyword'], top_increased['change_pct'], color='green')
                plt.title(f'Keywords with Largest Increase ({earliest} to {latest})', fontsize=16)
                plt.xlabel('Percentage Change (%)', fontsize=14)
                plt.ylabel('Keyword', fontsize=14)
                plt.grid(axis='x', alpha=0.3)
                plt.tight_layout()
                plt.savefig(os.path.join(self.output_dir, f'keywords_increased_{earliest}_to_{latest}.png'), dpi=300)
                plt.close()
            
            if not top_decreased.empty:
                # 绘制减少最多的关键词
                plt.figure(figsize=(12, 8))
                plt.barh(top_decreased['keyword'], top_decreased['change_pct'], color='red')
                plt.title(f'Keywords with Largest Decrease ({earliest} to {latest})', fontsize=16)
                plt.xlabel('Percentage Change (%)', fontsize=14)
                plt.ylabel('Keyword', fontsize=14)
                plt.grid(axis='x', alpha=0.3)
                plt.tight_layout()
                plt.savefig(os.path.join(self.output_dir, f'keywords_decreased_{earliest}_to_{latest}.png'), dpi=300)
                plt.close()
            
            print(f"已保存年度关键词对比图至 {self.output_dir}")
    
    def run_analysis(self):
        """运行完整分析流程"""
        print("开始关键词分析...")
        
        # 加载数据
        self.load_data()
        
        # 提取关键词
        self.extract_keywords()
        
        # 生成可视化
        print("生成关键词趋势图...")
        self.plot_keyword_trends(top_k=10)
        
        print("生成词云图...")
        self.plot_wordcloud()
        
        print("生成年度关键词对比图...")
        self.plot_yearly_keyword_comparison()
        
        print("分析完成！")
        print(f"所有结果保存在: {self.output_dir}")

if __name__ == "__main__":
    # 创建分析器实例
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
    analyzer = KeywordAnalyzer(data_dir=data_dir)
    
    # 运行分析
    analyzer.run_analysis() 