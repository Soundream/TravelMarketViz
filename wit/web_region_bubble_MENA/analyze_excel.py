import pandas as pd

# Load the Excel file
def load_excel_data(file_path):
    try:
        # Read the Excel file
        df = pd.read_excel(file_path, sheet_name=None)
        return df
    except Exception as e:
        print(f"Error loading Excel file: {e}")
        return None

# Analyze data for anomalies after 2008
def analyze_data(data):
    if not data:
        print("No data to analyze.")
        return

    # Iterate through each sheet
    for sheet_name, df in data.items():
        print(f"Analyzing sheet: {sheet_name}")
        # Filter data for years after 2008
        df_after_2008 = df[df['Year'] > 2008]
        if df_after_2008.empty:
            print("No data found for years after 2008.")
            continue

        # Check for anomalies in the data
        for index, row in df_after_2008.iterrows():
            if row['Gross Bookings'] <= 0 or row['Online Bookings'] <= 0:
                print(f"Anomaly found in row {index}: {row}")

# Main function to execute the analysis
def main():
    file_path = 'travel_market_summary.xlsx'
    data = load_excel_data(file_path)
    analyze_data(data)

# Function to print the column headers and a few rows from the 'Visualization Data' sheet
def print_visualization_data_structure(file_path):
    # Load the Excel file
    xls = pd.ExcelFile(file_path)
    
    # Load the 'Visualization Data' sheet
    df = pd.read_excel(xls, 'Visualization Data')
    
    # Print the column headers
    print("Column Headers:", df.columns.tolist())
    
    # Print the first few rows of data
    print("\nFirst few rows of data:")
    print(df.head())

# Call the function to print the structure of the 'Visualization Data' sheet
print_visualization_data_structure('travel_market_summary.xlsx')

if __name__ == "__main__":
    main() 