from unittest.mock import patch, Mock
from datetime import date
from app.controllers.client_menu_controller import ClientMenuController


class TestClientMenuController:
    """Test cases for client menu controller"""

    def setup_method(self, method):
        self.controller = ClientMenuController(current_user=Mock())

    @patch('app.controllers.client_menu_controller.show_error')
    def test_handle_menu_invalid_choice(self, mock_show_error):
        self.controller.view.show_clients_menu = Mock(side_effect=["5", "0"])
        self.controller.handle_menu()
        mock_show_error.assert_called_with("Choix invalide ou non autorisé.")

    @patch('app.controllers.client_menu_controller.SessionLocal')
    @patch('app.controllers.client_menu_controller.get_all_clients')
    def test_list_clients_success(self, mock_get_all_clients, mock_session_local, mock_database_session, mock_client):
        mock_session_local.return_value = mock_database_session
        mock_get_all_clients.return_value = [mock_client]

        self.controller.view.display_clients_list = Mock()
        self.controller.list_clients()

        mock_get_all_clients.assert_called_once_with(mock_database_session)
        self.controller.view.display_clients_list.assert_called_once_with([mock_client])
        mock_database_session.close.assert_called_once()

    @patch('app.controllers.client_menu_controller.SessionLocal')
    @patch('app.controllers.client_menu_controller.get_all_clients')
    @patch('app.controllers.client_menu_controller.show_info')
    def test_list_clients_empty(self, mock_show_info, mock_get_all_clients, mock_session_local, mock_database_session):
        mock_session_local.return_value = mock_database_session
        mock_get_all_clients.return_value = []

        self.controller.list_clients()

        mock_show_info.assert_called_once_with("Aucun client trouvé.")
        mock_database_session.close.assert_called_once()

    @patch('app.controllers.client_menu_controller.SessionLocal')
    @patch('app.controllers.client_menu_controller.get_all_clients')
    @patch('app.controllers.client_menu_controller.show_error')
    @patch('app.controllers.client_menu_controller.sentry_sdk')
    def test_list_clients_exception(self, mock_sentry, mock_show_error, mock_get_all_clients,
                                    mock_session_local, mock_database_session):
        mock_session_local.return_value = mock_database_session
        mock_get_all_clients.side_effect = Exception("Database error")

        self.controller.list_clients()

        mock_show_error.assert_called_once_with("Erreur lors de la récupération des clients: Database error")
        mock_sentry.capture_exception.assert_called_once()
        mock_database_session.close.assert_called_once()

    @patch('app.controllers.client_menu_controller.SessionLocal')
    @patch('app.controllers.client_menu_controller.create_client')
    @patch('app.controllers.client_menu_controller.show_success')
    @patch('app.controllers.client_menu_controller.sentry_sdk')
    def test_create_client_success(self, mock_sentry, mock_show_success, mock_create_client,
                                   mock_session_local, mock_user, mock_database_session):
        self.controller.current_user = mock_user
        mock_session_local.return_value = mock_database_session

        client_data = {
            'full_name': 'Test Client',
            'email': 'test@example.com',
            'phone': '123456789',
            'company_name': 'Test Company'
        }

        mock_client = Mock(id=1, full_name='Test Client')
        mock_create_client.return_value = mock_client

        self.controller.view.get_client_data = Mock(return_value=client_data)
        self.controller.create_client()

        expected_data = client_data.copy()
        expected_data['date_created'] = date.today()
        expected_data['last_contact'] = date.today()

        mock_create_client.assert_called_once_with(mock_database_session, mock_user.id, **expected_data)
        mock_show_success.assert_called_once_with("Client 'Test Client' créé avec succès (ID: 1)")
        mock_sentry.capture_message.assert_called_once()
        mock_database_session.close.assert_called_once()

    @patch('app.controllers.client_menu_controller.show_error')
    def test_create_client_unauthorized(self, mock_show_error, mock_support_user):
        self.controller.current_user = mock_support_user
        self.controller.create_client()
        mock_show_error.assert_called_once_with("Accès non autorisé. Seuls les commerciaux peuvent créer des clients.")

    @patch('app.controllers.client_menu_controller.show_error')
    def test_create_client_missing_required_fields(self, mock_show_error, mock_user):
        self.controller.current_user = mock_user  # Ensure correct role (COMMERCIAL)

        client_data = {'full_name': '', 'email': ''}
        self.controller.view.get_client_data = Mock(return_value=client_data)

        self.controller.create_client()

        mock_show_error.assert_called_once_with("Le nom complet et l'email sont obligatoires.")

    @patch('app.controllers.client_menu_controller.SessionLocal')
    @patch('app.controllers.client_menu_controller.get_clients_by_user')
    @patch('app.controllers.client_menu_controller.update_client')
    @patch('app.controllers.client_menu_controller.show_success')
    @patch('app.controllers.client_menu_controller.sentry_sdk')
    def test_update_client_success(self, mock_sentry, mock_show_success, mock_update_client,
                                   mock_get_clients, mock_session_local,
                                   mock_database_session, mock_user, mock_client):
        self.controller.current_user = mock_user
        mock_session_local.return_value = mock_database_session

        mock_get_clients.return_value = [mock_client]
        updated_data = {'full_name': 'Updated Client', 'email': 'updated@example.com'}
        mock_updated_client = Mock(full_name='Updated Client')
        mock_update_client.return_value = mock_updated_client

        self.controller.view.get_client_selection = Mock(return_value=mock_client)
        self.controller.view.get_client_update_data = Mock(return_value=updated_data)

        self.controller.update_client()

        expected_data = updated_data.copy()
        expected_data['last_contact'] = date.today()

        mock_update_client.assert_called_once_with(mock_database_session, mock_client.id, mock_user, **expected_data)
        mock_show_success.assert_called_once_with("Client 'Updated Client' modifié avec succès.")
        mock_sentry.capture_message.assert_called_once()
        mock_database_session.close.assert_called_once()

    @patch('app.controllers.client_menu_controller.show_error')
    def test_update_client_unauthorized(self, mock_show_error, mock_support_user):
        self.controller.current_user = mock_support_user
        self.controller.update_client()
        mock_show_error.assert_called_once_with("Accès non autorisé. Seuls les commerciaux et"
                                                " la gestion peuvent modifier des clients.")

    @patch('app.controllers.client_menu_controller.SessionLocal')
    @patch('app.controllers.client_menu_controller.get_clients_by_user')
    @patch('app.controllers.client_menu_controller.show_info')
    def test_update_client_no_clients(self, mock_show_info, mock_get_clients, mock_session_local, mock_database_session,
                                      mock_user):
        self.controller.current_user = mock_user
        mock_session_local.return_value = mock_database_session
        mock_get_clients.return_value = []

        self.controller.update_client()

        mock_show_info.assert_called_once_with("Aucun client disponible pour modification.")
        mock_database_session.close.assert_called_once()

    @patch('app.controllers.client_menu_controller.SessionLocal')
    @patch('app.controllers.client_menu_controller.get_clients_by_user')
    @patch('app.controllers.client_menu_controller.show_error')
    def test_update_client_permission_error(self, mock_show_error, mock_get_clients, mock_session_local,
                                            mock_database_session, mock_client, mock_user):
        self.controller.current_user = mock_user
        mock_client.commercial_id = 999  # Not the same as mock_user.id

        mock_session_local.return_value = mock_database_session
        mock_get_clients.return_value = [mock_client]
        self.controller.view.get_client_selection = Mock(return_value=mock_client)

        self.controller.update_client()

        mock_show_error.assert_called_once_with("Vous ne pouvez modifier que vos propres clients.")
        mock_database_session.close.assert_called_once()
