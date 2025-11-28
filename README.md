# data-governance-toolkit
A comprehensive toolkit for data governance automation across Unity Catalog, Alation, and Databricks. Sync catalogs, manage metadata, and streamline cross-platform data governance workflows.

## Installation

To install the `data-governance-toolkit`, clone the repository and install it as a Python package:

```bash
# Clone the repository
git clone https://github.com/alexane-rose/data-governance-toolkit.git
cd data-governance-toolkit

# Install the package
pip install .
```

## Features

- **Data Documentation**: Sync comments across Unity Catalogs.
- **Data Quality**: Validate data completeness and date ranges.

## Usage

### Sync Unity Catalog Comments

The `sync_unity_catalog_comments` module allows you to synchronize comments between catalogs in the Databricks Unity Catalog. This is particularly useful when you:

1. Use tools like Gini AI to generate comments for your staging catalog.
2. Make manual edits to improve the generated comments.
3. Want to push these refined comments to your production catalog.

#### Example

```python
from data_governance_toolkit.data_documentation.sync_unity_catalog_comments import sync_table_column_comments 

# Sync column comments for a specific table
sync_table_column_comments(origin_catalog="staging_catalog",
    target_catalog="prod_catalog",
    table_schema="my_schema", 
    table_name="my_table", 
    spark=spark)

```

### Data Quality Checks

The `data_quality` module provides utilities for validating data completeness and ensuring data falls within expected date ranges or respects certain basic rules. The easiest rule is a start date should be before or equal to an end date.

#### Example

```python
from data_governance_toolkit.data_quality.date_range import check_valid_date_range

# Validate date ranges
is_valid, invalid_count, invalid_percent, invalid_rows = check_valid_date_range(
    df=my_dataframe,
    start_date_col="start_date",
    end_date_col="end_date"
)

if not is_valid:
    print(f"Found {invalid_count} invalid rows ({invalid_percent:.2f}%).")
    invalid_rows.show()
```

## Rationale

### Why Sync Unity Catalog Comments?

In modern data governance workflows, maintaining accurate and up-to-date metadata is critical. Tools like Gini AI can help generate initial comments for your staging catalog. However, these comments often require manual refinement to ensure clarity and accuracy. Once refined, it is essential to synchronize these comments with your production catalog to maintain consistency and improve data discoverability for end-users.

## License

This project is licensed under the terms of the MIT license. See the [LICENSE](LICENSE) file for details.
