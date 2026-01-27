import pandas as pd
import plotly.graph_objects as go
import os

# Configuration
INPUT_FILE = "energy_results_MCmodel.csv"
OUTPUT_DIR = "eda_output/mc_overlays"
DOWNSAMPLE_POINTS = 1000  # Number of points per cycle to keep for overlay (optimization)

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def generate_overlays():
    print(f"Loading dataset for Overlay Analysis...")
    df = pd.read_csv(INPUT_FILE)
    
    # Process Time
    if 'Time' in df.columns:
        df['Time_Seconds'] = pd.to_timedelta(df['Time'], errors='coerce').dt.total_seconds()
        
    cycles = sorted(df['cycle'].unique())
    print(f"Total Cycles: {len(cycles)}")

    # Variables to plot
    # Logic: One separate HTML file per variable containing all cycles
    target_vars = {
        "SOC_battery_1": "State of Charge (Battery 1)",
        "Power_battery_1": "Power (Battery 1)",
        "V_battery_1": "Voltage (Battery 1)",
        "vehicle_speed": "Vehicle Speed",
        "distance": "Distance" # Checking this one as requested
    }

    for var_col, var_name in target_vars.items():
        if var_col not in df.columns:
            print(f"Skipping {var_name} (Col {var_col} not found)")
            continue

        print(f"Generating Overlay for {var_name}...")
        
        fig = go.Figure()
        
        for cycle_id in cycles:
            # Extract cycle data
            cycle_data = df[df['cycle'] == cycle_id].sort_values('Time_Seconds')
            
            if cycle_data.empty:
                continue
                
            # Downsample for performance (Spaghetti plots get heavy)
            # We take every Nth row to roughly match DOWNSAMPLE_POINTS
            step = max(1, len(cycle_data) // DOWNSAMPLE_POINTS)
            cycle_view = cycle_data.iloc[::step]
            
            # Use Scattergl for WebGL acceleration (crucial for 100s of lines)
            fig.add_trace(go.Scattergl(
                x=cycle_view['Time_Seconds'],
                y=cycle_view[var_col],
                mode='lines',
                name=f'Cycle {cycle_id}',
                opacity=0.5, # Enable transparency to see density
                line=dict(width=1)
            ))

        fig.update_layout(
            title=f"Monte Carlo Overlay: {var_name} vs Time",
            xaxis_title="Time (Seconds)",
            yaxis_title=var_name,
            template="plotly_dark",
            hovermode="closest",
            height=800
        )
        
        # Save
        filename = f"{OUTPUT_DIR}/overlay_{var_col}.html"
        fig.write_html(filename)
        print(f"Saved {filename}")

    # Special Request: Variable vs Distance (if Distance is meaningful)
    # Let's check if 'distance' looks like a valid X-axis (monotonic increasing)
    # We take Cycle 1 as proxy
    c1 = df[df['cycle'] == 1]
    if not c1.empty and c1['distance'].is_monotonic_increasing and c1['distance'].max() > 1:
        print("Distance appears valid for X-axis. Generating Distance Overlays...")
        # If valid, we generate similar plots but with X=distance
        for var_col, var_name in target_vars.items():
            if var_col == "distance": continue # Skip Dist vs Dist
            
            print(f"Generating Distance Overlay for {var_name}...")
            fig_dist = go.Figure()
            for cycle_id in cycles:
                cycle_data = df[df['cycle'] == cycle_id].sort_values('distance') # Sort by distance
                step = max(1, len(cycle_data) // DOWNSAMPLE_POINTS)
                cycle_view = cycle_data.iloc[::step]
                
                fig_dist.add_trace(go.Scattergl(
                    x=cycle_view['distance'],
                    y=cycle_view[var_col],
                    mode='lines',
                    name=f'Cycle {cycle_id}',
                    opacity=0.5,
                    line=dict(width=1)
                ))
            
            fig_dist.update_layout(
                title=f"Monte Carlo Overlay: {var_name} vs Distance",
                xaxis_title="Distance",
                yaxis_title=var_name,
                template="plotly_dark",
                height=800
            ) 
            fig_dist.write_html(f"{OUTPUT_DIR}/overlay_distance_{var_col}.html")
    else:
        print("Distance column does not appear to be a cumulative trip distance (Max value too small or not monotonic). Skipping Distance-X plots.")

if __name__ == "__main__":
    generate_overlays()
