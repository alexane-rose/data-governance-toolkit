"""
datagov.data_documentation.sync_unity_catalog

Utilities to synchronize table and column comments between Unity Catalog catalogs/schemas
in Databricks.

Design goals:
- Importable from notebooks: from datagov.data_documentation.sync_unity_catalog import sync_table_comment
- Easy to test: functions accept an optional SparkSession
- Safer SQL construction: identifiers are quoted, comments are escaped
- Clear docstrings and logging instead of prints

Example:
    from pyspark.sql import SparkSession
    from datagov.data_documentation.sync_unity_catalog import sync_schema_table_comments

    spark = SparkSession.builder.getOrCreate()
    sync_schema_table_comments("origin_catalog", "target_catalog", "my_schema", spark=spark)
"""

from typing import Optional, Tuple
import logging
from .utils import _quote_ident, _escape_comment, _execute_single_row_query

# Try to import SparkSession only for type hints (Databricks environment will already have `spark`).
try:
    from pyspark.sql import SparkSession, DataFrame  # type: ignore
except Exception:  # pragma: no cover - type hint fallback for non-Spark envs
    SparkSession = None  # type: ignore
    DataFrame = None  # type: ignore

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

__all__ = [
    "sync_table_comment",
    "sync_schema_table_comments",
    "update_column_comment",
    "sync_table_column_comments",
    "sync_schema_column_comments",
]


def _sync_table_comment(
    origin_catalog: str,
    target_catalog: str,
    table_schema: str,
    table_name: str,
    spark: "SparkSession",
) -> Tuple[bool, str]: 
    """
    Internal worker that attempts to sync the table-level comment and returns (success, message).

    The boolean is for internal control flow; the message is human readable.
    """
    if not all([origin_catalog, target_catalog, table_schema, table_name]):
        raise ValueError(
            "origin_catalog, target_catalog, table_schema, and table_name must be provided"
        )

    origin_tbl_ref = f"{origin_catalog}.information_schema.tables"
    origin_query = f"""
        SELECT comment
        FROM {origin_tbl_ref}
        WHERE table_schema = '{table_schema}'
        AND table_name = '{table_name}'
        LIMIT 1
    """
    row = _execute_single_row_query(spark, origin_query)
    if not row or not row["comment"]:
        msg = f"No comment found in origin for {origin_catalog}.{table_schema}.{table_name}"
        logger.info(msg)
        return False, msg

    comment = _escape_comment(row["comment"])

    # Check if table exists in target
    target_tbl_meta = f"{_quote_ident(target_catalog)}.information_schema.tables"
    exists_query = f"""
        SELECT 1
        FROM {target_tbl_meta}
        WHERE table_schema = '{table_schema}'
        AND table_name = '{table_name}'
        LIMIT 1
    """
    exists = bool(_execute_single_row_query(spark, exists_query))
    if not exists:
        msg = f"Table does not exist in target catalog: {target_catalog}.{table_schema}.{table_name}"
        logger.warning(msg)
        return False, msg

    # Apply comment on target table. Use quoted identifiers for execution.
    target_fq_quoted = f"{_quote_ident(target_catalog)}.{_quote_ident(table_schema)}.{_quote_ident(table_name)}"
    update_sql = f"COMMENT ON TABLE {target_fq_quoted} IS '{comment}'"
    spark.sql(update_sql)
    msg = f"Synced comment for {target_catalog}.{table_schema}.{table_name}"
    logger.info(msg)
    return True, msg


def sync_table_comment(
    origin_catalog: str,
    target_catalog: str,
    table_schema: str,
    table_name: str,
    spark: Optional["SparkSession"],
) -> str:
    """
    Sync the table-level comment for a specific table from origin_catalog to target_catalog.

    Returns a human-readable message indicating the result.
    Raises ValueError if required parameters are missing.
    """
    if spark is None:
        raise ValueError(
            "A SparkSession instance must be provided via the 'spark' parameter"
        )

    success, message = _sync_table_comment(
        origin_catalog, target_catalog, table_schema, table_name, spark
    )
    return message


def sync_schema_table_comments(
    origin_catalog: str,
    target_catalog: str,
    table_schema: str,
    spark: SparkSession,
) -> str:
    """
    Sync table-level comments for all tables in a given schema from origin_catalog to target_catalog.

    Returns a human-readable summary message describing how many table comments were applied.
    """
    if spark is None:
        raise ValueError(
            "A SparkSession instance must be provided via the 'spark' parameter"
        )
    if not all([origin_catalog, target_catalog, table_schema]):
        raise ValueError(
            "origin_catalog, target_catalog, and table_schema must be provided"
        )

    origin_tbl_ref = f"{_quote_ident(origin_catalog)}.information_schema.tables"
    tables_query = f"""
        SELECT table_name
        FROM {origin_tbl_ref}
        WHERE table_schema = '{table_schema}'
        AND table_name NOT LIKE '__materialization%'
        AND comment IS NOT NULL
        AND comment <> ''
    """
    df = spark.sql(tables_query)
    rows = df.collect()
    if not rows:
        msg = f"No tables with comments found in {origin_catalog}.{table_schema}"
        logger.info(msg)
        return msg

    applied = 0
    for r in rows:
        ok, _ = _sync_table_comment(
            origin_catalog, target_catalog, table_schema, r["table_name"], spark
        )
        if ok:
            applied += 1
    msg = f"Applied {applied} table comment(s) from {origin_catalog}.{table_schema} to {target_catalog}"
    logger.info(msg)
    return msg


