"""
analysis.py

This script is designed to process inflation data by calculating various indices based on predefined weights and attributes. It uses a dictionary (`inflation_weights`) to store the weights and attributes for different categories of the Consumer Price Index (CPI). The script provides functions to calculate indices such as Core Bottom Up, Core Index, CPI (ExVeggies), and others. These indices are added as new columns to the input dataset.

Key Components:
1. **inflation_weights**:
   - A dictionary containing weights and attributes for various CPI categories.
   - Attributes include flags for different indices (e.g., `Core Inflation`, `Protein`, etc.).

2. **Functions**:
   - `calculate_bottom_up_inflation`: Computes Core Bottom Up inflation.
   - `calculate_core_index`: Calculates the Core Index based on core inflation values and weights.
   - `calculate_cpi_ex_veggies`: Computes CPI excluding vegetables.
   - `calculate_core_ex_tnc_index`: Calculates Core Ex TnC Index using weighted sums.
   - `calculate_core_core_exc_index`: Computes Core Core Exc Index, accounting for negative weights.
   - `calculate_custom_index_1`: Calculates Custom Index 1.
   - `calculate_custom_index_2`: Calculates Custom Index 2.
   - `calculate_exclusion_index`: Computes the Exclusion Index.
   - `calculate_rbi_core_index`: Calculates the RBI Core Index.
   - `calculate_protein_index`: Computes the Protein Index based on relevant categories.
   - `calculate_generic_exclusion_index`: Calculates a generic exclusion index by excluding specified columns.

3. **Main Functionality**:
   - Reads the input CSV file containing cleaned inflation data.
   - Applies all the calculation functions to add new indices as columns.
   - Saves the processed data to a new CSV file.

4. **Usage**:
   - The script is executed as a standalone program.
   - Input file: `cleaned_inflation_merged_with_gold.csv`
   - Output file: `cleaned_inflation_with_calculations.csv`

5. **Error Handling**:
   - Includes checks for missing columns in the input data.
   - Raises errors for invalid configurations in `inflation_weights` (e.g., zero weights).

6. **Dependencies**:
   - Requires `pandas` library for data manipulation.

This script is a critical component for analyzing inflation data and generating insights based on various indices.
"""

import pandas as pd
import json

# Load weights from detailed_weights.json
with open("detailed_weights.json", "r") as file:
    detailed_weights = json.load(file)

