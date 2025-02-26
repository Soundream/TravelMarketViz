import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import pandas as pd
import numpy as np
from matplotlib.ticker import FuncFormatter
from matplotlib.ticker import MultipleLocator
import matplotlib.font_manager as fm
import os
import time

# Set up font configurations
plt.rcParams['font.family'] = 'sans-serif'

# Check for Open Sans font, otherwise use a system sans-serif font
font_path = None
system_fonts = fm.findSystemFonts()
for font in system_fonts:
    if 'opensans' in font.lower() or 'open-sans' in font.lower():
        font_path = font
        break

if font_path:
    open_sans_font = fm.FontProperties(fname=font_path)
else:
    open_sans_font = fm.FontProperties(family='sans-serif')

# Use DejaVu Sans Mono for fixed-width text
deja_vu_font = fm.FontProperties(family='DejaVu Sans Mono')

# Define the function to add text to the figure (similar to fig_text)
def fig_text(x, y, text, **kwargs):
    fig = kwargs.pop('fig', plt.gcf())
    fig.text(x, y, text, **kwargs)

# Function to get quarter and year from numeric year
def get_quarter_year(time_value):
    year = int(time_value)
    quarter = int((time_value - year) * 4) + 1
    return f"Q{quarter}'{str(year)[-2:]}"  # Using last 2 digits of year for shorter display

# After imports and before loading data
# Create required directories
logos_dir = 'logos'
output_dir = 'output'
for directory in [logos_dir, output_dir]:
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Created directory: {directory}")

# Load the data from Excel
print("Loading data...")
data = pd.read_excel('formatted_data.xlsx')
print(f"Loaded {len(data)} rows of data")

# Check if the values are in decimal format (between -1 and 1)
if data['Revenue Growth (%)'].abs().max() <= 1 or data['EBITDA Margin (%)'].abs().max() <= 1:
    print("Converting decimal values to percentages...")
    data['Revenue Growth (%)'] = data['Revenue Growth (%)'] * 100
    data['EBITDA Margin (%)'] = data['EBITDA Margin (%)'] * 100

# Interpolate the data for smoother animation
def interpolate_data(data, multiple=30):
    """
    对每个公司的数据进行独立插值
    data: 包含原始数据的DataFrame
    multiple: 插值点数的倍数
    """
    # 创建一个空的列表来存储所有插值结果
    all_interpolated = []
    
    # 按公司分组处理数据
    for company in data['Company'].unique():
        # 获取当前公司的数据
        company_data = data[data['Company'] == company].copy()
        company_data = company_data.sort_values('Numeric_Year')
        print(company_data)
        # 检查是否有足够的数据点进行插值
        if len(company_data) < 2:
            print(f"Warning: Not enough data points for {company}")
            continue
            
        # 获取该公司的有效时间范围
        company_min_year = company_data['Numeric_Year'].min()
        company_max_year = company_data['Numeric_Year'].max()
        
        # 计算该公司的插值点数
        time_span = company_max_year - company_min_year
        num_points = int(time_span * 4 * multiple) + 1  # 每季度multiple个点
        
        # 创建该公司的时间点数组
        time_points = np.linspace(company_min_year, company_max_year, num_points)
        
        # 创建该公司的插值DataFrame
        company_interp = pd.DataFrame()
        company_interp['Numeric_Year'] = time_points
        company_interp['Company'] = company
        
        # 对每个字段进行插值
        fields = ['Revenue', 'EBITDA Margin (%)', 'Revenue Growth (%)']
        for field in fields:
            # 获取非NaN的数据点
            valid_data = company_data[company_data[field].notna()]
            if len(valid_data) >= 2:
                # 使用线性插值
                company_interp[field] = np.interp(
                    time_points,
                    valid_data['Numeric_Year'].values,
                    valid_data[field].values
                )
                
                # 确保在原始数据点上的值保持不变
                for _, row in valid_data.iterrows():
                    mask = np.abs(time_points - row['Numeric_Year']) < 1e-10
                    if any(mask):
                        company_interp.loc[mask, field] = row[field]
            else:
                print(f"Warning: Not enough valid data points for {company} - {field}")
                company_interp[field] = np.nan
        # 将该公司的插值结果添加到列表中
        all_interpolated.append(company_interp)

    if not all_interpolated:
        raise ValueError("No data to interpolate")
    
    # 合并所有公司的数据
    result = pd.concat(all_interpolated, ignore_index=True)
    # 确保按照时间和公司正确排序
    result = result.sort_values(['Numeric_Year', 'Company']).reset_index(drop=True)
    
    # 打印每个公司在每个时间点的数据，用于调试
    for company in result['Company'].unique():
        company_data = result[result['Company'] == company].head(3)
        
    return result

# Generate interpolated data
print("\nInterpolating data...")
interp_data = interpolate_data(data)


# Save interpolated data to Excel
output_file = 'output/interpolated_data.xlsx'
if not os.path.exists('output'):
    os.makedirs('output')
interp_data.to_excel(output_file, index=False)
print(f"\nSaved interpolated data to {output_file}")

