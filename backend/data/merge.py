import pandas as pd
import re

def merge_data():
    date_re = re.compile(r'^\d{4}-\d{2}-\d{2}')
    cleaned_lines = []
    current_entry = ""

    print("Cleaning Data.csv...")
    with open('d:/hackathons/ET/backend/data/Data.csv', 'r', encoding='latin1') as f:
        header = f.readline()
        cleaned_lines.append(header)
        for line in f:
            stripped = line.strip()
            if not stripped: continue
            if date_re.match(stripped):
                if current_entry: cleaned_lines.append(current_entry + "\n")
                current_entry = stripped
            else:
                if current_entry: current_entry += " " + stripped
        if current_entry: cleaned_lines.append(current_entry + "\n")

    from io import StringIO
    data_df = pd.read_csv(StringIO("".join(cleaned_lines)))
    data_df['Date'] = pd.to_datetime(data_df['Date'], errors='coerce')
    data_df = data_df.dropna(subset=['Date'])

    print("Reading SBIN.csv...")
    sbin_df = pd.read_csv('d:/hackathons/ET/backend/data/SBIN.csv')
    sbin_df['Date'] = pd.to_datetime(sbin_df['Date'], errors='coerce')
    
    print("Merging on matching dates...")
    merged_df = pd.merge(data_df, sbin_df, on='Date', how='inner').sort_values('Date')
    
    output_path = 'd:/hackathons/ET/backend/data/merged_stock_data.csv'
    merged_df.to_csv(output_path, index=False)
    print(f"Success! {len(merged_df)} matching entries saved to {output_path}")

if __name__ == "__main__":
    merge_data()
