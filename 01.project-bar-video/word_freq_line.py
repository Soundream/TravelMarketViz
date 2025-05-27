import pandas as pd
import os
import plotly.graph_objs as go
import plotly.io as pio
import numpy as np
import json
import re
from datetime import datetime
from collections import defaultdict
import glob
from tqdm import tqdm

# 完全复用word_swarm_new.py的过滤词
ENGLISH_STOP_WORDS = {
    'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", 'your', 'yours', 
    'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', 'her', 'hers', 'herself', 
    'it', 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves',
    'what', 'which', 'who', 'whom', 'this', 'that', "that'll", 'these', 'those', 'where', 'when', 'why', 'how',
    'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having',
    'do', 'does', 'did', 'doing', 'can', 'could', 'should', 'would', 'shall', 'will', 'might',
    'must', 'may', 'says', 'said', 'say', 'like', 'liked', 'want', 'wants', 'wanted',
    'get', 'gets', 'got', 'make', 'makes', 'made', 'see', 'sees', 'saw', 'look', 'looks',
    'looking', 'take', 'takes', 'took', 'come', 'comes', 'came',
    'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 
    'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through', 'during', 
    'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 
    'off', 'over', 'under', 'again', 'further', 'than',
    'now', 'then', 'once', 'here', 'there', 'all', 'any', 'both', 'each', 'few', 'more',
    'most', 'other', 'some', 'such', 'first', 'last', 'many', 'much', 'one', 'two', 'three',
    'next', 'previous', 'today', 'tomorrow', 'yesterday', 'day', 'week', 'month', 'year',
    'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'too', 'very', 'just', 'well',
    'also', 'back', 'even', 'still', 'way', 'ways', 'thing', 'things', 'new', 'old',
    'good', 'better', 'best', 'bad', 'worse', 'worst', 'high', 'low', 'possible',
    'different', 'early', 'late', 'later', 'latest', 'hard', 'easy', 'earlier',
    "don't", 'cant', "can't", 'wont', "won't", "isn't", "aren't", "wasn't", "weren't",
    "hasn't", "haven't", "hadn't", "doesn't", "don't", "didn't", "shouldn't", "wouldn't",
    "couldn't", "mustn't", "mightn't", "shan't", 'let', "let's", 'lets',
}
FILTERED_WORDS = {
    'travel', 'hotel', 'hotels', 'company', 'companies', 'business', 'million', 'billion', 'really', 'across', 'around'
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
    'phocuswire', 'phocuswright', 'subscribe', 'subscribed', 'subscription',
    'click', 'clicks', 'read', 'reads', 'reading', 'view', 'views', 'viewing',
    'follow', 'follows', 'following', 'followed', 'join', 'joins', 'joining', 'joined',
    'sign', 'signs', 'signing', 'signed', 'register', 'registers', 'registering', 'registered',
    'newsletter', 'newsletters', 'email', 'emails', 'contact', 'contacts', 'contacting',
    'news', 'article', 'articles', 'story', 'stories', 'post', 'posts', 'posting',
    'content', 'contents', 'page', 'pages', 'site', 'sites', 'website', 'websites', 'via'
}
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
FILTERED_BIGRAMS = {
    'last year', 'next year', 'last month', 'next month',
    'last week', 'next week', 'per cent', 'press release',
    'chief executive', 'vice president', 'executive officer',
    'read more', 'find out', 'learn more', 'click here',
    'full story', 'full article', 'more information',
}

def parse_date(date_str):
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

def preprocess_text(text):
    """预处理文本，支持单词和双词短语"""
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
    # 只处理那些不是双词短语一部分的单词
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

def load_and_process_data(data_dir):
    """加载并处理文章数据，返回词频数据"""
    json_files = glob.glob(os.path.join(data_dir, "phocuswire_page_*.json"))
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
    
    # 处理文章数据，提取关键词频率
    word_freq_by_date = {}
    dates = set()
    
    for article in tqdm(all_articles, desc="处理文章"):
        try:
            date_str = article.get('date')
            if not date_str:
                continue
                
            date_obj = parse_date(date_str)
            if not date_obj:
                continue
            
            # 将日期转换为年月格式
            year_month = date_obj.strftime("%Y-%m")
            dates.add(year_month)
            
            # 预处理文章内容
            content = article.get('content', '')
            words = preprocess_text(content)
            
            # 更新词频
            if year_month not in word_freq_by_date:
                word_freq_by_date[year_month] = {}
            
            for word in words:
                word_freq_by_date[year_month][word] = word_freq_by_date[year_month].get(word, 0) + 1
                
        except Exception as e:
            print(f"处理文章时出错: {e}")
    
    return word_freq_by_date, sorted(list(dates))

