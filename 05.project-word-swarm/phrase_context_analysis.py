import json
import os
import glob
from collections import Counter, defaultdict
import matplotlib.pyplot as plt
import pandas as pd
import re
from pathlib import Path
from tqdm import tqdm
import seaborn as sns

class PhraseContextAnalyzer:
    def __init__(self, data_dir="output", window_size=2):
        """
        初始化短语上下文分析器
        
        Args:
            data_dir: 包含JSON文件的目录
            window_size: 目标词前后要分析的词数量
        """
        self.data_dir = data_dir
        self.window_size = window_size
        self.articles = []
        
        # 创建输出目录
        self.output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "context_analysis_results")
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        
        # 基础停用词（用于过滤上下文词）
        self.stop_words = {
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from', 
            'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the', 
            'to', 'was', 'were', 'will', 'with', 'the', 'this', 'but', 'they',
            'have', 'had', 'what', 'when', 'where', 'who', 'which', 'why', 'how'
        }
    
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

    def preprocess_text(self, text):
        """预处理文本，返回词列表"""
        if not text:
            return []
        
        # 移除非字母字符并转为小写
        text = re.sub(r'[^a-zA-Z\s]', ' ', text.lower())
        
        # 分词并移除空字符串
        words = [word.strip() for word in text.split() if word.strip()]
        
        return words

    def analyze_context(self, target_word, min_freq=5):
        """
        分析目标词的上下文
        
        Args:
            target_word: 要分析的目标词
            min_freq: 上下文词最小出现频率
        """
        before_words = Counter()  # 目标词前面的词统计
        after_words = Counter()   # 目标词后面的词统计
        phrases = []             # 完整短语存储
        
        print(f"开始分析词语 '{target_word}' 的上下文...")
        
        for article in tqdm(self.articles, desc="处理文章"):
            try:
                content = article.get('content', '')
                words = self.preprocess_text(content)
                
                # 查找目标词的所有位置
                for i, word in enumerate(words):
                    if word == target_word:
                        # 收集前面的词
                        start_idx = max(0, i - self.window_size)
                        before_context = words[start_idx:i]
                        before_words.update(w for w in before_context if w not in self.stop_words)
                        
                        # 收集后面的词
                        end_idx = min(len(words), i + self.window_size + 1)
                        after_context = words[i+1:end_idx]
                        after_words.update(w for w in after_context if w not in self.stop_words)
                        
                        # 收集完整短语
                        phrase = ' '.join(words[start_idx:end_idx])
                        phrases.append(phrase)
                        
            except Exception as e:
                print(f"处理文章时出错: {e}")
        
        # 过滤低频词
        before_words = Counter({k: v for k, v in before_words.items() if v >= min_freq})
        after_words = Counter({k: v for k, v in after_words.items() if v >= min_freq})
        
        return before_words, after_words, phrases

    def plot_context_distribution(self, target_word, before_words, after_words):
        """绘制上下文词分布图"""
        # 创建前置词和后置词的DataFrame
        before_df = pd.DataFrame(before_words.most_common(15), columns=['word', 'frequency'])
        before_df['position'] = 'before'
        
        after_df = pd.DataFrame(after_words.most_common(15), columns=['word', 'frequency'])
        after_df['position'] = 'after'
        
        # 合并数据
        df = pd.concat([before_df, after_df])
        
        # 创建分组柱状图
        plt.figure(figsize=(15, 8))
        
        # 使用seaborn绘制
        sns.barplot(data=df, x='word', y='frequency', hue='position', palette=['skyblue', 'lightgreen'])
        
        plt.title(f"Most Common Words Around '{target_word}'", fontsize=16)
        plt.xlabel('Context Words', fontsize=12)
        plt.ylabel('Frequency', fontsize=12)
        plt.xticks(rotation=45, ha='right')
        plt.legend(title='Position')
        plt.grid(True, alpha=0.3)
        
        # 调整布局
        plt.tight_layout()
        
        # 保存图表
        plt.savefig(os.path.join(self.output_dir, f'{target_word}_context_distribution.png'), dpi=300)
        plt.close()

    def save_results(self, target_word, before_words, after_words, phrases):
        """保存分析结果"""
        # 保存词频数据到CSV
        before_df = pd.DataFrame(before_words.most_common(), columns=['word', 'frequency'])
        before_df.to_csv(os.path.join(self.output_dir, f'{target_word}_before_words.csv'), index=False)
        
        after_df = pd.DataFrame(after_words.most_common(), columns=['word', 'frequency'])
        after_df.to_csv(os.path.join(self.output_dir, f'{target_word}_after_words.csv'), index=False)
        
        # 保存常见短语
        with open(os.path.join(self.output_dir, f'{target_word}_common_phrases.txt'), 'w', encoding='utf-8') as f:
            f.write(f"Common phrases containing '{target_word}':\n\n")
            for phrase in phrases[:100]:  # 只保存前100个短语
                f.write(f"{phrase}\n")

    def analyze_target_word(self, target_word, min_freq=5):
        """分析特定目标词"""
        print(f"\n开始分析目标词: {target_word}")
        
        # 加载数据（如果还没加载）
        if not self.articles:
            self.load_data()
        
        # 分析上下文
        before_words, after_words, phrases = self.analyze_context(target_word, min_freq)
        
        if not before_words and not after_words:
            print(f"未找到与 '{target_word}' 相关的上下文")
            return
        
        # 生成可视化
        print("\n生成可视化结果...")
        self.plot_context_distribution(target_word, before_words, after_words)
        
        # 保存结果
        print("\n保存分析结果...")
        self.save_results(target_word, before_words, after_words, phrases)
        
        # 打印一些统计信息
        print(f"\n分析完成！结果已保存至: {self.output_dir}")
        print(f"\n'{target_word}' 最常见的搭配词:")
        print("\n前置词 (top 10):")
        for word, freq in before_words.most_common(10):
            print(f"  {word}: {freq}")
        
        print("\n后置词 (top 10):")
        for word, freq in after_words.most_common(10):
            print(f"  {word}: {freq}")

def main():
    # 创建分析器实例
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
    analyzer = PhraseContextAnalyzer(data_dir=data_dir, window_size=3)
    
    # 分析多个目标词
    target_words = ['marketing', 'digital', 'technology']
    
    for target_word in target_words:
        analyzer.analyze_target_word(target_word, min_freq=3)
        print("\n" + "="*50 + "\n")

if __name__ == "__main__":
    main() 