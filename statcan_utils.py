import pandas as pd
from typing import Tuple

# Global constants
TECHNICAL_METADATA = [
    'UOM', 'UOM_ID', 'SCALAR_FACTOR', 'SCALAR_ID', 'DGUID',
    'VECTOR', 'COORDINATE', 'STATUS', 'SYMBOL',
    'TERMINATED', 'DECIMALS'
]

# ---------------------------
# METADATA SUMMARY
# ---------------------------

def build_metadata_summary(df: pd.DataFrame) -> str:
    if df is None or df.empty:
        return "The dataset is empty."

    metadata_info = {
        "UOM": "Unit of Measure (e.g., Number, Percentage, Dollars).",
        "SCALAR_FACTOR": "Scaling applied to values (units, thousands, millions, etc.).",
        "VECTOR": "Unique time-series identifier (e.g., V123456).",
        "COORDINATE": "Concatenation of dimension IDs (max 10 dimensions).",
        "STATUS": "Symbols indicating data state (e.g., A, B, C, X, 0s).",
        "SYMBOL": "Indicates preliminary or revised data (p, r).",
        "TERMINATED": "Indicates a series is no longer updated (t).",
        "DECIMALS": "Number of decimal places for the values."
    }

    header = (
        "\n--------------------------\n"
        "Metadata\n"
        "--------------------------\n"
        "StatCan CSV files contain a set of standardized technical columns.\n"
        "For each standard StatCan metadata field, the summary shows a brief description of what that field means,\n"
        "followed by the actual value(s) found in the dataset.\n"
        "See https://www.statcan.gc.ca/en/developers/csv/user-guide for more detail\n\n"
    )

    output_lines = []

    for col, description in metadata_info.items():
        if col in df.columns:
            values = df[col].dropna().unique()
            values_str = ", ".join(map(str, values))
        else:
            values_str = "Metadata column not found"

        line = f"{col}: {description}\nValue(s): {values_str}\n"
        output_lines.append(line)

    return header + "\n".join(output_lines)


def print_metadata_summary(df: pd.DataFrame) -> None:
    print(build_metadata_summary(df))


# ---------------------------
# DATASET CONSTANTS SUMMARY
# ---------------------------

def build_dataset_constants_summary(df: pd.DataFrame) -> Tuple[str, pd.DataFrame]:
    if df is None or df.empty:
        return "*The dataset is empty*", pd.DataFrame()

    df_no_metadata = df.loc[:, ~df.columns.isin(TECHNICAL_METADATA)]

    output_lines = []

    # ---- Fixed columns ----

    fixed_header = (
        "\n--------------------------\n"
        "Fixed Columns\n"
        "--------------------------\n"
        "These columns contain a single constant value across all rows.\n"
        "They provide context for the dataset but do not vary across observations.\n\n"
    )
    output_lines.append(fixed_header)

    fixed_cols = []
    fixed_lines = []

    for col in df_no_metadata.columns:
        if df_no_metadata[col].nunique(dropna=False) == 1:
            fixed_cols.append(col)
            fixed_value = df_no_metadata[col].iloc[0]
            if hasattr(fixed_value, "item"):
                fixed_value = fixed_value.item()
            fixed_lines.append(f"{col}: Constant value across all rows.\nValue(s): {fixed_value}\n")

    if fixed_lines:
        output_lines.append("\n".join(fixed_lines))
    else:
        output_lines.append("No fixed columns found.\n")

    # ---- Variable columns ----

    variable_header = (
        "\n--------------------------\n"
        "Variable Columns\n"
        "--------------------------\n"
        "These columns contain multiple distinct values across rows.\n"
        "Text columns list every distinct value found. Numeric columns show min, max, mean, and median.\n\n"
    )
    output_lines.append(variable_header)

    variable_cols = []
    variable_lines = []

    for col in df_no_metadata.columns:
        if df_no_metadata[col].nunique(dropna=False) > 1:
            variable_cols.append(col)

            if df_no_metadata[col].dtype == 'object':
                unique_vals = ", ".join(map(str, df_no_metadata[col].dropna().unique()))
                variable_lines.append(f"{col}: Categorical column with multiple distinct values.\nValue(s): {unique_vals}\n")

            elif pd.api.types.is_numeric_dtype(df_no_metadata[col]):
                stats = (
                    f"min={df_no_metadata[col].min()}, "
                    f"max={df_no_metadata[col].max()}, "
                    f"mean={df_no_metadata[col].mean():.2f}, "
                    f"median={df_no_metadata[col].median()}"
                )
                variable_lines.append(f"{col}: Numeric column.\nValue(s): {stats}\n")

    if variable_lines:
        output_lines.append("\n".join(variable_lines))
    else:
        output_lines.append("No variable columns found.\n")
        lines.append(
            "⚠  Numeric stats may be misleading. These values are computed across all rows \n"
            "without grouping. If variable columns above segment the data into distinct series\n "
            "(e.g. different units of measure, adjustment methods, or estimate types), \n"
            "these aggregates mix incompatible values. Filter or group by the categorical\n "
            "columns above before drawing conclusions."
        )
    # ---- Suggested dataframe ----

    suggested_header = (
        "\n--------------------------\n"
        "Suggested DataFrame\n"
        "--------------------------\n"
        "Columns recommended for analysis: those whose values vary across records.\n"
        "Constant-value and technical metadata columns are excluded.\n\n"
    )
    output_lines.append(suggested_header)

    if variable_cols:
        output_lines.append(f"Columns: {variable_cols}\n")
        suggested_df = df_no_metadata[variable_cols]
    else:
        output_lines.append("No variable columns to include.\n")
        suggested_df = pd.DataFrame()

    summary = "".join(output_lines)
    return summary, suggested_df


def print_dataset_constants_summary(df: pd.DataFrame) -> pd.DataFrame:
    summary, suggested_df = build_dataset_constants_summary(df)
    print(summary)
    return suggested_df

# ---------------------------
# COMBINED SCOPE SUMMARY
# ---------------------------

def summarize_dataset_scope(df: pd.DataFrame) -> pd.DataFrame:
    """
    Prints both the metadata summary and the dataset constants summary.
    Returns the suggested DataFrame for further analysis, including UOM
    and SCALAR_FACTOR if they contain more than one unique value.
    """
    print_metadata_summary(df)
    suggested_df = print_dataset_constants_summary(df)

    metadata_to_add = [col for col in ['UOM', 'SCALAR_FACTOR']
                       if col in df.columns and df[col].nunique(dropna=True) > 1]

    if metadata_to_add:
        suggested_df = pd.concat([suggested_df, df[metadata_to_add]], axis=1)

    return suggested_df