# After interpolation, check the ranges
print(f"\nValue ranges after processing:")
print(f"Revenue Growth range: {interp_data['Revenue Growth (%)'].min():.1f}% to {interp_data['Revenue Growth (%)'].max():.1f}%")
print(f"EBITDA Margin range: {interp_data['EBITDA Margin (%)'].min():.1f}% to {interp_data['EBITDA Margin (%)'].max():.1f}%")

# Cap extreme values for better visualization
interp_data['Revenue Growth (%)'] = interp_data['Revenue Growth (%)'].clip(-30, 100)
interp_data['EBITDA Margin (%)'] = interp_data['EBITDA Margin (%)'].clip(-50, 50)

# Replace Inf values with NaN and drop rows with NaN in key columns
interp_data.replace([np.inf, -np.inf], np.nan, inplace=True)
interp_data.dropna(subset=['EBITDA Margin (%)', 'Revenue Growth (%)'], inplace=True)

# Define the list of companies to display
selected_companies = [
    'ABNB',        # Airbnb
    'BKNG',        # Booking.com
    'DESP',        # Despegar
    'EaseMyTrip',  # EaseMyTrip
    'EDR',         # Edreams
    'EXPE',        # Expedia
    'LMN',         # Lastminute
    'OWW',         # Orbitz
    'SEERA',       # Seera Group
    'TCOM',        # Trip.com
    'TRIP',        # TripAdvisor
    'TRVG',        # Trivago
    'WEB',         # Webjet
    'YTRA'         # Yatra.com
]

# Manually create the dictionary for colors
color_dict = {
    'ABNB': '#ff5895',
    'BKNG': '#003480',
    'PCLN': '#003480',  # 使用和 BKNG 相同的颜色
    'DESP': '#755bd8',
    'EaseMyTrip': '#00a0e2',
    'EDR': '#2577e3',
    'LMN': '#fc03b1',
    'SEERA': '#750808',
    'TCOM': '#2577e3',
    'TRIP': '#00af87',
    'TRVG': '#c71585',
    'WEB': '#fa8072',
    'YTRA': '#800080',
    'Almosafer': '#bb5387',
    'EXPE': '#fbcc33',
    'IXIGO': '#e63946',
    'MMYT': '#ff0000',
    'Wego': '#4e843d',
    'OWW': '#8edbfa',
    'Travelocity': '#1d3e5c',
    'Traveloka': '#008080',
    'Cleartrip': '#4169e1',
    'FLT': '#ff4500',
    'Webjet': '#4682b4',
    'Webjet OTA': '#4682b4',
    'FlightCentre': '#ff4500',
    'Etraveli': '#2e8b57',
    'Kiwi': '#32cd32',
    'Skyscanner': '#00bfff'
}

# Create logo directory if it doesn't exist
if not os.path.exists(logos_dir):
    print(f"Please place company logo PNG files in the logos directory with filenames like 'ABNB_logo.png'")

# Get unique companies and prepare logo paths
unique_companies = interp_data['Company'].unique()
logos = {}

# Company name to logo filename mapping
logo_filename_map = {
    'ABNB': 'ABNB_logo.png',
    'Almosafer': 'Almosafer_logo.png',
    'BKNG': 'BKNG_logo.png',
    'DESP': 'DESP_logo.png',
    'EXPE': 'EXPE_logo.png',
    'EASEMYTRIP': 'EASEMYTRIP_logo.png',
    'IXIGO': 'IXIGO_logo.png',
    'MMYT': 'MMYT_logo.png',
    'TRIP': 'TRIP_logo.png',
    'TRVG': 'TRVG_logo.png',
    'Wego': 'Wego_logo.png',
    'YTRA': 'YTRA_logo.png',
    'TCOM': 'TCOM_logo.png',
    'EDR': 'EDR_logo.png',
    'LMN': 'LMN_logo.png',
    'WEB': 'WEB_logo.png',
    'SEERA': 'SEERA_logo.png',  # Default SEERA logo
    'PCLN': 'PCLN_logo.png',
    'OWW': 'OWW_logo.png',
    'Travelocity': 'Travelocity_logo.png',
    'Traveloka': 'Traveloka_logo.png',
    'Cleartrip': 'Cleartrip_logo.png',
    'FLT': 'FlightCentre_logo.png',
    'Webjet': 'WEB_logo.png',
    'Webjet OTA': 'WEB_logo.png',
    'FlightCentre': 'FlightCentre_logo.png',
    'Etraveli': 'Etraveli_logo.png',
    'Kiwi': 'Kiwi_logo.png',
    'Skyscanner': 'Skyscanner_logo.png'
}

