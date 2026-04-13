# StatCan Dataset Explorer

A Python utility for quickly understanding Statistics Canada (StatCan) datasets.
It scans a dataset and produces a clean, readable summary of its structure —
identifying what fields are fixed, what varies, and what columns are most
useful for analysis.

Intended for community organizations and volunteers working with open
government data who want a fast way to understand what a dataset contains
before diving into analysis.

---

## What it does

- Summarizes the standard StatCan metadata fields (UOM, SCALAR_FACTOR, VECTOR, etc.)
- Identifies columns that are fixed across all records (i.e. they describe the dataset, not the data)
- Identifies columns that vary, including all unique values for text fields and basic statistics for numeric fields
- Returns a suggested DataFrame containing only the columns useful for analysis

---

## Requirements

Python 3.9 or higher and the following package:

```
pandas
```

Install it with:

```bash
pip install pandas
```

---

## Usage

```python
import pandas as pd
from statcan_utils import summarize_dataset_scope

# Load your StatCan CSV file
df = pd.read_csv("your_dataset.csv")

# Print a full summary and get back a suggested DataFrame
suggested_df = summarize_dataset_scope(df)

# view the suggested dataframe
suggested_df.head(5)
```

The summary will print directly to your console or notebook, showing:
- Metadata fields and their values
- Fixed columns (constant across all rows)
- Variable columns (text values and numeric statistics)
- A suggested list of columns for analysis

---

## Data source

Data is sourced from [Statistics Canada](https://www.statcan.gc.ca).
For more information on the CSV format and metadata fields, see the
[StatCan CSV user guide](https://www.statcan.gc.ca/en/developers/csv/user-guide).

---

## License

MIT License — free to use, share, and adapt.
