from unittest.mock import Mock, patch
from datetime import datetime

from app.controllers.event_menu_controller import EventMenuController
from app.views.event_menu_view import EvenMenuView
from app.models.user import UserRole


class TestEventMenuController:
    """Test suite for EventMenuController"""

    def test_init(self, mock_user):
        """Test controller initialization"""
        controller = EventMenuController(mock_user)
        assert controller.current_user == mock_user
        assert isinstance(controller.view, EvenMenuView)

    @patch('app.controllers.event_menu_controller.SessionLocal')
    @patch('app.controllers.event_menu_controller.get_events_with_details')
    def test_list_events_success(self, mock_get_events, mock_session, mock_user, mock_event):
        """Test successful event listing"""
        # Setup mocks
        mock_db = Mock()
        mock_session.return_value = mock_db
        mock_get_events.return_value = [mock_event]

        controller = EventMenuController(mock_user)
        controller.view = Mock()

        # Execute
        controller.list_events()

        # Verify
        mock_get_events.assert_called_once_with(mock_db)
        controller.view.display_events_list.assert_called_once_with([mock_event])
        mock_db.close.assert_called_once()

    @patch('app.controllers.event_menu_controller.SessionLocal')
    @patch('app.controllers.event_menu_controller.get_signed_contracts_for_commercial')
    @patch('app.controllers.event_menu_controller.get_contract_by_id')
    @patch('app.controllers.event_menu_controller.create_event')
    @patch('app.controllers.event_menu_controller.show_success')
    def test_create_event_success(self, mock_show_success, mock_create_event,
                                  mock_get_contract, mock_get_signed_contracts,
                                  mock_session, mock_user, mock_contract):
        """Test successful event creation"""
        # Setup mocks
        mock_db = Mock()
        mock_session.return_value = mock_db
        mock_get_signed_contracts.return_value = [mock_contract]
        mock_get_contract.return_value = mock_contract

        mock_event = Mock()
        mock_event.id = 1
        mock_create_event.return_value = mock_event

        # Set user role to COMMERCIAL
        mock_user.role = UserRole.COMMERCIAL

        controller = EventMenuController(mock_user)
        controller.view = Mock()
        controller.view.get_event_data.return_value = {
            'contract_id': 1,
            'name': 'Test Event',
            'start_date': datetime(2025, 1, 1, 10, 0),
            'end_date': datetime(2025, 1, 1, 18, 0),
            'location': 'Test Location',
            'attendees': 100,
            'notes': 'Test notes'
        }

        # Execute
        controller.create_event()

        # Verify
        mock_create_event.assert_called_once()
        mock_show_success.assert_called_once_with("Événement créé avec succès (ID: 1)")
        mock_db.close.assert_called_once()

    def test_create_event_unauthorized(self, mock_support_user):
        """Test event creation with unauthorized user"""
        controller = EventMenuController(mock_support_user)

        with patch('app.controllers.event_menu_controller.show_error') as mock_show_error:
            controller.create_event()
            mock_show_error.assert_called_once_with(
                "Accès non autorisé. Seuls les commerciaux peuvent créer des événements."
            )

    @patch('app.controllers.event_menu_controller.SessionLocal')
    @patch('app.controllers.event_menu_controller.get_events_for_support_user')
    @patch('app.controllers.event_menu_controller.get_support_users')
    @patch('app.controllers.event_menu_controller.update_event')
    @patch('app.controllers.event_menu_controller.show_success')
    def test_update_event_support_user(self, mock_show_success, mock_update_event,
                                       mock_get_support_users, mock_get_events,
                                       mock_session, mock_support_user, mock_event):
        """Test event update by support user"""
        # Setup mocks
        mock_db = Mock()
        mock_session.return_value = mock_db
        mock_get_events.return_value = [mock_event]
        mock_get_support_users.return_value = []

        updated_event = Mock()
        updated_event.id = 1
        mock_update_event.return_value = updated_event

        controller = EventMenuController(mock_support_user)
        controller.view = Mock()
        controller.view.get_event_selection.return_value = mock_event
        controller.view.get_event_update_data.return_value = {
            'name': 'Updated Event',
            'start_date': datetime(2025, 1, 1, 10, 0),
            'end_date': datetime(2025, 1, 1, 18, 0),
            'location': 'Updated Location',
            'attendees': 150,
            'notes': 'Updated notes'
        }

        # Execute
        controller.update_event()

        # Verify
        mock_update_event.assert_called_once()
        mock_show_success.assert_called_once_with("Événement ID 1 modifié avec succès.")
        mock_db.close.assert_called_once()

    @patch('app.controllers.event_menu_controller.SessionLocal')
    @patch('app.controllers.event_menu_controller.get_filtered_events')
    @patch('app.controllers.event_menu_controller.show_info')
    def test_filter_events_success(self, mock_show_info, mock_get_filtered,
                                   mock_session, mock_user, mock_event):
        """Test successful event filtering"""
        # Setup mocks
        mock_db = Mock()
        mock_session.return_value = mock_db
        mock_get_filtered.return_value = [mock_event]

        controller = EventMenuController(mock_user)
        controller.view = Mock()
        controller.view.get_event_filter.return_value = {'support_contact_id': None}

        # Execute
        controller.filter_events()

        # Verify
        mock_get_filtered.assert_called_once_with(mock_db, {'support_contact_id': None})
        mock_show_info.assert_called_once_with("1 événement(s) trouvé(s) avec les critères sélectionnés.")
        controller.view.display_events_list.assert_called_once_with([mock_event])
        mock_db.close.assert_called_once()

    @patch("app.controllers.event_menu_controller.show_error")
    def test_handle_menu_invalid_choice(self, mock_show_error, mock_user):
        controller = EventMenuController(mock_user)
        controller.view = Mock()
        controller.view.show_events_menu.side_effect = ["invalid", "0"]

        controller.handle_menu()

        mock_show_error.assert_called_with("Choix invalide ou non autorisé.")

    @patch("app.controllers.event_menu_controller.show_error")
    def test_create_event_no_contracts(self, mock_show_error, mock_user):
        mock_user.role = UserRole.COMMERCIAL
        controller = EventMenuController(mock_user)
        controller.view = Mock()

        with patch("app.controllers.event_menu_controller.get_signed_contracts_for_commercial", return_value=[]), \
             patch("app.controllers.event_menu_controller.SessionLocal") as mock_session:
            db = Mock()
            mock_session.return_value = db

            controller.create_event()
            mock_show_error.assert_called_once_with("Aucun contrat signé disponible pour créer un événement.")
            db.close.assert_called_once()

    @patch("app.controllers.event_menu_controller.show_info")
    def test_create_event_cancelled_by_user(self, mock_show_info, mock_user, mock_contract):
        mock_user.role = UserRole.COMMERCIAL
        controller = EventMenuController(mock_user)
        controller.view = Mock()
        controller.view.get_event_data.return_value = None

        with patch("app.controllers.event_menu_controller.get_signed_contracts_for_commercial", return_value=[mock_contract]), \
             patch("app.controllers.event_menu_controller.SessionLocal") as mock_session:
            db = Mock()
            mock_session.return_value = db

            controller.create_event()
            mock_show_info.assert_called_once_with("Création d'événement annulée.")
            db.close.assert_called_once()

    @patch("app.controllers.event_menu_controller.show_error")
    def test_create_event_contract_not_found(self, mock_show_error, mock_user, mock_contract):
        mock_user.role = UserRole.COMMERCIAL
        controller = EventMenuController(mock_user)
        controller.view = Mock()
        controller.view.get_event_data.return_value = {
            'contract_id': 1, 'start_date': datetime.now(), 'end_date': datetime.now(),
            'location': '', 'attendees': 0, 'notes': '', 'name': ''
        }

        with patch("app.controllers.event_menu_controller.get_signed_contracts_for_commercial", return_value=[mock_contract]), \
             patch("app.controllers.event_menu_controller.get_contract_by_id", return_value=None), \
             patch("app.controllers.event_menu_controller.SessionLocal") as mock_session:
            db = Mock()
            mock_session.return_value = db

            controller.create_event()
            mock_show_error.assert_called_once_with("Contrat non trouvé.")
            db.close.assert_called_once()

    @patch("app.controllers.event_menu_controller.show_info")
    def test_update_event_cancelled_by_user(self, mock_show_info, mock_support_user, mock_event):
        controller = EventMenuController(mock_support_user)
        controller.view = Mock()
        controller.view.get_event_selection.return_value = None

        with patch("app.controllers.event_menu_controller.get_events_for_support_user", return_value=[mock_event]), \
             patch("app.controllers.event_menu_controller.SessionLocal") as mock_session:
            db = Mock()
            mock_session.return_value = db

            controller.update_event()
            mock_show_info.assert_called_once_with("Modification annulée.")
            db.close.assert_called_once()

    @patch("app.controllers.event_menu_controller.show_info")
    def test_update_event_cancelled_update_data(self, mock_show_info, mock_gestion_user, mock_event):
        controller = EventMenuController(mock_gestion_user)
        controller.view = Mock()
        controller.view.get_event_selection.return_value = mock_event
        controller.view.get_event_update_data.return_value = None

        with patch("app.controllers.event_menu_controller.get_all_events_for_management", return_value=[mock_event]), \
             patch("app.controllers.event_menu_controller.get_support_users", return_value=[]), \
             patch("app.controllers.event_menu_controller.SessionLocal") as mock_session:
            db = Mock()
            mock_session.return_value = db

            controller.update_event()
            mock_show_info.assert_called_once_with("Modification annulée.")
            db.close.assert_called_once()

    @patch("app.controllers.event_menu_controller.get_all_events_for_management")
    @patch("app.controllers.event_menu_controller.show_error")
    def test_update_event_no_events(self, mock_show_error, mock_get_events, mock_gestion_user):
        controller = EventMenuController(mock_gestion_user)
        controller.view = Mock()
        mock_get_events.return_value = []

        with patch("app.controllers.event_menu_controller.SessionLocal") as mock_session:
            db = Mock()
            mock_session.return_value = db

            controller.update_event()
            mock_show_error.assert_called_once_with("Aucun événement disponible pour modification.")
            db.close.assert_called_once()

    @patch("app.controllers.event_menu_controller.show_error")
    def test_update_event_unauthorized_user(self, mock_show_error, mock_user):
        mock_user.role = UserRole.COMMERCIAL
        controller = EventMenuController(mock_user)

        controller.update_event()

        mock_show_error.assert_called_once_with("Accès non autorisé. Seuls le support et"
                                                " la gestion peuvent modifier des événements.")

    @patch("app.controllers.event_menu_controller.get_all_events_for_management")
    @patch("app.controllers.event_menu_controller.get_support_users")
    @patch("app.controllers.event_menu_controller.update_event")
    @patch("app.controllers.event_menu_controller.show_success")
    def test_update_event_with_support_assignment(self, mock_show_success, mock_update_event, mock_get_support,
                                                  mock_get_events, mock_gestion_user, mock_event):
        updated_event = Mock(id=42)
        mock_update_event.return_value = updated_event

        mock_get_events.return_value = [mock_event]
        mock_get_support.return_value = []

        controller = EventMenuController(mock_gestion_user)
        controller.view = Mock()
        controller.view.get_event_selection.return_value = mock_event
        controller.view.get_event_update_data.return_value = {
            'name': 'Updated', 'start_date': datetime.now(), 'end_date': datetime.now(),
            'location': 'New Place', 'attendees': 100, 'notes': 'Note', 'support_contact_id': 99
        }

        with patch("app.controllers.event_menu_controller.SessionLocal") as mock_session:
            db = Mock()
            mock_session.return_value = db

            controller.update_event()
            mock_show_success.assert_called_once_with("Événement ID 42 modifié avec succès.")
            db.close.assert_called_once()