# Try to load company logos, if not available, use a placeholder
for company in unique_companies:
    logo_filename = logo_filename_map.get(company)
    if logo_filename:
        logo_path = os.path.join(logos_dir, logo_filename)
    else:
        logo_path = os.path.join(logos_dir, f"{company}_logo.png")
    
    if os.path.exists(logo_path):
        try:
            logos[company] = plt.imread(logo_path)
            print(f"Successfully loaded logo for {company} from {logo_path}")
        except Exception as e:
            print(f"Error loading logo for {company}: {e}")
            # Create placeholder if loading fails
            plt.close('all')  # Close any existing figures
            fig_temp = plt.figure(figsize=(1, 1), dpi=100)
            ax_temp = fig_temp.add_subplot(111)
            ax_temp.text(0.5, 0.5, company, ha='center', va='center', fontsize=9,
                        transform=ax_temp.transAxes)
            ax_temp.axis('off')
            temp_logo_path = os.path.join(logos_dir, f"{company}_temp_logo.png")
            fig_temp.savefig(temp_logo_path, format='png', transparent=True, bbox_inches='tight', pad_inches=0)
            plt.close(fig_temp)
            logos[company] = plt.imread(temp_logo_path)
    else:
        print(f"Logo not found for {company} at {logo_path}")
        # Create a simple text-based placeholder
        plt.close('all')  # Close any existing figures
        fig_temp = plt.figure(figsize=(1, 1), dpi=100)
        ax_temp = fig_temp.add_subplot(111)
        ax_temp.text(0.5, 0.5, company, ha='center', va='center', fontsize=9,
                    transform=ax_temp.transAxes)
        ax_temp.axis('off')
        temp_logo_path = os.path.join(logos_dir, f"{company}_temp_logo.png")
        fig_temp.savefig(temp_logo_path, format='png', transparent=True, bbox_inches='tight', pad_inches=0)
        plt.close(fig_temp)
        logos[company] = plt.imread(temp_logo_path)

# 特别处理 PCLN logo
pcln_logo_path = os.path.join(logos_dir, 'PCLN_logo.png')
if os.path.exists(pcln_logo_path):
    try:
        logos['PCLN'] = plt.imread(pcln_logo_path)
        print(f"Successfully loaded PCLN logo from {pcln_logo_path}")
    except Exception as e:
        print(f"Error loading PCLN logo: {e}")
        logos['PCLN'] = logos.get('BKNG')  # 如果加载失败，使用 BKNG 的 logo
else:
    print(f"PCLN logo not found at {pcln_logo_path}")
    logos['PCLN'] = logos.get('BKNG')  # 如果文件不存在，使用 BKNG 的 logo

# Set a fixed maximum for the bar chart to ensure absolute sizes
max_revenue_value = interp_data['Revenue'].max()

