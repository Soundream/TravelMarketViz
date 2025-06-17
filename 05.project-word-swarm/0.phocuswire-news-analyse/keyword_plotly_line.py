import pandas as pd
import os
import plotly.graph_objs as go
import plotly.io as pio
import numpy as np
import json
import glob
from collections import Counter
import re
from datetime import datetime
from pathlib import Path
from tqdm import tqdm

# Define stop words (same as in keyword_analysis.py)
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

# Add travel industry specific stop words
TRAVEL_STOP_WORDS = {
    'travel', 'company', 'business', 'market', 'service', 'services', 
    'industry', 'customers', 'customer', 'data', 'online', 'platform',
    'technology', 'app', 'product', 'experience', 'booking', 'bookings',
    'flight', 'flights', 'hotel', 'hotels', 'vacation', 'destination',
    'destinations', 'tour', 'tours', 'trip', 'trips', 'traveler', 'travelers',
    'agency', 'agencies', 'global', 'international', 'via'  # Added 'via' to stop words
}

# Combine all stop words
STOP_WORDS = ENGLISH_STOP_WORDS.union(TRAVEL_STOP_WORDS)

def simple_tokenize(text):
    """Simple tokenization function"""
    # Remove non-alphabetic characters and convert to lowercase
    text = re.sub(r'[^a-zA-Z\s]', ' ', text.lower())
    # Tokenize
    return [word.strip() for word in text.split() if word.strip()]

def preprocess_text(text):
    """Preprocess text for keyword extraction"""
    if not text:
        return []
        
    # Remove non-alphabetic characters
    text = re.sub(r'[^a-zA-Z\s]', ' ', text.lower())
    
    # Tokenize
    words = simple_tokenize(text)
    
    # Remove stop words and short words
    words = [word for word in words if word not in STOP_WORDS and len(word) > 2]
    
    return words

def parse_date(date_str):
    """Parse date string to date object"""
    try:
        # Try various possible date formats
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
                
        # If only year is provided
        if re.match(r"^\d{4}$", date_str.strip()):
            return datetime.strptime(date_str.strip(), "%Y")
            
        return None
    except:
        return None

# Load article data
def load_article_data(data_dir="output"):
    """Load article data from JSON files"""
    json_files = glob.glob(os.path.join(data_dir, "phocuswire_page_*.json"))
    all_articles = []
    
    print(f"Found {len(json_files)} JSON files")
    
    for json_file in tqdm(json_files, desc="Loading JSON files"):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                articles = json.load(f)
                all_articles.extend(articles)
        except Exception as e:
            print(f"Error reading file {json_file}: {e}")
    
    print(f"Loaded {len(all_articles)} articles in total")
    return all_articles

# Extract keywords by month
def extract_keywords_by_month(articles):
    """Extract keywords grouped by month"""
    monthly_keywords = {}
    
    for article in tqdm(articles, desc="Processing articles"):
        try:
            # Parse date
            date_str = article.get('date')
            if not date_str:
                continue
                
            date_obj = parse_date(date_str)
            if not date_obj:
                continue
            
            # Convert date to year-month format
            year_month = date_obj.strftime("%Y-%m")
            
            # Preprocess article content
            content = article.get('content', '')
            words = preprocess_text(content)
            
            # Add to monthly keywords
            if year_month not in monthly_keywords:
                monthly_keywords[year_month] = []
            monthly_keywords[year_month].extend(words)
        except Exception as e:
            print(f"Error processing article: {e}")
    
    # Count keywords for each month
    monthly_counts = {}
    for month, words in monthly_keywords.items():
        # Count word frequencies
        word_counts = Counter(words)
        # Get top keywords for each month
        monthly_counts[month] = word_counts.most_common(30)  # Get more keywords as backup
    
    return monthly_counts

# Main execution
print("Loading article data...")
data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
articles = load_article_data(data_dir)

print("Extracting keywords by month...")
monthly_keyword_counts = extract_keywords_by_month(articles)

# Sort months chronologically
months = sorted(monthly_keyword_counts.keys())

if not months:
    print("No valid month data found.")
    exit()

print(f"Found data for {len(months)} months")

# Sample data for debugging
print("\nSample of monthly keyword data:")
for month in months[:3]:  # Show first 3 months
    print(f"\nMonth: {month}")
    for keyword, count in monthly_keyword_counts[month][:10]:  # Show top 10
        print(f"  {keyword}: {count}")

