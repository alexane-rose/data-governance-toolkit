import pyspark.sql.functions as F
from pyspark.sql import DataFrame
from pyspark.sql.window import Window

def check_all_reference_in_master(df_ref: DataFrame, ref_col: str, master_df: DataFrame, master_col: str):
    """
    Check if all values in ref_col of df exist in master_col of master_df.

    Parameters:
    df (DataFrame): The DataFrame containing the reference column.
    ref_col (str): The name of the reference column in df.
    master_df (DataFrame): The master DataFrame containing the master column.
    master_col (str): The name of the master column in master_df.

    Returns:
    bool: True if all values in ref_col exist in master_col, False otherwise.
    """
    joined_df = df_ref.join(master_df.select(master_col).distinct(), df_ref[ref_col] == master_df[master_col], "left_anti")
    missing_count = joined_df.count()
    total_count = df_ref.count()
    invalid_percent = (missing_count / total_count) * 100 if total_count > 0 else 0
    return missing_count == 0, missing_count, invalid_percent, joined_df