inflation_weights = {
    "Consumer Food Price Index": {
        "weight": 39.060,
        "is_food_inflation": 0,
        "Core Inflation": 0,
        "Core Ex TnC": 0,
        "Core Core Exc": 0,
        "Custom Index 1": 0,
        "Custom Index 2": 0,
        "Exclusion Index": 0,
        "RBI Core": 0,
        "Protein": 0,  # Added Protein key
    },
    "Consumer Price Index: Food and Beverages": {
        "weight": 45.860,
        "is_food_inflation": 0,
        "Core Inflation": 0,
        "Core Ex TnC": 0,
        "Core Core Exc": 0,
        "Custom Index 1": 0,
        "Custom Index 2": 0,
        "Exclusion Index": 0,
        "RBI Core": 0,
        "Protein": 0,  # Added Protein key
    },
    "Consumer Price Index: Food and Beverages: Cereals and Products": {
        "weight": 9.670,
        "is_food_inflation": 1,
        "Core Inflation": 0,
        "Core Ex TnC": 0,
        "Core Core Exc": 0,
        "Custom Index 1": 0,
        "Custom Index 2": 0,
        "Exclusion Index": 1,
        "RBI Core": 0,
        "Protein": 0,  # Added Protein key
    },
    "Consumer Price Index: Food and Beverages: Meat and Fish": {
        "weight": 3.610,
        "is_food_inflation": 1,
        "Core Inflation": 0,
        "Core Ex TnC": 0,
        "Core Core Exc": 0,
        "Custom Index 1": 0,
        "Custom Index 2": 0,
        "Exclusion Index": 1,
        "RBI Core": 0,
        "Protein": 1,  # Added Protein key
    },
    "Consumer Price Index: Food and Beverages: Egg": {
        "weight": 0.430,
        "is_food_inflation": 1,
        "Core Inflation": 0,
        "Core Ex TnC": 0,
        "Core Core Exc": 0,
        "Custom Index 1": 0,
        "Custom Index 2": 0,
        "Exclusion Index": 1,
        "RBI Core": 0,
        "Protein": 1,  # Added Protein key
    },
    "Consumer Price Index: Food and Beverages: Milk and Milk Product": {
        "weight": 6.610,
        "is_food_inflation": 1,
        "Core Inflation": 0,
        "Core Ex TnC": 0,
        "Core Core Exc": 0,
        "Custom Index 1": 0,
        "Custom Index 2": 0,
        "Exclusion Index": 1,
        "RBI Core": 0,
        "Protein": 1,  # Added Protein key
    },
    "Consumer Price Index: Food and Beverages: Oils and Fats": {
        "weight": 3.560,
        "is_food_inflation": 1,
        "Core Inflation": 0,
        "Core Ex TnC": 0,
        "Core Core Exc": 0,
        "Custom Index 1": 0,
        "Custom Index 2": 0,
        "Exclusion Index": 0,
        "RBI Core": 0,
        "Protein": 0,  # Added Protein key
    },
    "Consumer Price Index: Food and Beverages: Fruits": {
        "weight": 2.890,
        "is_food_inflation": 1,
        "Core Inflation": 0,
        "Core Ex TnC": 0,
        "Core Core Exc": 0,
        "Custom Index 1": 0,
        "Custom Index 2": 0,
        "Exclusion Index": 0,
        "RBI Core": 0,
        "Protein": 0,  # Added Protein key
    },
    "Consumer Price Index: Food and Beverages: Vegetables": {
        "weight": 6.040,
        "is_food_inflation": 1,
        "Core Inflation": 0,
        "Core Ex TnC": 0,
        "Core Core Exc": 0,
        "Custom Index 1": 0,
        "Custom Index 2": 0,
        "Exclusion Index": 0,
        "RBI Core": 0,
        "Protein": 0,  # Added Protein key
    },
    "Consumer Price Index: Food and Beverages: Pulses and Products": {
        "weight": 2.380,
        "is_food_inflation": 1,
        "Core Inflation": 0,
        "Core Ex TnC": 0,
        "Core Core Exc": 0,
        "Custom Index 1": 0,
        "Custom Index 2": 0,
        "Exclusion Index": 1,
        "RBI Core": 0,
        "Protein": 1,  # Added Protein key
    },
    "Consumer Price Index: Food and Beverages: Sugar and Confectionery": {
        "weight": 1.360,
        "is_food_inflation": 1,
        "Core Inflation": 0,
        "Core Ex TnC": 0,
        "Core Core Exc": 0,
        "Custom Index 1": 0,
        "Custom Index 2": 0,
        "Exclusion Index": 1,
        "RBI Core": 0,
        "Protein": 0,  # Added Protein key
    },
    "Consumer Price Index: Food and Beverages: Spices": {
        "weight": 2.500,
        "is_food_inflation": 1,
        "Core Inflation": 0,
        "Core Ex TnC": 0,
        "Core Core Exc": 0,
        "Custom Index 1": 0,
        "Custom Index 2": 0,
        "Exclusion Index": 1,
        "RBI Core": 0,
        "Protein": 0  # Added Protein key
    },
    "Consumer Price Index: Food and Beverages: Non-alcholic Beverages": {
        "weight": 1.260,
        "is_food_inflation": 0,
        "Core Inflation": 0,
        "Core Ex TnC": 0,
        "Core Core Exc": 0,
        "Custom Index 1": 0,
        "Custom Index 2": 0,
        "Exclusion Index": 1,
        "RBI Core": 0,
        "Protein": 0,  # Added Protein key
    },
    "Consumer Price Index: Food and Beverages: Prepared Meals, Snacks, Sweets, etc": {
        "weight": 5.550,
        "is_food_inflation": 0,
        "Core Inflation": 0,
        "Core Ex TnC": 0,
        "Core Core Exc": 0,
        "Custom Index 1": 0,
        "Custom Index 2": 0,
        "Exclusion Index": 1,
        "RBI Core": 0,
        "Protein": 0,  # Added Protein key
    },
    "Consumer Price Index: Pan, Tobacco and Intoxicants": {
        "weight": 2.380,
        "is_food_inflation": 0,
        "Core Inflation": 1,
        "Core Ex TnC": 1,
        "Core Core Exc": 1,
        "Custom Index 1": 0,
        "Custom Index 2": 0,
        "Exclusion Index": 0,
        "RBI Core": 0,
        "Protein": 0,  # Added Protein key
    },
    "Consumer Price Index: Clothing and Footwear": {
        "weight": 6.530,
        "is_food_inflation": 0,
        "Core Inflation": 0,
        "Core Ex TnC": 0,
        "Core Core Exc": 1,
        "Custom Index 1": 0,
        "Custom Index 2": 0,
        "Exclusion Index": 0,
        "RBI Core": 1,
        "Protein": 0,  # Added Protein key
    },
        "Consumer Price Index: Clothing and Footwear: Clothing": {
        "weight": 5.580,
        "is_food_inflation": 0,
        "Core Inflation": 1,
        "Core Ex TnC": 1,
        "Core Core Exc": 0,
        "Custom Index 1": 1,
        "Custom Index 2": 1,
        "Exclusion Index": 0,
        "RBI Core": 0,
        "Protein": 0,  # Added Protein key
    },
        "Consumer Price Index: Clothing and Footwear: Footwear": {
        "weight": 0.950,
        "is_food_inflation": 0,
        "Core Inflation": 1,
        "Core Ex TnC": 1,
        "Core Core Exc": 0,
        "Custom Index 1": 1,
        "Custom Index 2": 1,
        "Exclusion Index": 0,
        "RBI Core": 0,
        "Protein": 0,  # Added Protein key
    },
    "Consumer Price Index: Housing": {
        "weight": 10.070,
        "is_food_inflation": 0,
        "Core Inflation": 1,
        "Core Ex TnC": 1,
        "Core Core Exc": 1,
        "Custom Index 1": 0,
        "Custom Index 2": 1,
        "Exclusion Index": 0,
        "RBI Core": 1,
        "Protein": 0,  # Added Protein key
    },
    "Consumer Price Index: Fuel and Light": {
        "weight": 6.840,
        "is_food_inflation": 0,
        "Core Inflation": 0,
        "Core Ex TnC": 0,
        "Core Core Exc": 0,
        "Custom Index 1": 0,
        "Custom Index 2": 0,
        "Exclusion Index": 0,
        "RBI Core": 0,
        "Protein": 0,  # Added Protein key
    },
    "Consumer Price Index: Miscellaneous": {
        "weight": 28.320,
        "is_food_inflation": 0,
        "Core Inflation": 0,
        "Core Ex TnC": 0,
        "Core Core Exc": 1,
        "Custom Index 1": 0,
        "Custom Index 2": 0,
        "Exclusion Index": 0,
        "RBI Core": 1,
        "Protein": 0,  # Added Protein key
    },
    "Consumer Price Index: Miscellaneous: Household Goods and Services": {
        "weight": 3.800,
        "is_food_inflation": 0,
        "Core Inflation": 1,
        "Core Ex TnC": 1,
        "Core Core Exc": 0,
        "Custom Index 1": 1,
        "Custom Index 2": 1,
        "Exclusion Index": 0,
        "RBI Core": 0,
        "Protein": 0,  # Added Protein key
    },
    "Consumer Price Index: Miscellaneous: Health": {
        "weight": 5.890,
        "is_food_inflation": 0,
        "Core Inflation": 1,
        "Core Ex TnC": 1,
        "Core Core Exc": 0,
        "Custom Index 1": 1,
        "Custom Index 2": 1,
        "Exclusion Index": 0,
        "RBI Core": 0,
        "Protein": 0,  # Added Protein key
    },
    "Consumer Price Index: Miscellaneous: Transport and Communication": {
        "weight": 8.590,
        "is_food_inflation": 0,
        "Core Inflation": 1,
        "Core Ex TnC": 0,
        "Core Core Exc": -1,
        "Custom Index 1": 1,
        "Custom Index 2": 1,
        "Exclusion Index": 0,
        "RBI Core": 0,
        "Protein": 0,  # Added Protein key
    },
    "Consumer Price Index: Miscellaneous: Recreation and Amusement": {
        "weight": 1.680,
        "is_food_inflation": 0,
        "Core Inflation": 1,
        "Core Ex TnC": 1,
        "Core Core Exc": 0,
        "Custom Index 1": 1,
        "Custom Index 2": 1,
        "Exclusion Index": 0,
        "RBI Core": 0,
        "Protein": 0,  # Added Protein key
    },
    "Consumer Price Index: Miscellaneous: Education": {
        "weight": 4.460,
        "is_food_inflation": 0,
        "Core Inflation": 1,
        "Core Ex TnC": 1,
        "Core Core Exc": 0,
        "Custom Index 1": 1,
        "Custom Index 2": 1,
        "Exclusion Index": 0,
        "RBI Core": 0,
        "Protein": 0,  # Added Protein key
    },
    "Consumer Price Index: Miscellaneous: Personal Care and Effects": {
        "weight": 3.890,
        "is_food_inflation": 0,
        "Core Inflation": 1,
        "Core Ex TnC": 1,
        "Core Core Exc": 0,
        "Custom Index 1": 1,
        "Custom Index 2": 1,
        "Exclusion Index": 0,
        "RBI Core": 0,
        "Protein": 0,  # Added Protein key
    },
    "Consumer Price Index: Gold": {
        "weight": 1.08035,
        "is_food_inflation": 0,
        "Core Inflation": 0,
        "Core Ex TnC": 0,
        "Core Core Exc": 0,
        "Custom Index 1": 0,
        "Custom Index 2": 0,
        "Exclusion Index": 0,
        "RBI Core": 0,
        "Protein": 0  # Added Protein key
    },
    "Consumer Price Index: Silver": {
        "weight": 0.11175,
        "is_food_inflation": 0,
        "Core Inflation": 0,
        "Core Ex TnC": 0,
        "Core Core Exc": 0,
        "Custom Index 1": 0,
        "Custom Index 2": 0,
        "Exclusion Index": 0,
        "RBI Core": 0,
        "Protein": 0  # Added Protein key
    },
}


