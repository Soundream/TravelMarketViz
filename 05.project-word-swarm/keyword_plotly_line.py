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
    'agency', 'agencies', 'global', 'international'
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
    
    for json_file in json_files:
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
    
    for article in articles:
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
        # Get top 10 keywords for each month
        monthly_counts[month] = word_counts.most_common(10)
    
    return monthly_counts

# Define colors for keywords
keyword_colors = {
    # Bright, distinguishable colors
    0: '#FF4B4B',  # Red
    1: '#4169E1',  # Royal Blue
    2: '#32CD32',  # Lime Green
    3: '#FFA500',  # Orange
    4: '#9370DB',  # Medium Purple
    5: '#40E0D0',  # Turquoise
    6: '#FF69B4',  # Hot Pink
    7: '#FFD700',  # Gold
    8: '#8B4513',  # Saddle Brown
    9: '#00CED1',  # Dark Turquoise
}

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

# Create a set of all keywords that appear in the top 10 for any month
all_top_keywords = set()
for month in months:
    keywords = [kw for kw, _ in monthly_keyword_counts[month]]
    all_top_keywords.update(keywords)

print(f"Total unique top keywords: {len(all_top_keywords)}")

# Create a DataFrame with months as columns and keywords as rows
keyword_data = {}
for month in months:
    keyword_data[month] = {}
    for keyword, count in monthly_keyword_counts[month]:
        keyword_data[month][keyword] = count

# Convert to DataFrame
df = pd.DataFrame(keyword_data)
df = df.fillna(0)  # Replace NaN with 0

# Generate numeric x-axis
month_numeric = np.arange(len(months))
interp_steps = 4
interp_x = np.linspace(0, len(months)-1, num=(len(months)-1)*interp_steps+1)

# Calculate total frames
total_frames = (len(months)-1)*interp_steps+1
print(f"Total frames: {total_frames}")

# Calculate frame duration
target_duration_sec = 60
frame_duration = int(target_duration_sec * 1000 / total_frames)
print(f"Frame duration: {frame_duration} ms")

# Set transition time
frame_transition = max(frame_duration - 10, 10)

# Interpolate keyword counts for smooth animation
interp_keyword_counts = {}
for keyword in all_top_keywords:
    # Get counts for this keyword across all months
    counts = []
    for month in months:
        month_data = dict(monthly_keyword_counts[month])
        counts.append(month_data.get(keyword, 0))
    
    # Interpolate
    interp_counts = np.interp(interp_x, month_numeric, counts)
    interp_keyword_counts[keyword] = interp_counts

# Calculate global y-axis fixed range
y_min = 0
all_values = []
for keyword in all_top_keywords:
    all_values.extend(interp_keyword_counts[keyword])
y_max = max(all_values) * 1.2

print(f"Fixed Y-axis range: {y_min} to {y_max:.2f}")

# Create frames
frames = []
fixed_x = 0.8  # Fixed position on x-axis for the keyword label

# Create base frame data
base_frame_data = []
for idx, keyword in enumerate(all_top_keywords):
    color_idx = idx % len(keyword_colors)
    color = keyword_colors[color_idx]
    
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
    
    # Point with keyword label
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

