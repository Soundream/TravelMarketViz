import sys
import os
import json
import glob
import argparse
from datetime import datetime
import re
from pathlib import Path
from tqdm import tqdm
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.colors import LinearSegmentedColormap
from sklearn.feature_extraction.text import CountVectorizer
from gensim import corpora, models
from gensim.models import LdaModel
from gensim.utils import simple_preprocess
from collections import defaultdict
import matplotlib.dates as mdates
from scipy.interpolate import make_interp_spline

# 英文停用词列表 (从原文件复制)
ENGLISH_STOP_WORDS = {
    # 人称代词
    'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", 'your', 'yours', 
    'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', 'her', 'hers', 'herself', 
    'it', 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves',
    
    # 疑问词和指示词
    'what', 'which', 'who', 'whom', 'this', 'that', "that'll", 'these', 'those', 'where', 'when', 'why', 'how',
    
    # 常见动词
    'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having',
    'do', 'does', 'did', 'doing', 'can', 'could', 'should', 'would', 'shall', 'will', 'might',
    'must', 'may', 'says', 'said', 'say', 'like', 'liked', 'want', 'wants', 'wanted',
    'get', 'gets', 'got', 'make', 'makes', 'made', 'see', 'sees', 'saw', 'look', 'looks',
    'looking', 'take', 'takes', 'took', 'come', 'comes', 'came',
    
    # 介词和连词
    'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 
    'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through', 'during', 
    'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 
    'off', 'over', 'under', 'again', 'further', 'than',
    
    # 时间和数量词
    'now', 'then', 'once', 'here', 'there', 'all', 'any', 'both', 'each', 'few', 'more',
    'most', 'other', 'some', 'such', 'first', 'last', 'many', 'much', 'one', 'two', 'three',
    'next', 'previous', 'today', 'tomorrow', 'yesterday', 'day', 'week', 'month', 'year',
    
    # 其他常见词
    'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'too', 'very', 'just', 'well',
    'also', 'back', 'even', 'still', 'way', 'ways', 'thing', 'things', 'new', 'old',
    'good', 'better', 'best', 'bad', 'worse', 'worst', 'high', 'low', 'possible',
    'different', 'early', 'late', 'later', 'latest', 'hard', 'easy', 'earlier',
    
    # 缩写和常见组合
    "don't", 'cant', "can't", 'wont', "won't", "isn't", "aren't", "wasn't", "weren't",
    "hasn't", "haven't", "hadn't", "doesn't", "don't", "didn't", "shouldn't", "wouldn't",
    "couldn't", "mustn't", "mightn't", "shan't", 'let', "let's", 'lets',
}