#Food Inflation - Change in % in Food Price Index

#Clothing and Footwear - Change in % of CPI Clothing and Footwear



#Misc - Change in percentage of Miscellaneous :  Health

#Core Bottom Up
#Formula - (Consumer Price Index - (Food and Beverages Weight * Food and Beverages Index)/100 - (Fuel and Light Weight * Fuel and Light Index)/100)
# The data is in the dictionary


#Core Index
#Formula - Sum product of core inflation value in the dictionary, weight of the column and then sum. After the sum divide by 47.29


#Core %Inflaftion - CPI Inflation

def calculate_bottom_up_inflation(df):
    """
    Calculate Core Bottom Up inflation using the formula:
    Consumer Price Index - (Food and Beverages Weight * Food and Beverages Index)/100 - (Fuel and Light Weight * Fuel and Light Index)/100
    """
    if "Consumer Price Index" in df.columns and \
       "Consumer Price Index: Food and Beverages" in df.columns and \
       "Consumer Price Index: Fuel and Light" in df.columns:
        df["Core Bottom Up"] = df["Consumer Price Index"] - \
            ((inflation_weights["Consumer Price Index: Food and Beverages"]["weight"]/100) * df["Consumer Price Index: Food and Beverages"]) - \
            ((inflation_weights["Consumer Price Index: Fuel and Light"]["weight"]/100) * df["Consumer Price Index: Fuel and Light"])
    return df

