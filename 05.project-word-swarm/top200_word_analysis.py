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
    'let', 'know', 'take', 'going', 'put', 'set', 'thing', 'things','million','based', 'years', 'companies'
}

def simple_tokenize(text):
    """简单的分词函数"""
    # 移除非字母字符并转为小写
    text = re.sub(r'[^a-zA-Z\s]', ' ', text.lower())
    # 分词
    return [word.strip() for word in text.split() if word.strip()]

class Top200WordAnalyzer:
    def __init__(self, data_dir="output"):
        """
        初始化词频分析器
        
        Args:
            data_dir: 包含JSON文件的目录
        """
        self.data_dir = data_dir
        self.articles = []
        
        # 使用内置停用词列表
        self.stop_words = ENGLISH_STOP_WORDS.copy()
        
        # 添加一些旅游行业特定的停用词
        travel_stops = {
            'travel', 'company', 'business', 'market', 'service', 'services', 
            'industry', 'customers', 'customer', 'data', 'online', 'platform',
            'technology', 'app', 'product', 'experience', 'booking', 'bookings',
            'flight', 'flights', 'hotel', 'hotels', 'vacation', 'destination',
            'destinations', 'tour', 'tours', 'trip', 'trips', 'traveler', 'travelers',
            'agency', 'agencies', 'global', 'international',
            # 新增的停用词
            'people', 'via', 'part', 'help', 'want', 'across', 'think', 'three', 
            'end', 'big', 'really', 'already', 'within', 'lot'
        }
        self.stop_words.update(travel_stops)
        
        # 创建输出目录
        self.output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "analysis_results")
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
    # TODO: use different data processing methods or
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
    # TODO: spliting：对于像marketing这样的词，我假设他通常是以marketing作为phrase当中的其中一个词，所以能不能对于某些特定的词作为输入（比如说marketing），然后根据这个词的前后词进行统计，
    # TODO: 是在一个一个时间段之内对关键词进行统计，而不是对于一个历史范围内的关键词进行统计（或者说用另外一个方法，现在统计的是总共的出现次数，可以是一段时间内的（速度？））
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

    def analyze_word_frequency(self):
        """分析词频并提取top 200词语"""
        all_words = []
        
        print("开始分析文章内容...")
        for article in tqdm(self.articles, desc="处理文章"):
            try:
                content = article.get('content', '')
                words = self.preprocess_text(content)
                all_words.extend(words)
            except Exception as e:
                print(f"处理文章时出错: {e}")
        
        # 统计词频
        word_counts = Counter(all_words)
        
        # 获取前200个高频词
        self.top_200_words = word_counts.most_common(200)
        
        print(f"\n分析完成！共处理了 {len(all_words)} 个单词")
        print(f"识别出 {len(word_counts)} 个不同的单词")
        
        return self.top_200_words

    def plot_top_200_distribution(self):
        """绘制top 200词语的分布图"""
        if not hasattr(self, 'top_200_words'):
            print("请先运行 analyze_word_frequency() 方法")
            return
            
        # 提取词语和频率
        words, frequencies = zip(*self.top_200_words)
        
        # 创建DataFrame
        df = pd.DataFrame({
            'word': words,
            'frequency': frequencies
        })
        
        # 绘制前50个词的柱状图
        plt.figure(figsize=(20, 10))
        plt.bar(range(50), df['frequency'][:50], color='skyblue')
        plt.xticks(range(50), df['word'][:50], rotation=45, ha='right')
        plt.title('Top 50 Most Frequent Words', fontsize=16)
        plt.xlabel('Words', fontsize=12)
        plt.ylabel('Frequency', fontsize=12)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, 'top_50_words.png'), dpi=300)
        plt.close()
        
        # 保存完整的top 200数据到CSV
        df.to_csv(os.path.join(self.output_dir, 'top_200_words.csv'), index=False)
        
        # 创建词云图
        wordcloud = WordCloud(
            width=1600, 
            height=800,
            background_color='white',
            max_words=200,
            contour_width=3,
            contour_color='steelblue',
            colormap='viridis'
        ).generate_from_frequencies(dict(self.top_200_words))
        
        plt.figure(figsize=(20, 10))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis("off")
        plt.tight_layout(pad=0)
        plt.savefig(os.path.join(self.output_dir, 'top_200_wordcloud.png'), dpi=300)
        plt.close()
        
        print(f"可视化结果已保存至: {self.output_dir}")
        print("\nTop 20 最常见词语:")
        for word, freq in self.top_200_words[:20]:
            print(f"{word}: {freq}")

    def run_analysis(self):
        """运行完整分析流程"""
        print("开始词频分析...")
        
        # 加载数据
        self.load_data()
        
        # 分析词频
        self.analyze_word_frequency()
        
        # 生成可视化
        print("\n生成可视化结果...")
        self.plot_top_200_distribution()
        
        print("\n分析完成！")
        print(f"所有结果保存在: {self.output_dir}")

if __name__ == "__main__":
    # 创建分析器实例
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
    analyzer = Top200WordAnalyzer(data_dir=data_dir)
    
    # 运行分析
    analyzer.run_analysis() 