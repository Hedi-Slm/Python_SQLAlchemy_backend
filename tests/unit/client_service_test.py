import pytest
from unittest.mock import patch, Mock

from app.models.user import UserRole
from app.services.client_service import (
    create_client, update_client, get_all_clients, get_clients_by_user
)
from app.models.client import Client


class TestClientService:
    """Test cases for client service"""

    @patch('app.services.client_service.Client')
    def test_create_client_success(self, mock_client_class, mock_database_session, sample_client_data):
        """Test successful client creation"""
        mock_client_instance = Mock()
        mock_client_instance.id = 1
        mock_client_class.return_value = mock_client_instance

        result = create_client(mock_database_session, 1, **sample_client_data)

        assert result == mock_client_instance
        mock_client_class.assert_called_once_with(commercial_id=1, **sample_client_data)
        mock_database_session.add.assert_called_once_with(mock_client_instance)
        mock_database_session.commit.assert_called_once()
        mock_database_session.refresh.assert_called_once_with(mock_client_instance)

    def test_update_client_success_commercial(self, mock_database_session, mock_user, mock_client):
        """Test successful client update by commercial user"""
        mock_user.role = mock_client.role = mock_user.role  # COMMERCIAL
        mock_client.commercial_id = mock_user.id

        mock_database_session.query.return_value.filter_by.return_value.first.return_value = mock_client

        update_fields = {"full_name": "New Name", "email": "new@example.com"}

        result = update_client(mock_database_session, 1, mock_user, **update_fields)

        assert result == mock_client
        assert mock_client.full_name == "New Name"
        assert mock_client.email == "new@example.com"
        mock_database_session.commit.assert_called_once()

    def test_update_client_permission_error(self, mock_database_session, mock_user, mock_client):
        """Test client update permission error for commercial user"""
        mock_client.commercial_id = mock_user.id + 1  # Different from user
        mock_user.role = UserRole.COMMERCIAL
        mock_database_session.query.return_value.filter_by.return_value.first.return_value = mock_client

        with pytest.raises(PermissionError, match="You can only update your own clients."):
            update_client(mock_database_session, 1, mock_user, full_name="New Name")

    def test_update_client_success_gestion(self, mock_database_session, mock_gestion_user, mock_client):
        """Test successful client update by gestion user"""
        mock_database_session.query.return_value.filter_by.return_value.first.return_value = mock_client
        update_fields = {"full_name": "Updated Name"}

        result = update_client(mock_database_session, 1, mock_gestion_user, **update_fields)

        assert result == mock_client
        assert mock_client.full_name == "Updated Name"
        mock_database_session.commit.assert_called_once()

    def test_get_all_clients(self, mock_database_session):
        """Test getting all clients"""
        mock_clients = [Mock(), Mock()]
        mock_database_session.query.return_value.all.return_value = mock_clients

        result = get_all_clients(mock_database_session)

        assert result == mock_clients
        mock_database_session.query.assert_called_once_with(Client)
        mock_database_session.query.return_value.all.assert_called_once()

    def test_get_clients_by_user_commercial(self, mock_database_session, mock_user):
        """Test getting clients for commercial user"""
        mock_user.role = UserRole.COMMERCIAL
        mock_user.id = 1
        mock_clients = [Mock(), Mock()]
        mock_database_session.query.return_value.filter_by.return_value.all.return_value = mock_clients

        result = get_clients_by_user(mock_database_session, mock_user)

        assert result == mock_clients
        mock_database_session.query.assert_called_once_with(Client)
        mock_database_session.query.return_value.filter_by.assert_called_once_with(commercial_id=1)

    def test_get_clients_by_user_gestion(self, mock_database_session, mock_gestion_user):
        """Test getting clients for gestion user"""
        mock_clients = [Mock(), Mock()]
        mock_database_session.query.return_value.all.return_value = mock_clients

        result = get_clients_by_user(mock_database_session, mock_gestion_user)

        assert result == mock_clients
        mock_database_session.query.assert_called_once_with(Client)
        mock_database_session.query.return_value.all.assert_called_once()

    def test_get_clients_by_user_support(self, mock_database_session, mock_support_user):
        """Test getting clients for support user"""
        mock_clients = [Mock(), Mock()]
        mock_database_session.query.return_value.all.return_value = mock_clients

        result = get_clients_by_user(mock_database_session, mock_support_user)

        assert result == mock_clients
        mock_database_session.query.assert_called_once_with(Client)
        mock_database_session.query.return_value.all.assert_called_once()
