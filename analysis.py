
"""
analysis.py (FIXED)

Processes CPI index-level data and computes additional CPI-style indices using
a consistent, CPI-correct aggregation framework.

Key fixes vs prior version:
1) Correct normalization for exclusion indices and bottom-up core indices (index levels).
2) Core/Protein/Exclusion indices now use inflation_weights flags (not detailed_weights coverage).
3) Unified weight getter: prefers detailed_weights, falls back to inflation_weights.
4) Handles gold/silver naming mismatches across datasets.
5) Avoids hierarchy double-counting by dropping aggregate series (configurable).
6) Removes broken f-string and reduces noisy prints; adds clear warnings.
"""

import json
import warnings
import pandas as pd


# ----------------------------- Load weights -----------------------------

DETAILED_WEIGHTS_PATH = "detailed_weights.json"

try:
    with open(DETAILED_WEIGHTS_PATH, "r") as file:
        detailed_weights = json.load(file)
except FileNotFoundError:
    detailed_weights = {}
    warnings.warn(
        f"'{DETAILED_WEIGHTS_PATH}' not found. Will fallback to inflation_weights only."
    )


# -------------------------- Inflation weights dict -----------------------
# NOTE: Keep your inflation_weights as-is (pasted from your original script).
# I have kept it unchanged except for formatting consistency.
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
        "Protein": 0,
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
        "Protein": 0,
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
        "Protein": 0,
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
        "Protein": 1,
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
        "Protein": 1,
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
        "Protein": 1,
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
        "Protein": 0,
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
        "Protein": 0,
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
        "Protein": 0,
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
        "Protein": 1,
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
        "Protein": 0,
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
        "Protein": 0,
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
        "Protein": 0,
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
        "Protein": 0,
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
        "Protein": 0,
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
        "Protein": 0,
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
        "Protein": 0,
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
        "Protein": 0,
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
        "Protein": 0,
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
        "Protein": 0,
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
        "Protein": 0,
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
        "Protein": 0,
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
        "Protein": 0,
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
        "Protein": 0,
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
        "Protein": 0,
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
        "Protein": 0,
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
        "Protein": 0,
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
        "Protein": 0,
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
        "Protein": 0,
    },
}


# ----------------------------- Configuration -----------------------------

BASE_CPI_COL = "Consumer Price Index"

# Drop aggregate parent series to reduce hierarchy double counting.
# You can expand/adjust this based on your CSV headers.
DROP_AGGREGATES = True
AGGREGATE_SERIES = {
    "Consumer Food Price Index",
    "Consumer Price Index: Food and Beverages",
    "Consumer Price Index: Clothing and Footwear",
    "Consumer Price Index: Miscellaneous",
}


# ------------------------------ Helper functions --------------------------

def get_weight(col: str) -> float:
    """Prefer detailed_weights; fallback to inflation_weights."""
    if col in detailed_weights:
        try:
            return float(detailed_weights[col])
        except Exception:
            return 0.0
    if col in inflation_weights:
        return float(inflation_weights[col].get("weight", 0.0))
    return 0.0


def _filter_cols_present(df: pd.DataFrame, cols: list) -> list:
    return [c for c in cols if c in df.columns]


def _maybe_drop_aggregates(cols: list) -> list:
    if not DROP_AGGREGATES:
        return cols
    return [c for c in cols if c not in AGGREGATE_SERIES]


def weighted_index(df: pd.DataFrame, cols: list, out_col: str) -> pd.DataFrame:
    """
    CPI basket index level:
        Index = sum(w_i * I_i) / sum(w_i)
    """
    cols = _maybe_drop_aggregates(_filter_cols_present(df, cols))
    if not cols:
        warnings.warn(f"[{out_col}] No input columns found in DataFrame. Skipping.")
        return df

    weights = pd.Series({c: get_weight(c) for c in cols}, dtype="float64")
    weights = weights[weights > 0]

    cols = weights.index.tolist()
    if not cols or weights.sum() <= 0:
        raise ValueError(f"[{out_col}] No positive weights found for selected columns.")

    comp = df[cols].fillna(0)
    df[out_col] = comp.mul(weights, axis=1).sum(axis=1) / weights.sum()
    return df


