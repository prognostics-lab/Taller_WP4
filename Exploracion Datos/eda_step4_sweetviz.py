import pandas as pd
import numpy as np

# Compatibility fix for newer Numpy versions where VisibleDeprecationWarning was removed
if not hasattr(np, "VisibleDeprecationWarning"):
    np.VisibleDeprecationWarning = UserWarning

import sweetviz as sv
import os

SAMPLE_FILE = "energy_results_MCmodel.csv"
OUTPUT_REPORT = "eda_output/sweetviz_report.html"

def run_sweetviz():
    print("Generating Sweetviz Report...")
    
    if not os.path.exists(SAMPLE_FILE):
        print(f"Error: Sample file {SAMPLE_FILE} not found. Please run eda_step2_analysis.py first.")
        return

    # Load the filtered sample
    df = pd.read_csv(SAMPLE_FILE)
    print(f"Loaded {len(df)} rows from sample.")

    # Analyze
    # We specify target_feat if there is a specific target, otherwise None
    # Assuming general EDA for now
    report = sv.analyze(df)
    
    # Show & Save
    report.show_html(OUTPUT_REPORT)
    print(f"Report saved to {OUTPUT_REPORT}")

if __name__ == "__main__":
    run_sweetviz()
