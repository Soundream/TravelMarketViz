import os
import jieba
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter
from wordcloud import WordCloud
import seaborn as sns
from pathlib import Path

class TextAnalyzer:
    def __init__(self, input_dir):
        self.input_dir = input_dir
        
        # 基础中文停用词
        self.stopwords = set({
            
        })
        # 英文基础停用词
        self.stopwords.update({
            'travel', 'podcasts', 'people', 'thank', 'us', 'go', 'talk', 'today',
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
            "wasn't", 'weren', "weren't", 'won', "won't", 'wouldn', "wouldn't"
        })
        # 行业特定停用词
        self.stopwords.update({
            'said', 'says', 'will', 'new', 'also', 'one', 'two', 'may', 'now', 'use',
            'using', 'used', 'can', 'could', 'would', 'should', 'get', 'many', 'much',
            'year', 'month', 'day', 'time', 'way', 'week', 'need', 'make', 'see', 'look',
            'even', 'first', 'last', 'still', 'going', 'however', 'including', 'according',
            'inc', 'ltd', 'co', 'com', 'org', 'net', 'www'
        })

        # 语气词和填充词
        self.stopwords.update({
            'um', 'uh', 'ah', 'oh', 'yeah', 'yes', 'no', 'right', 'okay', 'ok',
            'like', 'sort', 'kind', 'lot', 'lots', 'thing', 'things', 'way', 'ways',
            'actually', 'basically', 'literally', 'really', 'stuff', 'mean', 'means',
            'know', 'think', 'thought', 'thinking', 'going', 'goes', 'went', 'gone',
            'come', 'comes', 'coming', 'came', 'get', 'gets', 'getting', 'got',
            'want', 'wants', 'wanting', 'wanted', 'look', 'looks', 'looking', 'looked',
            'well', 'good', 'great', 'nice', 'better', 'best', 'sure', 'guess',
            'maybe', 'perhaps', 'probably', 'obviously', 'course', 'etc'
        })

        # 特定人名和相关词
        self.stopwords.update({
            'timothy', 'tim', 'neil', 'dunne', 'ross', 'veitch', 'hoon', 'siew',
            'mr', 'mrs', 'ms', 'dr', 'prof', 'sir', 'madam', 'miss',
            'name', 'names', 'called', 'call', 'calls', 'calling'
        })
        
        # 初始化词频计数器
        self.word_freq = None
        self.bigram_freq = None
        self.trigram_freq = None
        
    def read_files(self):
        """读取所有文本文件并合并内容"""
        all_text = []
        found_files = list(Path(self.input_dir).rglob('*.txt'))  # 只搜索txt文件
        
        if not found_files:
            raise FileNotFoundError(f"No .txt files found in directory: {self.input_dir}")
            
        for file in found_files:
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    text = f.read()
                    all_text.append(text)
                    print(f"Successfully read {file}")
            except Exception as e:
                print(f"Error reading {file}: {e}")
                try:
                    # 尝试使用其他编码
                    with open(file, 'r', encoding='gbk') as f:
                        text = f.read()
                        all_text.append(text)
                        print(f"Successfully read {file} with GBK encoding")
                except Exception as e:
                    print(f"Failed to read {file} with both UTF-8 and GBK encodings")
                
        if not all_text:
            raise ValueError(f"No valid text content found in {self.input_dir}")
            
        return ' '.join(all_text)

    def get_filtered_words(self, text):
        """获取过滤后的词列表"""
        words = jieba.cut(text)
        return [
            word.strip().lower() for word in words 
            if word.strip() and word.strip().lower() not in self.stopwords
            and len(word.strip()) > 1  # 过滤掉长度小于等于1的词
        ]

    def get_ngrams(self, words, n):
        """生成n-gram序列"""
        return [tuple(words[i:i+n]) for i in range(len(words)-n+1)]

    def analyze_text(self):
        """分析文本内容，包括单词、二元组和三元组"""
        try:
            text = self.read_files()
        except (FileNotFoundError, ValueError) as e:
            print(f"Error: {e}")
            return Counter(), Counter(), Counter()
            
        # 获取过滤后的词列表
        filtered_words = self.get_filtered_words(text)
        
        if not filtered_words:
            print("Warning: No valid words found after filtering")
            return Counter(), Counter(), Counter()
            
        # 统计单词频率
        self.word_freq = Counter(filtered_words)
        
        # 统计二元组频率
        self.bigram_freq = Counter(self.get_ngrams(filtered_words, 2))
        
        # 统计三元组频率
        self.trigram_freq = Counter(self.get_ngrams(filtered_words, 3))
        
        return self.word_freq, self.bigram_freq, self.trigram_freq

    def plot_top_words(self, top_n=20, ngram_type='unigram'):
        """绘制前N个高频词/词组柱状图"""
        if not self.word_freq:
            self.word_freq, self.bigram_freq, self.trigram_freq = self.analyze_text()
            
        # 选择要展示的n-gram类型
        if ngram_type == 'unigram':
            freq_data = self.word_freq
            title = 'Top Single Words Frequency'
        elif ngram_type == 'bigram':
            freq_data = self.bigram_freq
            title = 'Top Word Pairs (Bigrams) Frequency'
        else:  # trigram
            freq_data = self.trigram_freq
            title = 'Top Word Triplets (Trigrams) Frequency'
            
        if not freq_data:
            print(f"No data to plot for {ngram_type}")
            return
            
        # 获取前N个高频词/词组
        if ngram_type == 'unigram':
            top_items = pd.DataFrame(
                freq_data.most_common(top_n),
                columns=['Word', 'Frequency']
            )
        else:
            # 对于bigram和trigram，将元组转换为字符串
            top_items = pd.DataFrame(
                [(' '.join(k), v) for k, v in freq_data.most_common(top_n)],
                columns=['Word', 'Frequency']
            )
        
        # 设置图表风格
        plt.style.use('seaborn-v0_8')
        plt.figure(figsize=(15, 8))
        
        # 创建柱状图
        sns.barplot(data=top_items, x='Word', y='Frequency')
        plt.xticks(rotation=45, ha='right')
        plt.title(title)
        plt.tight_layout()
        
        # 保存图表
        output_file = f'word_frequency_{ngram_type}.png'
        plt.savefig(output_file)
        plt.close()
        print(f"Saved {ngram_type} plot to {output_file}")

    def generate_wordcloud(self):
        """生成词云图"""
        if not self.word_freq:
            self.word_freq, self.bigram_freq, self.trigram_freq = self.analyze_text()
            
        if not self.word_freq:
            print("No data to generate word cloud")
            return
            
        # 定义可能的字体路径
        possible_fonts = [
            '/System/Library/Fonts/PingFang.ttc',  # macOS
            '/System/Library/Fonts/Arial Unicode.ttf',  # macOS
            '/Library/Fonts/Arial Unicode.ttf',  # macOS
            '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',  # Linux
            'C:\\Windows\\Fonts\\arial.ttf',  # Windows
            'arial'  # 默认回退选项
        ]
        
        # 查找可用的字体
        font_path = None
        for font in possible_fonts:
            try:
                if font == 'arial':
                    font_path = font
                    break
                if os.path.exists(font):
                    font_path = font
                    break
            except:
                continue
        
        try:
            # 创建词云对象
            wordcloud = WordCloud(
                width=1200,
                height=800,
                background_color='white',
                font_path=font_path,  # 使用找到的字体
                max_words=100,
                collocations=False
            )
            
            # 生成词云
            wordcloud.generate_from_frequencies(self.word_freq)
            
            # 显示词云图
            plt.figure(figsize=(15, 10))
            plt.imshow(wordcloud, interpolation='bilinear')
            plt.axis('off')
            plt.title('Word Cloud')
            plt.tight_layout(pad=0)
            
            # 保存词云图
            plt.savefig('wordcloud.png')
            plt.close()
            
            print("Successfully generated word cloud")
            
        except Exception as e:
            print(f"Error generating word cloud: {e}")
            print("Continuing with other visualizations...")

    def save_word_frequency(self, ngram_type='all'):
        """保存词频统计结果到CSV文件"""
        if not self.word_freq:
            self.word_freq, self.bigram_freq, self.trigram_freq = self.analyze_text()
            
        if ngram_type in ['unigram', 'all']:
            df_unigram = pd.DataFrame(
                self.word_freq.most_common(),
                columns=['Word', 'Frequency']
            )
            df_unigram.to_csv('word_frequency_unigram.csv', index=False, encoding='utf-8-sig')
            
        if ngram_type in ['bigram', 'all']:
            df_bigram = pd.DataFrame(
                [(' '.join(k), v) for k, v in self.bigram_freq.most_common()],
                columns=['Word Pair', 'Frequency']
            )
            df_bigram.to_csv('word_frequency_bigram.csv', index=False, encoding='utf-8-sig')
            
        if ngram_type in ['trigram', 'all']:
            df_trigram = pd.DataFrame(
                [(' '.join(k), v) for k, v in self.trigram_freq.most_common()],
                columns=['Word Triplet', 'Frequency']
            )
            df_trigram.to_csv('word_frequency_trigram.csv', index=False, encoding='utf-8-sig')

