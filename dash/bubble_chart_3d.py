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
        
        df = pd.DataFrame(processed_data)
        
        # Add colors
        df['color'] = df['company'].map(color_dict)
        
        return df, quarters
        
    except Exception as e:
        print(f'Error processing file: {e}')
        return None, None

df, quarters = process_excel_file()
quarters_sorted = sorted(quarters)

app.layout = html.Div([
    html.H1('Travel Market 3D Visualization', style={'textAlign': 'center'}),
    dcc.Graph(id='bubble-chart', style={'height': '800px'})
])

@app.callback(
    Output('bubble-chart', 'figure'),
    Input('bubble-chart', 'id')
)
def update_figure(_):
    if df is None:
        return {}
    
    filtered_df = df.copy()
    
    # Create the 3D bubble chart
    fig = px.scatter_3d(
        filtered_df,
        x='ebitda_margin',
        y='revenue_growth',
        z='year',
        color='company_full_name',
        hover_name='company_full_name',
        size='size',
        hover_data={
            'company': False,
            'revenue': True,
            'ebitda_margin': ':.1%',
            'revenue_growth': ':.1%',
            'year': True
        },
        labels={
            'ebitda_margin': 'EBITDA Margin',
            'revenue_growth': 'Revenue Growth YoY',
            'revenue': 'Revenue',
            'company_full_name': 'Company',
            'year': 'Quarter'
        }
    )
    
    # Update marker colors and set all traces to initially hidden
    for i, company in enumerate(filtered_df['company'].unique()):
        fig.data[i].marker.color = color_dict[company]
        fig.data[i].visible = 'legendonly'  # This makes all traces hidden by default
    
    fig.update_layout(
        scene=dict(
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
            zaxis=dict(
                title='Quarter',
                showgrid=True,
                zeroline=True,
                zerolinecolor='#ccc',
                zerolinewidth=1
            ),
            camera=dict(
                eye=dict(x=1.5, y=1.5, z=1.5)
            )
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        showlegend=True,
        margin=dict(l=50, r=50, t=30, b=50),
        height=800,
        legend=dict(
            itemsizing='constant',
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=1.02
        )
    )

    return fig

if __name__ == '__main__':
    app.run_server(debug=True) 