# Get the top 10 keywords from the latest month for visualization
latest_month = months[-1]
top_keywords = [kw for kw, _ in monthly_keyword_counts[latest_month][:10]]
print(f"\nTop 10 keywords from latest month ({latest_month}):")
for kw, count in monthly_keyword_counts[latest_month][:10]:
    print(f"  {kw}: {count}")

# Create a dataframe with months as columns and keywords as rows
keyword_data = pd.DataFrame({month: {kw: count for kw, count in monthly_keyword_counts[month]} 
                             for month in months}).fillna(0)

# Select only the top 10 keywords to display
keyword_data = keyword_data.loc[top_keywords]

# Define colors for keywords
keyword_colors = {
    top_keywords[0]: '#FF4B4B',  # Red
    top_keywords[1]: '#4169E1',  # Royal Blue
    top_keywords[2]: '#32CD32',  # Lime Green
    top_keywords[3]: '#FFA500',  # Orange
    top_keywords[4]: '#9370DB',  # Medium Purple
    top_keywords[5]: '#40E0D0',  # Turquoise
    top_keywords[6]: '#FF69B4',  # Hot Pink
    top_keywords[7]: '#FFD700',  # Gold
    top_keywords[8]: '#8B4513',  # Saddle Brown
    top_keywords[9]: '#00CED1',  # Dark Turquoise
    # 我们的时间需要跟多
}

# Generate numeric x-axis (just like airline_plotly_line.py)
quarters = months
quarter_numeric = np.arange(len(quarters))
interp_steps = 4
interp_x = np.linspace(0, len(quarters)-1, num=(len(quarters)-1)*interp_steps+1)

# Calculate total frames
total_frames = (len(quarters)-1)*interp_steps+1
print(f"Total frames: {total_frames}")

# Calculate frame duration
target_duration_sec = 60
frame_duration = int(target_duration_sec * 1000 / total_frames)
print(f"Frame duration: {frame_duration} ms")

# Set transition time
frame_transition = max(frame_duration - 10, 10)

# Interpolate keyword counts for smooth animation (just like airline_plotly_line.py)
interp_revenue = {}  # Using the same variable name as the original for consistency
for keyword in top_keywords:
    y = keyword_data.loc[keyword].values
    interp_y = np.interp(interp_x, quarter_numeric, y)
    interp_revenue[keyword] = interp_y

# Calculate global y-axis fixed range (same as original)
y_min = 0
all_values = []
for keyword in top_keywords:
    all_values.extend(interp_revenue[keyword])
y_max = max(all_values) * 1.2 if all_values else 10  # Default to 10 if no values

print(f"Fixed Y-axis range: {y_min} to {y_max:.2f}")

# Create initial data (exactly like airline_plotly_line.py)
initial_data = []

# For each keyword create initial data
for keyword in top_keywords:
    color = keyword_colors[keyword]
    
    # Add line - initially empty
    initial_data.append(go.Scatter(
        x=[], 
        y=[], 
        mode='lines', 
        name=keyword,
        line=dict(color=color, width=3, shape='spline', smoothing=1.3),
        hoverinfo='none', 
        showlegend=False,
        uid=f"{keyword}_line"
    ))
    
    # Add point with keyword text - initially empty
    initial_data.append(go.Scatter(
        x=[], 
        y=[], 
        mode='markers+text', 
        name=keyword,
        marker=dict(color=color, size=12), 
        hoverinfo='text+y', 
        text=[], 
        textposition="middle right",
        textfont=dict(family="Monda, sans-serif", size=14, color=color),
        showlegend=False,
        uid=f"{keyword}_point"
    ))

# Create frames (exactly like airline_plotly_line.py)
frames = []
fixed_x = 0.8  # Point fixed on x-axis at 80% position

# Create base frame data
base_frame_data = []
for keyword in top_keywords:
    color = keyword_colors[keyword]
    
    # Line
    base_frame_data.append(go.Scatter(
        x=[], y=[], 
        mode='lines', 
        name=keyword,
        line=dict(color=color, width=2, shape='spline', smoothing=1.3), 
        hoverinfo='skip', 
        showlegend=False,
        uid=f"{keyword}_line"
    ))
    
    # Point with keyword text
    base_frame_data.append(go.Scatter(
        x=[], y=[], 
        mode='markers+text', 
        name=keyword,
        marker=dict(color=color, size=12), 
        text=[],
        textposition="middle right",
        textfont=dict(family="Monda, sans-serif", size=14, color=color),
        hoverinfo='text+y', 
        showlegend=False,
        uid=f"{keyword}_point"
    ))