def _update_column_comment(
    catalog: str,
    schema: str,
    table: str,
    column: str,
    comment: str,
    spark: "SparkSession",
) -> Tuple[bool, str]:
    """
    Internal worker: update the comment for a specific column and return (success, message).
    """
    if not all([catalog, schema, table, column]):
        raise ValueError("catalog, schema, table, and column must be provided")

    if not comment:
        msg = f"No comment provided for column {catalog}.{schema}.{table}.{column}"
        logger.info(msg)
        return False, msg

    comment_escaped = _escape_comment(comment)
    fq_column = f"{_quote_ident(catalog)}.{_quote_ident(schema)}.{_quote_ident(table)}.{_quote_ident(column)}"
    sql = f"COMMENT ON COLUMN {fq_column} IS '{comment_escaped}'"
    spark.sql(sql)
    msg = f"Updated comment for column {catalog}.{schema}.{table}.{column}"
    logger.info(msg)
    return True, msg


def update_column_comment(
    catalog: str,
    schema: str,
    table: str,
    column: str,
    comment: str,
    spark: SparkSession,
) -> str:
    """
    Update the comment for a specific column in a table.

    Returns a human-readable message indicating the result.
    """
    if spark is None:
        raise ValueError(
            "A SparkSession instance must be provided via the 'spark' parameter"
        )

    success, message = _update_column_comment(
        catalog, schema, table, column, comment, spark
    )
    return message


def sync_table_column_comments(
    origin_catalog: str,
    target_catalog: str,
    table_schema: str,
    table_name: str,
    spark: SparkSession,
) -> str:
    """
    Sync column comments from origin_catalog to target_catalog for a given table.

    Returns a human-readable summary message describing how many columns were updated.
    """
    if spark is None:
        raise ValueError(
            "A SparkSession instance must be provided via the 'spark' parameter"
        )
    if not all([origin_catalog, target_catalog, table_schema, table_name]):
        raise ValueError(
            "origin_catalog, target_catalog, table_schema, and table_name must be provided"
        )

    origin_cols_ref = f"{_quote_ident(origin_catalog)}.information_schema.columns"
    origin_query = f"""
        SELECT column_name, comment
        FROM {origin_cols_ref}
        WHERE table_schema = '{table_schema}'
        AND table_name = '{table_name}'
        AND comment IS NOT NULL
        AND comment <> ''
    """
    df = spark.sql(origin_query)
    rows = df.collect()
    if not rows:
        msg = (
            f"No column comments found in {origin_catalog}.{table_schema}.{table_name}"
        )
        logger.info(msg)
        return msg

    updated = 0
    for r in rows:
        ok, _ = _update_column_comment(
            target_catalog,
            table_schema,
            table_name,
            r["column_name"],
            r["comment"],
            spark,
        )
        if ok:
            updated += 1
    msg = f"Updated {updated} column comment(s) for {target_catalog}.{table_schema}.{table_name}"
    logger.info(msg)
    return msg


def sync_schema_column_comments(
    origin_catalog: str,
    target_catalog: str,
    table_schema: str,
    spark: SparkSession,
) -> str:
    """
    Sync column comments for all tables in a given schema from origin_catalog to target_catalog.

    Returns a human-readable summary message describing how many column comments were updated.
    """
    if spark is None:
        raise ValueError(
            "A SparkSession instance must be provided via the 'spark' parameter"
        )
    if not all([origin_catalog, target_catalog, table_schema]):
        raise ValueError(
            "origin_catalog, target_catalog, and table_schema must be provided"
        )

    origin_cols_ref = f"{_quote_ident(origin_catalog)}.information_schema.columns"
    origin_query = f"""
        SELECT column_name, comment, table_name
        FROM {origin_cols_ref}
        WHERE table_schema = '{table_schema}'
        AND table_name NOT LIKE '__materialization%'
        AND comment IS NOT NULL
        AND comment <> ''
    """
    df = spark.sql(origin_query)
    rows = df.collect()
    if not rows:
        msg = f"No column comments found in {origin_catalog}.{table_schema}"
        logger.info(msg)
        return msg

    updated = 0
    for r in rows:
        ok, _ = _update_column_comment(
            target_catalog,
            table_schema,
            r["table_name"],
            r["column_name"],
            r["comment"],
            spark,
        )
        if ok:
            updated += 1
    msg = f"Updated {updated} column comment(s) in {target_catalog}.{table_schema}"
    logger.info(msg)
    return msg
