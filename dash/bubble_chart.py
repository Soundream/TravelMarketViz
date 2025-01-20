from dash import Dash, dcc, html, Input, Output, State, callback_context
import plotly.express as px
import pandas as pd

# Initialize the Dash app
app = Dash(__name__)

def process_excel_file():
    try:
        # Read the Excel file directly from root folder
        df_raw = pd.read_excel('Animated Bubble Chart_ Historic Financials Online Travel Industry.xlsx', 
                             sheet_name='TTM (bounded)', 
                             header=0)
        
        # Process the data similar to Vue implementation
        # First part is revenue growth (rows 2-113)
        revenue_growth = df_raw.iloc[1:113].copy()
        # Second part is EBITDA margin (rows 116 onwards)
        ebitda_margin = df_raw.iloc[115:].copy()
        
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
            
            for company in companies:
                try:
                    rev_growth = quarter_revenue[company].iloc[0]
                    ebitda_marg = quarter_ebitda[company].iloc[0]
                    
                    # Check if values are within domain ranges (-0.7 to 1.2 for EBITDA, -0.3 to 1.2 for Revenue)
                    if (-0.7 <= ebitda_marg <= 1.2) and (-0.3 <= rev_growth <= 1.2):
                        processed_data.append({
                            'year': quarter,
                            'company': company,
                            'ebitda_margin': ebitda_marg,
                            'revenue_growth': rev_growth
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
third_point = len(quarters_sorted) // 3
two_thirds_point = 2 * third_point

# Create marks for three sliders
first_third_marks = {i: {'label': q, 'style': {'transform': 'rotate(45deg)'}} 
                    for i, q in enumerate(quarters_sorted[:third_point])}
second_third_marks = {i: {'label': q, 'style': {'transform': 'rotate(45deg)'}} 
                     for i, q in enumerate(quarters_sorted[third_point:two_thirds_point])}
last_third_marks = {i: {'label': q, 'style': {'transform': 'rotate(45deg)'}} 
                   for i, q in enumerate(quarters_sorted[two_thirds_point:])}

# Define the app layout
app.layout = html.Div([
    html.H1('Travel Market Visualization', style={'textAlign': 'center'}),
    
    # The graph
    dcc.Graph(id='bubble-chart'),
    
    # Container for sliders
    html.Div([
        # First third slider
        html.Div([
            dcc.Slider(
                id='slider-first-third',
                min=0,
                max=third_point-1,
                step=1,
                value=0,
                marks=first_third_marks
            )
        ], style={'margin-bottom': '40px'}),
        
        # Second third slider
        html.Div([
            dcc.Slider(
                id='slider-second-third',
                min=0,
                max=third_point-1,
                step=1,
                value=0,
                marks=second_third_marks
            )
        ], style={'margin-bottom': '40px'}),
        
        # Last third slider
        html.Div([
            dcc.Slider(
                id='slider-last-third',
                min=0,
                max=len(quarters_sorted[two_thirds_point:])-1,
                step=1,
                value=0,
                marks=last_third_marks
            )
        ])
    ], style={'padding': '20px 0px 50px 0px'})
])

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
    # Determine which slider triggered the callback
    trigger_id = callback_context.triggered[0]['prop_id'].split('.')[0]
    
    if trigger_id == 'slider-first-third':
        return first_value, 0, 0
    elif trigger_id == 'slider-second-third':
        return 0, second_value, 0
    else:
        return 0, 0, last_value

@app.callback(
    Output('bubble-chart', 'figure'),
    [Input('slider-first-third', 'value'),
     Input('slider-second-third', 'value'),
     Input('slider-last-third', 'value')]
)
def update_figure(first_value, second_value, last_value):
    if df is None:
        return {}
    
    # Determine which slider is active (non-zero)
    if first_value > 0:
        selected_quarter = quarters_sorted[first_value]
    elif second_value > 0:
        selected_quarter = quarters_sorted[third_point + second_value]
    else:
        selected_quarter = quarters_sorted[two_thirds_point + last_value]
    
    filtered_df = df[df['year'] == selected_quarter]
    
    # Create the bubble chart
    fig = px.scatter(
        filtered_df,
        x='ebitda_margin',
        y='revenue_growth',
        color='company',
        color_discrete_sequence=filtered_df['color'].unique(),
        hover_name='company',
        size=[40] * len(filtered_df),  # Fixed size for now
        size_max=50,
        labels={
            'ebitda_margin': 'EBITDA Margin',
            'revenue_growth': 'Revenue Growth YoY'
        },
        title=f'Quarter: {selected_quarter}'
    )
    
    # Update layout
    fig.update_layout(
        xaxis=dict(
            title='EBITDA Margin',
            tickformat='.0%',
            range=[-0.7, 1.2],  # Same range as Vue chart
            showgrid=True,
            zeroline=True,
            zerolinecolor='#ccc',
            zerolinewidth=1
        ),
        yaxis=dict(
            title='Revenue Growth YoY',
            tickformat='.0%',
            range=[-0.3, 1.2],  # Same range as Vue chart
            showgrid=True,
            zeroline=True,
            zerolinecolor='#ccc',
            zerolinewidth=1
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        showlegend=True,
        height=840  # Same height as Vue chart
    )

    return fig

if __name__ == '__main__':
    app.run_server(debug=True) 