# Create frame data
for i in range(len(interp_x)):
    # Copy base data structure
    frame_data = []
    for base_trace in base_frame_data:
        # Get base properties
        line_props = {} if 'line' not in base_trace else base_trace['line']
        marker_props = {} if 'marker' not in base_trace else base_trace['marker']
        textfont_props = {} if 'textfont' not in base_trace else base_trace['textfont']
        
        # Create new trace
        new_trace = go.Scatter(
            x=[], 
            y=[], 
            mode=base_trace['mode'] if 'mode' in base_trace else 'lines',
            name=base_trace['name'] if 'name' in base_trace else '',
            line=line_props,
            marker=marker_props,
            textfont=textfont_props,
            hoverinfo=base_trace['hoverinfo'] if 'hoverinfo' in base_trace else 'all',
            showlegend=base_trace['showlegend'] if 'showlegend' in base_trace else False,
            uid=base_trace['uid'] if 'uid' in base_trace else None
        )
        frame_data.append(new_trace)
    
    # Get current frame's time point
    nearest_q_idx = min(int(round(interp_x[i])), len(quarters)-1)
    current_quarter = quarters[nearest_q_idx]
    
    # For each keyword generate line and point
    for idx, keyword in enumerate(top_keywords):
        # Line's x coordinates: from 0 to fixed_x
        x_hist = np.linspace(0, fixed_x, i+1)
        
        # Line's y coordinates
        y_hist = list(interp_revenue[keyword][:i+1])
        
        color = keyword_colors[keyword]
        
        # Update line data
        line_trace_idx = idx * 2
        point_trace_idx = idx * 2 + 1
        
        if line_trace_idx < len(frame_data):
            frame_data[line_trace_idx]['x'] = x_hist
            frame_data[line_trace_idx]['y'] = y_hist
            if 'line' not in frame_data[line_trace_idx]:
                frame_data[line_trace_idx]['line'] = {}
            frame_data[line_trace_idx]['line']['color'] = color
            frame_data[line_trace_idx]['line']['shape'] = 'spline'
            frame_data[line_trace_idx]['line']['smoothing'] = 1.3

        # Update point data
        if point_trace_idx < len(frame_data):
            frame_data[point_trace_idx]['x'] = [fixed_x]
            frame_data[point_trace_idx]['y'] = [y_hist[-1]]
            frame_data[point_trace_idx]['text'] = [keyword]  # Use keyword as text
            if 'marker' not in frame_data[point_trace_idx]:
                frame_data[point_trace_idx]['marker'] = {}
            frame_data[point_trace_idx]['marker']['color'] = color
            frame_data[point_trace_idx]['marker']['size'] = 12
            if 'textfont' not in frame_data[point_trace_idx]:
                frame_data[point_trace_idx]['textfont'] = {}
            frame_data[point_trace_idx]['textfont']['family'] = "Monda, sans-serif"
            frame_data[point_trace_idx]['textfont']['size'] = 14
            frame_data[point_trace_idx]['textfont']['color'] = color
    
    # Create current frame layout with fixed y-axis range
    custom_layout = go.Layout(
        yaxis=dict(
            range=[y_min, y_max],  # Fixed Y-axis range
            title='Keyword Frequency',
            linecolor='gray', 
            showgrid=True, 
            gridcolor='lightgray', 
            griddash='dash', 
            zeroline=False,
            fixedrange=True,
            autorange=False  # Disable auto range adjustment
        ),
        xaxis=dict(
            fixedrange=True,
            autorange=False  # Disable auto range adjustment
        ),
        annotations=[
            dict(
                x=0.5,
                y=1.05,
                xref="paper",
                yref="paper",
                text=f"Month: {current_quarter}",
                showarrow=False,
                font=dict(
                    family="Monda, sans-serif",
                    size=18,
                    color="#000000"
                )
            )
        ]
    )
    
    # Add frame
    frames.append(go.Frame(
        data=frame_data, 
        name=str(i),
        layout=custom_layout
    ))

