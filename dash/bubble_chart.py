from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go

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
        
        # Add company colors and logos
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

        logo_dict = {
            'ABNB': '../logos/ABNB_logo.png',
            'BKNG': '../logos/BKNG_logo.png',
            'EXPE': '../logos/EXPE_logo.png',
            'TCOM': '../logos/TCOM_logo.png',
            'TRIP': '../logos/TRIP_logo.png',
            'TRVG': '../logos/TRVG_logo.png',
            'EDR': '../logos/EDR_logo.png',
            'DESP': '../logos/DESP_logo.png',
            'MMYT': '../logos/MMYT_logo.png',
            'Ixigo': '../logos/IXIGO_logo.png',
            'SEERA': '../logos/SEERA_logo.png',
            'Webjet': '../logos/WEB_logo.png',
            'LMN': '../logos/LMN_logo.png',
            'Yatra': '../logos/YTRA_logo.png',
            'EaseMyTrip': '../logos/EASEMYTRIP_logo.png',
            'Wego': '../logos/Wego_logo.png',
            'Almosafer': '../logos/Almosafer_logo.png'
        }

        company_names = {
            'ABNB': 'Airbnb',
            'BKNG': 'Booking.com',
            'EXPE': 'Expedia',
            'TCOM': 'Trip.com',
            'TRIP': 'TripAdvisor',
            'TRVG': 'Trivago',
            'EDR': 'Edreams',
            'DESP': 'Despegar',
            'MMYT': 'MakeMyTrip',
            'Ixigo': 'Ixigo',
            'SEERA': 'Seera Group',
            'Webjet': 'Webjet',
            'LMN': 'Lastminute',
            'Yatra': 'Yatra.com',
            'EaseMyTrip': 'EaseMyTrip',
            'Wego': 'Wego',
            'Almosafer': 'Almosafer'
        }
        
        df['color'] = df['company'].map(color_dict)
        df['logo'] = df['company'].map(logo_dict)
        df['company_name'] = df['company'].map(company_names)
        
        return df, quarters
        
    except Exception as e:
        print(f'Error processing file: {e}')
        return None, None

# Get initial data
df, quarters = process_excel_file()
quarters_sorted = sorted(quarters)
quarter_marks = {i: q for i, q in enumerate(quarters_sorted)}

# Define the app layout
app.layout = html.Div([
    html.H1('Travel Market Visualization', style={'textAlign': 'center'}),
    
    # The graph
    dcc.Graph(id='bubble-chart'),
    
    # Year slider
    dcc.Slider(
        id='year-slider',
        min=0,
        max=len(quarters_sorted)-1,
        step=1,
        value=0,
        marks=quarter_marks
    )
])

@app.callback(
    Output('bubble-chart', 'figure'),
    Input('year-slider', 'value')
)
def update_figure(selected_year_index):
    if df is None or selected_year_index is None:
        return {}
    
    selected_quarter = quarters_sorted[selected_year_index]
    filtered_df = df[df['year'] == selected_quarter]
    
    # Create the bubble chart using graph_objects for more control
    fig = go.Figure()

    # Add scatter plot
    fig.add_trace(
        go.Scatter(
            x=filtered_df['ebitda_margin'],
            y=filtered_df['revenue_growth'],
            mode='markers',
            marker=dict(
                size=40,
                color=filtered_df['color'],
                line=dict(width=2, color='white')
            ),
            text=filtered_df['company_name'],
            hovertemplate=(
                "<img src='%{customdata[0]}' width='100'><br>" +
                "<b>%{text}</b><br>" +
                "EBITDA Margin: %{x:.1%}<br>" +
                "Revenue Growth: %{y:.1%}<br>" +
                "<extra></extra>"
            ),
            customdata=filtered_df[['logo']].values
        )
    )
    
    # Update layout
    fig.update_layout(
        title=f'Quarter: {selected_quarter}',
        xaxis=dict(
            title='EBITDA Margin',
            tickformat='.0%',
            range=[-0.7, 1.2],
            showgrid=True,
            zeroline=True,
            zerolinecolor='#ccc',
            zerolinewidth=1
        ),
        yaxis=dict(
            title='Revenue Growth YoY',
            tickformat='.0%',
            range=[-0.3, 1.2],
            showgrid=True,
            zeroline=True,
            zerolinecolor='#ccc',
            zerolinewidth=1
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        showlegend=False,
        height=840,
        hoverlabel=dict(
            bgcolor="white",
            font_size=14,
            font_family="Arial"
        )
    )

    return fig

if __name__ == '__main__':
    app.run_server(debug=True) 