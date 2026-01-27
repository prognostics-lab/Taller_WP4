import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

# Use the pre-extracted data from the previous step to save time
INPUT_FILE = "eda_output/cycle_1_data.csv"
OUTPUT_DIR = "eda_output"

def generate_detailed_timeseries():
    print(f"Loading Cycle 1 data from {INPUT_FILE}...")
    
    if not os.path.exists(INPUT_FILE):
        print("Error: Cycle 1 data not found. Please run eda_step3_timeseries.py first.")
        return

    df = pd.read_csv(INPUT_FILE)
    
    # Ensure sorted by time
    if 'Time_Seconds' not in df.columns:
         # Re-create if missing (it should be there from step 3)
         df['Time_Seconds'] = pd.to_timedelta(df['Time'], errors='coerce').dt.total_seconds()
    
    df = df.sort_values(by='Time_Seconds')
    
    print(f"Data loaded: {len(df)} rows.")

    # --- PLOTTING ---
    print("Generating Detailed Electrical Analysis Plot...")
    
    # Create subplots
    # Row 1: Speed (Context)
    # Row 2: Voltage (Bat 1 vs Bat 2)
    # Row 3: Current (Bat 1 vs Bat 2)
    # Row 4: Power (Bat 1 vs Bat 2)
    # Row 5: SOC (Bat 1 vs Bat 2)
    
    fig = make_subplots(
        rows=5, cols=1, 
        shared_xaxes=True, 
        vertical_spacing=0.03,
        subplot_titles=("Vehicle Speed", "Voltage (V)", "Current (A)", "Power (W)", "State of Charge (SOC)")
    )

    # 1. Speed
    fig.add_trace(go.Scatter(x=df['Time_Seconds'], y=df['vehicle_speed'], 
                             name='Speed', line=dict(color='#00F0FF', width=1)), row=1, col=1)

    # 2. Voltage (Compare Bat 1 & 2)
    fig.add_trace(go.Scatter(x=df['Time_Seconds'], y=df['V_battery_1'], 
                             name='Voltage Bat 1', line=dict(color='#ff5757', width=1), legendgroup='Bat1'), row=2, col=1)
    fig.add_trace(go.Scatter(x=df['Time_Seconds'], y=df['V_battery_2'], 
                             name='Voltage Bat 2', line=dict(color='#ffbd57', width=1), legendgroup='Bat2'), row=2, col=1)

    # 3. Current
    fig.add_trace(go.Scatter(x=df['Time_Seconds'], y=df['I_battery_1'], 
                             name='Current Bat 1', line=dict(color='#57ff57', width=1), legendgroup='Bat1'), row=3, col=1)
    fig.add_trace(go.Scatter(x=df['Time_Seconds'], y=df['I_battery_2'], 
                             name='Current Bat 2', line=dict(color='#57ffbd', width=1), legendgroup='Bat2'), row=3, col=1)

    # 4. Power
    fig.add_trace(go.Scatter(x=df['Time_Seconds'], y=df['Power_battery_1'], 
                             name='Power Bat 1', line=dict(color='#d657ff', width=1), legendgroup='Bat1'), row=4, col=1)
    fig.add_trace(go.Scatter(x=df['Time_Seconds'], y=df['Power_battery_2'], 
                             name='Power Bat 2', line=dict(color='#ff57d6', width=1), legendgroup='Bat2'), row=4, col=1)

    # 5. SOC
    fig.add_trace(go.Scatter(x=df['Time_Seconds'], y=df['SOC_battery_1'], 
                             name='SOC Bat 1', line=dict(color='#ffffff', width=2), legendgroup='Bat1'), row=5, col=1)
    fig.add_trace(go.Scatter(x=df['Time_Seconds'], y=df['SOC_battery_2'], 
                             name='SOC Bat 2', line=dict(color='#aaaaaa', width=2, dash='dot'), legendgroup='Bat2'), row=5, col=1)

    # Update Layout with Range Slider
    fig.update_layout(
        title="Cycle 1: Electrical System Analysis",
        template="plotly_dark",
        height=1200,
        hovermode="x unified",
        xaxis5=dict(
            rangeslider=dict(visible=True),
            type="linear"
        )
    )
    
    # Improve y-axis labels
    fig.update_yaxes(title_text="m/s", row=1, col=1)
    fig.update_yaxes(title_text="Volts", row=2, col=1)
    fig.update_yaxes(title_text="Amps", row=3, col=1)
    fig.update_yaxes(title_text="Watts", row=4, col=1)
    fig.update_yaxes(title_text="SOC", row=5, col=1)

    output_path = f"{OUTPUT_DIR}/detailed_timeseries_v2.html"
    fig.write_html(output_path)
    print(f"Detailed plot saved to {output_path}")

if __name__ == "__main__":
    generate_detailed_timeseries()