# Initial frame data (just like airline_plotly_line.py)
initial_data = []
for idx, keyword in enumerate(top_keywords):
    x_hist = np.linspace(0, fixed_x, 1)
    
    # Get initial position
    initial_y = interp_revenue[keyword][0]
    
    y_hist = [initial_y]
    color = keyword_colors[keyword]
    
    initial_data.append(go.Scatter(
        x=x_hist, 
        y=y_hist, 
        mode='lines', 
        name=keyword,
        line=dict(color=color, shape='spline', smoothing=1.3), 
        hoverinfo='skip', 
        showlegend=False,
        uid=f"{keyword}_line"
    ))
    
    initial_data.append(go.Scatter(
        x=[fixed_x], 
        y=[initial_y], 
        mode='markers+text', 
        name=keyword,
        marker=dict(color=color, size=12), 
        hoverinfo='text+y', 
        text=[keyword], 
        textposition="middle right",
        textfont=dict(family="Monda, sans-serif", size=14, color=color),
        showlegend=False,
        uid=f"{keyword}_point"
    ))

# Build chart
fig = go.Figure(
    data=initial_data,
    layout=go.Layout(
        title='Monthly Keyword Trends',
        xaxis=dict(
            title='', 
            range=[0, 1], 
            linecolor='gray', 
            showgrid=False, 
            zeroline=False, 
            showticklabels=False,
            fixedrange=True,
            autorange=False  # Disable auto range adjustment
        ),
        yaxis=dict(
            title='Keyword Frequency', 
            range=[y_min, y_max],  # Use fixed Y-axis range
            linecolor='gray', 
            showgrid=True, 
            gridcolor='lightgray', 
            griddash='dash', 
            zeroline=False,
            fixedrange=True,
            autorange=False  # Disable auto range adjustment
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        updatemenus=[dict(
            type="buttons",
            showactive=False,
            y=1.15,
            x=1.05,
            xanchor="right",
            yanchor="top",
            buttons=[
                dict(label="播放",
                     method="animate",
                     args=[None, {
                         "frame": {"duration": frame_duration, "redraw": True},
                         "fromcurrent": True, 
                         "transition": {"duration": frame_transition, "easing": "linear"},
                         "mode": "immediate"
                     }]),
                dict(label="暂停",
                     method="animate",
                     args=[[None], {
                         "frame": {"duration": 0, "redraw": False},
                         "mode": "immediate",
                         "transition": {"duration": 0}
                     }])
            ]
        )],
        sliders=[],
        # Fixed chart aspect ratio
        height=600,
        width=900,
        margin=dict(l=50, r=150, t=80, b=50)  # Extra right margin for keyword labels
    ),
    frames=frames
)

# HTML output configuration
output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "animation_results")
try:
    # Check if directory exists first
    if not os.path.exists(output_dir):
        print(f"创建输出目录: {output_dir}")
        Path(output_dir).mkdir(parents=True, exist_ok=True)
    else:
        print(f"输出目录已存在: {output_dir}")
except Exception as e:
    print(f"创建输出目录时出错: {e}")
    # Fall back to current directory
    output_dir = "."

output_file = os.path.join(output_dir, "keyword_trends_animation.html")
print(f"将保存动画到: {output_file}")

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
        'doubleClick': False,
        'toImageButtonOptions': {
            'format': 'png',
            'width': 1200,
            'height': 800,
            'scale': 2
        }
    },
    animation_opts=dict(
        frame=dict(duration=frame_duration, redraw=False),
        transition=dict(duration=frame_transition, easing="linear"),
        mode="immediate"
    )
)

# Add simple CSS optimization for animation
custom_css = """
<style>
/* Simplify global settings */
.js-plotly-plot {
  position: relative;
}

/* Provide smooth transition for lines and points */
.scatterlayer .trace {
  transition: transform 20ms linear !important;
}

/* Smooth curve rendering */
.js-plotly-plot .scatterlayer .js-line {
  shape-rendering: geometricPrecision;
  stroke-linejoin: round;
  stroke-linecap: round;
  vector-effect: non-scaling-stroke;
}

/* Prevent axis jitter */
.js-plotly-plot .yaxislayer-above {
  transition: none !important;
  animation: none !important;
}

/* Import Monda font for keyword labels */
@import url('https://fonts.googleapis.com/css2?family=Monda:wght@400;700&display=swap');
</style>
"""