def create_word_freq_visualization(data_dir="../05.project-word-swarm/output"):
    """创建词频可视化"""
    word_freq_by_date, dates = load_and_process_data(data_dir)
    
    # 将日期按年份分组
    yearly_data = {}
    for date, freq_dict in word_freq_by_date.items():
        year = date.split('-')[0]
        if year not in yearly_data:
            yearly_data[year] = {}
        yearly_data[year][date] = freq_dict
    
    # 合并 covid 和 pandemic 的频率，以及 marketing 和 market 的频率
    for year in yearly_data:
        for date in yearly_data[year]:
            # 合并 covid 和 pandemic
            covid_freq = yearly_data[year][date].get('covid', 0)
            pandemic_freq = yearly_data[year][date].get('pandemic', 0)
            if covid_freq > 0 or pandemic_freq > 0:
                yearly_data[year][date]['covid'] = covid_freq + pandemic_freq
                if 'pandemic' in yearly_data[year][date]:
                    del yearly_data[year][date]['pandemic']
            
            # 合并 marketing 和 market
            marketing_freq = yearly_data[year][date].get('marketing', 0)
            market_freq = yearly_data[year][date].get('market', 0)
            if marketing_freq > 0 or market_freq > 0:
                yearly_data[year][date]['marketing'] = marketing_freq + market_freq
                if 'market' in yearly_data[year][date]:
                    del yearly_data[year][date]['market']
    
    # 获取所有年份并确保是字符串格式
    years = sorted([str(year) for year in yearly_data.keys()])
    print(f"处理年份范围: {years[0]} - {years[-1]}")
    print(f"总年份数: {len(years)}")
    print(f"所有年份: {years}")
    
    # 为每年选择top词汇
    yearly_top_words = {}
    for year in years:
        # 合并该年所有月份的词频
        year_freq = {}
        for date, freq_dict in yearly_data[year].items():
            for word, freq in freq_dict.items():
                year_freq[word] = year_freq.get(word, 0) + freq
        
        # 根据年份选择top词汇数量
        if '2014' <= year <= '2018' or '2023' <= year <= '2025':
            top_words = sorted(year_freq.items(), key=lambda x: x[1], reverse=True)[:2]  # 显示前2个词
        else:
            top_words = sorted(year_freq.items(), key=lambda x: x[1], reverse=True)[:1]  # 显示前1个词
        
        yearly_top_words[year] = [word for word, _ in top_words]
        print(f"{year}年top词汇: {yearly_top_words[year]}")
    
    # 收集所有出现过的词，并计算它们的总频率
    all_words = set()
    word_total_freq = {}
    for year in years:
        for word in yearly_top_words[year]:
            all_words.add(word)
            word_total_freq[word] = word_total_freq.get(word, 0) + 1
    
    # 根据词的总频率排序，高频词使用更醒目的颜色
    sorted_words = sorted(all_words, key=lambda x: word_total_freq[x], reverse=True)
    
    # 为每个词分配固定的颜色
    base_colors = ['#FF4B4B', '#4169E1', '#32CD32', '#FFA500', '#8A2BE2', '#20B2AA', '#FF69B4', '#40E0D0', '#DEB887']
    word_colors = {}
    for i, word in enumerate(sorted_words):
        # 高频词使用更醒目的颜色和更粗的线条
        if word_total_freq[word] >= 3:  # 如果词出现3次或以上
            word_colors[word] = {
                'color': base_colors[i % len(base_colors)],
                'width': 4,  # 更粗的线条
                'opacity': 1.0  # 完全不透明
            }
        else:
            word_colors[word] = {
                'color': base_colors[i % len(base_colors)],
                'width': 2,  # 正常线条
                'opacity': 0.8  # 稍微透明
            }
    
    # 计算所有词在所有时间点的最大频率
    max_freq = 0
    for date in dates:
        for word, freq in word_freq_by_date[date].items():
            max_freq = max(max_freq, freq)
    
    # 预计算所有可能需要的轨迹
    max_traces = len(years) * 4  # 每年最多2个词，每个词有线条和标签
    all_traces = []
    for i in range(max_traces):
        all_traces.append(go.Scatter(
            x=[],
            y=[],
            mode='lines',
            showlegend=False,
            hoverinfo='skip'
        ))
    
    # 记录每个词第一次出现的年份
    first_appearance = {}
    for year in years:
        for word in yearly_top_words[year]:
            if word not in first_appearance:
                first_appearance[word] = year
    
    # 为每个年份创建帧
    frames = []
    # 计算扫描步长
    total_steps = 100  # 总步数
    date_range = pd.date_range(start=dates[0], end=dates[-1], periods=total_steps)
    
    for step in range(total_steps):
        current_date = date_range[step]
        print(f"\n处理第{step+1}帧，当前日期: {current_date}")
        
        # 复制基础轨迹
        frame_data = [trace for trace in all_traces]
        trace_index = 0
        
        # 处理所有年份的词
        for year in years:
            # 获取该年的top词汇
            top_words = yearly_top_words[year]
            
            # 为每个词创建趋势线
            for word in top_words:
                color_info = word_colors[word]
                
                # 计算该词在前后一年的趋势
                start_year = str(int(year) - 1)
                end_year = str(int(year) + 1)
                
                # 获取相关日期范围内的数据
                word_data = []
                for date in dates:
                    date_year = date.split('-')[0]
                    if start_year <= date_year <= end_year:
                        freq = word_freq_by_date[date].get(word, 0)
                        word_data.append((date, freq))
                
                if word_data:
                    x = [d for d, _ in word_data]
                    y = [f for _, f in word_data]
                    
                    # 只显示到当前扫描位置的数据
                    visible_x = []
                    visible_y = []
                    for i, date in enumerate(x):
                        if pd.to_datetime(date) <= current_date:
                            visible_x.append(date)
                            visible_y.append(y[i])
                    
                    if visible_x:
                        # 更新线条
                        frame_data[trace_index] = go.Scatter(
                            x=visible_x,
                            y=visible_y,
                            mode='lines',
                            name=word,
                            line=dict(
                                color=color_info['color'],
                                width=color_info['width'],
                                shape='spline',
                                smoothing=1.3
                            ),
                            opacity=color_info['opacity'],
                            showlegend=False,
                            hoverinfo='x+y+name'
                        )
                        
                        # 更新标签 - 只在词第一次出现且扫描到该位置时显示
                        if year == first_appearance[word] and pd.to_datetime(visible_x[-1]) >= current_date:
                            mid_point = len(visible_x) // 2
                            frame_data[trace_index + 1] = go.Scatter(
                                x=[visible_x[mid_point]],
                                y=[visible_y[mid_point] + max_freq * 0.15],
                                mode='text',
                                text=[word],
                                textposition='top center',
                                textfont=dict(
                                    color=color_info['color'],
                                    size=16 if word_total_freq[word] >= 3 else 14
                                ),
                                showlegend=False,
                                hoverinfo='skip'
                            )
                    
                trace_index += 2
        
        frames.append(go.Frame(data=frame_data, name=str(step)))
        print(f"完成第{step+1}帧")
    
    # 初始帧使用第一帧的数据
    initial_data = frames[0].data
    
    # 动画参数
    total_frames = total_steps
    target_duration_sec = 60  # 1分钟
    frame_duration = int(target_duration_sec * 1000 / total_frames)
    
    # 图表
    fig = go.Figure(
        data=initial_data,
        layout=go.Layout(
            title='Top Word Frequencies Over Time (News from Phocuswire)',
            xaxis=dict(
                title='Date',
                linecolor='gray',
                showgrid=True,
                gridcolor='lightgray',
                griddash='dash',
                fixedrange=True,
                range=[dates[0], dates[-1]]  # 固定x轴范围
            ),
            yaxis=dict(
                title='Frequency',
                linecolor='gray',
                showgrid=True,
                gridcolor='lightgray',
                griddash='dash',
                zeroline=False,
                fixedrange=True,
                range=[0, max_freq * 1.3]  # 增加y轴范围以容纳更高的标签
            ),
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(family='Monda'),
            height=600,
            width=1500,
            margin=dict(l=50, r=150, t=80, b=50),  # 增加右边距以容纳标签
            transition=dict(duration=frame_duration, easing='linear'),
            updatemenus=[dict(
                type="buttons",
                showactive=False,
                y=1.15,
                x=1.05,
                xanchor="right",
                yanchor="top",
                buttons=[
                    dict(label="Play",
                         method="animate",
                         args=[None, {
                             "frame": {"duration": frame_duration, "redraw": True},
                             "fromcurrent": True,
                             "transition": {"duration": frame_duration, "easing": "linear"},
                             "mode": "immediate"
                         }]),
                    dict(label="Pause",
                         method="animate",
                         args=[[None], {
                             "frame": {"duration": 0, "redraw": False},
                             "mode": "immediate",
                             "transition": {"duration": 0}
                         }]),
                    dict(label="Restart",
                         method="animate",
                         args=[[0], {
                             "frame": {"duration": frame_duration, "redraw": True},
                             "fromcurrent": False,
                             "transition": {"duration": frame_duration, "easing": "linear"},
                             "mode": "immediate"
                         }])
                ]
            )]
        ),
        frames=frames
    )
    
    # 保存为HTML
    output_file = "output/word_freq_linechart.html"
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    html_content = pio.to_html(
        fig,
        include_plotlyjs='cdn',
        full_html=True,
        config={
            'responsive': True,
            'showAxisDragHandles': False,
            'staticPlot': False,
            'displayModeBar': False,
            'displaylogo': False,
            'scrollZoom': False,
            'doubleClick': False
        }
    )
    custom_css = """
    <style>
    .js-plotly-plot {
        position: relative;
    }
    .js-plotly-plot .scatterlayer .js-line {
        shape-rendering: geometricPrecision;
        stroke-linejoin: round;
        stroke-linecap: round;
        vector-effect: non-scaling-stroke;
    }
    </style>
    """
    html_content = html_content.replace('</head>', f'{custom_css}</head>')
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"可视化已保存至 {output_file}")
    print(f"动画总时长: {target_duration_sec}秒 ({total_frames}帧，每帧{frame_duration}毫秒)")

if __name__ == "__main__":
    create_word_freq_visualization() 