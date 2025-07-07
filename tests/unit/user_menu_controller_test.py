import pytest
from unittest.mock import Mock, patch
from app.controllers.user_menu_controller import UserMenuController
from app.models.user import User, UserRole


@pytest.fixture
@patch('app.controllers.user_menu_controller.UserMenuView')
def controller(mock_view_class, mock_gestion_user):
    return UserMenuController(mock_gestion_user)


class TestUserMenuController:
    def test_init_creates_view(self, mock_gestion_user):
        with patch('app.controllers.user_menu_controller.UserMenuView') as mock_view_class:
            controller = UserMenuController(mock_gestion_user)
            assert controller.current_user == mock_gestion_user
            mock_view_class.assert_called_once()

    @patch('app.controllers.user_menu_controller.show_error')
    def test_handle_menu_unauthorized_user(self, mock_show_error, mock_user):
        mock_user.role = UserRole.COMMERCIAL
        controller = UserMenuController(mock_user)
        controller.handle_menu()
        mock_show_error.assert_called_once_with("Accès non autorisé. Seule la gestion peut gérer les utilisateurs.")

    def test_handle_menu_choice_dispatch(self, controller):
        choices = [
            ("1", "list_users"),
            ("2", "create_user"),
            ("3", "update_user"),
            ("4", "delete_user")
        ]
        for choice, method in choices:
            setattr(controller, method, Mock())
            controller.view.show_users_menu.side_effect = [choice, "0"]
            controller.handle_menu()
            getattr(controller, method).assert_called_once()

    @patch('app.controllers.user_menu_controller.show_error')
    def test_handle_menu_invalid_choice(self, mock_show_error, controller):
        controller.view.show_users_menu.side_effect = ["9", "0"]
        controller.handle_menu()
        mock_show_error.assert_called_with("Choix invalide.")

    @patch('app.controllers.user_menu_controller.SessionLocal')
    @patch('app.controllers.user_menu_controller.list_all_users')
    def test_list_users_success(self, mock_list_all_users, mock_session_local, controller):
        mock_db = mock_session_local.return_value
        mock_users = [Mock(spec=User), Mock(spec=User)]
        mock_list_all_users.return_value = mock_users

        controller.list_users()

        mock_list_all_users.assert_called_once_with(mock_db)
        controller.view.display_users_list.assert_called_once_with(mock_users)
        mock_db.close.assert_called_once()

    @patch('app.controllers.user_menu_controller.SessionLocal')
    @patch('app.controllers.user_menu_controller.list_all_users')
    @patch('app.controllers.user_menu_controller.show_error')
    @patch('app.controllers.user_menu_controller.sentry_sdk')
    def test_list_users_exception(self, mock_sentry, mock_show_error, mock_list_all_users, mock_session_local, controller):
        mock_db = mock_session_local.return_value
        exception = Exception("Database error")
        mock_list_all_users.side_effect = exception

        controller.list_users()

        mock_show_error.assert_called_once_with("Erreur lors de la récupération des utilisateurs: Database error")
        mock_sentry.capture_exception.assert_called_once_with(exception)
        mock_db.close.assert_called_once()

    @patch('app.controllers.user_menu_controller.SessionLocal')
    @patch('app.controllers.user_menu_controller.get_user_by_email')
    @patch('app.controllers.user_menu_controller.create_user')
    @patch('app.controllers.user_menu_controller.show_success')
    @patch('app.controllers.user_menu_controller.show_info')
    @patch('app.controllers.user_menu_controller.sentry_sdk')
    def test_create_user_success(self, mock_sentry, mock_show_info, mock_show_success, mock_create_user,
                                 mock_get_user_by_email, mock_session_local, controller):
        mock_db = mock_session_local.return_value
        user_data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'password': 'password123',
            'role': UserRole.COMMERCIAL
        }
        controller.view.get_user_data.return_value = user_data
        mock_get_user_by_email.return_value = None
        mock_user = Mock(spec=User, name='Test User')
        mock_create_user.return_value = mock_user

        controller.create_user()

        mock_create_user.assert_called_once()
        mock_show_success.assert_called_once()
        mock_sentry.capture_message.assert_called_once()
        mock_db.close.assert_called_once()

    @patch('app.controllers.user_menu_controller.SessionLocal')
    @patch('app.controllers.user_menu_controller.show_info')
    def test_create_user_cancelled(self, mock_show_info, mock_session_local, controller):
        mock_db = mock_session_local.return_value
        controller.view.get_user_data.return_value = None

        controller.create_user()

        mock_show_info.assert_called_once_with("Création annulée.")
        mock_db.close.assert_called_once()

    @patch('app.controllers.user_menu_controller.SessionLocal')
    @patch('app.controllers.user_menu_controller.show_error')
    def test_create_user_missing_fields(self, mock_show_error, mock_session_local, controller):
        mock_db = mock_session_local.return_value
        controller.view.get_user_data.return_value = {
            'name': 'Test User', 'email': '', 'password': 'password123', 'role': UserRole.COMMERCIAL
        }

        controller.create_user()

        mock_show_error.assert_called_once_with("Tous les champs sont requis.")
        mock_db.close.assert_called_once()

    @patch('app.controllers.user_menu_controller.SessionLocal')
    @patch('app.controllers.user_menu_controller.get_user_by_email')
    @patch('app.controllers.user_menu_controller.show_error')
    def test_create_user_email_exists(self, mock_show_error, mock_get_user_by_email, mock_session_local, controller):
        mock_db = mock_session_local.return_value
        controller.view.get_user_data.return_value = {
            'name': 'Test User', 'email': 'test@example.com', 'password': 'password123', 'role': UserRole.COMMERCIAL
        }
        mock_get_user_by_email.return_value = Mock(spec=User)

        controller.create_user()

        mock_show_error.assert_called_once_with("Un utilisateur avec cet email existe déjà.")
        mock_db.close.assert_called_once()

    @patch('app.controllers.user_menu_controller.SessionLocal')
    @patch('app.controllers.user_menu_controller.list_all_users')
    @patch('app.controllers.user_menu_controller.show_info')
    def test_update_user_no_users(self, mock_show_info, mock_list_all_users, mock_session_local, controller):
        mock_db = mock_session_local.return_value
        mock_list_all_users.return_value = []

        controller.update_user()

        mock_show_info.assert_called_once_with("Aucun utilisateur à modifier.")
        mock_db.close.assert_called_once()

    @patch('app.controllers.user_menu_controller.SessionLocal')
    @patch('app.controllers.user_menu_controller.list_all_users')
    @patch('app.controllers.user_menu_controller.check_user_associations')
    @patch('app.controllers.user_menu_controller.delete_user')
    @patch('app.controllers.user_menu_controller.show_success')
    @patch('app.controllers.user_menu_controller.sentry_sdk')
    def test_delete_user_success(self, mock_sentry, mock_show_success, mock_delete_user, mock_check_associations,
                                 mock_list_all_users, mock_session_local, controller):
        mock_db = mock_session_local.return_value
        user = Mock(spec=User, id=2, name="User to Delete")
        mock_list_all_users.return_value = [user]
        controller.view.get_user_selection.return_value = user
        controller.view.confirm_user_deletion.return_value = True
        mock_check_associations.return_value = {'has_associations': False}

        controller.delete_user()

        mock_delete_user.assert_called_once_with(mock_db, 2)
        mock_show_success.assert_called_once()
        mock_sentry.capture_message.assert_called_once()
        mock_db.close.assert_called_once()

    @patch('app.controllers.user_menu_controller.SessionLocal')
    @patch('app.controllers.user_menu_controller.list_all_users')
    @patch('app.controllers.user_menu_controller.show_error')
    def test_delete_user_self_deletion(self, mock_show_error, mock_list_all_users, mock_session_local, controller):
        mock_db = mock_session_local.return_value
        user = Mock(spec=User, id=3)
        mock_list_all_users.return_value = [user]
        controller.view.get_user_selection.return_value = user

        controller.delete_user()

        mock_show_error.assert_called_once_with("Vous ne pouvez pas supprimer votre propre compte.")
        mock_db.close.assert_called_once()

    @patch('app.controllers.user_menu_controller.SessionLocal')
    @patch('app.controllers.user_menu_controller.list_all_users')
    @patch('app.controllers.user_menu_controller.check_user_associations')
    @patch('app.controllers.user_menu_controller.show_error')
    def test_delete_user_with_associations(self, mock_show_error, mock_check_associations, mock_list_all_users,
                                           mock_session_local, controller):
        mock_db = mock_session_local.return_value
        user = Mock(spec=User, id=2)
        mock_list_all_users.return_value = [user]
        controller.view.get_user_selection.return_value = user
        controller.view.confirm_user_deletion.return_value = True
        mock_check_associations.return_value = {
            'has_associations': True,
            'clients_count': 2,
            'contracts_count': 1,
            'events_count': 3
        }

        controller.delete_user()

        expected_error = (
            "Impossible de supprimer cet utilisateur. Il est associé à:\n"
            "- 2 client(s)\n- 1 contrat(s)\n- 3 événement(s)\n"
            "Veuillez d'abord réassigner ces éléments à un autre utilisateur."
        )
        mock_show_error.assert_called_once_with(expected_error)
        mock_db.close.assert_called_once()
