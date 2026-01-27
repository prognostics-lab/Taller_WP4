import pandas as pd
import os

FILE_PATH = "energy_results_MCmodel.csv"
OUTPUT_FILE = "data_inspection_report.txt"

def inspect_data():
    print(f"Inspecting {FILE_PATH}...")
    
    if not os.path.exists(FILE_PATH):
        print(f"Error: File not found at {os.getcwd()}")
        return

    try:
        # Load only first 100 rows to avoid memory issues
        df_head = pd.read_csv(FILE_PATH, nrows=100)
        
        with open(OUTPUT_FILE, "w") as f:
            f.write("=== Column Names ===\n")
            f.write(str(list(df_head.columns)) + "\n\n")
            
            f.write("=== Data Types ===\n")
            f.write(str(df_head.dtypes) + "\n\n")
            
            f.write("=== First 5 Rows ===\n")
            f.write(df_head.head().to_string() + "\n\n")
            
            # Use chunks to get full shape safely
            row_count = 0
            # Just estimating lines for speed or counting chunks
            # Reading entire file just for count might be slow, let's just estimate or skip for now
            # f.write(f"=== Estimated Rows ===\n (Skipped for speed)\n")

        print(f"Inspection complete. Report saved to {OUTPUT_FILE}")
        print("Columns found:", list(df_head.columns))

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    inspect_data()
