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
    
    # 获取所有年份并确保是字符串格式
    years = sorted([str(year) for year in yearly_data.keys()])
    print(f"处理年份范围: {years[0]} - {years[-1]}")
    print(f"总年份数: {len(years)}")
    print(f"所有年份: {years}")
    
    # 为每年选择top3词汇
    yearly_top_words = {}
    for year in years:
        # 合并该年所有月份的词频
        year_freq = {}
        for date, freq_dict in yearly_data[year].items():
            for word, freq in freq_dict.items():
                year_freq[word] = year_freq.get(word, 0) + freq
        
        # 选择top3
        top_words = sorted(year_freq.items(), key=lambda x: x[1], reverse=True)[:1]
        yearly_top_words[year] = [word for word, _ in top_words]
        print(f"{year}年top3词汇: {yearly_top_words[year]}")
    
    # 动画帧
    colors = ['#40E0D0', '#4169E1', '#FF4B4B', '#32CD32', '#DEB887', '#8A2BE2', '#FFA500', '#20B2AA', '#FF69B4']
    
    # 计算所有词在所有时间点的最大频率
    max_freq = 0
    for date in dates:
        for word, freq in word_freq_by_date[date].items():
            max_freq = max(max_freq, freq)
    
    # 预计算所有可能需要的轨迹
    max_traces = len(years) * 3 * 2  # 每年3个词，每个词有线条和标签
    all_traces = []
    for i in range(max_traces):
        all_traces.append(go.Scatter(
            x=[],
            y=[],
            mode='lines',
            showlegend=False,
            hoverinfo='skip'
        ))
    
    # 为每个年份创建帧
    frames = []
    for i, current_year in enumerate(years):
        print(f"\n处理第{i+1}帧，当前年份: {current_year}")
        # 复制基础轨迹
        frame_data = [trace for trace in all_traces]
        trace_index = 0
        
        # 处理之前所有年份的词
        for year in years[:i+1]:
            print(f"  处理{year}年的词")
            # 获取该年的top3词汇
            top_words = yearly_top_words[year]
            
            # 为每个词创建趋势线
            for word in top_words:
                color = colors[trace_index % len(colors)]
                
                # 计算该词在前后一年的趋势
                start_year = str(int(year) - 1)
                end_year = str(int(year) + 1)
                
                # 获取相关日期范围内的数据
                word_data = []
                for date in dates:
                    date_year = date.split('-')[0]
                    # 如果是当前年份，只显示到当前年份
                    if year == current_year:
                        if start_year <= date_year <= year:
                            freq = word_freq_by_date[date].get(word, 0)
                            word_data.append((date, freq))
                    # 如果是之前的年份，显示完整的三年龄趋势
                    else:
                        if start_year <= date_year <= end_year:
                            freq = word_freq_by_date[date].get(word, 0)
                            word_data.append((date, freq))
                
                if word_data:
                    x = [d for d, _ in word_data]
                    y = [f for _, f in word_data]
                    print(f"    添加词 '{word}' 的数据点: {len(x)}个")
                    
                    # 更新线条
                    frame_data[trace_index] = go.Scatter(
                        x=x,
                        y=y,
                        mode='lines',
                        name=f"{word} ({year})",
                        line=dict(color=color, width=3, shape='spline', smoothing=1.3),
                        showlegend=False,
                        hoverinfo='x+y+name'
                    )
                    
                    # 更新标签
                    frame_data[trace_index + 1] = go.Scatter(
                        x=[x[-1]],
                        y=[y[-1]],
                        mode='text',
                        text=[f"{word} ({year})"],
                        textposition='middle right',
                        textfont=dict(color=color, size=12),
                        showlegend=False,
                        hoverinfo='skip'
                    )
                
                trace_index += 2
        
        frames.append(go.Frame(data=frame_data, name=str(i)))
        print(f"完成第{i+1}帧，年份: {current_year}")
    
    # 初始帧使用第一帧的数据
    initial_data = frames[0].data
    
    # 动画参数
    total_frames = len(years)
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
                range=[0, max_freq * 1.1]  # 设置y轴范围从0到最大值的1.1倍
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