# Add JavaScript for axis stability
axis_stabilizer_js = """
<script>
document.addEventListener('DOMContentLoaded', function() {
    // Script to stabilize axes
    const plotDiv = document.querySelector('.js-plotly-plot');
    if (plotDiv) {
        // Ensure y-axis range is fixed
        const yAxisRange = [""" + str(y_min) + """, """ + str(y_max) + """];
        
        // Force lock y-axis range
        function enforceAxisRange() {
            Plotly.relayout(plotDiv, {
                'yaxis.range': yAxisRange,
                'yaxis.autorange': false,
                'yaxis.fixedrange': true
            });
        }
        
        // Apply on page load and after each frame
        enforceAxisRange();
        
        // Listen for animation events
        plotDiv.on('plotly_animatingframe', function() {
            enforceAxisRange();
        });
    }
});
</script>
"""

# Insert CSS and JavaScript
html_content = html_content.replace('</head>', f'{custom_css}</head>')
html_content = html_content.replace('</body>', f'{axis_stabilizer_js}</body>')

# Save final HTML file
try:
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"动画已成功保存到 {output_file}")
except Exception as e:
    print(f"保存HTML文件时出错: {e}")
    # Try saving to current directory
    fallback_file = "keyword_trends_animation.html"
    try:
        with open(fallback_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"动画已保存到备用位置: {fallback_file}")
    except Exception as e2:
        print(f"保存到备用位置也失败: {e2}")

print(f"动画总时长: {target_duration_sec} 秒 ({total_frames} 帧，每帧 {frame_duration} 毫秒)")
print(f"使用固定Y轴范围: {y_min} 到 {y_max:.2f}，以防止坐标轴抖动")

# 获取每个月份的前10个关键词
print("\n为每个月份确定前10个关键词...")
monthly_top_keywords = {}
all_top_keywords = set()

for month in months:
    # 获取当月前10个关键词
    top_keywords_this_month = [kw for kw, _ in monthly_keyword_counts[month][:10]]
    monthly_top_keywords[month] = top_keywords_this_month
    all_top_keywords.update(top_keywords_this_month)

# 打印一些统计信息
print(f"所有月份的不同关键词总数: {len(all_top_keywords)}")
print(f"将为所有 {len(months)} 个月份分别显示其前10个关键词")

# 为所有关键词分配颜色
color_palette = [
    '#FF4B4B',  # Red
    '#4169E1',  # Royal Blue
    '#32CD32',  # Lime Green
    '#FFA500',  # Orange
    '#9370DB',  # Medium Purple
    '#40E0D0',  # Turquoise
    '#FF69B4',  # Hot Pink
    '#FFD700',  # Gold
    '#8B4513',  # Saddle Brown
    '#00CED1',  # Dark Turquoise
    '#FF6347',  # Tomato
    '#4682B4',  # Steel Blue
    '#9ACD32',  # Yellow Green
    '#FF8C00',  # Dark Orange
    '#BA55D3',  # Medium Orchid
    '#20B2AA',  # Light Sea Green
    '#FF1493',  # Deep Pink
    '#DAA520',  # Goldenrod
    '#A0522D',  # Sienna
    '#48D1CC',  # Medium Turquoise
]

keyword_colors = {}
for i, keyword in enumerate(all_top_keywords):
    keyword_colors[keyword] = color_palette[i % len(color_palette)]

# 创建数据框，所有关键词作为索引，月份作为列
keyword_data = pd.DataFrame({month: {kw: count for kw, count in monthly_keyword_counts[month]} 
                           for month in months}).fillna(0)

# 仅保留所有月份前10的关键词
keyword_data = keyword_data.loc[list(all_top_keywords)]

# 对于每个月份，确定这个月应该显示哪些关键词（包括之前月份的累积）
visible_keywords_by_month = {}
active_keywords = set()  # 用于跟踪当前活跃的关键词

for month in months:
    # 添加当月的前10关键词到活跃集合
    current_month_keywords = monthly_top_keywords[month]
    active_keywords.update(current_month_keywords)
    
    # 存储当月应该显示的所有关键词（包括之前月份累积的关键词）
    visible_keywords_by_month[month] = list(active_keywords)