# Create frame data for each time point
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
    
    # Get current month
    nearest_month_idx = min(int(round(interp_x[i])), len(months)-1)
    current_month = months[nearest_month_idx]
    
    # Get top 10 keywords for this frame
    if i == 0:
        # For the first frame, use the first month's top keywords
        current_top_keywords = [kw for kw, _ in monthly_keyword_counts[months[0]]][:10]
    else:
        # For other frames, calculate current values and find top 10
        current_values = {}
        for keyword in all_top_keywords:
            current_values[keyword] = interp_keyword_counts[keyword][i]
        current_top_keywords = sorted(current_values.keys(), key=lambda k: current_values[k], reverse=True)[:10]
    
    # Update data for top keywords only
    for idx, keyword in enumerate(current_top_keywords):
        color_idx = idx % len(keyword_colors)
        color = keyword_colors[color_idx]
        
        # Find the trace indices for this keyword
        line_trace_idx = None
        point_trace_idx = None
        for j, trace in enumerate(frame_data):
            if trace['uid'] == f"{keyword}_line":
                line_trace_idx = j
            elif trace['uid'] == f"{keyword}_point":
                point_trace_idx = j
        
        if line_trace_idx is not None and point_trace_idx is not None:
            # Line's x-coordinates: from 0 to fixed_x
            x_hist = np.linspace(0, fixed_x, i+1)
            
            # Line's y-coordinates
            y_hist = list(interp_keyword_counts[keyword][:i+1])
            
            # Update line data
            frame_data[line_trace_idx]['x'] = x_hist
            frame_data[line_trace_idx]['y'] = y_hist
            if 'line' not in frame_data[line_trace_idx]:
                frame_data[line_trace_idx]['line'] = {}
            frame_data[line_trace_idx]['line']['color'] = color
            frame_data[line_trace_idx]['line']['shape'] = 'spline'
            frame_data[line_trace_idx]['line']['smoothing'] = 1.3

            # Update point data with keyword label
            frame_data[point_trace_idx]['x'] = [fixed_x]
            frame_data[point_trace_idx]['y'] = [y_hist[-1] if y_hist else 0]
            frame_data[point_trace_idx]['text'] = [keyword]  # Use keyword as label
            if 'marker' not in frame_data[point_trace_idx]:
                frame_data[point_trace_idx]['marker'] = {}
            frame_data[point_trace_idx]['marker']['color'] = color
            frame_data[point_trace_idx]['marker']['size'] = 12
            if 'textfont' not in frame_data[point_trace_idx]:
                frame_data[point_trace_idx]['textfont'] = {}
            frame_data[point_trace_idx]['textfont']['family'] = "Monda, sans-serif"
            frame_data[point_trace_idx]['textfont']['size'] = 14
            frame_data[point_trace_idx]['textfont']['color'] = color
    
    # Create layout with fixed y-axis range
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
            autorange=False
        ),
        xaxis=dict(
            fixedrange=True,
            autorange=False
        ),
        annotations=[
            dict(
                x=0.5,
                y=1.05,
                xref="paper",
                yref="paper",
                text=f"Month: {current_month}",
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

# Initial data
initial_data = []
if months:
    first_month_keywords = [kw for kw, _ in monthly_keyword_counts[months[0]]][:10]
    
    for idx, keyword in enumerate(first_month_keywords):
        x_hist = np.linspace(0, fixed_x, 1)
        
        # Get initial value
        initial_y = interp_keyword_counts[keyword][0] if keyword in interp_keyword_counts else 0
        
        y_hist = [initial_y]
        color_idx = idx % len(keyword_colors)
        color = keyword_colors[color_idx]
        
        # Line
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
        
        # Point with keyword label
        initial_data.append(go.Scatter(
            x=[fixed_x], 
            y=[initial_y], 
            mode='markers+text', 
            name=keyword,
            marker=dict(color=color, size=12),
            text=[keyword],
            textposition="middle right",
            textfont=dict(family="Monda, sans-serif", size=14, color=color),
            hoverinfo='text+y', 
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
            autorange=False
        ),
        yaxis=dict(
            title='Keyword Frequency', 
            range=[y_min, y_max],
            linecolor='gray', 
            showgrid=True, 
            gridcolor='lightgray', 
            griddash='dash', 
            zeroline=False,
            fixedrange=True,
            autorange=False
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
                dict(label="Play",
                     method="animate",
                     args=[None, {
                         "frame": {"duration": frame_duration, "redraw": True},
                         "fromcurrent": True, 
                         "transition": {"duration": frame_transition, "easing": "linear"},
                         "mode": "immediate"
                     }]),
                dict(label="Pause",
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
        margin=dict(l=50, r=150, t=80, b=50),  # Extra right margin for keyword labels
        annotations=[
            dict(
                x=0.5,
                y=1.05,
                xref="paper",
                yref="paper",
                text=f"Month: {months[0] if months else ''}",
                showarrow=False,
                font=dict(
                    family="Monda, sans-serif",
                    size=18,
                    color="#000000"
                )
            )
        ]
    ),
    frames=frames
)

# HTML output configuration
output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "animation_results")
Path(output_dir).mkdir(parents=True, exist_ok=True)
output_file = os.path.join(output_dir, "keyword_trends_animation.html")

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

# Add CSS for animation optimization
custom_css = """
<style>
/* Global settings */
.js-plotly-plot {
  position: relative;
}

/* Smooth transition for lines and points */
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
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"Animation saved to {output_file}")
print(f"Animation duration: {target_duration_sec} seconds ({total_frames} frames, {frame_duration} ms per frame)")
print(f"Using fixed Y-axis range: {y_min} to {y_max:.2f} to prevent axis jitter") 