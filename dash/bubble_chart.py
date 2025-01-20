from dash import Dash, dcc, html, Input, Output, State, callback_context
import plotly.express as px
import pandas as pd
import numpy as np

# Initialize the Dash app
app = Dash(__name__)

def process_excel_file():
    try:
        # Read both sheets from the Excel file
        df_raw = pd.read_excel('Animated Bubble Chart_ Historic Financials Online Travel Industry.xlsx', 
                             sheet_name='TTM (bounded)', 
                             header=0)
        
        df_revenue = pd.read_excel('Animated Bubble Chart_ Historic Financials Online Travel Industry.xlsx',
                                 sheet_name='Quarterly Revenue&EBITDA',
                                 header=0)
        
        # Process the TTM data similar to Vue implementation
        # First part is revenue growth (rows 2-113)
        revenue_growth = df_raw.iloc[1:113].copy()
        # Second part is EBITDA margin (rows 116 onwards)
        ebitda_margin = df_raw.iloc[115:].copy()
        
        # Process quarterly revenue data (rows 2-113)
        quarterly_revenue = df_revenue.iloc[2:113].copy()
        
        # Get all quarters (from first column)
        quarters = revenue_growth.iloc[:, 0].dropna().unique()
        
        # Get company names (from header)
        companies = df_raw.columns[1:]
        
        # Initialize processed data list
        processed_data = []
        
        # Process data for each quarter and company
        for quarter in quarters:
            quarter_revenue = revenue_growth[revenue_growth.iloc[:, 0] == quarter].iloc[:, 1:]
            quarter_ebitda = ebitda_margin[ebitda_margin.iloc[:, 0] == quarter].iloc[:, 1:]
            
            # Get quarterly revenue for size
            raw_revenue = quarterly_revenue[quarterly_revenue.iloc[:, 0] == quarter].iloc[:, 1:]
            
            # Get all revenue values for this quarter for normalization
            quarter_revenues = raw_revenue.values.flatten()
            quarter_revenues = quarter_revenues[~np.isnan(quarter_revenues)]  # Remove NaN values
            
            # Calculate min and max for normalization (excluding zeros and NaN)
            if len(quarter_revenues) > 0:
                revenue_min = np.min(quarter_revenues[quarter_revenues > 0]) if any(quarter_revenues > 0) else 1
                revenue_max = np.max(quarter_revenues) if len(quarter_revenues) > 0 else 1
            else:
                revenue_min = 1
                revenue_max = 1
            
            for company in companies:
                try:
                    rev_growth = quarter_revenue[company].iloc[0]
                    ebitda_marg = quarter_ebitda[company].iloc[0]
                    raw_rev = raw_revenue[company].iloc[0]
                    
                    # Normalize revenue for bubble size (log scale to handle large variations)
                    if pd.notna(raw_rev) and raw_rev > 0:
                        normalized_size = np.log(raw_rev / revenue_min) / np.log(revenue_max / revenue_min)
                        # Scale to reasonable bubble sizes (between 20 and 100)
                        bubble_size = 20 + normalized_size * 80
                    else:
                        bubble_size = 20  # Minimum size for companies with no revenue data
                    
                    # Check if values are within domain ranges (-0.7 to 1.2 for EBITDA, -0.3 to 1.2 for Revenue)
                    if (-0.7 <= ebitda_marg <= 1.2) and (-0.3 <= rev_growth <= 1.2):
                        processed_data.append({
                            'year': quarter,
                            'company': company,
                            'ebitda_margin': ebitda_marg,
                            'revenue_growth': rev_growth,
                            'revenue': raw_rev,
                            'size': bubble_size
                        })
                except:
                    continue
        
        # Convert to DataFrame
        df = pd.DataFrame(processed_data)
        
        # Add company colors
        color_dict = {
            'ABNB': '#ff5895',
            'BKNG': '#003480',
            'EXPE': '#fbcc33',
            'TCOM': '#2577e3',
            'TRIP': '#00af87',
            'TRVG': '#e74c3c',
            'EDR': '#2577e3',
            'DESP': '#755bd8',
            'MMYT': '#e74c3c',
            'Ixigo': '#e74c3c',
            'SEERA': '#750808',
            'Webjet': '#e74c3c',
            'LMN': '#fc03b1',
            'Yatra': '#e74c3c',
            'EaseMyTrip': '#00a0e2',
            'Wego': '#4e843d',
            'Almosafer': '#bb5387'
        }
        
        df['color'] = df['company'].map(color_dict)
        
        return df, quarters
        
    except Exception as e:
        print(f'Error processing file: {e}')
        return None, None

