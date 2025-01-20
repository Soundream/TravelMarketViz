from dash import Dash, dcc, html, Input, Output, State, callback_context
import plotly.express as px
import pandas as pd
import numpy as np

app = Dash(__name__)

company_names = {
    "ABNB": "Airbnb",
    "BKNG": "Booking.com",
    "EXPE": "Expedia",
    "TCOM": "Trip.com",
    "TRIP": "TripAdvisor",
    "TRVG": "Trivago",
    "EDR": "Edreams",
    "DESP": "Despegar",
    "MMYT": "MakeMyTrip",
    "Ixigo": "Ixigo",
    "SEERA": "Seera Group",
    "Webjet": "Webjet",
    "LMN": "Lastminute",
    "Yatra": "Yatra.com",
    "Orbitz": "Orbitz",
    "Travelocity": "Travelocity",
    "EaseMyTrip": "EaseMyTrip",
    "Wego": "Wego",
    "Skyscanner": "Skyscanner",
    "Etraveli": "Etraveli",
    "Kiwi": "Kiwi",
    "Cleartrip": "Cleartrip",
    "FLT": "Flight Centre",
    "Almosafer": "Almosafer",
    "Traveloka": "Traveloka",
    "Webjet OTA": "Webjet OTA"
}

# Update color dictionary
color_dict = {
    'ABNB': '#ff5895',
    'Almosafer': '#ba0d86',
    'BKNG': '#003480',
    'DESP': '#755bd8',
    'EXPE': '#fbcc33',
    'EaseMyTrip': '#00a0e2',
    'Ixigo': '#e74c3c',
    'MMYT': '#e74c3c',
    'TRIP': '#00af87',
    'TRVG': '#e74c3c',
    'Wego': '#4e843d',
    'Yatra': '#e74c3c',
    'TCOM': '#2577e3',
    'EDR': '#2577e3',
    'LMN': '#fc03b1',
    'Webjet': '#e74c3c',
    'SEERA': '#750808',
    'PCLN': '#003480',
    'Orbitz': '#8edbfa',
    'Travelocity': '#1d3e5c',
    'Skyscanner': '#0770e3',
    'Etraveli': '#b2e9ff',
    'Kiwi': '#e5fdd4',
    'Cleartrip': '#e74c3c',
    'Traveloka': '#38a0e2',
    'FLT': '#d2b6a8',
    'Webjet OTA': '#e74c3c'
}

def process_excel_file():
    try:
        # Read both sheets from the Excel file
        df_raw = pd.read_excel('Animated Bubble Chart_ Historic Financials Online Travel Industry.xlsx', 
                             sheet_name='TTM (bounded)', 
                             header=0)
        
        df_revenue = pd.read_excel('Animated Bubble Chart_ Historic Financials Online Travel Industry.xlsx',
                                 sheet_name='Quarterly Revenue&EBITDA',
                                 header=0)
        
        revenue_growth = df_raw.iloc[1:113].copy()
        ebitda_margin = df_raw.iloc[115:].copy()
        quarterly_revenue = df_revenue.iloc[2:113].copy()
        
        quarters = revenue_growth.iloc[:, 0].dropna().unique()
        
        companies = df_raw.columns[1:]
        
        processed_data = []
        
        for quarter in quarters:
            quarter_revenue = revenue_growth[revenue_growth.iloc[:, 0] == quarter].iloc[:, 1:]
            quarter_ebitda = ebitda_margin[ebitda_margin.iloc[:, 0] == quarter].iloc[:, 1:]
            
            raw_revenue = quarterly_revenue[quarterly_revenue.iloc[:, 0] == quarter].iloc[:, 1:]
            
            quarter_revenues = raw_revenue.values.flatten()
            quarter_revenues = quarter_revenues[~np.isnan(quarter_revenues)]  
            
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
                    
                    if pd.notna(raw_rev) and raw_rev > 0:
                        normalized_size = np.log(raw_rev / revenue_min) / np.log(revenue_max / revenue_min)
                        bubble_size = 20 + normalized_size * 80
                    else:
                        bubble_size = 20  
                    
                    if (-0.7 <= ebitda_marg <= 1.2) and (-0.3 <= rev_growth <= 1.2):
                        processed_data.append({
                            'year': quarter,
                            'company': company,
                            'company_full_name': company_names.get(company, company), 
                            'ebitda_margin': ebitda_marg,
                            'revenue_growth': rev_growth,
                            'revenue': raw_rev,
                            'size': bubble_size
                        })
                except:
                    continue
        
        # Convert to DataFrame
        df = pd.DataFrame(processed_data)
        
        # Add colors
        df['color'] = df['company'].map(color_dict)
        
        return df, quarters
        
    except Exception as e:
        print(f'Error processing file: {e}')
        return None, None

df, quarters = process_excel_file()
quarters_sorted = sorted(quarters)

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

app.layout = html.Div([
    html.H1('Travel Market Visualization', style={'textAlign': 'center'}),
    
    dcc.Graph(id='bubble-chart', style={'height': '600px'}),  
    
    html.Div([
        html.Div(id='quarter-display', style={
            'textAlign': 'center',
            'fontSize': '18px',
            'margin': '10px 0'
        }),
        
        dcc.Slider(
            id='quarter-slider',
            min=0,
            max=len(quarters_sorted)-1,
            step=1,
            value=0,
            marks=None, 
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
        color='company_full_name',  # Use full name for legend
        hover_name='company_full_name',
        size='size',
        hover_data={
            'company': False,
            'revenue': True,
            'ebitda_margin': ':.1%',
            'revenue_growth': ':.1%'
        },
        labels={
            'ebitda_margin': 'EBITDA Margin',
            'revenue_growth': 'Revenue Growth YoY',
            'revenue': 'Revenue',
            'company_full_name': 'Company'  # Legend label
        }
    )
    
    for i, company in enumerate(filtered_df['company']):
        fig.data[i].marker.color = color_dict[company]
    
    fig.update_layout(
        xaxis=dict(
            title='EBITDA Margin',
            tickformat='.0%',
            range=[-1.0, 1.5],
            showgrid=True,
            zeroline=True,
            zerolinecolor='#ccc',
            zerolinewidth=1
        ),
        yaxis=dict(
            title='Revenue Growth YoY',
            tickformat='.0%',
            range=[-0.5, 1.5],
            showgrid=True,
            zeroline=True,
            zerolinecolor='#ccc',
            zerolinewidth=1
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        showlegend=True,
        margin=dict(l=50, r=50, t=30, b=50),
        height=600,
        legend=dict(
            itemsizing='constant',  # Make legend markers the same size
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=1.02
        )
    )

    return fig

if __name__ == '__main__':
    app.run_server(debug=True) 