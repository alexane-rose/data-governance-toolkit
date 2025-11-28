
def _quote_ident(identifier: str) -> str:
    """
    Safely quote a SQL identifier using backticks and escape any backticks in the identifier.
    Example: my`name -> `my``name`
    """
    if identifier is None:
        raise ValueError("Identifier must not be None")
    return f"`{identifier.replace('`', '``')}`"


def _escape_comment(comment: str) -> str:
    """
    Escape single quotes in SQL string literal by doubling them.
    """
    return comment.replace("'", "''") if comment is not None else comment


def _execute_single_row_query(spark: "SparkSession", query: str):
    """
    Execute a query and return the first row or None if no rows.
    Uses DataFrame.take(1) to avoid collecting entire result.
    """
    df = spark.sql(query)
    rows = df.take(1)
    return rows[0] if rows else None
