# cleaning.py
# This script processes inflation data from Excel files and merges datasets into cleaned CSV files.
#
# Summary:
#
# 1. clean_xlsx_to_csv:
#    - Reads an Excel sheet, extracts relevant data, and saves it as a cleaned CSV file.
#
# 2. merge_datasets:
#    - Merges two datasets (DetData and CEIC Data) into a single CSV file using 'time' as the key.
#
# 3. merge_with_gold_column:
#    - Merges CEIC Data with the "Consumer Price Index: Miscellaneous: Gold" column from DetData.
#
# 4. merge_with_silver_column:
#    - Merges CEIC Data with the "Consumer Price Index: Miscellaneous: Silver" column from DetData
#      (with fallback auto-detection if the exact name differs).
#
# 5. merge_with_gold_and_silver_columns (NEW):
#    - Merges CEIC Data with BOTH Gold and Silver columns from DetData into ONE output file.
#
# 6. merge_with_all_columns (NEW):
#    - Merges CEIC Data with ALL columns from DetData based on the 'time' column.
#
# Usage:
#    python cleaning.py <xlsx_path> <csv_path>
#    - <xlsx_path>: Path to the input Excel file.
#    - <csv_path>: Base path to save the cleaned and merged CSV files (e.g., output.csv)

import pandas as pd
import sys
import os


def _standardize_time_column(df: pd.DataFrame, df_name: str = "df") -> pd.DataFrame:
    """
    Standardize the 'time' column for reliable merges.
    - Attempts to parse 'time' as datetime.
    - Drops rows where 'time' cannot be parsed.

    Returns:
        DataFrame with standardized 'time' column.
    """
    if "time" not in df.columns:
        raise KeyError(f"'time' column missing in {df_name}")

    df = df.copy()
    df["time"] = pd.to_datetime(df["time"], errors="coerce")
    before = len(df)
    df = df.dropna(subset=["time"])
    after = len(df)

    if before != after:
        print(f"[{df_name}] Dropped {before - after} rows due to unparseable 'time' values.")

    return df


# Function to clean and convert an Excel sheet to a CSV file
def clean_xlsx_to_csv(xlsx_path, csv_path, sheet_name, data_start_row, category_row, month_col, data_start_col):
    """
    Reads an Excel sheet, extracts relevant data, and saves it as a CSV file.

    Parameters:
        xlsx_path (str): Path to the input Excel file.
        csv_path (str): Path to save the cleaned CSV file.
        sheet_name (str): Name of the sheet to process.
        data_start_row (int): Row number where data starts.
        category_row (int): Row number containing category headers.
        month_col (int): Column number containing month data.
        data_start_col (int): Column number where data starts.

    Returns:
        None
    """
    # Read the Excel file without headers, from specific sheet
    df = pd.read_excel(xlsx_path, sheet_name=sheet_name, header=None)
    print(f"Full DataFrame shape for sheet {sheet_name}: {df.shape}")
    print(f"First few rows of full DF for sheet {sheet_name}:")
    print(df.head())

    # Extract category headers from the specified row, starting from the specified column
    categories = df.iloc[category_row, data_start_col:].tolist()
    print(f"Number of categories in sheet {sheet_name}: {len(categories)}")
    print(f"First few categories in sheet {sheet_name}: {categories[:5]}")

    # Extract months from the specified column, starting from the data row
    months = df.iloc[data_start_row:, month_col].tolist()
    print(f"Number of months in sheet {sheet_name}: {len(months)}")
    print(f"First few months in sheet {sheet_name}: {months[:5]}")

    # Extract the data grid starting from the specified column
    data = df.iloc[data_start_row:, data_start_col:]
    print(f"Data shape for sheet {sheet_name}: {data.shape}")
    print(f"First few rows of data for sheet {sheet_name}:")
    print(data.head())

    # Create a DataFrame with time as index and categories as columns
    data_df = pd.DataFrame(data.values, index=months, columns=categories)
    print(f"Data DF head for sheet {sheet_name}:")
    print(data_df.head())

    # Save to CSV with index
    data_df.to_csv(csv_path, index=True, index_label="time")
    print(f"Cleaned data for sheet {sheet_name} saved to {csv_path}")


