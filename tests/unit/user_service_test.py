from unittest.mock import Mock, patch

from app.services.user_service import (
    create_user, update_user, delete_user, list_all_users,
    get_user_by_email, get_user_by_id, check_user_associations,
    email_exists_for_different_user
)
from app.models.user import User, UserRole
from app.models.client import Client
from app.models.contract import Contract
from app.models.event import Event


class TestUserService:
    @patch('app.services.user_service.hash_password')
    def test_create_user_success(self, mock_hash_password, mock_database_session):
        mock_hash_password.return_value = "hashed_password"
        mock_user = Mock(spec=User, id=1, name="Test User", email="test@example.com",
                         role=UserRole.COMMERCIAL, password="hashed_password")

        with patch('app.services.user_service.User', return_value=mock_user):
            result = create_user(
                db=mock_database_session,
                name="Test User",
                email="test@example.com",
                role=UserRole.COMMERCIAL,
                password="plain_password"
            )

        assert result == mock_user
        mock_hash_password.assert_called_once_with("plain_password")
        mock_database_session.add.assert_called_once_with(mock_user)
        mock_database_session.commit.assert_called_once()
        mock_database_session.refresh.assert_called_once_with(mock_user)

    def test_update_user_success(self, mock_database_session, mock_user):
        mock_database_session.query.return_value.filter_by.return_value.first.return_value = mock_user

        result = update_user(
            db=mock_database_session,
            user_id=1,
            name="Updated Name",
            email="updated@example.com"
        )

        assert result == mock_user
        assert mock_user.name == "Updated Name"
        assert mock_user.email == "updated@example.com"
        mock_database_session.commit.assert_called_once()

    def test_delete_user_success(self, mock_database_session, mock_user):
        mock_database_session.query.return_value.filter_by.return_value.first.return_value = mock_user

        delete_user(db=mock_database_session, user_id=1)

        mock_database_session.delete.assert_called_once_with(mock_user)
        mock_database_session.commit.assert_called_once()

    def test_list_all_users_success(self, mock_database_session):
        mock_users = [Mock(spec=User), Mock(spec=User)]
        mock_database_session.query.return_value.all.return_value = mock_users

        result = list_all_users(db=mock_database_session)

        assert result == mock_users
        mock_database_session.query.assert_called_once_with(User)

    def test_get_user_by_email_found(self, mock_database_session, mock_user):
        mock_database_session.query.return_value.filter_by.return_value.first.return_value = mock_user

        result = get_user_by_email(db=mock_database_session, email="test@example.com")

        assert result == mock_user
        mock_database_session.query.assert_called_once_with(User)

    def test_get_user_by_email_not_found(self, mock_database_session):
        mock_database_session.query.return_value.filter_by.return_value.first.return_value = None

        result = get_user_by_email(db=mock_database_session, email="nonexistent@example.com")

        assert result is None

    def test_get_user_by_id_found(self, mock_database_session, mock_user):
        mock_database_session.query.return_value.filter_by.return_value.first.return_value = mock_user

        result = get_user_by_id(db=mock_database_session, user_id=1)

        assert result == mock_user
        mock_database_session.query.assert_called_once_with(User)

    def test_get_user_by_id_not_found(self, mock_database_session):
        mock_database_session.query.return_value.filter_by.return_value.first.return_value = None

        result = get_user_by_id(db=mock_database_session, user_id=999)

        assert result is None

    def test_check_user_associations_with_associations(self, mock_database_session):
        mock_database_session.query.return_value.filter_by.return_value.count.side_effect = [2, 1, 3]

        result = check_user_associations(db=mock_database_session, user_id=1)

        assert result == {
            'clients_count': 2,
            'contracts_count': 1,
            'events_count': 3,
            'has_associations': True
        }

    def test_check_user_associations_without_associations(self, mock_database_session):
        mock_database_session.query.return_value.filter_by.return_value.count.side_effect = [0, 0, 0]

        result = check_user_associations(db=mock_database_session, user_id=1)

        assert result == {
            'clients_count': 0,
            'contracts_count': 0,
            'events_count': 0,
            'has_associations': False
        }

    def test_email_exists_for_different_user_true(self, mock_database_session):
        mock_existing_user = Mock(spec=User, id=2)
        mock_database_session.query.return_value.filter_by.return_value.first.return_value = mock_existing_user

        result = email_exists_for_different_user(db=mock_database_session, email="test@example.com", user_id=1)

        assert result is True

    def test_email_exists_for_different_user_false_same_user(self, mock_database_session):
        mock_existing_user = Mock(spec=User, id=1)
        mock_database_session.query.return_value.filter_by.return_value.first.return_value = mock_existing_user

        result = email_exists_for_different_user(db=mock_database_session, email="test@example.com", user_id=1)

        assert result is False

    def test_email_exists_for_different_user_false_no_user(self, mock_database_session):
        mock_database_session.query.return_value.filter_by.return_value.first.return_value = None

        result = email_exists_for_different_user(db=mock_database_session, email="test@example.com", user_id=1)

        assert result is False

    def test_update_user_multiple_fields(self, mock_database_session, mock_user):
        mock_database_session.query.return_value.filter_by.return_value.first.return_value = mock_user

        result = update_user(
            db=mock_database_session,
            user_id=1,
            name="New Name",
            email="new@example.com",
            role=UserRole.GESTION
        )

        assert result == mock_user
        assert mock_user.name == "New Name"
        assert mock_user.email == "new@example.com"
        assert mock_user.role == UserRole.GESTION
        mock_database_session.commit.assert_called_once()

    def test_check_user_associations_calls_correct_queries(self, mock_database_session):
        mock_database_session.query.return_value.filter_by.return_value.count.return_value = 0

        check_user_associations(db=mock_database_session, user_id=1)

        calls = mock_database_session.query.call_args_list
        assert len(calls) == 3
        assert calls[0][0][0] == Client
        assert calls[1][0][0] == Contract
        assert calls[2][0][0] == Event
