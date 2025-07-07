from unittest.mock import patch
from datetime import datetime

from app.views.event_menu_view import EvenMenuView
from app.models.user import UserRole


class TestEventMenuView:
    """Test suite for EventMenuView"""

    def test_show_events_menu_commercial(self, mock_user):
        """Test events menu display for commercial user"""
        view = EvenMenuView()
        mock_user.role = UserRole.COMMERCIAL

        with patch('click.clear'), patch('click.echo'), patch('click.prompt') as mock_prompt:
            mock_prompt.return_value = "2"
            result = view.show_events_menu(mock_user)
            assert result == "2"

    def test_show_events_menu_support(self, mock_support_user):
        """Test events menu display for support user"""
        view = EvenMenuView()

        with patch('click.clear'), patch('click.echo'), patch('click.prompt') as mock_prompt:
            mock_prompt.return_value = "3"
            result = view.show_events_menu(mock_support_user)
            assert result == "3"

    def test_get_event_data_success(self, mock_contract):
        """Test successful event data input"""
        view = EvenMenuView()

        with patch('click.echo'), patch('click.prompt') as mock_prompt, \
                patch.object(view, 'get_contract_selection') as mock_get_contract, \
                patch.object(view, 'get_datetime_input') as mock_get_datetime:
            mock_get_contract.return_value = mock_contract
            mock_prompt.side_effect = ["Test Event", "Test Location", 100, "Test notes"]
            mock_get_datetime.side_effect = [
                datetime(2025, 1, 1, 10, 0),
                datetime(2025, 1, 1, 18, 0)
            ]

            result = view.get_event_data([mock_contract])

            assert result['contract_id'] == mock_contract.id
            assert result['name'] == "Test Event"
            assert result['location'] == "Test Location"
            assert result['attendees'] == 100
            assert result['notes'] == "Test notes"

    def test_get_event_data_invalid_dates(self, mock_contract):
        """Test event data input with invalid dates"""
        view = EvenMenuView()

        with patch('click.echo'), patch('click.prompt') as mock_prompt, \
                patch.object(view, 'get_contract_selection') as mock_get_contract, \
                patch.object(view, 'get_datetime_input') as mock_get_datetime:
            mock_get_contract.return_value = mock_contract
            mock_prompt.side_effect = ["Test Event"]
            # End date before start date
            mock_get_datetime.side_effect = [
                datetime(2025, 1, 1, 18, 0),
                datetime(2025, 1, 1, 10, 0)
            ]

            result = view.get_event_data([mock_contract])
            assert result is None

    def test_get_datetime_input_success(self):
        """Test successful datetime input"""
        view = EvenMenuView()

        with patch('click.prompt') as mock_prompt:
            mock_prompt.return_value = "01/01/2025 10:00"
            result = view.get_datetime_input("Test prompt")
            assert result == datetime(2025, 1, 1, 10, 0)

    def test_get_datetime_input_with_default(self):
        """Test datetime input with default value"""
        view = EvenMenuView()
        default_date = datetime(2025, 1, 1, 10, 0)

        with patch('click.prompt') as mock_prompt:
            mock_prompt.return_value = "01/01/2025 10:00"
            result = view.get_datetime_input("Test prompt", default=default_date)
            assert result == datetime(2025, 1, 1, 10, 0)

    def test_get_datetime_input_invalid_format(self):
        """Test datetime input with invalid format"""
        view = EvenMenuView()

        with patch('click.prompt') as mock_prompt, patch('click.echo') as mock_echo:
            mock_prompt.side_effect = ["invalid", "01/01/2025 10:00"]
            result = view.get_datetime_input("Test prompt")
            assert result == datetime(2025, 1, 1, 10, 0)
            mock_echo.assert_called_with(
                "❌ Format invalide. Utilisez le format DD/MM/YYYY HH:MM (ex: 25/12/2023 14:30)")

    def test_display_events_list_empty(self):
        """Test display of empty events list"""
        view = EvenMenuView()

        with patch('click.echo') as mock_echo, patch('click.pause'):
            view.display_events_list([])
            mock_echo.assert_any_call("Aucun événement trouvé.")

    def test_display_events_list_with_data(self, mock_event, mock_contract, mock_client, mock_support_user):
        """Test display of events list with data"""
        view = EvenMenuView()
        mock_event.contract = mock_contract
        mock_event.contract.client = mock_client
        mock_event.support_contact = mock_support_user

        with patch('click.echo') as mock_echo, patch('click.pause'):
            view.display_events_list([mock_event])
            # Verify that event information is displayed
            mock_echo.assert_any_call(f"ID: {mock_event.id} | {mock_event.name}")

    def test_get_event_filter_support_user(self, mock_support_user):
        """Test event filter for support user"""
        view = EvenMenuView()

        with patch('click.echo'), patch('click.prompt') as mock_prompt:
            mock_prompt.return_value = "1"
            result = view.get_event_filter(mock_support_user)
            assert result == {"support_contact_id": mock_support_user.id}

    def test_get_event_filter_gestion_user(self, mock_gestion_user):
        """Test event filter for gestion user"""
        view = EvenMenuView()

        with patch('click.echo'), patch('click.prompt') as mock_prompt:
            mock_prompt.return_value = "1"
            result = view.get_event_filter(mock_gestion_user)
            assert result == {"support_contact_id": None}

    def test_get_event_filter_commercial_user(self, mock_user):
        """Test event filter for commercial user"""
        view = EvenMenuView()
        mock_user.role = UserRole.COMMERCIAL

        with patch('click.echo'), patch('click.prompt') as mock_prompt:
            mock_prompt.return_value = "1"
            result = view.get_event_filter(mock_user)
            assert result == {"commercial_contact_id": mock_user.id}

    def test_get_support_selection_success(self, mock_support_user):
        """Test successful support selection"""
        view = EvenMenuView()

        with patch('click.echo'), patch('click.prompt') as mock_prompt:
            mock_prompt.return_value = 1
            result = view.get_support_selection([mock_support_user])
            assert result == mock_support_user

    def test_get_support_selection_cancelled(self, mock_support_user):
        """Test cancelled support selection"""
        view = EvenMenuView()

        with patch('click.echo'), patch('click.prompt') as mock_prompt:
            mock_prompt.return_value = 0
            result = view.get_support_selection([mock_support_user])
            assert result is None