def flagged_columns(df: pd.DataFrame, flag_name: str, value=1) -> list:
    """Return df columns where inflation_weights[col][flag_name] == value."""
    cols = []
    for col, attr in inflation_weights.items():
        if col in df.columns and attr.get(flag_name, 0) == value:
            cols.append(col)
    return _maybe_drop_aggregates(cols)


def exclusion_index(df: pd.DataFrame, base_col: str, exclude_cols: list, out_col: str) -> pd.DataFrame:
    """
    CPI-style exclusion index level:
        ExIndex = (100*Base - sum(w_excl * I_excl)) / (100 - sum(w_excl))
    """
    if base_col not in df.columns:
        raise KeyError(f"[{out_col}] Base column '{base_col}' missing from DataFrame.")

    exclude_cols = _filter_cols_present(df, exclude_cols)
    if not exclude_cols:
        # If nothing to exclude exists, define exclusion index = base
        df[out_col] = df[base_col]
        warnings.warn(f"[{out_col}] No exclude columns present. Copied base index.")
        return df

    w = pd.Series({c: get_weight(c) for c in exclude_cols}, dtype="float64")
    w = w[w > 0]
    exclude_cols = w.index.tolist()

    excl_w = w.sum()
    remaining_w = 100.0 - excl_w
    if remaining_w <= 0:
        raise ValueError(f"[{out_col}] Remaining weight <= 0. Excluded weight = {excl_w}")

    excl_value = df[exclude_cols].fillna(0).mul(w, axis=1).sum(axis=1)
    df[out_col] = (100.0 * df[base_col] - excl_value) / remaining_w
    return df


def resolve_gold_cols(df: pd.DataFrame):
    """Support multiple naming conventions for gold/silver series in your CSV."""
    gold_candidates = [
        "Consumer Price Index: Gold",
        "Consumer Price Index: Miscellaneous: Gold",
    ]
    silver_candidates = [
        "Consumer Price Index: Silver",
        "Consumer Price Index: Miscellaneous: Silver",
    ]
    gold = [c for c in gold_candidates if c in df.columns]
    silver = [c for c in silver_candidates if c in df.columns]
    return gold, silver


# ---------------------------- Index calculations --------------------------

def calculate_core_bottom_up_index(df: pd.DataFrame) -> pd.DataFrame:
    """
    Proper bottom-up core index level:
        Core = (100*CPI - w_food*Food - w_fuel*Fuel) / (100 - w_food - w_fuel)
    """
    print("\n=== Calculating Core Bottom Up Index ===")
    food_col = "Consumer Price Index: Food and Beverages"
    fuel_col = "Consumer Price Index: Fuel and Light"

    if BASE_CPI_COL not in df.columns or food_col not in df.columns or fuel_col not in df.columns:
        warnings.warn("[Core Bottom Up Index] Required columns missing. Skipping.")
        print("❌ SKIPPED: Missing required columns")
        return df

    w_food = get_weight(food_col)
    w_fuel = get_weight(fuel_col)

    remaining = 100.0 - (w_food + w_fuel)
    if remaining <= 0:
        raise ValueError("[Core Bottom Up Index] Remaining weight <= 0. Check weights.")

    df["Core Bottom Up Index"] = (
        (100.0 * df[BASE_CPI_COL]) - (w_food * df[food_col]) - (w_fuel * df[fuel_col])
    ) / remaining
    
    print(f"✓ SUCCESS: Food weight={w_food:.3f}, Fuel weight={w_fuel:.3f}, Remaining={remaining:.3f}")
    print(f"  Sample values (first 3): {df['Core Bottom Up Index'].head(3).tolist()}")

    return df


def calculate_core_index(df: pd.DataFrame) -> pd.DataFrame:
    """Core basket index using 'Core Inflation' flag."""
    print("\n=== Calculating Core Index ===")
    core_cols = flagged_columns(df, "Core Inflation", value=1)
    print(f"  Found {len(core_cols)} components: {core_cols[:5]}{'...' if len(core_cols) > 5 else ''}")
    result = weighted_index(df, core_cols, "Core Index")
    if "Core Index" in result.columns:
        print(f"✓ SUCCESS: Sample values (first 3): {result['Core Index'].head(3).tolist()}")
    return result


