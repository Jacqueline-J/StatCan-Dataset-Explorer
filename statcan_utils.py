import pandas as pd
from typing import Tuple

# Global constants

# Statistics Canada provides standardized data, the metadata reported includes
# the following columns. These should be the same for all datasets.
# While they provide important information for understanding the dataset
# these are not directly useful in the analysis, and so can be excluded
# from the dataframe when analyzing trends/gathering data

TECHNICAL_METADATA = [
    'UOM', 'UOM_ID', 'SCALAR_FACTOR', 'SCALAR_ID', 'DGUID',
    'VECTOR', 'COORDINATE', 'STATUS', 'SYMBOL',
    'TERMINATED', 'DECIMALS'
]

# ---------------------------
# METADATA SUMMARY
# ---------------------------

def build_metadata_summary(df: pd.DataFrame) -> str:
    """
    Builds and returns a formatted string summarizing the StatCan metadata
    fields present in the dataset. StatCan CSV files contain standardized
    technical columns (e.g., UOM, SCALAR_FACTOR, VECTOR, STATUS) that
    describe how data should be interpreted rather than representing
    analytical variables themselves.
    """

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
        "\033[1mMetadata\033[0m:\n"
        "--------------------------\n"
        "StatCan CSV files contain a set of standardized technical columns.\n"
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
    """Prints the metadata summary to the console."""
    print(build_metadata_summary(df))


# ---------------------------
# DATASET CONSTANTS SUMMARY
# ---------------------------

def build_dataset_constants_summary(df: pd.DataFrame) -> Tuple[str, pd.DataFrame]:

    """
    Builds a formatted string summary of the dataset by identifying:
    - Fixed columns (single unique value across all rows)
    - Variable columns (multiple values)
    - Basic statistics for numeric variable columns

    Also returns a suggested DataFrame containing only variable columns,
    with technical metadata columns excluded.

    Returns:
        summary (str): The formatted summary text.
        suggested_df (pd.DataFrame): DataFrame with only variable columns.
    """

    if df is None or df.empty:
        return "*The dataset is empty*", pd.DataFrame()

    df_no_metadata = df.loc[:, ~df.columns.isin(TECHNICAL_METADATA)]

    lines = []

    # ---- Fixed columns ----

    lines.append("\n-------------------")
    lines.append("\033[1mFIXED SUMMARY\033[0m:")
    lines.append("-------------------")
    lines.append("The dataset contains the following fixed attributes:\n")
    lines.append(f"{'Column':<25} {'Value':<30}")

    fixed_cols = []

    for col in df_no_metadata.columns:
        if df_no_metadata[col].nunique(dropna=False) == 1:
            fixed_cols.append(col)
            fixed_value = df_no_metadata[col].iloc[0]

            if hasattr(fixed_value, "item"):
                fixed_value = fixed_value.item()

            lines.append(f"\033[1m{col:<25}\033[0m: {fixed_value:<30}")

    if not fixed_cols:
        lines.append("*No fixed columns found*")

    if df_no_metadata.empty:
        lines.append("No non-metadata columns remain.")

    lines.append("\nThese columns provide context but do not change across observations.")

    # ---- Variable columns ----

    lines.append("\n-------------------")
    lines.append("\033[1mVARIABLE SUMMARY\033[0m:")
    lines.append("-------------------")
    lines.append("The dataset contains the following variable attributes:\n")

    variable_cols = []
    object_cols = []
    numeric_cols = []

    for col in df_no_metadata.columns:
        if df_no_metadata[col].nunique(dropna=True) > 1:
            variable_cols.append(col)

            if df_no_metadata[col].dtype == 'object':
                object_cols.append(col)
            elif pd.api.types.is_numeric_dtype(df_no_metadata[col]):
                numeric_cols.append(col)

    if not object_cols:
        lines.append("*No non-numeric columns found*")
    else:
        for col in object_cols:
            unique_vals = df_no_metadata[col].dropna().unique()
            lines.append(f"\033[1m{col}\033[0m:")
            lines.append(", ".join(map(str, unique_vals)))

    lines.append("")

    if not numeric_cols:
        lines.append("*No numeric columns found*")
    else:
        for col in numeric_cols:
            stats = {
                'min': df_no_metadata[col].min(),
                'max': df_no_metadata[col].max(),
                'mean': df_no_metadata[col].mean(),
                'median': df_no_metadata[col].median()
            }
            lines.append(f"\033[1m{col}\033[0m:")
            for k, v in stats.items():
                lines.append(f"  {k}: {v}")
            lines.append("")

    # ---- Suggested dataframe ----

    lines.append("\n-------------------")
    lines.append("\033[1mSUGGESTED DATAFRAME\033[0m:")
    lines.append("-------------------")
    lines.append("The following columns are suggested for analysis because")
    lines.append("their values vary across records. Columns containing only")
    lines.append("constant values, as well as metadata columns, are not included.\n")

    if not variable_cols:
        lines.append("*No variable columns to include*")
        return "\n".join(lines), pd.DataFrame()

    lines.append(str(variable_cols))

    suggested_df = df_no_metadata[variable_cols]
    summary = "\n".join(lines)

    return summary, suggested_df


def print_dataset_constants_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Prints the dataset constants summary to the console.
    Returns the suggested DataFrame for further use.
    """
    summary, suggested_df = build_dataset_constants_summary(df)
    print(summary)
    return suggested_df

# ---------------------------
# COMBINED SCOPE SUMMARY
# ---------------------------

def summarize_dataset_scope(df: pd.DataFrame) -> pd.DataFrame:
    """
    Prints both the metadata summary and the dataset constants summary.
    Returns the suggested DataFrame for further analysis.
    """
    print_metadata_summary(df)
    suggested_df = print_dataset_constants_summary(df)
    
    return suggested_df
