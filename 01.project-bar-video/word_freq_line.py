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
from scipy.interpolate import interp1d

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
    
    # 将每个月的前15个关键词保存到txt文件
    output_file = "output/monthly_top_keywords.txt"
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("每个月的前15个关键词:\n")
        f.write("-" * 50 + "\n")
        for date in sorted(dates):
            words = sorted(word_freq_by_date[date].items(), key=lambda x: x[1], reverse=True)
            top15 = words[:15]
            f.write(f"\n{date}:\n")
            for word, freq in top15:
                f.write(f"  {word}: {freq}\n")
        f.write("-" * 50 + "\n")
    
    print(f"\n每月关键词统计已保存至: {output_file}")
    
    return word_freq_by_date, sorted(list(dates))

def create_word_freq_visualization(data_dir="../05.project-word-swarm/output"):
    """创建词频可视化"""
    word_freq_by_date, dates = load_and_process_data(data_dir)
    
    # 合并 covid 和 pandemic 的频率
    for date in dates:
        if date in word_freq_by_date:
            covid_freq = word_freq_by_date[date].get('covid', 0)
            pandemic_freq = word_freq_by_date[date].get('pandemic', 0)
            word_freq_by_date[date]['pandemic'] = covid_freq + pandemic_freq
            if 'covid' in word_freq_by_date[date]:
                del word_freq_by_date[date]['covid']
    
    # 合并 generative 和 artificial intelligence 的频率
    for date in dates:
        if date in word_freq_by_date:
            generative_freq = word_freq_by_date[date].get('generative', 0)
            ai_freq = word_freq_by_date[date].get('artificial intelligence', 0)
            word_freq_by_date[date]['artificial intelligence'] = generative_freq + ai_freq
            if 'generative' in word_freq_by_date[date]:
                del word_freq_by_date[date]['generative']
    
    # 定义关键词显示时间范围
    keyword_ranges = {
        "mobile": { "2010-05": "2018-12" },
        "american": { "2010-11": "2011-02" },
        "airbnb": { "2016-09": "2020-12"},
        "china": {  "2018-09": "2019-03" },
        "pandemic": { "2020-03": "2024-01" },  # 合并后的时间范围
        "google": { "2010-05": "2013-10", "2013-12": "2014-10" },
        "sustainability": { "2020-01": "2022-12" },
        "artificial intelligence": { "2024-01": "2025-04" },
        "marketing": { "2011-04": "2018-12" },
        "distribution": { "2015-09": "2019-12" },
        "blockchain": { "2017-08": "2018-06"},
        "expedia": { "2015-03": "2015-10" }
    }
    
    # 动画帧
    colors = ['#40E0D0', '#4169E1', '#FF4B4B', '#32CD32', '#DEB887', '#8A2BE2', '#FFA500', 
              '#20B2AA', '#FF69B4', '#4B0082', '#FFD700', '#00CED1', '#FF4500', '#7B68EE', '#00FA9A']
    
    # 计算所有词在所有时间点的最大频率
    max_freq = 0
    for date in dates:
        for word, freq in word_freq_by_date[date].items():
            max_freq = max(max_freq, freq)

    # 获取所有需要显示的关键词，并按照开始时间排序
    all_keywords = []
    for word, ranges in keyword_ranges.items():
        start_dates = []
        for start_date, _ in ranges.items():
            start_dates.append(start_date)
        all_keywords.append((word, min(start_dates)))
    all_keywords.sort(key=lambda x: x[1])  # 按开始时间排序
    all_keywords = [word for word, _ in all_keywords]
    
    # 预先计算每个关键词的所有频率数据，保持连续性
    keyword_freq_data = {}
    for word in all_keywords:
        freq_data = []
        last_valid_value = None
        
        for date in dates:
            # 检查当前日期是否在任何显示范围内
            in_range = False
            for start_date, end_date in keyword_ranges[word].items():
                if start_date <= date <= end_date:
                    in_range = True
                    break
            
            # 在显示范围内且有数据时更新值
            if in_range and date in word_freq_by_date and word in word_freq_by_date[date]:
                last_valid_value = word_freq_by_date[date][word]
                freq_data.append(last_valid_value)
            else:
                # 如果不在显示范围内，使用None
                freq_data.append(None)
        
        keyword_freq_data[word] = freq_data
    # 1. 生成插值后的时间轴和数据
    interp_steps = 10  # 增加插值帧数
    date_objs = [datetime.strptime(d, "%Y-%m") for d in dates]
    x_old = np.array([d.timestamp() for d in date_objs])
    interp_x = np.linspace(x_old[0], x_old[-1], num=(len(dates)-1)*interp_steps+1)
    total_frames = len(interp_x)
    target_duration_sec = 600
    frame_duration = int(target_duration_sec * 1000 / total_frames)
    frame_transition = int(frame_duration * 0.8)

    # 2. 对每个关键词做平滑插值
    interp_freq = {}
    for word in all_keywords:
        y = np.array([v if v is not None else 0 for v in keyword_freq_data[word]])
        valid_mask = ~np.isnan(y)
        if np.sum(valid_mask) > 1:
            f = interp1d(x_old[valid_mask], y[valid_mask], kind='cubic', bounds_error=False, fill_value="extrapolate")
            interp_y = f(interp_x)
            interp_y = np.maximum(interp_y, 0)
        else:
            interp_y = np.zeros_like(interp_x)
        interp_freq[word] = interp_y

    # 3. 固定y轴范围
    y_min = 0
    y_max = max([np.max(v) for v in interp_freq.values()]) * 1.2

    # 4. 生成初始trace
    initial_data = []
    for idx, word in enumerate(all_keywords):
        color = colors[idx % len(colors)]
        initial_data.append(go.Scatter(
            x=[], y=[], mode='lines', name=word,
            line=dict(color=color, width=3, shape='spline', smoothing=1.3),
            hoverinfo='skip', showlegend=False, uid=f'{word}_line'))
        initial_data.append(go.Scatter(
            x=[], y=[], mode='markers+text', name=word,
            marker=dict(color=color, size=10),
            text=[],
            textposition='middle right',
            hoverinfo='text+y', showlegend=False, uid=f'{word}_point'))

    # 5. 生成帧
    frames = []
    for i in range(total_frames):
        frame_data = []
        current_time = datetime.fromtimestamp(interp_x[i])
        window_size = (date_objs[-1] - date_objs[0]).total_seconds() * 0.4
        start_time = current_time - pd.Timedelta(seconds=window_size)
        start_time = max(start_time, date_objs[0])

        for idx, word in enumerate(all_keywords):
            color = colors[idx % len(colors)]
            
            # 获取当前时间点之前的所有数据
            mask = interp_x <= interp_x[i]
            x_dt = [datetime.fromtimestamp(x) for x in interp_x[mask]]
            y_hist = interp_freq[word][mask]
            
            # 过滤显示范围内的数据
            filtered_x = []
            filtered_y = []
            for x, y in zip(x_dt, y_hist):
                in_range = False
                for start_date, end_date in keyword_ranges[word].items():
                    start_dt = datetime.strptime(start_date, "%Y-%m")
                    end_dt = datetime.strptime(end_date, "%Y-%m")
                    if start_dt <= x <= end_dt:
                        in_range = True
                        break
                if in_range:
                    filtered_x.append(x)
                    filtered_y.append(y)
            
            if len(filtered_x) == 0:
                filtered_x = []
                filtered_y = []
                text = []
            else:
                text = [f"{word} ({filtered_x[-1].strftime('%Y-%m')})"]
            
            frame_data.append(go.Scatter(
                x=filtered_x, y=filtered_y, mode='lines', name=word,
                line=dict(color=color, width=3, shape='spline', smoothing=1.3),
                hoverinfo='skip', showlegend=False, uid=f'{word}_line'))
            frame_data.append(go.Scatter(
                x=filtered_x[-1:] if filtered_x else [], y=filtered_y[-1:] if filtered_y else [], mode='markers+text', name=word,
                marker=dict(color=color, size=10),
                text=text,
                textposition='middle right',
                hoverinfo='text+y', showlegend=False, uid=f'{word}_point'))
        
        frames.append(go.Frame(
            data=frame_data,
            name=str(i),
            layout=go.Layout(
                xaxis=dict(
                    range=[start_time, current_time],
                    type='date',
                    tickformat='%Y-%m',
                    showgrid=True,
                    gridcolor='lightgray',
                    griddash='dash',
                    fixedrange=True,
                    autorange=False
                ),
                yaxis=dict(
                    range=[y_min, y_max],
                    title='Frequency',
                    linecolor='gray',
                    showgrid=True,
                    gridcolor='lightgray',
                    griddash='dash',
                    zeroline=False,
                    fixedrange=True,
                    autorange=False
                )
            )
        ))

    # 6. 构建图表
    fig = go.Figure(
        data=frames[0].data,
        layout=go.Layout(
            title='Top Word Frequencies Over Time (News from Phocuswire)',
            xaxis=dict(
                title='Date',
                type='date',
                tickformat='%Y-%m',
                showgrid=True,
                gridcolor='lightgray',
                griddash='dash',
                fixedrange=True,
                autorange=False,
                range=[date_objs[0], date_objs[-1]]
            ),
            yaxis=dict(
                title='Frequency',
                linecolor='gray',
                showgrid=True,
                gridcolor='lightgray',
                griddash='dash',
                zeroline=False,
                fixedrange=True,
                autorange=False,
                range=[y_min, y_max]
            ),
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(family='Monda'),
            height=600,
            width=1500,
            margin=dict(l=50, r=150, t=80, b=50),
            updatemenus=[dict(
                type='buttons',
                showactive=False,
                y=1.15,
                x=1.05,
                xanchor='right',
                yanchor='top',
                buttons=[
                    dict(
                        label='Play',
                        method='animate',
                        args=[None, {
                            "frame": {"duration": frame_duration, "redraw": True},
                            "fromcurrent": True,
                            "transition": {"duration": frame_transition, "easing": "linear"},
                            "mode": "immediate"
                        }]
                    ),
                    dict(
                        label='Pause',
                        method='animate',
                        args=[[None], {
                            "frame": {"duration": 0, "redraw": False},
                            "mode": "immediate",
                            "transition": {"duration": 0}
                        }]
                    )
                ]
            )]
        ),
        frames=frames
    )

    # 7. 输出HTML
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
        },
        animation_opts=dict(
            frame=dict(duration=frame_duration, redraw=True),
            transition=dict(duration=frame_transition, easing="linear"),
            mode="immediate"
        )
    )
    
    # 添加自定义CSS和JS
    custom_css = """
    <style>
    .js-plotly-plot { position: relative; }
    .scatterlayer .trace { transition: transform 20ms linear !important; }
    .js-plotly-plot .scatterlayer .js-line { 
        shape-rendering: geometricPrecision; 
        stroke-linejoin: round; 
        stroke-linecap: round; 
        vector-effect: non-scaling-stroke; 
    }
    .js-plotly-plot .yaxislayer-above { 
        transition: none !important; 
        animation: none !important; 
    }
    </style>
    """
    
    animation_js = f"""
    <script>
    document.addEventListener('DOMContentLoaded', function() {{
        const plotDiv = document.querySelector('.js-plotly-plot');
        if (plotDiv) {{
            const yAxisRange = [{y_min}, {y_max}];
            
            function enforceAxisRange() {{
                Plotly.relayout(plotDiv, {{
                    'yaxis.range': yAxisRange,
                    'yaxis.autorange': false,
                    'yaxis.fixedrange': true
                }});
            }}
            
            plotDiv.on('plotly_animatingframe', function() {{
                enforceAxisRange();
            }});
            
            enforceAxisRange();
        }}
    }});
    </script>
    """
    
    html_content = html_content.replace('</head>', f'{custom_css}</head>')
    html_content = html_content.replace('</body>', f'{animation_js}</body>')
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"动画保存至 {output_file}")
    print(f"动画总时长: {target_duration_sec}秒 ({total_frames}帧，每帧{frame_duration}毫秒)")
    print(f"使用固定Y轴范围: {y_min} 到 {y_max:.2f}，避免坐标轴抖动")

if __name__ == "__main__":
    create_word_freq_visualization() 