def calculate_core_index(df):
    """
    Calculate Core Index using the formula:
    Sum product of core inflation values and weights, divided by the sum of weights.
    """
    core_columns = [col for col in df.columns if col in detailed_weights]
    if core_columns:
        # Create a Series of weights indexed by column names for alignment
        weights = pd.Series({col: detailed_weights[col] for col in core_columns})
        # Multiply the DataFrame columns by their corresponding weights
        df["Core Index"] = df[core_columns].mul(weights, axis=1).sum(axis=1) / weights.sum()
    return df

def calculate_cpi_ex_veggies(df):
    """
    Calculate CPI (ExVeggies) using the formula:
    Consumer Price Index - (Weight of Food and Beverages: Vegetables * Food and Beverages: Vegetables Index) / 100
    """
    if "Consumer Price Index" in df.columns and "Consumer Price Index: Food and Beverages: Vegetables" in df.columns:
        df["CPI (ExVeggies)"] = df["Consumer Price Index"] - \
            ((inflation_weights["Consumer Price Index: Food and Beverages: Vegetables"]["weight"] / 100) * 
             df["Consumer Price Index: Food and Beverages: Vegetables"])
    return df

def calculate_cpi_ex_gold(df):
    """
    Calculate CPI (ExGold) using the generic exclusion function.
    """
    exclude_columns = ["Consumer Price Index: Miscellaneous: Gold"]
    base_column = "Consumer Price Index"
    print(f"Calculating CPI (ExGold) by excluding columns: {exclude_columns}")
    df = calculate_generic_exclusion_index(df, exclude_columns, base_column)
    print("CPI (ExGold) calculation completed.")
    return df