# Define a list of events with timestamps (Numeric_Year) and descriptions
events = [
    (1999.25, "Mar'1999 Priceline.com lists on NASDAQ"),
    (1999.92, "Nov'1999 Expedia lists on NASDAQ"),
    (2000.25, "Mar'2000 Lastminute.com lists on LSE"),
    (2000.25, "Mar'2000 Sabre Holdings merges Travelocity with Preview Travel, owns 70%"),
    (2000.25, "Mar'2000 Dot-com bubble. NASDAQ peaks in Mar'2000 before falling 78% by Oct'2002"),
    (2000.42, "May'2000 Webjet lists on ASX"),
    (2000.50, "Jun'2000 Bookings.nl merges with Bookings Online, forming Booking.com"),
    (2001.50, "Jun'2001 Expedia acquires Hotels.com"),
    (2001.75, "Sep'2001 9/11 Terrorist attack. 20% cutback in air capacity in North America"),
    (2002.25, "Mar'2002 Sabre reacquires Travelocity's outstanding shares"),
    (2003.92, "Dec'2003 Ctrip lists on NASDAQ"),
    (2003.92, "Dec'2003 Orbitz lists on NYSE"),
    (2004.75, "Sep'2004 Orbitz taken private by Cendant Corp"),
    (2004.75, "Sep'2004 Priceline.com acquires Active Hotels for $160mil"),
    (2005.42, "May'2005 Sabre Holdings-owned Travelocity takes lastminute.com private for $1.1bn"),
    (2005.58, "Jul'2005 Priceline.com acquires Booking.com for $133mil, merging it with Active Hotels"),
    (2006.67, "Aug'2006 Cendant Corp sells Orbitz to Blackstone Group as part of Travelport deal"),
    (2007.25, "Mar'2007 Sabre Holdings taken private by TPG & Silver Lake Partners"),
    (2007.58, "Jul'2007 Orbitz lists on NYSE for the second time"),
    (2008.08, "Jan'2008 The US housing bubble leads to the Great Recession (2008-2009)"),
    (2010.58, "Jul'2010 ITA Software accepts $700mil acquisition bid by Google"),
    (2010.67, "Aug'2010 MakeMyTrip lists on NASDAQ"),
    (2011.25, "Apr'2011 US DoJ approves Google's acquisition of ITA Software, Google enters travel"),
    (2011.50, "Jun'2011 eDreams, GO Voyages and Opodo merge, forming eDreams ODIGEO"),
    (2011.92, "Dec'2011 Expedia spins off Tripadvisor, listing it on NASDAQ"),
    (2012.33, "Apr'2012 Al Tayyar Travel lists on Saudi Stock Exchange"),
    (2012.75, "Sep'2012 Traveloka starts as a metasearch, quickly pivots to an OTA model"),
    (2012.92, "Dec'2012 Expedia Group acquires 62% of Trivago"),
    (2013.42, "May'2013 Priceline.com acquires Kayak for $1.8bn"),
    (2014.25, "Apr'2014 eDreams ODIGEO lists on Madrid Stock Exchange"),
    (2014.25, "Apr'2014 Bravofly Rumbo lists on SIX Swiss Exchange"),
    (2014.25, "Apr'2014 Priceline.com rebrands as The Priceline Group"),
    (2014.92, "Dec'2014 Travelocity sells lastminute.com to Bravofly Rumbo"),
    (2014.67, "Aug'2014 ixigo expands to trains"),
    (2015.08, "Feb'2015 Expedia Group acquires Orbitz for $1.6bn & Travelocity for $280mil"),
    (2015.17, "Mar'2015 New CEO restructures Edreams ODIGEO. Subscriptions launch in 2017"),
    (2015.42, "May'2015 Bravofly Rumbo rebrands as Lastminute Group"),
    (2015.83, "Oct'2015 ProSiebenSat.1 acquires Etraveli for €235mil"),
    (2015.92, "Nov'2015 Expedia Group acquires HomeAway and VRBO for $3.9bn"),
    (2016.42, "May'2016 Skypicker rebrands to Kiwi.com"),
    (2016.75, "Sep'2016 Google launches Google Trips"),
    (2016.83, "Oct'2016 Yatra lists on NASDAQ"),
    (2016.92, "Nov'2016 Ctrip acquires Skyscanner for £1.4bn"),
    (2016.92, "Dec'2016 Trivago lists on NASDAQ. Expedia maintains majority ownership"),
    (2017.50, "Jun'2017 CVC Capital Partners acquires Etraveli for €508mil"),
    (2017.50, "Jun'2017 Booking.com pulls out of Trivago. Trivago shares lose 80% in the next 12 months"),
    (2017.58, "Jul'2017 Expedia leads 350mil Series C funding for Traveloka"),
    (2017.75, "Sep'2017 Despegar lists on NASDAQ"),
    (2018.08, "Feb'2018 The Priceline Group rebrands to Booking Holdings"),
    (2018.83, "Nov'2018 Webjet acquires Destinations of the World, boosting its bedbank business"),
    (2019.25, "Mar'2019 Airbnb acquires HotelTonight for $400m"),
    (2019.33, "Apr'2019 Al Tayyar Travel rebrands as SEERA Group"),
    (2019.42, "May'2019 Google consolidates Flights, Hotel Finder & Trips products under one interface"),
    (2019.67, "Aug'2019 Google sunsets Trips app"),
    (2019.75, "Sep'2019 Ctrip rebrands as Trip.com Group"),
    (2020.08, "Feb'2020 Start of COVID-19 pandemic. Severe travel restrictions worldwide"),
    (2020.92, "Dec'2020 Airbnb lists on NASDAQ"),
    (2021.25, "Mar'2021 EaseMyTrip lists on Bombay Stock Exchange"),
    (2021.92, "Nov'2021 Etraveli Group accepts Booking Holdings' €1.6bn takeover bid"),
    (2023.75, "Sep'2023 EC blocks Booking Holdings-Etraveli merger"),
    (2024.00, "May'2024 EC designates Booking Holdings, Google Shopping a 'gatekeeper' status"),
    (2024.05, "Jun'2024 ixigo lists on Bombay Stock Exchange"),
    (2024.10, "Aug'2024 US DoJ rules Google a monopoly in search and advertising"),
    (2024.21, "Sep'2024 Webjet's demerger splits its wholesale and consumer business")
]

# Helper functions
def get_recent_events(frame, events, max_events=3):
    """ Return the most recent max_events up to the current frame. """
    # Filter events that occurred up to the current frame
    recent_events = [event for event in events if event[0] <= frame]
    # Return only the last max_events (most recent ones)
    return recent_events[-max_events:]

def get_zoom_factor(image, desired_width, ax):
    """ Calculate the appropriate zoom factor to maintain a consistent logo size. """
    # Get the width of the current data limits on the x-axis
    data_width = ax.get_xlim()[1] - ax.get_xlim()[0]
    
    # Get the figure width in inches
    fig_width = fig.get_size_inches()[0]
    
    # Scale is the ratio of data width to figure width in inches
    scale = data_width / (fig_width * fig.dpi)
    
    # Native width of the image in pixels
    native_width_in_pixels = image.shape[1]
    
    # Calculate the zoom factor for the image to match the desired width in inches
    zoom_factor = (desired_width * fig.dpi) / (native_width_in_pixels * scale)
    
    return zoom_factor

def get_time_period(frame):
    """ Return the appropriate time period label based on the frame (year). """
    if 1997 <= frame <= 2002.99:
        return "Dot-com bubble"
    elif 2003 <= frame <= 2007.99:
        return "Dot-com recovery"
    elif 2008 <= frame <= 2009.99:
        return "Great Recession"
    elif 2010 <= frame <= 2019.99:
        return "Rise of smartphones"
    elif 2020 <= frame <= 2020.99:
        return "COVID-19 pandemic"
    elif 2021 <= frame <= 2023.99:
        return "Post-pandemic rebound"
    elif frame >= 2024:
        return "Present"
    return ""

