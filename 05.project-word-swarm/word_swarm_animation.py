import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.colors import LinearSegmentedColormap
import seaborn as sns
from datetime import datetime
import json
import os
import glob
from pathlib import Path
from tqdm import tqdm
import re
import random

# 英文停用词列表
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

# 过滤掉的特定高频词
FILTERED_WORDS = {'travel', 'hotel', 'hotels', 'company', 'companies', 'business', 'million', 'based', 'online'}

# 添加随机但固定的颜色生成函数
def get_word_color(word, saturation=0.7, value=0.95):
    """为每个词生成一个固定的颜色"""
    import hashlib
    # 使用词的哈希值生成一个固定的色调
    hash_val = int(hashlib.md5(word.encode()).hexdigest(), 16)
    hue = hash_val % 360 / 360.0  # 0-1范围的色调
    import colorsys
    r, g, b = colorsys.hsv_to_rgb(hue, saturation, value)
    return (r, g, b)

class WordSwarmAnimation:
    def __init__(self, data_dir="output", output_dir="animation_results"):
        """
        初始化词云动画生成器
        
        Args:
            data_dir: 包含JSON文件的目录
            output_dir: 输出动画的目录
        """
        self.data_dir = data_dir
        self.output_dir = output_dir
        self.articles = []
        self.word_frequencies = {}
        self.dates = []
        
        # 创建输出目录
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # 缓存词颜色以保持一致性
        self.word_colors = {}
        
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
    
    def process_articles(self):
        """处理文章数据，提取关键词频率"""
        word_freq_by_date = {}
        dates = set()
        
        for article in tqdm(self.articles, desc="处理文章"):
            try:
                date_str = article.get('date')
                if not date_str:
                    continue
                    
                date_obj = self.parse_date(date_str)
                if not date_obj:
                    continue
                
                # 将日期转换为年月格式
                year_month = date_obj.strftime("%Y-%m")
                dates.add(year_month)
                
                # 预处理文章内容
                content = article.get('content', '')
                words = self.preprocess_text(content)
                
                # 更新词频
                if year_month not in word_freq_by_date:
                    word_freq_by_date[year_month] = {}
                
                for word in words:
                    word_freq_by_date[year_month][word] = word_freq_by_date[year_month].get(word, 0) + 1
                    
            except Exception as e:
                print(f"处理文章时出错: {e}")
        
        self.word_frequencies = word_freq_by_date
        self.dates = sorted(list(dates))
        
        # 打印调试信息
        print(f"\n处理完成，共有 {len(dates)} 个不同的日期")
        print(f"第一个日期的词频示例:")
        if self.dates:
            first_date = self.dates[0]
            print(f"日期: {first_date}")
            print(f"词数: {len(word_freq_by_date[first_date])}")
            print("前10个高频词:")
            sorted_words = sorted(word_freq_by_date[first_date].items(), 
                                key=lambda x: x[1], 
                                reverse=True)[:10]
            for word, freq in sorted_words:
                print(f"  {word}: {freq}")
        
    def create_animation(self, top_n=50, fps=24):
        """创建更流畅的词云动画，模拟物理引擎效果"""
        if not self.word_frequencies or not self.dates:
            print("请先运行 process_articles() 方法")
            return
            
        # 获取所有时间点的前N个关键词
        all_words = set()
        for date in self.dates:
            words = sorted(self.word_frequencies[date].items(), 
                         key=lambda x: x[1], 
                         reverse=True)[:top_n]
            all_words.update([w[0] for w in words])
        
        print(f"\n动画生成信息:")
        print(f"总词数: {len(all_words)}")
        print(f"时间点数量: {len(self.dates)}")
        
        # 为每个词分配初始颜色
        for word in all_words:
            if word not in self.word_colors:
                self.word_colors[word] = get_word_color(word)
        
        # 创建更多帧以实现平滑过渡
        frame_multiplier = 4  # 每个时间点之间创建更多帧
        total_frames = (len(self.dates) - 1) * frame_multiplier + 1
        frames_dir = os.path.join(self.output_dir, "frames")
        os.makedirs(frames_dir, exist_ok=True)
        
        # 计算所有时间点的最大词频，用于归一化
        global_max_freq = 0
        for date in self.dates:
            if self.word_frequencies[date]:
                max_freq = max(self.word_frequencies[date].values())
                global_max_freq = max(global_max_freq, max_freq)
        
        # 初始化词的位置 - 使用螺旋布局，更紧密
        word_positions = {}
        word_sizes = {}  # 记录每个词的大小，用于避免重叠
        
        def get_spiral_position(idx, total, min_radius=0.15):
            """生成螺旋布局的位置"""
            # 黄金比例角度 ~137.5度
            golden_angle = np.pi * (3 - np.sqrt(5))
            
            # 生成半径随索引增加
            radius = min_radius + 0.35 * np.sqrt(idx / total)
            
            # 角度随索引按黄金角递增
            theta = idx * golden_angle
            
            # 转换为笛卡尔坐标
            x = 0.5 + radius * np.cos(theta)
            y = 0.5 + radius * np.sin(theta)
            
            return x, y
        
        # 初始化每个词的位置
        for i, word in enumerate(sorted(all_words, key=lambda w: w.lower())):
            word_positions[word] = get_spiral_position(i, len(all_words))
        
        # 创建平滑过渡的动画帧
        print("\n开始生成平滑动画帧...")
        frame_paths = []
        
        # 定义插值函数
        def interpolate(start_val, end_val, fraction):
            return start_val + (end_val - start_val) * fraction
        
        # 生成插值帧
        for t in tqdm(range(total_frames), desc="生成帧"):
            # 确定当前插值的时间点位置
            if t % frame_multiplier == 0:
                date_idx = t // frame_multiplier
                date = self.dates[date_idx]
                next_date = date
                fraction = 0
            else:
                date_idx = t // frame_multiplier
                date = self.dates[date_idx]
                next_date_idx = min(date_idx + 1, len(self.dates) - 1)
                next_date = self.dates[next_date_idx]
                fraction = (t % frame_multiplier) / frame_multiplier
            
            # 创建图形
            plt.figure(figsize=(15, 8))
            plt.style.use('dark_background')
            ax = plt.gca()
            ax.set_facecolor('black')
            
            # 获取当前和下一个时间点的词频
            curr_word_freq = self.word_frequencies[date]
            next_word_freq = self.word_frequencies[next_date]
            
            # 计算词的大小和位置
            words_to_draw = []
            
            # 处理每个词
            for word in all_words:
                curr_freq = curr_word_freq.get(word, 0)
                next_freq = next_word_freq.get(word, 0)
                
                # 插值当前帧的词频
                freq = interpolate(curr_freq, next_freq, fraction)
                
                # 只显示频率不为0的词
                if freq > 0:
                    # 词的大小比例：更大的对比
                    rel_freq = freq / global_max_freq
                    size = 20 + 60 * np.power(rel_freq, 0.7)
                    
                    # 获取词的颜色
                    color = self.word_colors[word]
                    
                    pos = word_positions[word]
                    words_to_draw.append({
                        'word': word,
                        'size': size,
                        'freq': freq,
                        'color': color,
                        'position': pos
                    })
            
            # 按大小排序，先画小的词
            words_to_draw.sort(key=lambda x: x['size'])
            
            # 绘制词
            for word_info in words_to_draw:
                word = word_info['word']
                size = word_info['size']
                color = word_info['color']
                x, y = word_info['position']
                
                plt.text(x, y, word, 
                       fontsize=size,
                       color=color,
                       ha='center',
                       va='center',
                       alpha=0.9,
                       weight='bold')
            
            # 绘制时间线
            date_str = date if fraction < 0.5 else next_date
            title_size = 20
            plt.text(0.5, 0.95, f'关键词趋势 - {date_str}', 
                    fontsize=title_size, color='white', 
                    ha='center', va='top',
                    transform=ax.transAxes)
            
            # 添加进度条 - 修复进度条绘制
            progress = t / (total_frames - 1)
            bar_width = 0.6
            bar_height = 0.01
            
            # 使用矩形而不是axhline来绘制进度条
            bar_x = 0.5 - bar_width/2
            bar_y = 0.02
            
            # 背景条
            plt.gca().add_patch(plt.Rectangle((bar_x, bar_y), 
                                            bar_width, bar_height, 
                                            color='white', alpha=0.3,
                                            transform=ax.transAxes))
            
            # 进度条
            plt.gca().add_patch(plt.Rectangle((bar_x, bar_y), 
                                            bar_width * progress, bar_height, 
                                            color='white', alpha=1.0,
                                            transform=ax.transAxes))
            
            # 设置边界，不显示坐标轴
            plt.xlim(0, 1)
            plt.ylim(0, 1)
            plt.axis('off')
            
            # 保存当前帧
            frame_path = os.path.join(frames_dir, f"frame_{t:04d}.png")
            plt.savefig(frame_path, dpi=120, bbox_inches='tight', facecolor='black')
            frame_paths.append(frame_path)
            plt.close()
        
        # 使用ffmpeg合并帧为视频
        output_path = os.path.join(self.output_dir, 'word_swarm.mp4')
        
        # 命令行方式使用ffmpeg，添加-vf "pad=width=ceil(iw/2)*2:height=ceil(ih/2)*2"确保宽高为偶数
        cmd = f"ffmpeg -y -framerate {fps} -i {os.path.join(frames_dir, 'frame_%04d.png')} -vf \"pad=width=ceil(iw/2)*2:height=ceil(ih/2)*2\" -c:v libx264 -pix_fmt yuv420p -crf 18 {output_path}"
        
        print(f"\n使用ffmpeg合成视频: {cmd}")
        os.system(cmd)
        
        print(f"动画已保存至: {output_path}")
    
    def parse_date(self, date_str):
        """解析日期字符串为日期对象"""
        try:
            date_formats = [
                "%B %d, %Y",
                "%d %B %Y",
                "%B %Y",
                "%b %d, %Y",
                "%d %b %Y",
                "%d-%m-%Y",
                "%Y-%m-%d",
                "%m/%d/%Y",
                "%d/%m/%Y"
            ]
            
            for date_format in date_formats:
                try:
                    return datetime.strptime(date_str.strip(), date_format)
                except ValueError:
                    continue
                    
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
        words = [word.strip() for word in text.split() if word.strip()]
        
        # 移除停用词、短词和特定过滤词
        words = [word for word in words if word not in ENGLISH_STOP_WORDS 
                and word not in FILTERED_WORDS 
                and len(word) > 2]
        
        return words

if __name__ == "__main__":
    # 创建动画生成器实例
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "animation_results")
    
    animator = WordSwarmAnimation(data_dir=data_dir, output_dir=output_dir)
    
    # 加载数据
    animator.load_data()
    
    # 处理文章
    animator.process_articles()
    
    # 创建动画
    animator.create_animation(top_n=50, fps=24) 