def calculate_cpi_ex_gold_and_silver(df):
    """
    Calculate CPI (ExGold and Silver) using the generic exclusion function.
    """
    exclude_columns = ["Consumer Price Index: Miscellaneous: Gold", "Consumer Price Index: Miscellaneous: Silver"]
    base_column = "Consumer Price Index"
    print(f"Calculating CPI (ExGold and Silver) by excluding columns: {exclude_columns}")
    df = calculate_generic_exclusion_index(df, exclude_columns, base_column)
    print("CPI (ExGold and Silver) calculation completed.")
    return df

def calculate_core_ex_tnc_index(df):
    """
    Calculate Core Ex TnC Index using the formula:
    Sum product of Core Ex TnC values and weights, divided by the sum of Core Ex TnC weights.
    """
    # Filter columns where Core Ex TnC is 1
    core_ex_tnc_columns = [col for col, attr in inflation_weights.items() if attr.get("Core Ex TnC", 0) and col in df.columns]
    if core_ex_tnc_columns:
        # Create a Series of weights indexed by column names for alignment
        weights = pd.Series({col: inflation_weights[col]["weight"] for col in core_ex_tnc_columns})
        # Multiply the DataFrame columns by their corresponding weights
        df["Core Ex TnC Index"] = df[core_ex_tnc_columns].mul(weights, axis=1).sum(axis=1) / weights.sum()
    return df


def calculate_core_core_exc_index(df):
    """
    Calculate Core Core Exc Index using the formula:
    Sum product of Core Core Exc values and weights (including negative weights), divided by the sum of weights.
    """
    # Filter columns where Core Core Exc is not 0
    core_core_exc_columns = [col for col, attr in inflation_weights.items() if attr.get("Core Core Exc", 0) != 0 and col in df.columns]
    print(f"Core Core Exc Columns: {core_core_exc_columns}")  # Debugging

    if core_core_exc_columns:
        # Create a Series of weights indexed by column names for alignment
        weights = pd.Series({col: inflation_weights[col]["weight"] * attr["Core Core Exc"] for col, attr in inflation_weights.items() if col in core_core_exc_columns})
        print(f"Weights (with signs): {weights}")  # Debugging

        # Check for zero weights
        if weights.sum() == 0:
            raise ValueError("Sum of weights for Core Core Exc Index is zero. Check inflation_weights configuration.")

        # Multiply the DataFrame columns by their corresponding weights
        df["Core Core Exc Index"] = df[core_core_exc_columns].mul(weights, axis=1).sum(axis=1) / weights.sum()
    else:
        raise KeyError("No columns found for Core Core Exc Index. Check inflation_weights or input data.")

    return df

def calculate_custom_index_1(df):
    """
    Calculate Custom Index 1 using the formula:
    Sum product of Custom Index 1 values and weights, divided by the sum of Custom Index 1 weights.
    """
    custom_index_1_columns = [col for col, attr in inflation_weights.items() if attr.get("Custom Index 1", 0) and col in df.columns]
    if custom_index_1_columns:
        weights = pd.Series({col: inflation_weights[col]["weight"] for col in custom_index_1_columns})
        df["Custom Index 1"] = df[custom_index_1_columns].mul(weights, axis=1).sum(axis=1) / weights.sum()
    return df

def calculate_custom_index_2(df):
    """
    Calculate Custom Index 2 using the formula:
    Sum product of Custom Index 2 values and weights, divided by the sum of Custom Index 2 weights.
    """
    custom_index_2_columns = [col for col, attr in inflation_weights.items() if attr.get("Custom Index 2", 0) and col in df.columns]
    if custom_index_2_columns:
        weights = pd.Series({col: inflation_weights[col]["weight"] for col in custom_index_2_columns})
        df["Custom Index 2"] = df[custom_index_2_columns].mul(weights, axis=1).sum(axis=1) / weights.sum()
    return df

def calculate_exclusion_index(df):
    """
    Calculate Exclusion Index using the formula:
    Sum product of Exclusion Index values and weights, divided by the sum of weights.
    """
    exclusion_index_columns = [col for col in df.columns if col in detailed_weights]
    if exclusion_index_columns:
        weights = pd.Series({col: detailed_weights[col] for col in exclusion_index_columns})
        df["Exclusion Index"] = df[exclusion_index_columns].mul(weights, axis=1).sum(axis=1) / weights.sum()
    return df

def calculate_rbi_core_index(df):
    """
    Calculate RBI Core Index using the formula:
    Sum product of RBI Core values and weights, divided by the sum of RBI Core weights.
    """
    rbi_core_columns = [col for col, attr in inflation_weights.items() if attr.get("RBI Core", 0) and col in df.columns]
    if rbi_core_columns:
        weights = pd.Series({col: inflation_weights[col]["weight"] for col in rbi_core_columns})
        df["RBI Core Index"] = df[rbi_core_columns].mul(weights, axis=1).sum(axis=1) / weights.sum()
    return df


