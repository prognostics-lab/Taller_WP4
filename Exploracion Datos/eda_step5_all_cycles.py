import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
import shutil

# Load the FULL dataset
INPUT_FILE = "energy_results_MCmodel.csv"
OUTPUT_DIR = "eda_output/cycles_detailed"

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def generate_all_cycles():
    print(f"Loading FULL dataset from {INPUT_FILE}...")
    
    # Load full file (Assuming memory is sufficient based on user feedback)
    df = pd.read_csv(INPUT_FILE)
    
    # Create Time_Seconds column if needed
    if 'Time' in df.columns:
         print("Converting Time column...")
         df['Time_Seconds'] = pd.to_timedelta(df['Time'], errors='coerce').dt.total_seconds()
    
    # Identify cycles
    cycles = sorted(df['cycle'].unique())
    print(f"Found {len(cycles)} unique cycles: {cycles}")
    
    for cycle_id in cycles:
        print(f"Processing Cycle {cycle_id}...", end='\r')
        
        # Filter data for this cycle
        cycle_df = df[df['cycle'] == cycle_id].copy()
        cycle_df = cycle_df.sort_values(by='Time_Seconds')
        
        # Skip empty cycles
        if cycle_df.empty:
            continue
            
        # Create Plot
        fig = make_subplots(
            rows=5, cols=1, 
            shared_xaxes=True, 
            vertical_spacing=0.03,
            subplot_titles=(f"Cycle {cycle_id} - Speed", "Voltage", "Current", "Power", "SOC")
        )

        # 1. Speed
        fig.add_trace(go.Scatter(x=cycle_df['Time_Seconds'], y=cycle_df['vehicle_speed'], 
                                 name='Speed', line=dict(color='#00F0FF', width=1)), row=1, col=1)

        # 2. Voltage
        fig.add_trace(go.Scatter(x=cycle_df['Time_Seconds'], y=cycle_df['V_battery_1'], 
                                 name='V Bat 1', line=dict(color='#ff5757', width=1), legendgroup='Bat1'), row=2, col=1)
        fig.add_trace(go.Scatter(x=cycle_df['Time_Seconds'], y=cycle_df['V_battery_2'], 
                                 name='V Bat 2', line=dict(color='#ffbd57', width=1), legendgroup='Bat2'), row=2, col=1)

        # 3. Current
        fig.add_trace(go.Scatter(x=cycle_df['Time_Seconds'], y=cycle_df['I_battery_1'], 
                                 name='I Bat 1', line=dict(color='#57ff57', width=1), legendgroup='Bat1'), row=3, col=1)
        fig.add_trace(go.Scatter(x=cycle_df['Time_Seconds'], y=cycle_df['I_battery_2'], 
                                 name='I Bat 2', line=dict(color='#57ffbd', width=1), legendgroup='Bat2'), row=3, col=1)

        # 4. Power
        fig.add_trace(go.Scatter(x=cycle_df['Time_Seconds'], y=cycle_df['Power_battery_1'], 
                                 name='P Bat 1', line=dict(color='#d657ff', width=1), legendgroup='Bat1'), row=4, col=1)
        fig.add_trace(go.Scatter(x=cycle_df['Time_Seconds'], y=cycle_df['Power_battery_2'], 
                                 name='P Bat 2', line=dict(color='#ff57d6', width=1), legendgroup='Bat2'), row=4, col=1)

        # 5. SOC
        fig.add_trace(go.Scatter(x=cycle_df['Time_Seconds'], y=cycle_df['SOC_battery_1'], 
                                 name='SOC Bat 1', line=dict(color='#ffffff', width=2), legendgroup='Bat1'), row=5, col=1)
        fig.add_trace(go.Scatter(x=cycle_df['Time_Seconds'], y=cycle_df['SOC_battery_2'], 
                                 name='SOC Bat 2', line=dict(color='#aaaaaa', width=2, dash='dot'), legendgroup='Bat2'), row=5, col=1)

        # Layout
        fig.update_layout(
            title=f"Cycle {cycle_id} Analysis",
            template="plotly_dark",
            height=1200,
            hovermode="x unified",
            xaxis5=dict(rangeslider=dict(visible=True), type="linear")
        )
        
        # Save
        filename = f"{OUTPUT_DIR}/cycle_{cycle_id:03d}.html"
        fig.write_html(filename)
        
    print(f"\nCompleted! All plots saved to {OUTPUT_DIR}/")

if __name__ == "__main__":
    generate_all_cycles()