def main():
    try:
        # 使用正确的文件夹路径
        input_dir = input("请输入文本文件所在的文件夹路径（按回车使用默认路径）: ").strip()
        if not input_dir:
            input_dir = "05.project-word-swarm/WiT Studio Episodes"  # 默认路径
            
        analyzer = TextAnalyzer(input_dir)
        
        # 分析文本
        print("\nAnalyzing text...")
        word_freq, bigram_freq, trigram_freq = analyzer.analyze_text()
        
        if not word_freq and not bigram_freq and not trigram_freq:
            print("No valid text data found. Please check the input directory and file contents.")
            return
            
        # 输出单词频率
        print("\nTop 20 most frequent single words:")
        for word, freq in word_freq.most_common(20):
            print(f"{word}: {freq}")
            
        # 输出二元组频率
        print("\nTop 20 most frequent word pairs:")
        for pair, freq in bigram_freq.most_common(20):
            print(f"{' '.join(pair)}: {freq}")
            
        # 输出三元组频率
        print("\nTop 20 most frequent word triplets:")
        for triplet, freq in trigram_freq.most_common(20):
            print(f"{' '.join(triplet)}: {freq}")
        
        # 生成可视化
        print("\nGenerating visualizations...")
        analyzer.plot_top_words(ngram_type='unigram')
        analyzer.plot_top_words(ngram_type='bigram')
        analyzer.plot_top_words(ngram_type='trigram')
        analyzer.generate_wordcloud()
        
        # 保存词频统计结果
        print("\nSaving word frequency to CSV...")
        analyzer.save_word_frequency(ngram_type='all')
        
        print("\nAnalysis complete! Check the following files:")
        print("- word_frequency_unigram.png (Single words bar chart)")
        print("- word_frequency_bigram.png (Word pairs bar chart)")
        print("- word_frequency_trigram.png (Word triplets bar chart)")
        print("- word_frequency_unigram.csv (Single words frequency data)")
        print("- word_frequency_bigram.csv (Word pairs frequency data)")
        print("- word_frequency_trigram.csv (Word triplets frequency data)")
        print("- wordcloud.png (Word cloud)")
        
    except Exception as e:
        print(f"An error occurred: {e}")
        raise

if __name__ == "__main__":
    main() 