# 打印一些关键月份的可见关键词数量，用于调试
print("\n各月份可见关键词数量（累积）:")
for i, month in enumerate(months):
    if i == 0 or i == len(months)-1 or i % 45 == 0:  # 仅显示第一个、最后一个和每45个月份
        print(f"月份 {month}: {len(visible_keywords_by_month[month])} 个关键词")

# Generate numeric x-axis (just like airline_plotly_line.py)
quarters = months
quarter_numeric = np.arange(len(quarters))
interp_steps = 4
interp_x = np.linspace(0, len(quarters)-1, num=(len(quarters)-1)*interp_steps+1)

# Calculate total frames
total_frames = (len(quarters)-1)*interp_steps+1
print(f"Total frames: {total_frames}")

# Calculate frame duration
target_duration_sec = 60
frame_duration = int(target_duration_sec * 1000 / total_frames)
print(f"Frame duration: {frame_duration} ms")

# Set transition time
frame_transition = max(frame_duration - 10, 10)

# 为每个关键词的每个月份生成插值数据
interp_revenue = {}  # 使用与原始代码相同的变量名
for keyword in all_top_keywords:
    y = keyword_data.loc[keyword].values
    interp_y = np.interp(interp_x, quarter_numeric, y)
    interp_revenue[keyword] = interp_y

# 创建每一帧应显示的关键词列表
frame_keywords = []
for i in range(len(interp_x)):
    # 确定当前帧对应的月份
    nearest_q_idx = min(int(round(interp_x[i])), len(quarters)-1)
    current_quarter = quarters[nearest_q_idx]
    
    # 获取该月份应该显示的所有关键词
    visible_keywords = visible_keywords_by_month[current_quarter]
    
    # 按照当前值排序，取前10个
    if len(visible_keywords) > 10:
        # 计算当前值
        current_values = {kw: interp_revenue[kw][i] for kw in visible_keywords}
        # 按值排序并取前10个
        visible_keywords = sorted(visible_keywords, 
                                 key=lambda kw: current_values[kw], 
                                 reverse=True)[:10]
    
    frame_keywords.append(visible_keywords)

