#!/usr/bin/env python
import subprocess
import os
import webbrowser

def main():
    """Run the Plotly visualization and open it in the default browser"""
    
    # Define output path
    output_path = 'output/airline_revenue_plotly.html'
    
    # Create directory if it doesn't exist
    os.makedirs('output', exist_ok=True)
    
    # Run the visualization script
    print("Generating the Plotly visualization...")
    
    subprocess.run([
        'python3', 'airline_plotly_viz.py',
        '--output', output_path,
        '--frames-per-year', '0',
        '--height', '800',
        '--width', '1300',
        '--max-airlines', '15',
        '--transition-duration', '500'
    ])
    
    # Open the visualization in the browser
    print(f"Opening visualization in browser: {output_path}")
    webbrowser.open('file://' + os.path.abspath(output_path))

if __name__ == "__main__":
    main() 