def add_flag_images(fig, ax, events, fig_position_y=0.92, fig_position_x=0.12, fontsize=12):
    """ Add flag images next to the event text at the top of the figure. """
    
    # Ensure events are available and sorted by date
    if len(events) == 0:
        return
    
    # Determine the most recent events
    most_recent_event = events[-1]
    second_most_recent_event = events[-2] if len(events) > 1 else None
    third_most_recent_event = events[-3] if len(events) > 2 else None
    
    for i, event in enumerate(events):
        # Safely unpack event: only assign flag_path if the tuple has 3 elements
        event_date, event_text = event
        
        # Format the date and event description for alignment
        formatted_text = event_text
        
        # Modify x_position and text_y_offset to adjust the location of the text
        x_position = fig_position_x  # Use fig_position_x to control the horizontal position
        text_y_offset = fig_position_y - i * 0.04  # Vertical position based on fig_position_y

        # Determine the style based on the event's recency
        if event == most_recent_event:
            # Most recent event: fully bold and black
            fontweight = 'bold'
            text_alpha = 1.0
            color = "black"
        elif event == second_most_recent_event:
            # Second most recent event: slightly bold and slightly faded
            fontweight = 'semibold'
            text_alpha = 0.6
            color = "black"
        elif event == third_most_recent_event:
            # Third most recent event: normal weight and more faded
            fontweight = 'semibold'
            text_alpha = 0.3
            color = "black"
        else:
            # Older events: light gray and highly faded
            fontweight = 'normal'
            text_alpha = 0.3
            color = "lightgray"

        # Add the event description text with DejaVu Sans Mono font
        fig_text(x_position, text_y_offset, formatted_text, ha='left', fontsize=fontsize, 
                 color=color, alpha=text_alpha, fontweight=fontweight, fig=fig, fontproperties=deja_vu_font)

# Setup the figure and gridspec for the layout
fig = plt.figure(figsize=(19.2, 10.8), dpi=300)
gs = fig.add_gridspec(2, 2, width_ratios=[3, 1], height_ratios=[0.4, 4.5], hspace=0.15,
                     top=0.95, bottom=0.15)  # 调整height_ratios和hspace使图表上移

# Timeline spanning both columns (top row)
ax_timeline = fig.add_subplot(gs[0, :])

# Bubble chart (bottom-left)
ax = fig.add_subplot(gs[1, 0])

# Bar chart (bottom-right)
ax_barchart = fig.add_subplot(gs[1, 1])

# Change the desired width for logos to make them smaller
desired_width_in_inches = 0.002  # 减小 logo 尺寸

