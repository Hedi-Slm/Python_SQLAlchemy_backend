from unittest.mock import patch, Mock
from app.controllers.contract_menu_controller import ContractMenuController
from app.models.user import UserRole
from app.views.contract_menu_view import ContractMenuView


class TestContractMenuController:
    """Test suite for ContractMenuController"""

    def test_init(self, mock_user):
        """Test controller initialization"""
        controller = ContractMenuController(mock_user)
        assert controller.current_user == mock_user
        assert isinstance(controller.view, ContractMenuView)

    @patch('app.controllers.contract_menu_controller.SessionLocal')
    @patch('app.controllers.contract_menu_controller.get_all_contracts')
    def test_list_contracts_success(self, mock_get_contracts, mock_session_local, mock_user, mock_contract):
        """Test successful contract listing"""
        db = Mock()
        mock_session_local.return_value = db
        mock_get_contracts.return_value = [mock_contract]

        controller = ContractMenuController(mock_user)
        controller.view = Mock()

        controller.list_contracts()

        mock_get_contracts.assert_called_once_with(db)
        controller.view.display_contracts_list.assert_called_once_with([mock_contract])
        db.close.assert_called_once()

    @patch('app.controllers.contract_menu_controller.SessionLocal')
    @patch('app.controllers.contract_menu_controller.get_all_contracts')
    @patch('app.controllers.contract_menu_controller.show_error')
    @patch('app.controllers.contract_menu_controller.sentry_sdk')
    def test_list_contracts_error(self, mock_sentry, mock_show_error, mock_get_contracts,
                                  mock_session_local, mock_user):
        """Test contract listing with error"""
        db = Mock()
        mock_session_local.return_value = db
        mock_get_contracts.side_effect = Exception("Database error")

        controller = ContractMenuController(mock_user)
        controller.view = Mock()

        controller.list_contracts()

        mock_show_error.assert_called_once_with("Erreur lors de la récupération des contrats: Database error")
        mock_sentry.capture_exception.assert_called_once()
        db.close.assert_called_once()

    @patch('app.controllers.contract_menu_controller.SessionLocal')
    @patch('app.controllers.contract_menu_controller.get_all_clients')
    @patch('app.controllers.contract_menu_controller.get_commercial_users')
    @patch('app.controllers.contract_menu_controller.create_contract')
    @patch('app.controllers.contract_menu_controller.show_success')
    def test_create_contract_success(self, mock_show_success, mock_create_contract,
                                     mock_get_commercials, mock_get_clients, mock_session_local,
                                     mock_gestion_user, mock_client):
        """Test successful contract creation"""
        db = Mock()
        mock_session_local.return_value = db
        mock_get_clients.return_value = [mock_client]
        mock_commercial = Mock(id=1)
        mock_get_commercials.return_value = [mock_commercial]

        mock_contract = Mock(id=1)
        mock_create_contract.return_value = mock_contract

        controller = ContractMenuController(mock_gestion_user)
        controller.view = Mock()
        controller.view.get_contract_data.return_value = {
            'client_id': 1,
            'total_amount': 10000.0,
            'amount_due': 5000.0,
            'is_signed': False
        }
        controller.view.get_commercial_selection.return_value = mock_commercial

        controller.create_contract()

        mock_create_contract.assert_called_once()
        mock_show_success.assert_called_once_with("Contrat créé avec succès (ID: 1)")
        db.commit.assert_called_once()
        db.close.assert_called_once()

    def test_create_contract_unauthorized(self, mock_user):
        """Test contract creation with unauthorized user"""
        controller = ContractMenuController(mock_user)
        controller.view = Mock()

        with patch('app.controllers.contract_menu_controller.show_error') as mock_show_error:
            controller.create_contract()
            mock_show_error.assert_called_once_with(
                "Accès non autorisé. Seule la gestion peut créer des contrats."
            )

    @patch('app.controllers.contract_menu_controller.SessionLocal')
    @patch('app.controllers.contract_menu_controller.get_contracts_by_user')
    @patch('app.controllers.contract_menu_controller.update_contract')
    @patch('app.controllers.contract_menu_controller.show_success')
    def test_update_contract_success(self, mock_show_success, mock_update_contract,
                                     mock_get_contracts, mock_session_local,
                                     mock_gestion_user, mock_contract):
        """Test successful contract update"""
        db = Mock()
        mock_session_local.return_value = db
        mock_get_contracts.return_value = [mock_contract]
        mock_contract.commercial_id = mock_gestion_user.id

        updated_contract = Mock(id=1)
        mock_update_contract.return_value = updated_contract

        controller = ContractMenuController(mock_gestion_user)
        controller.view = Mock()
        controller.view.get_contract_selection.return_value = mock_contract
        controller.view.get_contract_update_data.return_value = {
            'total_amount': 15000.0,
            'amount_due': 7500.0,
            'is_signed': True
        }

        controller.update_contract()

        mock_update_contract.assert_called_once()
        mock_show_success.assert_called_once_with("Contrat 1 modifié avec succès.")
        db.close.assert_called_once()

    @patch('app.controllers.contract_menu_controller.SessionLocal')
    @patch('app.controllers.contract_menu_controller.list_unsigned_contracts')
    def test_filter_contracts_unsigned(self, mock_list_unsigned, mock_session_local, mock_gestion_user):
        """Test filtering unsigned contracts"""
        db = Mock()
        mock_session_local.return_value = db
        contracts = [Mock(), Mock()]
        mock_list_unsigned.return_value = contracts

        controller = ContractMenuController(mock_gestion_user)
        controller.view = Mock()
        controller.view.get_contract_filter.return_value = "unsigned"

        controller.filter_contracts()

        mock_list_unsigned.assert_called_once_with(db)
        controller.view.display_contracts_list.assert_called_once_with(contracts)
        db.close.assert_called_once()

    @patch("app.controllers.contract_menu_controller.show_error")
    def test_handle_menu_invalid_choice(self, mock_show_error, mock_user):
        """Test invalid menu choice"""
        controller = ContractMenuController(mock_user)
        controller.view = Mock()
        controller.view.show_contracts_menu.side_effect = ["invalid", "0"]

        controller.handle_menu()

        mock_show_error.assert_called_with("Choix invalide ou non autorisé.")

    @patch("app.controllers.contract_menu_controller.show_error")
    def test_create_contract_no_clients(self, mock_show_error, mock_gestion_user):
        """Test create contract with no clients available"""
        controller = ContractMenuController(mock_gestion_user)
        controller.view = Mock()

        with patch("app.controllers.contract_menu_controller.get_all_clients", return_value=[]), \
                patch("app.controllers.contract_menu_controller.SessionLocal") as mock_session:
            db = Mock()
            mock_session.return_value = db

            controller.create_contract()
            mock_show_error.assert_called_once_with("Aucun client disponible. Créez d'abord des clients.")
            db.close.assert_called_once()

    @patch("app.controllers.contract_menu_controller.show_error")
    def test_create_contract_no_commercials(self, mock_show_error, mock_gestion_user, mock_client):
        """Test create contract with no commercial users"""
        controller = ContractMenuController(mock_gestion_user)
        controller.view = Mock()
        controller.view.get_contract_data.return_value = {
            'client_id': 1, 'total_amount': 5000.0
        }

        with patch("app.controllers.contract_menu_controller.get_all_clients", return_value=[mock_client]), \
                patch("app.controllers.contract_menu_controller.get_commercial_users", return_value=[]), \
                patch("app.controllers.contract_menu_controller.SessionLocal") as mock_session:
            db = Mock()
            mock_session.return_value = db

            controller.create_contract()
            mock_show_error.assert_called_once_with("Aucun commercial disponible.")
            db.close.assert_called_once()

    def test_create_contract_cancelled_by_user(self, mock_gestion_user, mock_client):
        """Test when user cancels contract creation after data input"""
        controller = ContractMenuController(mock_gestion_user)
        controller.view = Mock()
        controller.view.get_contract_data.return_value = None  # simulate cancellation

        with patch("app.controllers.contract_menu_controller.get_all_clients", return_value=[mock_client]), \
                patch("app.controllers.contract_menu_controller.SessionLocal") as mock_session:
            db = Mock()
            mock_session.return_value = db

            controller.create_contract()
            db.close.assert_called_once()

    def test_create_contract_commercial_selection_cancelled(self, mock_gestion_user, mock_client):
        """Test contract creation cancelled during commercial selection"""
        controller = ContractMenuController(mock_gestion_user)
        controller.view = Mock()
        controller.view.get_contract_data.return_value = {
            'client_id': 1, 'total_amount': 5000.0
        }
        controller.view.get_commercial_selection.return_value = None

        with patch("app.controllers.contract_menu_controller.get_all_clients", return_value=[mock_client]), \
                patch("app.controllers.contract_menu_controller.get_commercial_users", return_value=[Mock(id=1)]), \
                patch("app.controllers.contract_menu_controller.SessionLocal") as mock_session:
            db = Mock()
            mock_session.return_value = db

            controller.create_contract()
            db.close.assert_called_once()

    @patch("app.controllers.contract_menu_controller.show_error")
    def test_update_contract_no_contracts(self, mock_show_error, mock_gestion_user):
        """Test update contract when no contracts found"""
        controller = ContractMenuController(mock_gestion_user)
        controller.view = Mock()

        with patch("app.controllers.contract_menu_controller.get_contracts_by_user", return_value=[]), \
                patch("app.controllers.contract_menu_controller.SessionLocal") as mock_session:
            db = Mock()
            mock_session.return_value = db

            controller.update_contract()
            mock_show_error.assert_called_once_with("Aucun contrat disponible pour modification.")
            db.close.assert_called_once()

    def test_update_contract_cancelled_by_user(self, mock_gestion_user, mock_contract):
        """Test user cancels contract update"""
        controller = ContractMenuController(mock_gestion_user)
        controller.view = Mock()
        controller.view.get_contract_selection.return_value = None

        with patch("app.controllers.contract_menu_controller.get_contracts_by_user", return_value=[mock_contract]), \
                patch("app.controllers.contract_menu_controller.SessionLocal") as mock_session:
            db = Mock()
            mock_session.return_value = db

            controller.update_contract()
            db.close.assert_called_once()

    @patch("app.controllers.contract_menu_controller.show_error")
    def test_update_contract_unauthorized_commercial(self, mock_show_error, mock_user, mock_contract):
        """Test COMMERCIAL user can't update other user's contract"""
        # Setup user and contract with different IDs
        mock_user.role = UserRole.COMMERCIAL  # Make sure to use UserRole enum
        mock_user.id = 2
        mock_contract.commercial_id = 1  # Different from user ID

        # Create controller with mocked view
        controller = ContractMenuController(mock_user)
        controller.view = Mock()
        controller.view.get_contract_selection.return_value = mock_contract

        # Mock database session and contracts query
        with patch("app.controllers.contract_menu_controller.get_contracts_by_user",
                   return_value=[mock_contract]), \
                patch("app.controllers.contract_menu_controller.SessionLocal") as mock_session:
            # Mock database session
            db = Mock()
            mock_session.return_value = db

            # Execute the method
            controller.update_contract()

            # Verify the error message was shown
            mock_show_error.assert_called_once_with("Vous ne pouvez modifier que vos propres contrats.")

            # Verify session was closed
            db.close.assert_called_once()

    @patch("app.controllers.contract_menu_controller.get_contracts_by_user")
    def test_filter_contracts_signed(self, mock_get_contracts, mock_gestion_user):
        """Test filtering signed contracts"""
        controller = ContractMenuController(mock_gestion_user)
        controller.view = Mock()
        controller.view.get_contract_filter.return_value = "signed"

        with patch("app.controllers.contract_menu_controller.SessionLocal") as mock_session, \
                patch("app.controllers.contract_menu_controller.list_signed_contracts") as mock_list_signed:
            db = Mock()
            contracts = [Mock()]
            mock_session.return_value = db
            mock_list_signed.return_value = contracts

            controller.filter_contracts()

            mock_list_signed.assert_called_once_with(db)
            controller.view.display_contracts_list.assert_called_once_with(contracts)
            db.close.assert_called_once()

    @patch("app.controllers.contract_menu_controller.get_contracts_by_user")
    def test_filter_contracts_paid(self, mock_get_contracts, mock_gestion_user):
        """Test filtering paid contracts"""
        controller = ContractMenuController(mock_gestion_user)
        controller.view = Mock()
        controller.view.get_contract_filter.return_value = "paid"

        with patch("app.controllers.contract_menu_controller.SessionLocal") as mock_session, \
                patch("app.controllers.contract_menu_controller.list_paid_contracts") as mock_list_paid:
            db = Mock()
            contracts = [Mock()]
            mock_session.return_value = db
            mock_list_paid.return_value = contracts

            controller.filter_contracts()

            mock_list_paid.assert_called_once_with(db)
            controller.view.display_contracts_list.assert_called_once_with(contracts)
            db.close.assert_called_once()

    @patch("app.controllers.contract_menu_controller.show_error")
    def test_update_contract_no_update_data(self, mock_show_error, mock_gestion_user, mock_contract):
        """Test when user provides no update data (lines 98-101)"""
        controller = ContractMenuController(mock_gestion_user)
        controller.view = Mock()
        controller.view.get_contract_selection.return_value = mock_contract
        controller.view.get_contract_update_data.return_value = None  # Simulate cancellation

        with patch("app.controllers.contract_menu_controller.get_contracts_by_user", return_value=[mock_contract]), \
                patch("app.controllers.contract_menu_controller.SessionLocal") as mock_session:
            db = Mock()
            mock_session.return_value = db

            controller.update_contract()
            db.close.assert_called_once()

    @patch("app.controllers.contract_menu_controller.show_error")
    @patch("app.controllers.contract_menu_controller.sentry_sdk")
    def test_update_contract_exception(self, mock_sentry, mock_show_error, mock_gestion_user, mock_contract):
        """Test exception handling during contract update"""
        controller = ContractMenuController(mock_gestion_user)
        controller.view = Mock()
        controller.view.get_contract_selection.return_value = mock_contract
        controller.view.get_contract_update_data.return_value = {"total_amount": 15000.0}

        with patch("app.controllers.contract_menu_controller.get_contracts_by_user", return_value=[mock_contract]), \
                patch("app.controllers.contract_menu_controller.SessionLocal") as mock_session, \
                patch("app.controllers.contract_menu_controller.update_contract") as mock_update:
            db = Mock()
            mock_session.return_value = db

            # Make the update_contract function raise a non-PermissionError exception
            mock_update.side_effect = RuntimeError("Update error")

            controller.update_contract()

            mock_show_error.assert_called_once_with("Erreur lors de la modification du contrat: Update error")
            db.rollback.assert_called_once()
            db.close.assert_called_once()

    @patch("app.controllers.contract_menu_controller.show_error")
    def test_filter_contracts_default_case(self, mock_show_error, mock_user):
        """Test default case in filter contracts"""
        controller = ContractMenuController(mock_user)
        controller.view = Mock()
        controller.view.get_contract_filter.return_value = "invalid_choice"

        # Create a mock contract with commercial_id matching user id
        mock_contract = Mock()
        mock_contract.commercial_id = mock_user.id

        with patch("app.controllers.contract_menu_controller.get_contracts_by_user",
                   return_value=[mock_contract]), \
                patch("app.controllers.contract_menu_controller.SessionLocal") as mock_session:
            db = Mock()
            mock_session.return_value = db

            controller.filter_contracts()

            # The contract should be displayed for COMMERCIAL users since commercial_id matches
            expected_contracts = [mock_contract] if mock_user.role == UserRole.COMMERCIAL else [mock_contract]
            controller.view.display_contracts_list.assert_called_once_with(expected_contracts)
            db.close.assert_called_once()

    @patch("app.controllers.contract_menu_controller.show_error")
    @patch("app.controllers.contract_menu_controller.sentry_sdk")
    def test_filter_contracts_error(self, mock_sentry, mock_show_error, mock_user):
        """Test error handling in filter contracts"""
        controller = ContractMenuController(mock_user)
        controller.view = Mock()
        controller.view.get_contract_filter.return_value = "unsigned"

        with patch("app.controllers.contract_menu_controller.list_unsigned_contracts") as mock_list_unsigned, \
                patch("app.controllers.contract_menu_controller.SessionLocal") as mock_session:
            db = Mock()
            mock_session.return_value = db
            mock_list_unsigned.side_effect = Exception("Filter error")

            controller.filter_contracts()

            mock_show_error.assert_called_once_with("Erreur lors du filtrage des contrats: Filter error")
            mock_sentry.capture_exception.assert_called_once()
            db.close.assert_called_once()

    @patch("app.controllers.contract_menu_controller.show_error")
    def test_update_contract_permission_error(self, mock_show_error, mock_gestion_user, mock_contract):
        """Test PermissionError handling in update_contract"""
        controller = ContractMenuController(mock_gestion_user)
        controller.view = Mock()
        controller.view.get_contract_selection.return_value = mock_contract
        controller.view.get_contract_update_data.return_value = {"total_amount": 15000.0}

        with patch("app.controllers.contract_menu_controller.get_contracts_by_user", return_value=[mock_contract]), \
                patch("app.controllers.contract_menu_controller.SessionLocal") as mock_session, \
                patch("app.controllers.contract_menu_controller.update_contract") as mock_update:
            db = Mock()
            mock_session.return_value = db

            # Make the update_contract function raise a PermissionError
            mock_update.side_effect = PermissionError("Permission denied")

            controller.update_contract()

            mock_show_error.assert_called_once_with("Permission denied")
            db.close.assert_called_once()
