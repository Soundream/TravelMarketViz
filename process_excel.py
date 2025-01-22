import pandas as pd
import numpy as np

# Read the Excel file
excel_file = "Animated Bubble Chart_ Historic Financials Online Travel Industry.xlsx"
sheet_name = "Quarterly Revenue&EBITDA"

# Read the specific sheet
df = pd.read_excel(excel_file, sheet_name=sheet_name)

# Print debug information
print(f"Total rows in dataframe: {len(df)}")
print(f"Columns in dataframe: {df.columns.tolist()}")
print("\nChecking data around row 114:")
# Print a few rows before and after row 114 for the first few columns
print(df.iloc[110:115, :3].to_string())  # Show rows 111-115 for first 3 columns

# Function to calculate average of previous 4 rows if no null values
def calculate_average(series, row_index):
    if row_index < 4:
        return None
    
    previous_4_values = series[row_index-4:row_index]
    if previous_4_values.isna().any():
        return None
    
    return previous_4_values.mean()

# Process row 112 (2024'Q4) using previous 4 rows
row_index = 111  # Python is 0-based, so row 112 is index 111

# Create a new row for averages
new_row = pd.Series(index=df.columns)
new_row.iloc[0] = "2024'Q4"  # First column label

# For each column except the first one
for column in df.columns[1:]:
    avg_value = calculate_average(df[column], row_index)
    
    if pd.notna(avg_value):
        # Format as currency with commas and dollar sign
        formatted_value = f"${avg_value:,.0f}"
        print(f"Column {column}: {formatted_value}")
        new_row[column] = formatted_value
    else:
        print(f"Column {column}: blank (contains null values in previous 4 rows)")
        new_row[column] = ""

# Insert the new row at position 111 (row 112)
df_result = pd.concat([df.iloc[:row_index], 
                      pd.DataFrame([new_row], columns=df.columns), 
                      df.iloc[row_index:]]).reset_index(drop=True)

# Save to a new Excel file
output_file = "processed_data.xlsx"
df_result.to_excel(output_file, index=False)
print(f"\nResults have been saved to {output_file}") 