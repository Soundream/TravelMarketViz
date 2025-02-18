import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.regression.linear_model import OLS
from statsmodels.tools import add_constant

def load_data(file_path):
    """Load data from Excel file's Summary sheet"""
    # Read the Excel file
    df = pd.read_excel(file_path, sheet_name='Summary')
    
    # Print unique values in each column to understand the data structure
    print("\nData Structure Analysis:")
    for col in ['Data Level', 'Region', 'Market', 'Channel Type', 'Breakdown']:
        print(f"\nUnique values in {col}:")
        print(df[col].unique())
    
    # Filter for the appropriate level of data (e.g., only use the highest level to avoid double counting)
    # Group by Year and sum the bookings
    df_grouped = df.groupby(['Year', 'Data Level', 'Region', 'Channel Type', 'Breakdown'])['Total Market Gross Bookings'].sum().reset_index()
    
    # Print the grouped data to understand the structure
    print("\nGrouped Data Sample:")
    print(df_grouped.head())
    
    # Get the final yearly totals
    final_data = df_grouped.groupby('Year')['Total Market Gross Bookings'].sum().reset_index()
    
    return final_data

def prepare_data(data, crisis_year=2009):
    """Prepare data for segmented regression"""
    # Create time variable (t)
    data['t'] = data['Year'] - data['Year'].min() + 1
    
    # Create dummy variable for crisis period
    data['D'] = (data['Year'] >= crisis_year).astype(int)
    
    # Create interaction term for trend change after crisis
    data['t_D'] = data['t'] * data['D']
    
    return data

def fit_segmented_regression(data, y_column='Total Market Gross Bookings'):
    """Fit segmented regression model"""
    # Create design matrix with time trend and post-crisis trend change
    X = data[['t', 't_D']].copy()
    X = add_constant(X)
    
    # Prepare y vector
    y = data[y_column]
    
    # Fit model
    model = OLS(y, X).fit()
    
    return model

def predict_historical(model, years, min_year, crisis_year=2009):
    """Generate predictions for historical period"""
    # Create prediction data
    pred_data = pd.DataFrame({'Year': years})
    pred_data['t'] = pred_data['Year'] - min_year + 1
    pred_data['D'] = (pred_data['Year'] >= crisis_year).astype(int)
    pred_data['t_D'] = pred_data['t'] * pred_data['D']
    
    # Create design matrix for prediction
    X_pred = add_constant(pred_data[['t', 't_D']])
    
    # Generate predictions
    predictions = model.predict(X_pred)
    
    return pd.DataFrame({'Year': years, 'Predicted_Bookings': predictions})

def visualize_results(original_data, predictions, y_column='Total Market Gross Bookings'):
    """Create visualization of the results"""
    plt.figure(figsize=(12, 8))
    
    # Plot original data points
    plt.scatter(original_data['Year'], original_data[y_column], 
                color='blue', label='Actual Data', alpha=0.6)
    
    # Plot predictions
    plt.plot(predictions['Year'], predictions['Predicted_Bookings'], 
             color='red', label='Predicted Values', linestyle='--')
    
    # Add vertical line for crisis year
    plt.axvline(x=2009, color='gray', linestyle=':', label='Base Year (2009)')
    
    plt.title('Global Travel Market Bookings: Actual vs Predicted\nSegmented Regression Analysis')
    plt.xlabel('Year')
    plt.ylabel('Total Market Gross Bookings (USD)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Format y-axis to show billions
    current_values = plt.gca().get_yticks()
    plt.gca().set_yticklabels(['${:.1f}B'.format(x/1e9) for x in current_values])
    
    # Save plot
    plt.savefig('regression_analysis.png', dpi=300, bbox_inches='tight')
    plt.close()

def main():
    # Load data
    data = load_data('wit/web_region_bubble/travel_market_summary.xlsx')
    
    # Print the loaded data
    print("\nLoaded Data:")
    print(data)
    
    # Prepare data
    prepared_data = prepare_data(data)
    
    # Print prepared data
    print("\nPrepared Data:")
    print(prepared_data)
    
    # Fit model
    model = fit_segmented_regression(prepared_data)
    
    # Print model summary
    print("\nModel Summary:")
    print(model.summary())
    
    # Generate predictions for 2005-2009
    historical_years = range(2005, 2010)
    predictions = predict_historical(model, historical_years, data['Year'].min())
    
    # Print predictions
    print("\nPredicted Values for 2005-2009:")
    print(predictions)
    
    # Visualize results
    visualize_results(data, predictions)
    
    print("\nVisualization has been saved as 'regression_analysis.png'")

if __name__ == "__main__":
    main() 