# Function to merge two datasets into a single CSV file
def merge_datasets(detdata_path, ceicdata_path, output_path):
    """
    Merges two datasets (DetData and CEIC Data) and saves the result as a CSV file.

    Note:
        This merge is performed on 'time'. Using pd.merge without specifying 'on'
        can merge on all common columns and cause unexpected results.

    Parameters:
        detdata_path (str): Path to the DetData CSV file.
        ceicdata_path (str): Path to the CEIC Data CSV file.
        output_path (str): Path to save the merged CSV file.

    Returns:
        None
    """
    detdata = pd.read_csv(detdata_path)
    ceicdata = pd.read_csv(ceicdata_path)

    if "time" not in detdata.columns or "time" not in ceicdata.columns:
        print("The 'time' column is missing in one or both datasets.")
        return

    detdata = _standardize_time_column(detdata, "DetData")
    ceicdata = _standardize_time_column(ceicdata, "CEIC Data")

    # Outer merge on time
    merged_data = pd.merge(detdata, ceicdata, on="time", how="outer")

    # Sort by time for readability
    merged_data = merged_data.sort_values("time")

    merged_data.to_csv(output_path, index=False)
    print(f"Merged dataset saved to {output_path}")


# Function to merge datasets and include a specific column (Gold) from DetData
def merge_with_gold_column(detdata_path, ceicdata_path, output_path):
    """
    Merges the CEIC Data with the "Consumer Price Index: Miscellaneous: Gold"
    column from DetData based on the 'time' column.

    Parameters:
        detdata_path (str): Path to the DetData CSV file.
        ceicdata_path (str): Path to the CEIC Data CSV file.
        output_path (str): Path to save the merged CSV file with the Gold column.

    Returns:
        None
    """
    detdata = pd.read_csv(detdata_path)
    ceicdata = pd.read_csv(ceicdata_path)

    if "time" not in detdata.columns or "time" not in ceicdata.columns:
        print("The 'time' column is missing in one or both datasets.")
        return

    detdata = _standardize_time_column(detdata, "DetData")
    ceicdata = _standardize_time_column(ceicdata, "CEIC Data")

    gold_col = "Consumer Price Index: Miscellaneous: Gold"
    if gold_col not in detdata.columns:
        print("The specified Gold column does not exist in DetData.")
        print("Available DetData columns (sample):", list(detdata.columns)[:30])
        return

    gold_column = detdata[["time", gold_col]].drop_duplicates(subset=["time"])

    merged_data = pd.merge(ceicdata, gold_column, on="time", how="outer").sort_values("time")
    merged_data.to_csv(output_path, index=False)

    print(f"Merged dataset with Gold column saved to {output_path}")


def merge_with_silver_column(detdata_path, ceicdata_path, output_path):
    """
    Merges the CEIC Data with the Silver column from DetData based on the 'time' column.

    Attempts:
      1) exact name: "Consumer Price Index: Miscellaneous: Silver"
      2) auto-detect any column containing 'silver' (case-insensitive)

    Parameters:
        detdata_path (str): Path to the DetData CSV file.
        ceicdata_path (str): Path to the CEIC Data CSV file.
        output_path (str): Path to save the merged CSV file with the Silver column.

    Returns:
        None
    """
    detdata = pd.read_csv(detdata_path)
    ceicdata = pd.read_csv(ceicdata_path)

    if "time" not in detdata.columns or "time" not in ceicdata.columns:
        print("The 'time' column is missing in one or both datasets.")
        return

    detdata = _standardize_time_column(detdata, "DetData")
    ceicdata = _standardize_time_column(ceicdata, "CEIC Data")

    expected_col = "Consumer Price Index: Miscellaneous: Silver"

    if expected_col not in detdata.columns:
        silver_candidates = [c for c in detdata.columns if "silver" in str(c).lower()]
        if not silver_candidates:
            print("No Silver column found in DetData.")
            print("Available DetData columns (sample):", list(detdata.columns)[:30])
            return
        expected_col = silver_candidates[0]
        print(f"Using detected Silver column: {expected_col}")

    silver_column = detdata[["time", expected_col]].drop_duplicates(subset=["time"])

    merged_data = pd.merge(ceicdata, silver_column, on="time", how="outer").sort_values("time")
    merged_data.to_csv(output_path, index=False)

    print(f"Merged dataset with Silver column saved to {output_path}")