# Get initial data
df, quarters = process_excel_file()
quarters_sorted = sorted(quarters)

# Comment out three sliders code
'''
third_point = len(quarters_sorted) // 3
two_thirds_point = 2 * third_point

# Create marks for three sliders
first_third_marks = {i: {'label': q, 'style': {'transform': 'rotate(45deg)'}} 
                    for i, q in enumerate(quarters_sorted[:third_point])}
second_third_marks = {i: {'label': q, 'style': {'transform': 'rotate(45deg)'}} 
                     for i, q in enumerate(quarters_sorted[third_point:two_thirds_point])}
last_third_marks = {i: {'label': q, 'style': {'transform': 'rotate(45deg)'}} 
                   for i, q in enumerate(quarters_sorted[two_thirds_point:])}
'''

# Define the app layout
app.layout = html.Div([
    html.H1('Travel Market Visualization', style={'textAlign': 'center'}),
    
    # The graph
    dcc.Graph(id='bubble-chart', style={'height': '600px'}),  # Reduced height
    
    # Container for single slider
    html.Div([
        # Quarter display
        html.Div(id='quarter-display', style={
            'textAlign': 'center',
            'fontSize': '18px',
            'margin': '10px 0'
        }),
        
        # Single slider
        dcc.Slider(
            id='quarter-slider',
            min=0,
            max=len(quarters_sorted)-1,
            step=1,
            value=0,
            marks=None,  # Remove marks
            included=True
        )
    ], style={'padding': '20px 0px 50px 0px', 'margin': '0 40px'})
])

'''
# Comment out three sliders callback
@app.callback(
    [Output('slider-first-third', 'value'),
     Output('slider-second-third', 'value'),
     Output('slider-last-third', 'value')],
    [Input('slider-first-third', 'value'),
     Input('slider-second-third', 'value'),
     Input('slider-last-third', 'value')],
    [State('slider-first-third', 'value'),
     State('slider-second-third', 'value'),
     State('slider-last-third', 'value')]
)
def sync_sliders(first_value, second_value, last_value, prev_first, prev_second, prev_last):
    trigger_id = callback_context.triggered[0]['prop_id'].split('.')[0]
    
    if trigger_id == 'slider-first-third':
        return first_value, 0, 0
    elif trigger_id == 'slider-second-third':
        return third_point-1, second_value, 0
    else:
        return third_point-1, third_point-1, last_value
'''

# Add callback to update quarter display
@app.callback(
    Output('quarter-display', 'children'),
    Input('quarter-slider', 'value')
)
def update_quarter_display(slider_value):
    return f'Quarter: {quarters_sorted[slider_value]}'

@app.callback(
    Output('bubble-chart', 'figure'),
    Input('quarter-slider', 'value')
)
def update_figure(slider_value):
    if df is None:
        return {}
    
    selected_quarter = quarters_sorted[slider_value]
    filtered_df = df[df['year'] == selected_quarter]
    
    # Create the bubble chart
    fig = px.scatter(
        filtered_df,
        x='ebitda_margin',
        y='revenue_growth',
        color='company',
        color_discrete_sequence=filtered_df['color'].unique(),
        hover_name='company',
        size='size',
        hover_data=['revenue'],
        labels={
            'ebitda_margin': 'EBITDA Margin',
            'revenue_growth': 'Revenue Growth YoY',
            'revenue': 'Revenue'
        }
    )
    
    # Update layout with wider ranges
    fig.update_layout(
        xaxis=dict(
            title='EBITDA Margin',
            tickformat='.0%',
            range=[-1.0, 1.5],  # Wider range
            showgrid=True,
            zeroline=True,
            zerolinecolor='#ccc',
            zerolinewidth=1
        ),
        yaxis=dict(
            title='Revenue Growth YoY',
            tickformat='.0%',
            range=[-0.5, 1.5],  # Wider range
            showgrid=True,
            zeroline=True,
            zerolinecolor='#ccc',
            zerolinewidth=1
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        showlegend=True,
        margin=dict(l=50, r=50, t=30, b=50),  # Reduced margins
        height=600  # Reduced height
    )

    return fig

if __name__ == '__main__':
    app.run_server(debug=True) 