import pyspark.sql.functions as F
from pyspark.sql import DataFrame
from pyspark.sql.window import Window


def check_valid_date_range(df: DataFrame, start_date_col: str, end_date_col: str):
    """
    Check if the date range defined by start_date_col and end_date_col is valid.
    A valid date range means that for each row, the start date is less than or equal to the end date.

    Parameters:
    df (pd.DataFrame): The DataFrame containing the date columns.
    start_date_col (str): The name of the column containing start dates.
    end_date_col (str): The name of the column containing end dates.

    Returns:
    bool: True if all date ranges are valid, False otherwise.
    """
    invalid_ranges = df.filter(F.col(start_date_col) > F.col(end_date_col))
    invalid_row_count = invalid_ranges.count()
    total_rows = df.count()
    invalid_rows_percent = (invalid_row_count / total_rows) * 100 if total_rows > 0 else 0
    return invalid_row_count == 0, invalid_row_count, invalid_rows_percent, invalid_ranges


def check_for_gaps(df: DataFrame, id_cols: list, start_date_col: str, end_date_col: str):
    """
    Check for gaps in date ranges for each group defined by id_cols.
    A gap is defined as a period where there is no coverage between the end date of one range
    and the start date of the next range.

    Parameters:
    df (pd.DataFrame): The DataFrame containing the date columns and identifier columns.
    id_cols (list): List of column names to group by.
    start_date_col (str): The name of the column containing start dates.
    end_date_col (str): The name of the column containing end dates.

    Returns:
    bool: True if no gaps are found, False otherwise.
    """
    window_spec = Window.partitionBy(*id_cols).orderBy(start_date_col)
    df_with_prev_end = df.withColumn("prev_end_date", F.lag(end_date_col).over(window_spec))
    df_with_gap = df_with_prev_end.withColumn("gap", F.col(start_date_col) > F.date_add(F.col("prev_end_date"), 1))
    
    gaps = df_with_gap.filter(F.col("gap"))
    gap_row_count = gaps.count()
    total_rows = df.count()
    gap_rows_percent = (gap_row_count / total_rows) * 100 if total_rows > 0 else 0
    return gap_row_count == 0, gap_row_count, gap_rows_percent, gaps[id_cols +[start_date_col, end_date_col, "prev_end_date"]]


def check_for_no_overlaps(df: DataFrame, id_cols: list, start_date_col: str, end_date_col: str):
    """
    Check for overlaps in date ranges for each group defined by id_cols.
    An overlap is defined as a period where the start date of one range is less than or equal to
    the end date of the previous range.

    Parameters:
    df (pd.DataFrame): The DataFrame containing the date columns and identifier columns.
    id_cols (list): List of column names to group by.
    start_date_col (str): The name of the column containing start dates.
    end_date_col (str): The name of the column containing end dates.

    Returns:
    bool: True if no overlaps are found, False otherwise.
    """
    window_spec = Window.partitionBy(*id_cols).orderBy(start_date_col)
    df_with_prev_end = df.withColumn("prev_start_date", F.lag(start_date_col).over(window_spec)).withColumn("prev_end_date", F.lag(end_date_col).over(window_spec))
    df_with_overlap = df_with_prev_end.withColumn("overlap", F.col(start_date_col) <= F.col("prev_end_date"))
    
    overlaps = df_with_overlap.filter(F.col("overlap"))
    overlap_row_count = overlaps.count()
    total_rows = df.count()
    overlap_rows_percent = (overlap_row_count / total_rows) * 100 if total_rows > 0 else 0
    return overlap_row_count == 0, overlap_row_count, overlap_rows_percent, overlaps[id_cols +[start_date_col, end_date_col,"prev_start_date","prev_end_date"]]