def merge_with_gold_and_silver_columns(detdata_path, ceicdata_path, output_path):
    """
    Merges CEIC Data with BOTH Gold and Silver columns from DetData in ONE file.

    This is useful when you want one final dataset that includes both commodity series.

    Parameters:
        detdata_path (str): Path to the DetData CSV file.
        ceicdata_path (str): Path to the CEIC Data CSV file.
        output_path (str): Path to save the merged CSV file with Gold and Silver.

    Returns:
        None
    """
    detdata = pd.read_csv(detdata_path)
    ceicdata = pd.read_csv(ceicdata_path)

    if "time" not in detdata.columns or "time" not in ceicdata.columns:
        print("The 'time' column is missing in one or both datasets.")
        return

    detdata = _standardize_time_column(detdata, "DetData")
    ceicdata = _standardize_time_column(ceicdata, "CEIC Data")

    gold_col = "Consumer Price Index: Miscellaneous: Gold"
    silver_col = "Consumer Price Index: Miscellaneous: Silver"

    if gold_col not in detdata.columns:
        print("The specified Gold column does not exist in DetData.")
        print("Available DetData columns (sample):", list(detdata.columns)[:30])
        return

    # Silver: allow auto-detect fallback
    if silver_col not in detdata.columns:
        silver_candidates = [c for c in detdata.columns if "silver" in str(c).lower()]
        if not silver_candidates:
            print("No Silver column found in DetData. Cannot create gold+silver merged output.")
            print("Available DetData columns (sample):", list(detdata.columns)[:30])
            return
        silver_col = silver_candidates[0]
        print(f"Using detected Silver column for combined output: {silver_col}")

    add_cols = detdata[["time", gold_col, silver_col]].drop_duplicates(subset=["time"])

    merged_data = pd.merge(ceicdata, add_cols, on="time", how="outer").sort_values("time")
    merged_data.to_csv(output_path, index=False)

    print(f"Merged dataset with Gold + Silver columns saved to {output_path}")


def merge_with_all_columns(detdata_path, ceicdata_path, output_path):
    """
    Merges CEIC Data with all columns from DetData based on the 'time' column.

    Parameters:
        detdata_path (str): Path to the DetData CSV file.
        ceicdata_path (str): Path to the CEIC Data CSV file.
        output_path (str): Path to save the merged CSV file with all columns.

    Returns:
        None
    """
    detdata = pd.read_csv(detdata_path)
    ceicdata = pd.read_csv(ceicdata_path)

    if "time" not in detdata.columns or "time" not in ceicdata.columns:
        print("The 'time' column is missing in one or both datasets.")
        return

    detdata = _standardize_time_column(detdata, "DetData")
    ceicdata = _standardize_time_column(ceicdata, "CEIC Data")

    # Exclude the 'time' column from DetData for merging
    detdata_columns = [col for col in detdata.columns if col != "time"]

    # Merge all columns from DetData with CEIC Data
    merged_data = pd.merge(ceicdata, detdata[["time"] + detdata_columns], on="time", how="outer")

    # Sort by time for readability
    merged_data = merged_data.sort_values("time")

    # Save the merged dataset to the output file
    merged_data.to_csv(output_path, index=False)
    print(f"Merged dataset with all columns saved to {output_path}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python cleaning.py <xlsx_path> <csv_path>")
        sys.exit(1)

    xlsx_path = sys.argv[1]
    csv_path = sys.argv[2]

    # Clean the 'DetData' sheet
    clean_xlsx_to_csv(
        xlsx_path=xlsx_path,
        csv_path=csv_path.replace(".csv", "_DetData.csv"),
        sheet_name="DetData",
        data_start_row=29,
        category_row=3,
        month_col=2,
        data_start_col=3,
    )

    # Clean the 'CEIC Data' sheet
    clean_xlsx_to_csv(
        xlsx_path=xlsx_path,
        csv_path=csv_path.replace(".csv", "_CEIC_Data.csv"),
        sheet_name="CEIC Data",
        data_start_row=28,
        category_row=2,
        month_col=2,
        data_start_col=3,
    )

    # Define file paths
    detdata_path = csv_path.replace(".csv", "_DetData.csv")
    ceicdata_path = csv_path.replace(".csv", "_CEIC_Data.csv")
    output_path = csv_path.replace(".csv", "_merged.csv")

    # Check if files exist
    if not os.path.exists(detdata_path) or not os.path.exists(ceicdata_path):
        print("One or both input files are missing. Please check the file paths.")
        sys.exit(1)

    # Merge the datasets (DetData + CEIC Data) on time
    merge_datasets(detdata_path, ceicdata_path, output_path)

    # Output: merged with Gold only
    gold_output_path = csv_path.replace(".csv", "_merged_with_gold.csv")
    merge_with_gold_column(detdata_path, ceicdata_path, gold_output_path)

    # Output: merged with Silver only
    silver_output_path = csv_path.replace(".csv", "_merged_with_silver.csv")
    merge_with_silver_column(detdata_path, ceicdata_path, silver_output_path)

    # Output: merged with BOTH Gold + Silver in one file (recommended)
    gold_silver_output_path = csv_path.replace(".csv", "_merged_with_gold_silver.csv")
    merge_with_gold_and_silver_columns(detdata_path, ceicdata_path, gold_silver_output_path)

    # Output: merged with ALL columns from DetData
    all_columns_output_path = csv_path.replace(".csv", "_merged_with_all_columns.csv")
    merge_with_all_columns(detdata_path, ceicdata_path, all_columns_output_path)
