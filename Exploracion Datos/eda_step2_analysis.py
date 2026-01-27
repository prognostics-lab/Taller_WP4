import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import os

# Configuration
FILE_PATH = "energy_results_MCmodel.csv"
SAMPLE_SIZE = 100000  # Number of rows to sample for plotting
CHUNK_SIZE = 100000   # Rows per chunk to process
OUTPUT_DIR = "eda_output"

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def process_data():
    print(f"Starting analysis on {FILE_PATH}...")
    
    # Initialize trackers
    total_rows = 0
    missing_values = None
    
    # Reservoir sampling for plots
    sample_df = []
    
    # Process in chunks
    chunk_iter = pd.read_csv(FILE_PATH, chunksize=CHUNK_SIZE)
    
    for i, chunk in enumerate(chunk_iter):
        # 1. Basic Cleaning on Chunk
        # Fix 'Time' if it's a timedelta string (e.g., "0 days 00:00:00")
        # We can convert to seconds for easier numerical analysis
        if 'Time' in chunk.columns and chunk['Time'].dtype == 'object':
             chunk['Time_Seconds'] = pd.to_timedelta(chunk['Time'], errors='coerce').dt.total_seconds()
        
        # 2. Accumulate Missing Values Count
        if missing_values is None:
            missing_values = chunk.isna().sum()
        else:
            missing_values += chunk.isna().sum()
            
        # 3. Sampling for Plots (Simple random sampling from each chunk)
        # We want approx SAMPLE_SIZE total, so we take a fraction from each chunk
        # Fraction ~ SAMPLE_SIZE / ESTIMATED_TOTAL_ROWS. 
        # Since we don't know total, let's just take a fixed 1% or similar ensuring we don't blow up memory
        # A safer way without knowing total size: simple random sample of chunk
        sampled_chunk = chunk.sample(frac=0.01, random_state=42)
        sample_df.append(sampled_chunk)
        
        total_rows += len(chunk)
        print(f"Processed chunk {i+1} (Total rows: {total_rows})", end='\r')
        
    print(f"\nTotal rows processed: {total_rows}")
    
    # Combine samples
    full_sample = pd.concat(sample_df)
    print(f"Sample size for plotting: {len(full_sample)}")
    
    # --- Generate Report ---
    with open(f"{OUTPUT_DIR}/eda_summary.txt", "w") as f:
        f.write("=== Data Quality Report ===\n")
        f.write(f"Total Rows: {total_rows}\n")
        f.write("\n=== Missing Values ===\n")
        f.write(missing_values.to_string() + "\n")
        
        f.write("\n=== Sample Descriptive Statistics ===\n")
        f.write(full_sample.describe().to_string() + "\n")

    # --- Visualizations ---
    print("Generating plots...")
    
    # 1. Correlation Heatmap
    numeric_cols = full_sample.select_dtypes(include=[np.number]).columns
    # Drop columns that are completely empty or constant in sample if any
    valid_numeric = full_sample[numeric_cols].dropna(axis=1, how='all')
    
    if not valid_numeric.empty:
        corr = valid_numeric.corr()
        fig_corr = px.imshow(corr, text_auto=True, title="Correlation Matrix (Sampled Data)", template="plotly_dark")
        fig_corr.write_image(f"{OUTPUT_DIR}/correlation_matrix.png", width=1200, height=1000)
    
    # 2. Key Distributions
    # Power Distribution
    if 'Power_battery_1' in full_sample.columns:
        fig_hist = px.histogram(full_sample, x="Power_battery_1", nbins=50, title="Distribution of Power (Battery 1)", template="plotly_dark")
        fig_hist.write_image(f"{OUTPUT_DIR}/power_dist_bat1.png")

    # SOC Relationship
    if 'SOC_battery_1' in full_sample.columns and 'SOC_battery_2' in full_sample.columns:
        fig_soc = px.scatter(full_sample, x="SOC_battery_1", y="SOC_battery_2", title="SOC Battery 1 vs Battery 2", template="plotly_dark")
        fig_soc.write_image(f"{OUTPUT_DIR}/soc_scatter.png")
        
    # Vehicle Speed Profile (Sample of one cycle or just distribution)
    if 'vehicle_speed' in full_sample.columns:
         fig_speed = px.histogram(full_sample, x="vehicle_speed", title="Vehicle Speed Distribution", template="plotly_dark")
         fig_speed.write_image(f"{OUTPUT_DIR}/speed_dist.png")

    # Save sample for further quick inspection if needed
    full_sample.to_csv(f"{OUTPUT_DIR}/eda_sample.csv", index=False)
    print(f"Analysis complete. Outputs saved to {OUTPUT_DIR}/")

if __name__ == "__main__":
    process_data()
