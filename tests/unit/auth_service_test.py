import pytest
from unittest.mock import patch
from app.services.auth_service import login_user
from app.models.user import User


class TestAuthService:
    """Test cases for authentication service"""

    @patch('app.services.auth_service.SessionLocal')
    @patch('app.services.auth_service.verify_password')
    def test_login_user_success(self, mock_verify_password, mock_session_local, mock_database_session, mock_user):
        """Test successful user login"""
        mock_session_local.return_value = mock_database_session
        mock_database_session.query.return_value.filter_by.return_value.first.return_value = mock_user
        mock_verify_password.return_value = True

        result = login_user("test@example.com", "password123")

        assert result == mock_user
        mock_database_session.query.assert_called_once_with(User)
        mock_verify_password.assert_called_once_with("password123", "hashed_password")
        mock_database_session.close.assert_called_once()

    @patch('app.services.auth_service.SessionLocal')
    @patch('app.services.auth_service.verify_password')
    def test_login_user_invalid_password(self, mock_verify_password, mock_session_local,
                                         mock_database_session, mock_user):
        """Test login with invalid password"""
        mock_session_local.return_value = mock_database_session
        mock_database_session.query.return_value.filter_by.return_value.first.return_value = mock_user
        mock_verify_password.return_value = False

        result = login_user("test@example.com", "wrong_password")

        assert result is None
        mock_verify_password.assert_called_once_with("wrong_password", "hashed_password")
        mock_database_session.close.assert_called_once()

    @patch('app.services.auth_service.SessionLocal')
    def test_login_user_not_found(self, mock_session_local, mock_database_session):
        """Test login with non-existent user"""
        mock_session_local.return_value = mock_database_session
        mock_database_session.query.return_value.filter_by.return_value.first.return_value = None

        result = login_user("nonexistent@example.com", "password123")

        assert result is None
        mock_database_session.close.assert_called_once()

    @patch('app.services.auth_service.SessionLocal')
    def test_login_user_database_error(self, mock_session_local, mock_database_session):
        """Test login with database error"""
        mock_session_local.return_value = mock_database_session
        mock_database_session.query.side_effect = Exception("Database error")

        with pytest.raises(Exception, match="Database error"):
            login_user("test@example.com", "password123")

        mock_database_session.close.assert_called_once()