# 打印一些帧的关键词，用于调试
print("\n部分帧的关键词:")
sample_frames = [0, len(interp_x)//4, len(interp_x)//2, 3*len(interp_x)//4, len(interp_x)-1]
for i in sample_frames:
    nearest_q_idx = min(int(round(interp_x[i])), len(quarters)-1)
    current_quarter = quarters[nearest_q_idx]
    print(f"帧 {i} (月份 {current_quarter}): {len(frame_keywords[i])} 个关键词")
    print(f"  前5个关键词: {', '.join(frame_keywords[i][:5])}")

# Calculate global y-axis fixed range (same as original)
y_min = 0
all_values = []
for keyword in all_top_keywords:
    all_values.extend(interp_revenue[keyword])
y_max = max(all_values) * 1.2 if all_values else 10  # Default to 10 if no values

print(f"Fixed Y-axis range: {y_min} to {y_max:.2f}")

# 重新定义base_frame_data，确保其包含所有关键词
base_frame_data = []
for keyword in all_top_keywords:
    color = keyword_colors[keyword]
    
    # 线
    base_frame_data.append(go.Scatter(
        x=[], y=[], 
        mode='lines', 
        name=keyword,
        line=dict(color=color, width=2, shape='spline', smoothing=1.3), 
        hoverinfo='skip', 
        showlegend=False,
        uid=f"{keyword}_line"
    ))
    
    # 点和文本
    base_frame_data.append(go.Scatter(
        x=[], y=[], 
        mode='markers+text', 
        name=keyword,
        marker=dict(color=color, size=12),
        text=[],
        textposition="middle right",
        textfont=dict(family="Monda, sans-serif", size=14, color=color),
        hoverinfo='text+y', 
        showlegend=False,
        uid=f"{keyword}_point"
    ))

# 创建帧
frames = []
for frame_idx, keywords_for_frame in enumerate(frame_keywords):
    frame_data = []
    
    x_value = interp_x[frame_idx]
    nearest_q_idx = min(int(round(x_value)), len(quarters)-1)
    current_quarter = quarters[nearest_q_idx]
    
    for keyword in all_top_keywords:
        uid_line = f"{keyword}_line"
        uid_point = f"{keyword}_point"
        
        # 当前关键词是否应该可见
        visible = keyword in keywords_for_frame
        
        if visible:
            # 构建线的历史数据
            line_x = []
            line_y = []
            
            # 获取到当前帧为止的所有x和y值
            for i in range(frame_idx + 1):
                line_x.append(interp_x[i])
                line_y.append(interp_revenue[keyword][i])
            
            # 更新线数据
            frame_data.append(go.Scatter(
                x=line_x, y=line_y,
                uid=uid_line,
                visible=True
            ))
            
            # 更新点和文本数据
            current_y = interp_revenue[keyword][frame_idx]
            frame_data.append(go.Scatter(
                x=[x_value], y=[current_y],
                text=[f"{keyword} ({current_y:.0f})"],  # 添加频率到标签
                uid=uid_point,
                visible=True
            ))
        else:
            # 如果不可见，保持空数据但保留占位符
            frame_data.append(go.Scatter(x=[], y=[], uid=uid_line, visible=False))
            frame_data.append(go.Scatter(x=[], y=[], text=[], uid=uid_point, visible=False))
    
    frames.append(go.Frame(data=frame_data, name=str(frame_idx)))

# 初始帧设置
initial_traces = []
for keyword in all_top_keywords:
    # 对于初始帧，所有线条都不显示
    initial_traces.append(go.Scatter(x=[], y=[], uid=f"{keyword}_line", visible=False))
    initial_traces.append(go.Scatter(x=[], y=[], text=[], uid=f"{keyword}_point", visible=False))

# 创建布局
layout = go.Layout(
    title=dict(
        text='Monthly Keyword Frequency Trends',
        font=dict(size=24, family='Monda, sans-serif')
    ),
    xaxis=dict(
        title='Month',
        showgrid=True,
        gridwidth=1,
        gridcolor='lightgray',
        tickvals=list(range(len(quarters))),
        ticktext=quarters,
        tickangle=45,
        tickfont=dict(size=12),
        range=[-0.5, len(quarters) - 0.5]  # 确保x轴范围固定
    ),
    yaxis=dict(
        title='Frequency',
        showgrid=True,
        gridwidth=1,
        gridcolor='lightgray',
        range=[y_min, y_max]  # 使用固定的y轴范围
    ),
    showlegend=False,
    margin=dict(l=50, r=100, t=50, b=80),  # 右侧留出更多空间显示文字
    hovermode='closest',
    plot_bgcolor='white',
    updatemenus=[{
        'type': 'buttons',
        'showactive': False,
        'buttons': [{
            'label': 'Play',
            'method': 'animate',
            'args': [None, {
                'frame': {'duration': frame_duration, 'redraw': True},
                'fromcurrent': True,
                'transition': {'duration': 0}
            }]
        }],
        'x': 0.1, 'y': 0, 'xanchor': 'right', 'yanchor': 'bottom'
    }],
    sliders=[{
        'steps': [
            {
                'method': 'animate',
                'label': '',
                'args': [[str(i)], {
                    'frame': {'duration': frame_duration, 'redraw': True},
                    'mode': 'immediate',
                    'transition': {'duration': 0}
                }]
            }
            for i in range(len(frames))
        ],
        'x': 0.1, 'y': 0, 'xanchor': 'left', 'yanchor': 'bottom',
        'len': 0.9, 'pad': {'t': 50, 'b': 10},
        'currentvalue': {
            'visible': True,
            'prefix': 'Month: ',
            'xanchor': 'right',
            'font': {'size': 12, 'color': '#666'}
        }
    }]
)

# 创建图表
fig = go.Figure(data=initial_traces, layout=layout, frames=frames)

# 确保输出目录存在
output_dir = 'animation_results'
os.makedirs(output_dir, exist_ok=True)

# 保存为HTML文件
output_file = os.path.join(output_dir, 'keyword_trends_animation.html')
fig.write_html(output_file)
print(f"\n动画已保存到: {os.path.abspath(output_file)}")

# 计算统计信息
print(f"\n动画总时长: {target_duration_sec} 秒 ({total_frames} 帧，每帧 {frame_duration} 毫秒)")
print(f"使用固定Y轴范围: {y_min} 到 {y_max:.2f}，以防止坐标轴抖动") 