def calculate_protein_index(df):
    """
    Calculate Protein Index using the formula:
    Sum product of Protein values and weights, divided by the sum of Protein weights.
    """
    protein_columns = [col for col in df.columns if col in detailed_weights]
    if protein_columns:
        weights = pd.Series({col: detailed_weights[col] for col in protein_columns})
        df["Protein Index"] = df[protein_columns].mul(weights, axis=1).sum(axis=1) / weights.sum()
    return df

def calculate_generic_exclusion_index(df, exclude_columns, base_column):
    """
    Calculate a generic exclusion index by excluding specified columns.

    Parameters:
        df (pd.DataFrame): The input DataFrame containing the data.
        exclude_columns (list): List of column names to exclude from the calculation.
        base_column (str): The column to use as the base for the calculation.

    Returns:
        pd.DataFrame: The DataFrame with the calculated exclusion index added as a new column.
    """
    print(f"Base column: {base_column}")
    print(f"Exclude columns: {exclude_columns}")

    # Validate that the base column exists
    if base_column not in df.columns:
        raise KeyError(f"Base column '{base_column}' is missing from the DataFrame.")

    # Validate that all exclude columns exist
    missing_columns = [col for col in exclude_columns if col not in df.columns]
    if missing_columns:
        print(f"Warning: The following columns are missing and will be ignored: {missing_columns}")
        exclude_columns = [col for col in exclude_columns if col in df.columns]

    print(f"Columns after validation: {exclude_columns}")

    # Replace NaN values in the excluded columns with zeros
    df[exclude_columns] = df[exclude_columns].fillna(0)

    # Calculate the total weight excluding the specified columns
    total_weight = 100 - sum(detailed_weights.get(col, 0) for col in exclude_columns)
    print(f"Total weight after exclusions: {total_weight}")

    if total_weight == 0:
        raise ValueError("Total weight after exclusions is zero. Cannot calculate exclusion index.")

    # Calculate the exclusion index
    exclusion_value = 0
    for col in exclude_columns:
        if col in df.columns:
            weight = detailed_weights.get(col, 0)
            print(f"Column: {col}, Weight: {weight}, Data: {df[col].head().to_list()}")
            exclusion_value += weight * df[col]

    print(f"Exclusion value: {exclusion_value.head().to_list()}")

    df[f"Exclusion Index (Excluding {', '.join(exclude_columns)})"] = (
        (100 * df[base_column] - exclusion_value) / total_weight
    )

    print(f"Exclusion Index calculated: {df[f'Exclusion Index (Excluding {', '.join(exclude_columns)})'].head().to_list()}")

    return df


def process_cleaned_inflation(input_file, output_file):
    """
    Process the cleaned inflation file to add calculated columns.
    """
    # Read the input file
    df = pd.read_csv(input_file)

    # Calculate Core Bottom Up inflation
    df = calculate_bottom_up_inflation(df)

    # Calculate Core Index
    df = calculate_core_index(df)

    # Calculate CPI (ExVeggies)
    df = calculate_cpi_ex_veggies(df)

    # Calculate CPI (ExGold)
    df = calculate_cpi_ex_gold(df)

    # Calculate CPI (ExGold and Silver)
    df = calculate_cpi_ex_gold_and_silver(df)

    # Calculate Core Ex TnC Index
    df = calculate_core_ex_tnc_index(df)

    # Calculate Core Core Exc Index
    df = calculate_core_core_exc_index(df)

    # Calculate Custom Index 1
    df = calculate_custom_index_1(df)

    # Calculate Custom Index 2
    df = calculate_custom_index_2(df)

    # Calculate Exclusion Index
    df = calculate_exclusion_index(df)

    # Calculate RBI Core Index
    df = calculate_rbi_core_index(df)

    # Add this line to calculate Protein Index
    df = calculate_protein_index(df)

    # Save the resulting DataFrame to a new CSV file
    df.to_csv(output_file, index=False)
    print(f"Processed inflation data saved to {output_file}")


if __name__ == "__main__":
    # Define file paths
    input_file = "cleaned_merged_with_all_columns.csv"
    output_file = "cleaned_inflation_with_calculations.csv"

    # Process the cleaned inflation file
    process_cleaned_inflation(input_file, output_file)