# 过滤掉的特定高频词 (从原文件复制)
FILTERED_WORDS = {
    'travel', 'hotel', 'hotels', 'company', 'companies', 'business', 'million', 'billion',
    'market', 'markets', 'year', 'years', 'month', 'months', 'week', 'weeks', 'day', 'days',
    'time', 'times', 'report', 'reported', 'according', 'says', 'said', 'say', 'told',
    'announced', 'launched', 'based', 'include', 'includes', 'including', 'included',
    'percent', 'percentage', 'number', 'numbers', 'group', 'groups', 'service', 'services',
    'use', 'used', 'using', 'provide', 'provides', 'provided', 'providing', 'make', 'makes',
    'made', 'making', 'set', 'sets', 'setting', 'need', 'needs', 'needed', 'needing',
    'work', 'works', 'working', 'worked', 'call', 'calls', 'called', 'calling',
    'find', 'finds', 'finding', 'found', 'show', 'shows', 'showed', 'shown', 'showing',
    'think', 'thinks', 'thinking', 'thought', 'way', 'ways', 'thing', 'things',
    'people', 'person', 'world', 'global', 'international', 'domestic', 'local',
    'industry', 'industries', 'sector', 'sectors', 'customer', 'customers',
    'data', 'information', 'technology', 'technologies', 'platform', 'platforms',
    'solution', 'solutions', 'system', 'systems', 'product', 'products',
    'place', 'places', 'area', 'areas', 'region', 'regions', 'country', 'countries',
    'city', 'cities', 'state', 'states', 'part', 'parts', 'end', 'ends', 'start', 'starts',
    'level', 'levels', 'rate', 'rates', 'value', 'values', 'price', 'prices',
    'cost', 'costs', 'revenue', 'revenues', 'sale', 'sales', 'growth', 'increase',
    'decrease', 'change', 'changes', 'changed', 'changing', 'development', 'developments',
    'plan', 'plans', 'planned', 'planning', 'strategy', 'strategies', 'strategic',
    'operation', 'operations', 'operating', 'operated', 'management', 'managing',
    'managed', 'manager', 'managers', 'executive', 'executives', 'director', 'directors',
    'leader', 'leaders', 'leadership', 'team', 'teams', 'staff', 'employee', 'employees',
    'partner', 'partners', 'partnership', 'partnerships', 'client', 'clients',
    'user', 'users', 'consumer', 'consumers', 'visitor', 'visitors', 'guest', 'guests',
    'passenger', 'passengers', 'traveler', 'travelers', 'tourist', 'tourists',
    'booking', 'bookings', 'booked', 'reservation', 'reservations', 'reserved',
    'flight', 'flights', 'airline', 'airlines', 'airport', 'airports',
    'destination', 'destinations', 'location', 'locations', 'site', 'sites',
    'property', 'properties', 'room', 'rooms', 'accommodation', 'accommodations',
    'tour', 'tours', 'trip', 'trips', 'experience', 'experiences', 'experienced',
    'offer', 'offers', 'offered', 'offering', 'deal', 'deals', 'option', 'options',
    'feature', 'features', 'featured', 'featuring', 'support', 'supports', 'supported',
    'supporting', 'help', 'helps', 'helped', 'helping', 'create', 'creates', 'created',
    'creating', 'build', 'builds', 'building', 'built', 'develop', 'develops',
    'developed', 'developing', 'launch', 'launches', 'launched', 'launching',
    'implement', 'implements', 'implemented', 'implementing', 'introduce', 'introduces',
    'introduced', 'introducing', 'bring', 'brings', 'bringing', 'brought',
    # 添加新的过滤词
    'phocuswire', 'phocuswright', 'subscribe', 'subscribed', 'subscription',
    'click', 'clicks', 'read', 'reads', 'reading', 'view', 'views', 'viewing',
    'follow', 'follows', 'following', 'followed', 'join', 'joins', 'joining', 'joined',
    'sign', 'signs', 'signing', 'signed', 'register', 'registers', 'registering', 'registered',
    'newsletter', 'newsletters', 'email', 'emails', 'contact', 'contacts', 'contacting',
    'news', 'article', 'articles', 'story', 'stories', 'post', 'posts', 'posting',
    'content', 'contents', 'page', 'pages', 'site', 'sites', 'website', 'websites'
}

# 添加双词短语的过滤集合 (从原文件复制)
IMPORTANT_BIGRAMS = {
    'artificial intelligence', 'machine learning', 'deep learning',
    'travel industry', 'business travel', 'online travel',
    'travel management', 'digital transformation', 'customer experience',
    'mobile app', 'real time', 'artificial intelligence',
    'revenue management', 'data analytics', 'business model',
    'travel technology', 'booking platform', 'travel platform',
    'travel agency', 'travel agencies', 'corporate travel',
    'travel demand', 'travel market', 'travel sector',
    'travel tech', 'travel trends', 'travel distribution',
    'travel startup', 'travel startups', 'travel ecosystem',
    'travel payments', 'travel recovery', 'travel restrictions',
    'virtual reality', 'augmented reality', 'blockchain technology',
    'big data', 'cloud computing', 'internet things',
    'user experience', 'supply chain', 'market share',
}

# 添加要过滤的双词短语 (从原文件复制)
FILTERED_BIGRAMS = {
    'last year', 'next year', 'last month', 'next month',
    'last week', 'next week', 'per cent', 'press release',
    'chief executive', 'vice president', 'executive officer',
    'read more', 'find out', 'learn more', 'click here',
    'full story', 'full article', 'more information',
}

