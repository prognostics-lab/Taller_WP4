import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

FILE_PATH = "energy_results_MCmodel.csv"
OUTPUT_DIR = "eda_output"
TARGET_CYCLE = 1  # We will extract this specific cycle for clear time series

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def generate_timeseries():
    print(f"Extraction of Time Series for Cycle {TARGET_CYCLE}...")
    
    cycle_data = []
    chunk_size = 100000
    
    # Reads the file looking for the specific cycle
    # Since data might be shuffled, we scan the full file (efficiently via chunks)
    # 2GB is manageable for a full scan if we only keep a subset of rows
    try:
        chunk_iter = pd.read_csv(FILE_PATH, chunksize=chunk_size)
        for i, chunk in enumerate(chunk_iter):
            print(f"Scanning chunk {i+1}...", end='\r')
            if 'cycle' in chunk.columns:
                filtered = chunk[chunk['cycle'] == TARGET_CYCLE].copy()
                if not filtered.empty:
                    cycle_data.append(filtered)
        
        print("\nmerging data...")
        if not cycle_data:
            print(f"No data found for cycle {TARGET_CYCLE}!")
            return

        df_cycle = pd.concat(cycle_data)
        
        # Process Time
        if 'Time' in df_cycle.columns:
            # Convert '0 days 00:00:00' format to total seconds
            df_cycle['Time_Seconds'] = pd.to_timedelta(df_cycle['Time'], errors='coerce').dt.total_seconds()
            
        # Sort by Time to ensure correct plotting order
        df_cycle = df_cycle.sort_values(by='Time_Seconds')
        
        print(f"Data for Cycle {TARGET_CYCLE}: {len(df_cycle)} rows.")
        
        # --- PLOTTING ---
        print("Generating Time Series Plot...")
        
        # Create a subplot with shared x-axis
        fig = make_subplots(rows=3, cols=1, shared_xaxes=True, 
                            vertical_spacing=0.05,
                            subplot_titles=("Vehicle Speed", "Battery Power", "SOC"))

        # 1. Speed
        if 'vehicle_speed' in df_cycle.columns:
            fig.add_trace(go.Scatter(x=df_cycle['Time_Seconds'], y=df_cycle['vehicle_speed'], 
                                   name='Speed (m/s)', line=dict(color='#00F0FF')), row=1, col=1)

        # 2. Power
        if 'Power_battery_1' in df_cycle.columns:
            fig.add_trace(go.Scatter(x=df_cycle['Time_Seconds'], y=df_cycle['Power_battery_1'], 
                                   name='Power Bat 1 (W)', line=dict(color='#FFA500')), row=2, col=1)

        # 3. SOC
        if 'SOC_battery_1' in df_cycle.columns:
            fig.add_trace(go.Scatter(x=df_cycle['Time_Seconds'], y=df_cycle['SOC_battery_1'], 
                                   name='SOC Bat 1', line=dict(color='#00FF00')), row=3, col=1)

        fig.update_layout(
            title=f"Time Series Analysis - Cycle {TARGET_CYCLE}",
            template="plotly_dark",
            height=900,
            xaxis3_title="Time (Seconds)"
        )
        
        output_path = f"{OUTPUT_DIR}/timeseries_cycle_{TARGET_CYCLE}.html"
        fig.write_html(output_path)
        print(f"Plot saved to {output_path}")
        
        # Save processed single cycle data for persistent use
        df_cycle.to_csv(f"{OUTPUT_DIR}/cycle_{TARGET_CYCLE}_data.csv", index=False)

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    generate_timeseries()
