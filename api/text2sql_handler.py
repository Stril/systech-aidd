"""Text to SQL handler for admin mode queries"""

import logging
import re
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from src.openai_client import OpenAIClient

logger = logging.getLogger(__name__)


class Text2SQLHandler:
    """Handles natural language to SQL conversion and execution"""

    def __init__(self, openai_client: OpenAIClient, database_url: str, text2sql_prompt: str):
        """Initialize Text2SQL handler

        Args:
            openai_client: OpenAI client for LLM interactions
            database_url: Database connection string
            text2sql_prompt: System prompt for SQL generation
        """
        self._openai_client = openai_client
        self._engine: AsyncEngine = create_async_engine(database_url, echo=False)
        self._text2sql_prompt = text2sql_prompt

        logger.info("text2sql_handler|initialized")

    async def close(self) -> None:
        """Close database connections"""
        await self._engine.dispose()
        logger.info("text2sql_handler|closed")

    def _validate_sql(self, sql: str) -> bool:
        """Validate that SQL is a safe SELECT query

        Args:
            sql: SQL query to validate

        Returns:
            True if query is valid, False otherwise
        """
        # Remove leading/trailing whitespace and convert to uppercase for checking
        sql_upper = sql.strip().upper()

        # Check if it's a SELECT query
        if not sql_upper.startswith("SELECT"):
            logger.warning("text2sql_handler|validation_failed|reason=not_select_query")
            return False

        # Check for dangerous keywords using word boundaries
        dangerous_keywords = [
            "INSERT",
            "UPDATE",
            "DELETE",
            "DROP",
            "CREATE",
            "ALTER",
            "TRUNCATE",
            "EXEC",
            "EXECUTE",
        ]

        # Split into words to avoid matching substrings (e.g., "deleted_at" contains "DELETE")
        import re
        words = re.findall(r'\b[A-Z_]+\b', sql_upper)

        for keyword in dangerous_keywords:
            if keyword in words:
                logger.warning(
                    f"text2sql_handler|validation_failed|reason=dangerous_keyword|keyword={keyword}"
                )
                return False

        return True

    def _clean_sql(self, sql: str) -> str:
        """Clean SQL query from markdown and extra formatting

        Args:
            sql: Raw SQL from LLM

        Returns:
            Cleaned SQL query
        """
        # Remove markdown code blocks
        sql = re.sub(r"```sql\n?", "", sql)
        sql = re.sub(r"```\n?", "", sql)

        # Remove extra whitespace
        sql = sql.strip()

        return sql

    async def _generate_sql(self, question: str) -> str:
        """Generate SQL query from natural language question

        Args:
            question: Natural language question

        Returns:
            SQL query string

        Raises:
            ValueError: If generated SQL is invalid or unsafe
        """
        # Format prompt with question
        prompt = self._text2sql_prompt.format(question=question)

        # Send to LLM with minimal system prompt
        messages = [{"role": "user", "content": question}]
        sql = await self._openai_client.send_message(messages, prompt)

        # Clean SQL
        sql = self._clean_sql(sql)

        logger.info(
            f"text2sql_handler|sql_generated|question_length={len(question)}|sql_length={len(sql)}"
        )

        # Validate SQL
        if not self._validate_sql(sql):
            raise ValueError("Generated SQL query is invalid or unsafe")

        return sql

    async def _execute_sql(self, sql: str) -> list[dict[str, Any]]:
        """Execute SQL query and return results

        Args:
            sql: SQL query to execute

        Returns:
            List of result rows as dictionaries

        Raises:
            Exception: If SQL execution fails
        """
        try:
            async with self._engine.begin() as conn:
                result = await conn.execute(text(sql))
                rows = result.fetchall()

                # Convert rows to list of dicts
                if rows:
                    columns = result.keys()
                    results = [dict(zip(columns, row, strict=False)) for row in rows]
                else:
                    results = []

                logger.info(f"text2sql_handler|sql_executed|rows_returned={len(results)}")
                return results

        except Exception as e:
            logger.error(f"text2sql_handler|sql_execution_error|error={str(e)}")
            raise

    async def _format_answer(self, question: str, sql: str, results: list[dict[str, Any]]) -> str:
        """Format SQL results into natural language answer

        Args:
            question: Original question
            sql: SQL query that was executed
            results: Query results

        Returns:
            Formatted natural language answer
        """
        # Create context for LLM
        results_text = "\n".join([str(row) for row in results[:50]])  # Limit to 50 rows for context

        prompt = f"""You are a helpful assistant analyzing bot statistics.

Original question: {question}

SQL query used: {sql}

Query results ({len(results)} rows):
{results_text}

Provide a clear, concise answer to the original question based on these results.
If there are no results, explain what that means.
Format numbers nicely and provide context."""

        messages = [{"role": "user", "content": "Format the results"}]
        answer = await self._openai_client.send_message(messages, prompt)

        logger.info(f"text2sql_handler|answer_formatted|answer_length={len(answer)}")
        return answer

    async def process_question(self, question: str) -> tuple[str, str]:
        """Process natural language question and return SQL + answer

        Args:
            question: Natural language question about bot statistics

        Returns:
            Tuple of (sql_query, formatted_answer)

        Raises:
            ValueError: If SQL generation or validation fails
            Exception: If SQL execution fails
        """
        logger.info(f"text2sql_handler|process_question|question_length={len(question)}")

        try:
            # Generate SQL from question
            sql = await self._generate_sql(question)

            # Execute SQL
            results = await self._execute_sql(sql)

            # Format answer
            answer = await self._format_answer(question, sql, results)

            return (sql, answer)

        except ValueError as e:
            # SQL generation/validation error
            error_msg = f"Не удалось сгенерировать корректный SQL запрос: {str(e)}"
            logger.error(f"text2sql_handler|error|type=validation|error={str(e)}")
            return ("", error_msg)

        except Exception as e:
            # SQL execution or other error
            error_msg = f"Ошибка при выполнении запроса: {str(e)}"
            logger.error(f"text2sql_handler|error|type=execution|error={str(e)}")
            return ("", error_msg)