class ThemeRiverViz:
    def __init__(self, data_dir="output", output_dir="theme_river_results"):
        self.data_dir = data_dir
        self.output_dir = output_dir
        self.articles = []
        self.topic_model = None
        self.dictionary = None
        self.corpus = None
        self.dates = []
        self.article_texts_by_date = {}
        self.topic_distributions = {}
        self.topic_keywords = {}
        self.num_topics = 8  # 默认主题数量
        
        # 创建输出目录
        Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    def load_data(self):
        """从JSON文件加载文章数据"""
        # 支持多种文件模式，包括直接的JSON文件和嵌套目录
        patterns = [
            os.path.join(self.data_dir, "phocuswire_page_*.json"),
            os.path.join(self.data_dir, "*.json"),
            os.path.join(self.data_dir, "**", "*.json")
        ]
        
        json_files = []
        for pattern in patterns:
            json_files.extend(glob.glob(pattern, recursive=True))
        
        # 去重
        json_files = list(set(json_files))
        
        print(f"找到 {len(json_files)} 个JSON文件")
        
        if not json_files:
            print(f"警告: 在目录 '{self.data_dir}' 中未找到JSON文件")
            print("请检查数据目录路径是否正确。可用的目录内容:")
            
            try:
                # 列出可用的目录内容
                if os.path.exists(self.data_dir):
                    print(f"目录 '{self.data_dir}' 的内容:")
                    for item in os.listdir(self.data_dir):
                        print(f"  - {item}")
                else:
                    print(f"目录 '{self.data_dir}' 不存在")
                    
                # 检查父目录
                parent_dir = os.path.dirname(self.data_dir)
                if os.path.exists(parent_dir):
                    print(f"父目录 '{parent_dir}' 的内容:")
                    for item in os.listdir(parent_dir):
                        print(f"  - {item}")
            except Exception as e:
                print(f"列出目录内容时出错: {e}")
            
            return []
            
        all_articles = []
        
        for json_file in tqdm(json_files, desc="加载文章数据"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # 处理不同的JSON格式
                    if isinstance(data, list):
                        articles = data
                    elif isinstance(data, dict) and 'articles' in data:
                        articles = data['articles']
                    else:
                        articles = [data]  # 单篇文章
                        
                    all_articles.extend(articles)
            except Exception as e:
                print(f"读取文件 {json_file} 时出错: {e}")
        
        print(f"总共加载了 {len(all_articles)} 篇文章")
        self.articles = all_articles
        return all_articles
        
    def parse_date(self, date_str):
        """解析日期字符串为日期对象"""
        try:
            date_formats = [
                "%B %d, %Y",
                "%d %B %Y",
                "%B %Y",
                "%Y-%m-%d",
            ]
            
            for date_format in date_formats:
                try:
                    return datetime.strptime(date_str.strip(), date_format)
                except ValueError:
                    continue
                    
            return None
        except:
            return None
    
    def preprocess_text(self, text):
        """预处理文本，返回单词列表"""
        if not text:
            return []
            
        # 移除非字母字符，但保留空格
        text = re.sub(r'[^a-zA-Z\s]', ' ', text.lower())
        
        # 分词
        words = [word.strip() for word in text.split() if word.strip()]
        
        # 提取单词和双词短语
        processed_terms = []
        
        # 处理双词短语
        for i in range(len(words) - 1):
            bigram = f"{words[i]} {words[i+1]}"
            # 如果是重要的双词短语，添加到结果中
            if bigram in IMPORTANT_BIGRAMS and bigram not in FILTERED_BIGRAMS:
                processed_terms.append(bigram)
        
        # 处理单个词
        for i, word in enumerate(words):
            # 检查这个词是否是任何重要双词短语的一部分
            is_part_of_bigram = False
            if i < len(words) - 1:
                current_bigram = f"{word} {words[i+1]}"
                if current_bigram in IMPORTANT_BIGRAMS:
                    is_part_of_bigram = True
            if i > 0:
                previous_bigram = f"{words[i-1]} {word}"
                if previous_bigram in IMPORTANT_BIGRAMS:
                    is_part_of_bigram = True
            
            # 如果不是双词短语的一部分，且符合其他条件，则添加这个单词
            if not is_part_of_bigram and word not in ENGLISH_STOP_WORDS and word not in FILTERED_WORDS and len(word) > 2:
                processed_terms.append(word)
        
        return processed_terms
    
    def process_articles(self):
        """处理文章数据，按日期分组并提取文本"""
        articles_by_date = {}
        texts_by_date = {}
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
                processed_words = self.preprocess_text(content)
                
                # 至少需要10个词才有意义
                if len(processed_words) < 10:
                    continue
                
                # 按日期分组文章
                if year_month not in articles_by_date:
                    articles_by_date[year_month] = []
                    texts_by_date[year_month] = []
                
                articles_by_date[year_month].append(article)
                texts_by_date[year_month].append(processed_words)
                    
            except Exception as e:
                print(f"处理文章时出错: {e}")
        
        self.dates = sorted(list(dates))
        self.article_texts_by_date = texts_by_date
        
        print(f"按日期分组后，共有 {len(self.dates)} 个时间点")
        return articles_by_date
    
    def build_lda_model(self, num_topics=8):
        """构建LDA主题模型"""
        self.num_topics = num_topics
        
        print("构建LDA主题模型...")
        
        # 检查是否有足够的数据
        if not self.dates or not self.article_texts_by_date:
            print("错误：没有足够的文章数据来构建LDA模型")
            print("请确保数据目录包含有效的文章数据")
            return None
            
        # 合并所有文档，创建字典和语料库
        all_texts = []
        for date in self.dates:
            all_texts.extend(self.article_texts_by_date[date])
            
        if not all_texts:
            print("错误：处理后的文本为空，无法构建LDA模型")
            return None
            
        print(f"使用 {len(all_texts)} 篇文档构建LDA模型")
        
        # 创建字典
        self.dictionary = corpora.Dictionary(all_texts)
        
        # 过滤极端频率的词 - 调整参数以获得更好的主题区分
        self.dictionary.filter_extremes(no_below=2, no_above=0.85)
        
        if len(self.dictionary) == 0:
            print("错误：过滤后的词典为空，请调整过滤参数")
            return None
            
        print(f"词典中包含 {len(self.dictionary)} 个独特词条")
        
        # 创建语料库
        self.corpus = [self.dictionary.doc2bow(text) for text in all_texts]
        
        # 检查语料库是否为空
        if not any(self.corpus):
            print("错误：语料库为空，无法构建LDA模型")
            return None
        
        # 尝试不同数量的主题，寻找最优主题数量
        if len(all_texts) > 100 and num_topics > 5:
            print("尝试确定最佳主题数量...")
            coherence_scores = []
            tested_models = []
            
            # 测试范围内的主题数量
            min_topics = max(2, num_topics - 3)
            max_topics = min(num_topics + 3, 15)
            
            for n_topics in range(min_topics, max_topics + 1):
                print(f"测试 {n_topics} 个主题...")
                temp_model = LdaModel(
                    corpus=self.corpus,
                    id2word=self.dictionary,
                    num_topics=n_topics,
                    passes=10,
                    alpha='auto',
                    eta='auto',
                    random_state=42  # 设置随机种子以获得可重复的结果
                )
                
                # 计算主题相干性
                cm = models.CoherenceModel(
                    model=temp_model, 
                    texts=all_texts, 
                    dictionary=self.dictionary, 
                    coherence='c_v'
                )
                coherence = cm.get_coherence()
                coherence_scores.append(coherence)
                tested_models.append(temp_model)
                print(f"主题数量 {n_topics} 的相干性得分: {coherence:.4f}")
            
            # 选择相干性最高的模型
            best_index = coherence_scores.index(max(coherence_scores))
            best_num_topics = min_topics + best_index
            self.topic_model = tested_models[best_index]
            self.num_topics = best_num_topics
            print(f"选择最佳主题数量: {best_num_topics}，相干性得分: {coherence_scores[best_index]:.4f}")
        else:
            # 直接使用指定的主题数量
            self.topic_model = LdaModel(
                corpus=self.corpus,
                id2word=self.dictionary,
                num_topics=num_topics,
                passes=15,  # 增加传递次数以获得更好的收敛
                alpha='auto',
                eta='auto',
                random_state=42  # 设置随机种子以获得可重复的结果
            )
            
        # 检测并合并相似主题
        self.detect_similar_topics()
            
        # 获取每个主题的关键词
        self.topic_keywords = {}
        for i in range(self.num_topics):
            # 提取前10个关键词
            topic_words = [word for word, _ in self.topic_model.show_topic(i, topn=10)]
            self.topic_keywords[i] = topic_words
        
        # 按日期计算主题分布
        self.topic_distributions = {}
        
        for date in tqdm(self.dates, desc="计算各时间点主题分布"):
            date_texts = self.article_texts_by_date[date]
            date_corpus = [self.dictionary.doc2bow(text) for text in date_texts]
            
            # 初始化主题分布
            topic_dist = np.zeros(self.num_topics)
            
            # 计算所有文档的平均主题分布
            doc_count = 0
            for doc_bow in date_corpus:
                if not doc_bow:  # 跳过空文档
                    continue
                    
                doc_topics = self.topic_model[doc_bow]
                for topic_id, prob in doc_topics:
                    topic_dist[topic_id] += prob
                doc_count += 1
            
            # 计算平均值
            if doc_count > 0:
                topic_dist /= doc_count
                
            self.topic_distributions[date] = topic_dist
        
        return self.topic_model
        
    def detect_similar_topics(self, similarity_threshold=0.7):
        """检测并处理相似主题"""
        if not self.topic_model:
            return
            
        # 获取所有主题的词分布
        topic_terms = []
        for i in range(self.num_topics):
            terms = dict(self.topic_model.get_topic_terms(i, topn=30))
            topic_terms.append(terms)
        
        # 计算主题之间的相似度
        similar_topics = []
        for i in range(self.num_topics):
            for j in range(i+1, self.num_topics):
                # 计算Jaccard相似度
                terms_i = set(topic_terms[i].keys())
                terms_j = set(topic_terms[j].keys())
                
                intersection = len(terms_i.intersection(terms_j))
                union = len(terms_i.union(terms_j))
                
                if union > 0:
                    similarity = intersection / union
                    
                    # 检查关键词重叠
                    top_terms_i = [word for word, _ in self.topic_model.show_topic(i, topn=5)]
                    top_terms_j = [word for word, _ in self.topic_model.show_topic(j, topn=5)]
                    
                    common_top_terms = set(top_terms_i).intersection(set(top_terms_j))
                    
                    if similarity > similarity_threshold or len(common_top_terms) >= 2:
                        similar_topics.append((i, j, similarity, common_top_terms))
        
        # 输出相似主题信息
        if similar_topics:
            print("\n发现相似主题:")
            for i, j, sim, common_terms in similar_topics:
                print(f"主题 {i+1} 和主题 {j+1} 相似度: {sim:.2f}")
                print(f"  主题 {i+1}: {', '.join([word for word, _ in self.topic_model.show_topic(i, topn=5)])}")
                print(f"  主题 {j+1}: {', '.join([word for word, _ in self.topic_model.show_topic(j, topn=5)])}")
                print(f"  共同关键词: {', '.join(common_terms)}")
                print()
                
            print("建议: 考虑减少主题数量或调整模型参数以获得更清晰的主题区分")
    
    def create_theme_river_visualization(self, smooth=True, colors=None):
        """创建主题河流可视化"""
        if not self.topic_model or not self.topic_distributions:
            print("请先运行 build_lda_model() 方法")
            return
            
        print("创建主题河流可视化...")
        
        # 准备数据
        dates = [datetime.strptime(date, "%Y-%m") for date in self.dates]
        date_nums = mdates.date2num(dates)
        
        # 获取主题分布数据
        topic_data = np.array([self.topic_distributions[date] for date in self.dates])
        
        # 创建颜色映射
        if colors is None:
            # 使用预定义的颜色方案
            base_colors = [
                '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
                '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'
            ]
            # 如果主题数超过预定义颜色，则循环使用
            colors = [base_colors[i % len(base_colors)] for i in range(self.num_topics)]
        
        # 创建渐变色映射
        color_maps = []
        for color in colors:
            # 为每个主题创建从浅到深的渐变
            cmap = LinearSegmentedColormap.from_list(
                f"custom_{color}", 
                [(1, 1, 1), mcolors.hex2color(color)],
                N=256
            )
            color_maps.append(cmap)
        
        # 创建平滑插值（如果启用）
        if smooth:
            # 创建更密集的日期点进行插值
            smooth_date_nums = np.linspace(date_nums.min(), date_nums.max(), 200)
            
            # 对每个主题进行样条插值
            smooth_topic_data = np.zeros((len(smooth_date_nums), self.num_topics))
            
            for i in range(self.num_topics):
                # 使用三次样条插值
                spline = make_interp_spline(date_nums, topic_data[:, i], k=3)
                smooth_values = spline(smooth_date_nums)
                # 确保没有负值
                smooth_values = np.maximum(0, smooth_values)
                smooth_topic_data[:, i] = smooth_values
                
            # 使用平滑后的数据
            plot_date_nums = smooth_date_nums
            plot_topic_data = smooth_topic_data
            
            # 转换回日期对象用于绘图
            smooth_dates = mdates.num2date(smooth_date_nums)
        else:
            # 使用原始数据
            plot_date_nums = date_nums
            plot_topic_data = topic_data
            smooth_dates = dates
        
        # 创建图形
        plt.figure(figsize=(16, 8))
        ax = plt.gca()
        
        # 绘制堆叠区域图
        layers = []
        labels = []
        
        for i in range(self.num_topics):
            # 获取主题关键词作为标签
            topic_label = f"主题 {i+1}: " + ", ".join(self.topic_keywords[i][:5])
            labels.append(topic_label)
            
            # 使用自定义颜色映射
            layer = ax.fill_between(
                plot_date_nums if smooth else date_nums,
                plot_topic_data[:, i] if i == 0 else plot_topic_data[:, :i].sum(axis=1),
                plot_topic_data[:, :i+1].sum(axis=1),
                color=colors[i],
                alpha=0.7,
                label=topic_label
            )
            layers.append(layer)
        
        # 设置图表属性
        ax.set_title("旅游市场主题演变 (2010-2013)", fontsize=16, pad=20)
        ax.set_xlabel("日期", fontsize=14)
        ax.set_ylabel("主题强度", fontsize=14)
        
        # 设置x轴日期格式
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
        plt.xticks(rotation=45)
        
        # 添加图例
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15),
                  fancybox=True, shadow=True, ncol=2)
        
        # 添加网格线
        ax.grid(True, alpha=0.3)
        
        # 调整布局
        plt.tight_layout()
        
        # 保存图像
        output_path = os.path.join(self.output_dir, "theme_river.png")
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        
        # 保存PDF版本
        pdf_path = os.path.join(self.output_dir, "theme_river.pdf")
        plt.savefig(pdf_path, format='pdf', bbox_inches='tight')
        
        print(f"主题河流可视化已保存至: {output_path}")
        plt.close()
        
        return output_path
        
    def create_interactive_theme_river(self):
        """创建交互式主题河流可视化（使用Plotly）"""
        try:
            import plotly.graph_objects as go
            import plotly.offline as pyo
            from plotly.subplots import make_subplots
        except ImportError:
            print("请安装plotly库以创建交互式可视化: pip install plotly")
            return None
        
        if not self.topic_distributions or not self.topic_keywords:
            print("请先运行 build_lda_model() 方法")
            return
        
        # 准备数据
        dates = self.dates
        date_objects = [datetime.strptime(date, "%Y-%m") for date in dates]
        
        # 创建颜色映射
        colors = plt.cm.viridis(np.linspace(0, 1, self.num_topics))
        plotly_colors = [f'rgb({int(r*255)}, {int(g*255)}, {int(b*255)})' for r, g, b, _ in colors]
        
        # 创建图形对象
        fig = go.Figure()
        
        # 添加主题河流层
        for i in range(self.num_topics):
            topic_probs = [self.topic_distributions[date][i] for date in dates]
            topic_label = f"Topic {i+1}: {', '.join(self.topic_keywords[i][:3])}"
            
            fig.add_trace(go.Scatter(
                x=date_objects,
                y=topic_probs,
                mode='lines',
                line=dict(width=0.5, color=plotly_colors[i]),
                fillcolor=plotly_colors[i],
                fill='tonexty' if i > 0 else 'tozeroy',
                name=topic_label,
                hoverinfo='text+name',
                text=[f"{', '.join(self.topic_keywords[i][:5])}<br>强度: {prob:.3f}" for prob in topic_probs]
            ))
        
        # 更新布局
        fig.update_layout(
            title="旅游市场主题演变 (2010-2013)",
            xaxis_title="日期",
            yaxis_title="主题强度",
            hovermode='closest',
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.2,
                xanchor="center",
                x=0.5
            ),
            height=700,
            width=1200
        )
        
        # 保存为HTML文件
        output_path = os.path.join(self.output_dir, "interactive_theme_river.html")
        pyo.plot(fig, filename=output_path, auto_open=False)
        
        print(f"交互式主题河流图已保存至: {output_path}")
        
        return output_path

    def load_sample_data(self):
        """加载示例数据（当无法找到实际数据时使用）"""
        print("加载示例文章数据...")
        
        # 创建一些示例文章
        sample_articles = []
        
        # 设定一些更加差异化的主题和关键词
        topics = {
            "移动技术": ["mobile", "smartphone", "app", "android", "ios", "device", "tablet", "screen", "phone", "touchscreen"],
            "社交媒体": ["social", "media", "facebook", "twitter", "network", "share", "post", "like", "follow", "engagement"],
            "在线预订": ["booking", "reservation", "online", "platform", "direct", "channel", "commission", "inventory", "availability", "calendar"],
            "数据分析": ["data", "analytics", "big data", "insight", "analysis", "predict", "algorithm", "pattern", "visualization", "dashboard"],
            "旅游体验": ["experience", "guest", "service", "quality", "satisfaction", "personalization", "memory", "authentic", "local", "unique"],
            "商业模式": ["model", "business", "revenue", "strategy", "growth", "profit", "investment", "startup", "venture", "entrepreneur"]
        }
        
        # 为每个月份创建示例文章
        start_date = datetime(2010, 1, 1)
        end_date = datetime(2013, 12, 31)
        current_date = start_date
        
        while current_date <= end_date:
            month_str = current_date.strftime("%Y-%m")
            
            # 为每个月创建5-10篇文章
            for _ in range(np.random.randint(5, 11)):
                content = []
                
                # 随机选择主要主题，确保更清晰的主题区分
                main_topic = np.random.choice(list(topics.keys()))
                second_topic = np.random.choice([t for t in topics.keys() if t != main_topic])
                
                # 生成文章内容，主要主题的词出现频率更高
                for _ in range(25):  # 增加主题词的数量
                    content.extend(np.random.choice(topics[main_topic], size=np.random.randint(4, 8)))
                
                for _ in range(8):  # 减少次要主题词的比例
                    content.extend(np.random.choice(topics[second_topic], size=np.random.randint(1, 3)))
                
                # 添加一些通用词，但减少数量
                general_words = ["travel", "industry", "company", "market", "customer", "technology"]
                content.extend(np.random.choice(general_words, size=np.random.randint(3, 6)))
                
                # 打乱顺序
                np.random.shuffle(content)
                
                # 创建文章
                article = {
                    "title": f"Sample Article about {main_topic}",
                    "date": current_date.strftime("%B %d, %Y"),
                    "content": " ".join(content)
                }
                
                sample_articles.append(article)
                
            # 移至下一个月
            if current_date.month == 12:
                current_date = datetime(current_date.year + 1, 1, 1)
            else:
                current_date = datetime(current_date.year, current_date.month + 1, 1)
        
        print(f"创建了 {len(sample_articles)} 篇示例文章")
        self.articles = sample_articles
        return sample_articles

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="主题河流可视化工具")
    
    parser.add_argument("--data-dir", type=str, default="output",
                        help="包含JSON文件的数据目录路径")
    parser.add_argument("--output-dir", type=str, default="theme_river_results",
                        help="保存可视化结果的输出目录")
    parser.add_argument("--topics", type=int, default=10,
                        help="设置LDA主题数量 (默认: 10)")
    parser.add_argument("--sample", action="store_true",
                        help="使用示例数据而不是尝试加载实际数据")
    
    return parser.parse_args()

if __name__ == "__main__":
    # 解析命令行参数
    args = parse_arguments()
    
    # 创建ThemeRiverViz实例
    visualizer = ThemeRiverViz(
        data_dir=args.data_dir,
        output_dir=args.output_dir
    )
    
    # 加载和处理数据
    if args.sample:
        visualizer.load_sample_data()
    else:
        articles = visualizer.load_data()
        if not articles:
            print("未找到实际数据，切换到示例数据...")
            visualizer.load_sample_data()
    
    visualizer.process_articles()
    
    # 构建LDA模型
    model = visualizer.build_lda_model(num_topics=args.topics)
    
    if model:
        # 创建主题河流可视化
        visualizer.create_theme_river_visualization()
        
        # 创建交互式可视化（如果安装了plotly）
        try:
            visualizer.create_interactive_theme_river()
        except Exception as e:
            print(f"创建交互式可视化时出错: {e}")
    else:
        print("由于模型构建失败，无法生成可视化") 