"""Unit tests for Text2SQLHandler"""

from unittest.mock import AsyncMock, Mock, patch

import pytest

from api.text2sql_handler import Text2SQLHandler


@pytest.mark.unit
def test_validate_sql_valid_select() -> None:
    """Test SQL validation accepts valid SELECT query"""
    mock_client = Mock()
    handler = Text2SQLHandler(mock_client, "sqlite+aiosqlite:///:memory:", "test prompt")

    # Valid SELECT queries
    assert handler._validate_sql("SELECT * FROM users")
    assert handler._validate_sql("  SELECT id, name FROM conversations  ")
    assert handler._validate_sql("SELECT COUNT(*) FROM messages WHERE deleted_at IS NULL")


@pytest.mark.unit
def test_validate_sql_rejects_dangerous() -> None:
    """Test SQL validation rejects dangerous queries"""
    mock_client = Mock()
    handler = Text2SQLHandler(mock_client, "sqlite+aiosqlite:///:memory:", "test prompt")

    # Dangerous queries
    assert not handler._validate_sql("INSERT INTO users VALUES (1, 'test')")
    assert not handler._validate_sql("UPDATE users SET username = 'hacked'")
    assert not handler._validate_sql("DELETE FROM messages")
    assert not handler._validate_sql("DROP TABLE users")
    assert not handler._validate_sql("CREATE TABLE evil (id INT)")
    assert not handler._validate_sql("ALTER TABLE users ADD COLUMN evil TEXT")

    # Not starting with SELECT
    assert not handler._validate_sql("UNION SELECT * FROM users")


@pytest.mark.unit
def test_clean_sql() -> None:
    """Test SQL cleaning removes markdown and whitespace"""
    mock_client = Mock()
    handler = Text2SQLHandler(mock_client, "sqlite+aiosqlite:///:memory:", "test prompt")

    # Clean markdown
    assert handler._clean_sql("```sql\nSELECT * FROM users\n```") == "SELECT * FROM users"
    assert handler._clean_sql("```\nSELECT * FROM users\n```") == "SELECT * FROM users"

    # Clean whitespace
    assert handler._clean_sql("  SELECT * FROM users  ") == "SELECT * FROM users"
    assert handler._clean_sql("\n\nSELECT * FROM users\n\n") == "SELECT * FROM users"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_generate_sql_success() -> None:
    """Test successful SQL generation"""
    mock_client = Mock()
    mock_client.send_message = AsyncMock(
        return_value="SELECT * FROM users WHERE deleted_at IS NULL"
    )

    handler = Text2SQLHandler(
        mock_client, "sqlite+aiosqlite:///:memory:", "test prompt: {question}"
    )

    sql = await handler._generate_sql("How many users do we have?")

    assert sql == "SELECT * FROM users WHERE deleted_at IS NULL"
    mock_client.send_message.assert_called_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_generate_sql_invalid() -> None:
    """Test SQL generation fails for invalid SQL"""
    mock_client = Mock()
    mock_client.send_message = AsyncMock(return_value="DELETE FROM users")

    handler = Text2SQLHandler(
        mock_client, "sqlite+aiosqlite:///:memory:", "test prompt: {question}"
    )

    with pytest.raises(ValueError, match="invalid or unsafe"):
        await handler._generate_sql("Delete all users")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_process_question_success() -> None:
    """Test successful question processing"""
    mock_client = Mock()
    mock_client.send_message = AsyncMock()

    # First call: generate SQL
    # Second call: format answer
    mock_client.send_message.side_effect = [
        "SELECT COUNT(*) as user_count FROM users WHERE deleted_at IS NULL",
        "There are 42 active users in the system.",
    ]

    handler = Text2SQLHandler(
        mock_client, "sqlite+aiosqlite:///:memory:", "test prompt: {question}"
    )

    # Mock engine and connection
    with patch.object(handler, "_execute_sql", new_callable=AsyncMock) as mock_execute:
        mock_execute.return_value = [{"user_count": 42}]

        sql, answer = await handler.process_question("How many users do we have?")

        assert sql == "SELECT COUNT(*) as user_count FROM users WHERE deleted_at IS NULL"
        assert answer == "There are 42 active users in the system."
        assert mock_execute.called


@pytest.mark.unit
@pytest.mark.asyncio
async def test_process_question_sql_error() -> None:
    """Test question processing handles SQL errors gracefully"""
    mock_client = Mock()
    mock_client.send_message = AsyncMock(return_value="SELECT * FROM users")

    handler = Text2SQLHandler(
        mock_client, "sqlite+aiosqlite:///:memory:", "test prompt: {question}"
    )

    # Mock SQL execution error
    with patch.object(handler, "_execute_sql", new_callable=AsyncMock) as mock_execute:
        mock_execute.side_effect = Exception("Database error")

        sql, answer = await handler.process_question("Show me users")

        assert sql == ""
        assert "Ошибка при выполнении запроса" in answer


@pytest.mark.unit
@pytest.mark.asyncio
async def test_process_question_validation_error() -> None:
    """Test question processing handles validation errors"""
    mock_client = Mock()
    mock_client.send_message = AsyncMock(return_value="DROP TABLE users")

    handler = Text2SQLHandler(
        mock_client, "sqlite+aiosqlite:///:memory:", "test prompt: {question}"
    )

    sql, answer = await handler.process_question("Delete everything")

    assert sql == ""
    assert "Не удалось сгенерировать корректный SQL запрос" in answer
