import pandas as pd
import plotly.graph_objects as go
import os

# Configuration
INPUT_FILE = "energy_results_MCmodel.csv"
OUTPUT_DIR = "eda_output"
OUTPUT_FILE = "eda_output/master_overlay_analysis.html"
DOWNSAMPLE_POINTS = 1000  # Points per cycle per variable
INITIAL_VISIBLE_CYCLES = 5 # Only show these many cycles initially

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def generate_master_plot():
    print(f"Loading dataset...")
    df = pd.read_csv(INPUT_FILE)
    
    if 'Time' in df.columns:
        df['Time_Seconds'] = pd.to_timedelta(df['Time'], errors='coerce').dt.total_seconds()
        
    cycles = sorted(df['cycle'].unique())
    print(f"Loaded {len(cycles)} cycles.")

    # Variables to Include (Reordered: SOC First)
    variables = {
        "SOC_battery_1": "SOC Battery 1",
        "SOC_battery_2": "SOC Battery 2",
        "Power_battery_1": "Power Bat 1 (W)",
        "Power_battery_2": "Power Bat 2 (W)",
        "V_battery_1": "Voltage Bat 1 (V)",
        "V_battery_2": "Voltage Bat 2 (V)",
        "I_battery_1": "Current Bat 1 (A)",
        "I_battery_2": "Current Bat 2 (A)",
        "vehicle_speed": "Speed (m/s)",
        "SoMPA_battery_1": "SoMPA Bat 1",
        "SoMPA_battery_2": "SoMPA Bat 2"
    }
    
    # Filter valid columns
    valid_vars = {k: v for k, v in variables.items() if k in df.columns}
    var_keys = list(valid_vars.keys())
    
    fig = go.Figure()

    # Pre-process data for each cycle to avoid repeated filtering
    cycle_data_cache = {}
    for cid in cycles:
        cycle_subset = df[df['cycle'] == cid].sort_values('Time_Seconds')
        if not cycle_subset.empty:
             step = max(1, len(cycle_subset) // DOWNSAMPLE_POINTS)
             cycle_data_cache[cid] = cycle_subset.iloc[::step]
    
    print("Generating Traces...")
    
    # Generate Colors (Turbo for better visibility)
    import plotly.colors as pcolors
    # Get a list of colors from a sequential scale
    color_scale = pcolors.sample_colorscale("Turbo", [n/(len(cycles)-1) for n in range(len(cycles))])

    total_traces_per_var = len(cycles)
    
    for var_code in var_keys:
        print(f"  Adding traces for {var_code}...", end='\r')
        for i, cid in enumerate(cycles):
            if cid not in cycle_data_cache:
                continue
                
            cdata = cycle_data_cache[cid]
            
            # Visibility Logic:
            is_first_var = (var_code == var_keys[0]) # Now SOC_battery_1
            is_initial_cycle = (i < INITIAL_VISIBLE_CYCLES)
            
            visible_status = True if (is_first_var and is_initial_cycle) else 'legendonly'
            if not is_first_var:
                visible_status = False 
            elif not is_initial_cycle:
                visible_status = 'legendonly'
            
            fig.add_trace(go.Scattergl(
                x=cdata['Time_Seconds'],
                y=cdata[var_code],
                mode='lines',
                name=f"Cycle {cid}",
                visible=visible_status,
                line=dict(width=1.5, color=color_scale[i]), # Thinner, colored lines
                opacity=0.8,
                hovertemplate=f"<b>Cycle {cid}</b><br>Time: %{{x:.1f}}s<br>Value: %{{y}}<extra></extra>"
            ))
            
    print("\nCreating Layout & Menus...")

    # Create Buttons
    buttons = []
    
    for i, var_code in enumerate(var_keys):
        label = valid_vars[var_code]
        
        # Visibility list
        visibility = [False] * (len(var_keys) * len(cycle_data_cache))
        
        start_idx = i * len(cycle_data_cache)
        end_idx = start_idx + len(cycle_data_cache)
        
        for idx in range(start_idx, end_idx):
            cycle_idx = idx - start_idx
            if cycle_idx < INITIAL_VISIBLE_CYCLES:
                visibility[idx] = True
            else:
                visibility[idx] = 'legendonly'
                
        button = dict(
            label=label,
            method="update",
            args=[
                {"visible": visibility},
                {"title.text": f"Master Analysis: {label}",  # Update TEXT only to keep formatting
                 "yaxis.title.text": label} # Safe update for axis title too
            ]
        )
        buttons.append(button)

    fig.update_layout(
        title=dict(
            text=f"Master Analysis: {valid_vars[var_keys[0]]}",
            font=dict(size=24, color="#ffffff")
        ),
        updatemenus=[dict(
            type="dropdown",
            direction="down",
            x=1.0, y=1.15, # Position above graph, right aligned
            xanchor="right",
            showactive=True,
            bgcolor="#2d2d2d",
            bordercolor="#555",
            font=dict(color="white"),
            buttons=buttons
        )],
        template="plotly_dark",
        xaxis=dict(
            title="Time (Seconds)",
            showgrid=True,
            gridcolor="#333",
            zerolinecolor="#444"
        ),
        yaxis=dict(
            title=valid_vars[var_keys[0]],
            showgrid=True,
            gridcolor="#333",
            zerolinecolor="#444"
        ),
        height=900,
        margin=dict(t=100, r=50, l=80, b=80),
        legend=dict(
            title="Cycles",
            font=dict(size=10),
            itemsizing="constant"
        ),
        plot_bgcolor="#111111", # Darker background for contrast
        paper_bgcolor="#000000"
    )

    fig.write_html(OUTPUT_FILE)
    print(f"Master Plot saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    generate_master_plot()