def calculate_cpi_ex_veggies(df: pd.DataFrame) -> pd.DataFrame:
    print("\n=== Calculating CPI (ExVeggies) ===")
    veg_col = "Consumer Price Index: Food and Beverages: Vegetables"
    result = exclusion_index(df, BASE_CPI_COL, [veg_col], "CPI (ExVeggies)")
    if "CPI (ExVeggies)" in result.columns:
        print(f"✓ SUCCESS: Sample values (first 3): {result['CPI (ExVeggies)'].head(3).tolist()}")
    return result


def calculate_cpi_ex_gold(df: pd.DataFrame) -> pd.DataFrame:
    print("\n=== Calculating CPI (ExGold) ===")
    gold_cols, _ = resolve_gold_cols(df)
    print(f"  Gold columns found: {gold_cols}")
    result = exclusion_index(df, BASE_CPI_COL, gold_cols, "CPI (ExGold)")
    if "CPI (ExGold)" in result.columns:
        print(f"✓ SUCCESS: Sample values (first 3): {result['CPI (ExGold)'].head(3).tolist()}")
    return result


def calculate_cpi_ex_gold_and_silver(df: pd.DataFrame) -> pd.DataFrame:
    print("\n=== Calculating CPI (ExGold & Silver) ===")
    gold_cols, silver_cols = resolve_gold_cols(df)
    print(f"  Gold: {gold_cols}, Silver: {silver_cols}")
    result = exclusion_index(df, BASE_CPI_COL, gold_cols + silver_cols, "CPI (ExGold & Silver)")
    if "CPI (ExGold & Silver)" in result.columns:
        print(f"✓ SUCCESS: Sample values (first 3): {result['CPI (ExGold & Silver)'].head(3).tolist()}")
    return result


def calculate_core_ex_tnc_index(df: pd.DataFrame) -> pd.DataFrame:
    print("\n=== Calculating Core Ex TnC Index ===")
    cols = flagged_columns(df, "Core Ex TnC", value=1)
    print(f"  Found {len(cols)} components: {cols[:5]}{'...' if len(cols) > 5 else ''}")
    result = weighted_index(df, cols, "Core Ex TnC Index")
    if "Core Ex TnC Index" in result.columns:
        print(f"✓ SUCCESS: Sample values (first 3): {result['Core Ex TnC Index'].head(3).tolist()}")
    return result


def calculate_core_core_exc_index(df: pd.DataFrame) -> pd.DataFrame:
    """
    FIXED CPI-consistent interpretation of 'Core Core Exc':
      - flag == 1  : include
      - flag == -1 : exclude
      - flag == 0  : ignore

    This avoids negative weights and produces a proper basket index.
    """
    print("\n=== Calculating Core Core Exc Index ===")
    include = flagged_columns(df, "Core Core Exc", value=1)
    exclude = flagged_columns(df, "Core Core Exc", value=-1)
    print(f"  Include ({len(include)}): {include[:3]}{'...' if len(include) > 3 else ''}")
    print(f"  Exclude ({len(exclude)}): {exclude}")

    include = [c for c in include if c not in exclude]
    if not include:
        warnings.warn("[Core Core Exc Index] No included columns found. Skipping.")
        print("❌ SKIPPED: No columns to include")
        return df

    result = weighted_index(df, include, "Core Core Exc Index")
    if "Core Core Exc Index" in result.columns:
        print(f"✓ SUCCESS: Sample values (first 3): {result['Core Core Exc Index'].head(3).tolist()}")
    return result


def calculate_custom_index_1(df: pd.DataFrame) -> pd.DataFrame:
    print("\n=== Calculating Custom Index 1 ===")
    cols = flagged_columns(df, "Custom Index 1", value=1)
    print(f"  Found {len(cols)} components: {cols[:5]}{'...' if len(cols) > 5 else ''}")
    result = weighted_index(df, cols, "Custom Index 1")
    if "Custom Index 1" in result.columns:
        print(f"✓ SUCCESS: Sample values (first 3): {result['Custom Index 1'].head(3).tolist()}")
    return result