# After helper functions and before preview generation
# Define the update function first
def update(frame, preview=False):
    """
    更新动画帧
    frame: 当前时间点
    preview: 是否为预览模式
    """
    # Add progress indicator and debug info
    if not preview and hasattr(update, 'last_frame_time'):
        time_diff = time.time() - update.last_frame_time
        print(f"\rProcessing frame {frame:.2f} ({time_diff:.1f}s per frame)", end="", flush=True)
    update.last_frame_time = time.time()
    
    # Use the correct figure and axes based on whether this is a preview or animation
    if preview:
        current_fig = fig_preview
        current_ax = ax_preview
        current_ax_timeline = ax_timeline_preview
        current_ax_bar = ax_barchart_preview
    else:
        current_fig = fig
        current_ax = ax
        current_ax_timeline = ax_timeline
        current_ax_bar = ax_barchart
    
    # Clear the current plot
    current_ax.clear()
    current_ax_timeline.clear()
    current_ax_bar.clear()
    
    # Set symmetric axes limits for bubble chart
    current_ax.set_xlim(-60, 60)
    current_ax.set_ylim(-30, 120)

    # Filter data for the specific frame with a small time tolerance
    time_tolerance = 0.001
    yearly_data = interp_data[
        (interp_data['Numeric_Year'] >= frame - time_tolerance) & 
        (interp_data['Numeric_Year'] <= frame + time_tolerance)
    ].copy()
    
    # 处理 Lastminute 的显示逻辑
    if 2003.75 <= frame < 2014:
        # 在这个时间段内，从数据中移除 LMN
        yearly_data = yearly_data[yearly_data['Company'] != 'LMN']
    
    # 处理 EDR 的显示逻辑
    if frame < 2013:
        # 在2013年之前，从数据中移除 EDR
        yearly_data = yearly_data[yearly_data['Company'] != 'EDR']
    
    # 只保留选定的公司
    yearly_data = yearly_data[yearly_data['Company'].isin(selected_companies)]
    
    # 根据时间点修改 BKNG/PCLN 的显示
    if frame < 2018.08:  # 2018年第一季度之前
        yearly_data.loc[yearly_data['Company'] == 'BKNG', 'Company'] = 'PCLN'

    # 确保每个公司只有一个数据点，选择最接近当前frame的数据点
    if len(yearly_data) > len(yearly_data['Company'].unique()):
        yearly_data['time_diff'] = abs(yearly_data['Numeric_Year'] - frame)
        yearly_data = yearly_data.sort_values('time_diff').groupby('Company', as_index=False).first()
        yearly_data = yearly_data.drop('time_diff', axis=1)
    
    # Print debug information for the current frame
    print(f"\nData points for frame {frame:.3f}:")
    for _, row in yearly_data.iterrows():
        print(f"Company: {row['Company']}, EBITDA: {row['EBITDA Margin (%)']:.1f}, Growth: {row['Revenue Growth (%)']:.1f}, Revenue: {row['Revenue']:.1f}")

    # Ensure the correct color mapping from color_dict
    yearly_data['color'] = yearly_data.apply(lambda row: 
        '#800080' if row['Company'] == 'LMN' and frame < 2015.42 else 
        color_dict.get(row['Company'], '#808080'), axis=1)
    
    # Print debug information for companies without color mapping
    missing_colors = yearly_data[~yearly_data['Company'].isin(color_dict.keys())]['Company'].unique()
    if len(missing_colors) > 0:
        print(f"Warning: Missing colors for companies: {missing_colors}")

    # Set up the timeline (spanning across both the bubble chart and bar chart)
    current_ax_timeline.set_xlim(1998.8, 2025)  # 扩展左侧显示范围
    current_ax_timeline.set_ylim(-0.04, 0.12)
    current_ax_timeline.get_yaxis().set_visible(False)
    current_ax_timeline.spines['top'].set_visible(False)
    current_ax_timeline.spines['right'].set_visible(False)
    current_ax_timeline.spines['left'].set_visible(False)
    current_ax_timeline.spines['bottom'].set_position(('data', 0))
    current_ax_timeline.spines['bottom'].set_color('black')  # Changed back to default color
    current_ax_timeline.tick_params(axis='x', which='major', labelsize=10, colors='black')  # 改回黑色
    current_ax_timeline.xaxis.set_major_locator(MultipleLocator(1))  # 设置主刻度为1年
    current_ax_timeline.xaxis.set_minor_locator(MultipleLocator(0.25))  # 设置小刻度为季度
    current_ax_timeline.set_xticks(np.arange(1999, 2025, 1))  # 设置显示的刻度位置
    current_ax_timeline.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{int(x)}'))  # 格式化刻度标签

    # Moving marker on timeline
    marker_position = frame  # frame should represent quarters, e.g., 1998.75 for Q4 of 1998
    marker = current_ax_timeline.plot([marker_position], [0.02], marker='v', color='#4e843d', markersize=10)[0]  # 改为Wego的颜色
    artists_to_return = [marker]

    # Scatter plot for the specific year (bubble chart)
    for i, point in yearly_data.iterrows():
        # Scale the bubble size based on the revenue, and ensure a minimum size for OWW
        bubble_size = max((point['Revenue'] / max_revenue_value) * 1500, 50)
        if point['Company'] == 'OWW' and point['Revenue'] == 0:
            bubble_size = 50  # Minimum size for OWW when revenue is zero

        # Plot the colored dot for each company
        dot = current_ax.scatter(
            x=point['EBITDA Margin (%)'],
            y=point['Revenue Growth (%)'],
            color=point['color'],
            s=bubble_size,
            alpha=0.8,
            edgecolors="white", 
            linewidths=2,
            zorder=2
        )
        artists_to_return.append(dot)
        
        # Add logos
        if point['Company'] in logos:
            # 根据时间点选择正确的logo
            if point['Company'] == 'PCLN':
                print(f"Displaying PCLN logo at frame {frame}")
                if 2014.25 <= frame < 2018.08:  # 2014年第二季度到2018年第一季度之前
                    logo_path = os.path.join(logos_dir, '1PCLN_logo.png')
                    if os.path.exists(logo_path):
                        image_path = plt.imread(logo_path)
                        print(f"Using 1PCLN logo at frame {frame}")
                    else:
                        print(f"Warning: 1PCLN logo not found at {logo_path}")
                        image_path = logos['PCLN']
                else:
                    image_path = logos['PCLN']
            elif point['Company'] == 'SEERA':
                if frame < 2019:
                    image_path = plt.imread(os.path.join(logos_dir, '1SEERA_logo.png'))
                else:
                    image_path = logos['SEERA']
            elif point['Company'] == 'LMN':
                if frame < 2015.42 and frame > 2004:  # 2015年第二季度之前
                    image_path = plt.imread(os.path.join(logos_dir, '1LMN_logo.png'))
                else:
                    image_path = logos['LMN']
            elif point['Company'] == 'TRIP':
                if frame < 2020:
                    image_path = plt.imread(os.path.join(logos_dir, ' TRIP_logo.png'))
                else:
                    image_path = logos['TRIP']
            elif point['Company'] == 'TCOM':
                if frame < 2019.50:
                    image_path = plt.imread(os.path.join(logos_dir, ' TCOM_logo.png'))
                else:
                    image_path = logos['TCOM']
            else:
                image_path = logos[point['Company']]
            
            base_zoom = get_zoom_factor(image_path, desired_width_in_inches, current_ax)
            relative_size = (point['Revenue'] / max_revenue_value) ** 0.5
            zoom_factor = base_zoom * (0.8 + 0.4 * relative_size)
            
            imagebox = OffsetImage(image_path, zoom=zoom_factor)
            # Special y_offset for BKNG/PCLN
            y_offset = 9 if point['Company'] in ['BKNG', 'PCLN'] and frame >= 2018.08 else 5
            ab = AnnotationBbox(imagebox, 
                              (float(point['EBITDA Margin (%)']), float(point['Revenue Growth (%)']) + y_offset),
                              frameon=False,
                              box_alignment=(0.5, 0.5),
                              zorder=3)
            current_ax.add_artist(ab)
            artists_to_return.append(ab)

    # Adjust spines to put zero in the middle for the bubble chart
    current_ax.spines['left'].set_position('zero')
    current_ax.spines['bottom'].set_position('zero')
    current_ax.spines['right'].set_visible(False)
    current_ax.spines['top'].set_visible(False)
    current_ax.spines['left'].set_color('#4e843d')  # Changed to Wego's color
    current_ax.spines['left'].set_linestyle('solid')  # Changed from dashed to solid
    current_ax.spines['bottom'].set_color('#4e843d')  # Changed to Wego's color
    current_ax.spines['bottom'].set_linestyle('solid')  # Changed from dashed to solid

    # Custom formatting for axes in the bubble chart
    current_ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{x:.0f}%'))
    current_ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _: f'{y:.0f}%'))
    current_ax.tick_params(axis='x', which='both', labelsize=10, colors='#4e843d')  # Changed tick color
    current_ax.tick_params(axis='y', which='both', labelsize=10, colors='#4e843d')  # Changed tick color

    for label in current_ax.get_xticklabels():
        label.set_fontproperties(open_sans_font)

    for label in current_ax.get_yticklabels():
        label.set_fontproperties(open_sans_font)

    time_period_label = get_time_period(frame)
    
    # Add background text directly to the axes, using zorder to place it behind the bubbles
    current_ax.text(
        0.485, 0.45, time_period_label, transform=current_ax.transAxes, fontsize=50, 
        color="lightgrey", alpha=0.8, ha='center', fontproperties=open_sans_font, zorder=1
    )

    # Static secondary axes for the bubble chart
    ax2_x = current_ax.secondary_xaxis('bottom')
    ax2_y = current_ax.secondary_yaxis('left')
    ax2_x.xaxis.set_major_locator(MultipleLocator(10))
    ax2_x.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{x:.0f}%'))
    ax2_y.yaxis.set_major_formatter(FuncFormatter(lambda y, _: f'{y:.0f}%'))
    
    # Set the tick labels on the secondary x-axis and y-axis to use Open Sans font
    for label in ax2_x.get_xticklabels():
        label.set_fontproperties(open_sans_font)
    for label in ax2_y.get_yticklabels():
        label.set_fontproperties(open_sans_font)

    # Set axis labels using Open Sans font
    current_ax.set_xlabel("EBITDA Margin TTM (%)", horizontalalignment='center', x=0.5, labelpad=140, fontproperties=open_sans_font, fontsize=14)
    current_ax.set_ylabel("Revenue Growth TTM (%)", verticalalignment='center', y=0.5, labelpad=30, fontproperties=open_sans_font, fontsize=14)
    current_ax.spines['left'].set_position('zero')
    current_ax.yaxis.set_label_coords(-0.08, 0.5)
    # Hide ticks on the axes crossing at zero in the bubble chart


    # Hide ticks on the axes crossing at zero in the bubble chart
    current_ax.tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False)
    current_ax.tick_params(axis='y', which='both', left=False, right=False, labelleft=False)

    # Background text for data source
    fig_text(0.1, 0.03, "Data source: Company financial reports, EDGAR, Orbis, Bloomberg", ha='left', va='bottom', fontsize=9, color='black', 
        fig=current_fig, fontproperties=open_sans_font)

    fig_text(0.1, 0.01, "Note: Extreme values capped for display purposes. Revenue growth between -30% and +100%, EBITDA Margin within ±50%", 
            ha='left', va='bottom', fontsize=9, color='black', fig=current_fig, fontproperties=open_sans_font)

    # Limit the number of bars to display
    max_bars = 16

    # Set a constant height for the bars
    bar_height = 0.7

    # Filter data for companies with revenue > 0 (except OWW which we want to show in bubble chart only)
    filtered_data = yearly_data[
        (yearly_data['Revenue'] > 0) & 
        (yearly_data['Company'] != 'OWW')
    ].copy()

    # Sort the data by revenue in ascending order
    sorted_data = filtered_data.sort_values(by='Revenue', ascending=True)

    # Get the number of companies to display
    num_companies = min(len(sorted_data), max_bars)

    # Get the data for the top companies
    top_companies = sorted_data.tail(num_companies)

    # Reverse the y_positions so that the highest revenue is at the top
    y_positions = np.arange(num_companies)
    y_positions = y_positions[::-1]

    # Map company names to colors and handle missing colors
    bar_colors = [color_dict.get(company, '#808080') for company in top_companies['Company']]

    # Create horizontal bar chart
    bars = current_ax_bar.barh(
        y_positions,
        top_companies['Revenue'],
        color=bar_colors,
        height=bar_height
    )
    
    # Add all bars to the list of artists to return
    for bar in bars:
        artists_to_return.append(bar)

    # Set y-axis limits
    current_ax_bar.set_ylim(-0.5, max_bars - 0.5)

    # Add company names as y-tick labels
    current_ax_bar.set_yticks(y_positions)
    current_ax_bar.set_yticklabels(top_companies['Company'], fontproperties=open_sans_font)

    # Invert y-axis to have highest revenue at the top
    current_ax_bar.invert_yaxis()

    # Add revenue labels to the bars
    for bar, revenue in zip(bars, top_companies['Revenue']):
        width = bar.get_width()
        if width > 0:
            label = current_ax_bar.text(
                width,
                bar.get_y() + bar.get_height() / 2,
                f'{width:,.0f}',
                va='center',
                ha='left',
                fontsize=9,
                fontproperties=open_sans_font
            )
            artists_to_return.append(label)

    # Adjust aesthetics
    current_ax_bar.set_xlim(0, max_revenue_value * 1.1)
    current_ax_bar.spines['top'].set_visible(False)
    current_ax_bar.spines['right'].set_visible(False)
    current_ax_bar.spines['left'].set_visible(False)
    current_ax_bar.spines['bottom'].set_visible(False)
    current_ax_bar.tick_params(axis='y', which='both', length=0)
    current_ax_bar.tick_params(axis='x', which='both', bottom=False, labelbottom=False)
    current_ax_bar.set_xlabel('Revenue TTM (in Millions)', fontsize=14, fontproperties=open_sans_font, labelpad=33)

    # Return all artists that need to be updated
    return artists_to_return

