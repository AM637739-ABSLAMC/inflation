"""
Data Preparation Script for Detailed CPI Analysis
Extracts 298 granular CPI components with weights from Excel file
Prepares cleaned dataset for inflation_analysis.qmd
"""

import pandas as pd
import numpy as np
import json
from datetime import datetime

print("=" * 80)
print("DETAILED CPI DATA PREPARATION")
print("=" * 80)

# Step 1: Read DetData from CSV (already processed)
print("\n[1/6] Reading DetData from CSV...")
df_data = pd.read_csv('data_DetData.csv')
print(f"   ✓ Data shape: {df_data.shape}")

# Step 2: Extract weights from Excel - Row 2 (index 2) contains weights
print("\n[2/6] Extracting weights from Excel DetData sheet row 2...")
weights_raw = pd.read_excel('cpi.xlsx', sheet_name='DetData', 
                             header=None, nrows=1, skiprows=2)

# Create weight dictionary mapping column names to weights
# Weights start from column 3 in Excel (columns 0-2 are metadata)
weight_dict = {}
for i, col in enumerate(df_data.columns):
    if i == 0:  # Skip time column
        continue
    # Excel columns start from 3 for actual data (after metadata columns)
    excel_col_idx = i + 2  # Offset to match Excel structure
    weight_val = weights_raw.iloc[0, excel_col_idx] if excel_col_idx < len(weights_raw.columns) else None
    if pd.notna(weight_val) and isinstance(weight_val, (int, float)):
        weight_dict[col] = float(weight_val)
    else:
        weight_dict[col] = 0.0  # Default for missing weights

print(f"   ✓ Extracted {len(weight_dict)} weights")
print(f"   ✓ Total weight sum: {sum(weight_dict.values()):.2f}")

# Show top 10 items by weight
top_weights = sorted(weight_dict.items(), key=lambda x: x[1], reverse=True)[:10]
print("\n   Top 10 items by weight:")
for item, weight in top_weights:
    item_short = item.replace('Consumer Price Index: ', '')[:50]
    print(f"     - {item_short}: {weight:.3f}")

# Step 3: Clean and prepare data
print("\n[3/6] Cleaning and preparing data...")

# Rename time column if needed
if df_data.columns[0] != 'time':
    df_data.rename(columns={df_data.columns[0]: 'time'}, inplace=True)

# Convert time to datetime with dayfirst=True
df_data['time'] = pd.to_datetime(df_data['time'], dayfirst=True, errors='coerce')

# Sort by time
df_data = df_data.sort_values('time').reset_index(drop=True)

# Extract year and month
df_data['Year'] = df_data['time'].dt.year
df_data['Month'] = df_data['time'].dt.month
df_data['Month_Name'] = df_data['time'].dt.strftime('%b')

print(f"   ✓ Data cleaned and sorted")
print(f"   ✓ Date range: {df_data['time'].min()} to {df_data['time'].max()}")

# Step 4: Calculate YoY and MoM changes
print("\n[4/6] Calculating YoY and MoM percentage changes...")

# Get all CPI component columns (exclude metadata columns)
meta_cols = ['time', 'Year', 'Month', 'Month_Name']
cpi_cols = [col for col in df_data.columns if col not in meta_cols]

# Convert all CPI columns to numeric (coerce errors to NaN)
for col in cpi_cols:
    df_data[col] = pd.to_numeric(df_data[col], errors='coerce')

# Calculate changes for each component
for col in cpi_cols:
    # Year-on-Year (12 months)
    df_data[f'{col}_YoY'] = df_data[col].pct_change(12, fill_method=None) * 100
    # Month-on-Month (1 month)
    df_data[f'{col}_MoM'] = df_data[col].pct_change(1, fill_method=None) * 100

print(f"   ✓ Calculated YoY and MoM for {len(cpi_cols)} components")

# Step 5: Save processed data
print("\n[5/6] Saving processed data...")

output_csv = 'cleaned_detailed_inflation.csv'
df_data.to_csv(output_csv, index=False)
print(f"   ✓ Saved to: {output_csv}")
print(f"   ✓ File size: {df_data.shape[0]} rows × {df_data.shape[1]} columns")

# Step 6: Save weights as JSON
print("\n[6/6] Saving weight mappings...")

output_json = 'detailed_weights.json'
with open(output_json, 'w') as f:
    json.dump(weight_dict, f, indent=2)
print(f"   ✓ Saved to: {output_json}")

# Summary statistics
print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"Total CPI components:     {len(cpi_cols)}")
min_date = pd.to_datetime(df_data['time'].min())
max_date = pd.to_datetime(df_data['time'].max())
print(f"Time period:              {min_date.strftime('%b %Y')} to {max_date.strftime('%b %Y')}")
print(f"Total observations:       {len(df_data)}")
print(f"Total weight coverage:    {sum(weight_dict.values()):.2f}")
print(f"\nComponents by category:")

# Count components by main category
categories = {}
for col in cpi_cols:
    if ':' in col:
        main_cat = col.split(':')[1].strip().split(':')[0].strip()
    else:
        main_cat = 'Other'
    categories[main_cat] = categories.get(main_cat, 0) + 1

for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
    print(f"  - {cat}: {count} items")

# Latest month statistics
latest_date_str = df_data['time'].max()
latest_date = pd.to_datetime(latest_date_str)
latest_data = df_data[df_data['time'] == latest_date_str].iloc[0]

print(f"\nLatest month: {latest_date.strftime('%B %Y')}")

# Count non-null YoY values
yoy_cols = [col for col in df_data.columns if col.endswith('_YoY')]
non_null_yoy = sum([pd.notna(latest_data[col]) for col in yoy_cols])
print(f"  - Components with YoY data: {non_null_yoy}/{len(yoy_cols)}")

# Show inflation distribution
yoy_values = [latest_data[col] for col in yoy_cols if pd.notna(latest_data[col])]
if yoy_values:
    print(f"  - YoY inflation range: {min(yoy_values):.2f}% to {max(yoy_values):.2f}%")
    print(f"  - YoY median inflation: {np.median(yoy_values):.2f}%")

print("\n" + "=" * 80)
print("✓ DATA PREPARATION COMPLETE!")
print("=" * 80)
print(f"\nNext steps:")
print(f"1. Review: {output_csv}")
print(f"2. Review: {output_json}")
print(f"3. Update inflation_analysis.qmd to use detailed data")
print()
