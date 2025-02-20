# from datetime import datetime, timedelta

# import pytest
# from pytest_mock import mocker
# from sqlmodel import Session

# from timescaledb.hypertables.chunks import show_chunks
# from timescaledb.hypertables.chunks import sql_statements as sql


# @pytest.fixture
# def mock_execute(mocker):
#     """Mock the session.execute() to return a predefined result"""
#     mock = mocker.patch("sqlmodel.Session.execute")
#     mock.return_value.fetchall.return_value = [("chunk1",), ("chunk2",)]
#     return mock


# def test_show_all_chunks(mock_execute, session: Session):
#     """Test showing all chunks without any filters"""
#     result = show_chunks(session, "test_table")

#     mock_execute.assert_called_once()
#     query = mock_execute.call_args[0][0]
#     assert str(query) == sql.SHOW_CHUNKS
#     assert len(result) == 2


# def test_show_chunks_older_than(mock_execute, session: Session):
#     """Test showing chunks older than an interval"""
#     result = show_chunks(session, "test_table", older_than="7 days")

#     mock_execute.assert_called_once()
#     query = mock_execute.call_args[0][0]
#     assert str(query) == sql.SHOW_CHUNKS_OLDER_THAN_INTERVAL_SQL
#     params = mock_execute.call_args[1]
#     assert params["older_than"] == "7 days"


# def test_show_chunks_older_than_timestamp(mock_execute, session: Session):
#     """Test showing chunks older than a timestamp"""
#     timestamp = "2024-01-01"
#     result = show_chunks(session, "test_table", older_than=timestamp, is_timestamp=True)

#     mock_execute.assert_called_once()
#     query = mock_execute.call_args[0][0]
#     assert str(query) == sql.SHOW_CHUNKS_TIMESTAMP_SQL
#     params = mock_execute.call_args[1]
#     assert params["timestamp"] == timestamp


# def test_show_chunks_newer_than(mock_execute, session: Session):
#     """Test showing chunks newer than an interval"""
#     result = show_chunks(session, "test_table", newer_than="7 days")

#     mock_execute.assert_called_once()
#     query = mock_execute.call_args[0][0]
#     assert str(query) == sql.SHOW_CHUNKS_NEWER_THAN_INTERVAL_SQL
#     params = mock_execute.call_args[1]
#     assert params["newer_than"] == "7 days"


# def test_show_chunks_between_intervals(mock_execute, session: Session):
#     """Test showing chunks between two intervals"""
#     result = show_chunks(
#         session,
#         "test_table",
#         older_than="14 days",
#         newer_than="7 days",
#     )

#     mock_execute.assert_called_once()
#     query = mock_execute.call_args[0][0]
#     assert str(query) == sql.SHOW_CHUNKS_BETWEEN_INTERVALS_SQL
#     params = mock_execute.call_args[1]
#     assert params["end_timestamp"] == "14 days"
#     assert params["start_timestamp"] == "7 days"


# def test_show_chunks_created_between_intervals(mock_execute, session: Session):
#     """Test showing chunks created between two intervals"""
#     result = show_chunks(
#         session,
#         "test_table",
#         created_before="14 days",
#         created_after="7 days",
#     )

#     mock_execute.assert_called_once()
#     query = mock_execute.call_args[0][0]
#     assert str(query) == sql.SHOW_CHUNKS_CREATED_BETWEEN_INTERVALS_SQL
#     params = mock_execute.call_args[1]
#     assert params["created_before"] == "14 days"
#     assert params["created_after"] == "7 days"


# def test_show_chunks_created_before(mock_execute, session: Session):
#     """Test showing chunks created before an interval"""
#     result = show_chunks(session, "test_table", created_before="7 days")

#     mock_execute.assert_called_once()
#     query = mock_execute.call_args[0][0]
#     assert str(query) == sql.SHOW_CHUNKS_CREATED_BEFORE_INTERVAL_SQL
#     params = mock_execute.call_args[1]
#     assert params["created_before"] == "7 days"