# Before animation, generate preview images for each quarter
print("\nGenerating preview images for each quarter...")
preview_dir = os.path.join(output_dir, 'previews')
if not os.path.exists(preview_dir):
    os.makedirs(preview_dir)

# Get all unique quarters from original data (not interpolated)
all_quarters = np.unique(data[data['Numeric_Year'] >= 1999]['Numeric_Year'])
print(f"\nGenerating previews for {len(all_quarters)} quarters...")

# Generate preview for each quarter
for quarter in all_quarters:
    print(f"\nGenerating preview for Q{int((quarter % 1) * 4 + 1)}'{int(quarter)}")
    
    # Create preview figure and axes
    fig_preview = plt.figure(figsize=(19.2, 10.8), dpi=100)
    gs_preview = fig_preview.add_gridspec(2, 2, width_ratios=[3, 1], height_ratios=[0.4, 4.5], hspace=0.15,
                                        top=0.95, bottom=0.15)
    ax_timeline_preview = fig_preview.add_subplot(gs_preview[0, :])
    ax_preview = fig_preview.add_subplot(gs_preview[1, 0])
    ax_barchart_preview = fig_preview.add_subplot(gs_preview[1, 1])

    # Set current figure and axes for the update function
    current_fig = fig_preview
    current_ax = ax_preview
    current_ax_timeline = ax_timeline_preview
    current_ax_bar = ax_barchart_preview

    # Update the visualization for this quarter
    update(quarter, preview=True)

    # Save preview
    quarter_str = f"{int(quarter)}_{int((quarter % 1) * 4 + 1)}"  # Changed format to put year first
    preview_path = os.path.join(preview_dir, f'preview_{quarter_str}.png')
    plt.savefig(preview_path)
    plt.close(fig_preview)
    print(f"Preview saved as {preview_path}")