def calculate_custom_index_2(df: pd.DataFrame) -> pd.DataFrame:
    print("\n=== Calculating Custom Index 2 ===")
    cols = flagged_columns(df, "Custom Index 2", value=1)
    print(f"  Found {len(cols)} components: {cols[:5]}{'...' if len(cols) > 5 else ''}")
    result = weighted_index(df, cols, "Custom Index 2")
    if "Custom Index 2" in result.columns:
        print(f"✓ SUCCESS: Sample values (first 3): {result['Custom Index 2'].head(3).tolist()}")
    return result


def calculate_exclusion_index(df: pd.DataFrame) -> pd.DataFrame:
    """Exclusion basket index using 'Exclusion Index' flag."""
    print("\n=== Calculating Exclusion Index ===")
    cols = flagged_columns(df, "Exclusion Index", value=1)
    print(f"  Found {len(cols)} components: {cols[:5]}{'...' if len(cols) > 5 else ''}")
    result = weighted_index(df, cols, "Exclusion Index")
    if "Exclusion Index" in result.columns:
        print(f"✓ SUCCESS: Sample values (first 3): {result['Exclusion Index'].head(3).tolist()}")
    return result


def calculate_rbi_core_index(df: pd.DataFrame) -> pd.DataFrame:
    print("\n=== Calculating RBI Core Index ===")
    cols = flagged_columns(df, "RBI Core", value=1)
    print(f"  Found {len(cols)} components: {cols}")
    result = weighted_index(df, cols, "RBI Core Index")
    if "RBI Core Index" in result.columns:
        print(f"✓ SUCCESS: Sample values (first 3): {result['RBI Core Index'].head(3).tolist()}")
    return result


def calculate_protein_index(df: pd.DataFrame) -> pd.DataFrame:
    print("\n=== Calculating Protein Index ===")
    cols = flagged_columns(df, "Protein", value=1)
    print(f"  Found {len(cols)} components: {cols}")
    result = weighted_index(df, cols, "Protein Index")
    if "Protein Index" in result.columns:
        print(f"✓ SUCCESS: Sample values (first 3): {result['Protein Index'].head(3).tolist()}")
    return result


# ----------------------------- Processing pipeline ------------------------

def process_cleaned_inflation(input_file: str, output_file: str) -> None:
    print(f"\n{'='*70}")
    print(f"STARTING INFLATION INDEX CALCULATIONS")
    print(f"{'='*70}")
    print(f"Input file: {input_file}")
    print(f"Output file: {output_file}")
    
    df = pd.read_csv(input_file)
    print(f"\n✓ Loaded data: {len(df)} rows, {len(df.columns)} columns")

    if BASE_CPI_COL not in df.columns:
        raise KeyError(f"'{BASE_CPI_COL}' is missing from the input CSV. Cannot proceed.")
    
    print(f"✓ Base CPI column found: '{BASE_CPI_COL}'")
    
    # Track which indices were successfully created
    initial_cols = set(df.columns)

    # 1) Bottom-up core (normalized)
    df = calculate_core_bottom_up_index(df)

    # 2) Basket-based indices (flag-driven)
    df = calculate_core_index(df)
    df = calculate_core_ex_tnc_index(df)
    df = calculate_core_core_exc_index(df)
    df = calculate_rbi_core_index(df)
    df = calculate_protein_index(df)
    df = calculate_custom_index_1(df)
    df = calculate_custom_index_2(df)
    df = calculate_exclusion_index(df)

    # 3) Exclusion indices (normalized)
    df = calculate_cpi_ex_veggies(df)
    df = calculate_cpi_ex_gold(df)
    df = calculate_cpi_ex_gold_and_silver(df)

    # Summary
    new_cols = set(df.columns) - initial_cols
    print(f"\n{'='*70}")
    print(f"CALCULATION SUMMARY")
    print(f"{'='*70}")
    print(f"✓ Created {len(new_cols)} new indices:")
    for col in sorted(new_cols):
        non_null = df[col].notna().sum()
        print(f"  - {col:40s} ({non_null:,} non-null values)")
    
    df.to_csv(output_file, index=False)
    print(f"\n✓ Processed inflation data saved to: {output_file}")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    input_file = "cleaned_merged_with_all_columns.csv"
    output_file = "cleaned_inflation_with_calculations.csv"
    process_cleaned_inflation(input_file, output_file)