print("\nAll quarter previews generated. Starting animation generation...")
print("This may take a while depending on the number of frames...")
total_frames = len(all_quarters)
print(f"Total frames to generate: {total_frames}")

# Create main figure and axes for animation
fig = plt.figure(figsize=(19.2, 10.8), dpi=300)
gs = fig.add_gridspec(2, 2, width_ratios=[3, 1], height_ratios=[0.4, 4.5], hspace=0.15,
                     top=0.95, bottom=0.15)  # 调整height_ratios和hspace使图表上移
ax_timeline = fig.add_subplot(gs[0, :])
ax = fig.add_subplot(gs[1, 0])
ax_barchart = fig.add_subplot(gs[1, 1])

# Before animation
print("\nStarting animation generation...")
print("This may take a while depending on the number of frames...")
total_frames = len(np.unique(interp_data['Numeric_Year']))
print(f"Total frames to generate: {total_frames}")

# Create the animation using FuncAnimation
ani = FuncAnimation(fig, lambda frame: update(frame, preview=False), 
                   frames=np.unique(interp_data[interp_data['Numeric_Year'] >= 1999]['Numeric_Year']), 
                   repeat=False, blit=True,  # 改回 True 以提高性能
                   interval=50)  # 调整帧间隔

# Before saving animation
print("\nSaving animation...")
start_time = time.time()

# Save the animation with higher bitrate and fps
ani.save('output/evolution_of_online_travel.mp4', 
         writer='ffmpeg',
         fps=24,  # 增加帧率
         bitrate=5000)  # 增加比特率，提高视频质量

# After saving animation
end_time = time.time()
total_time = end_time - start_time
print(f"\nAnimation saved successfully!")
print(f"Total time: {total_time:.1f} seconds")

# Show the animation
plt.show()