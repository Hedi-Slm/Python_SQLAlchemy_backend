import sentry_sdk

from app.views.user_menu_view import UserMenuView
from app.services.user_service import *
from app.db.connection import SessionLocal
from app.utils.password import hash_password
from app.views.utils_view import show_error, show_success, show_info, show_warning


class UserMenuController:
    """Handle users menu navigation (GESTION only)"""

    def __init__(self, current_user):
        self.current_user = current_user
        self.view = UserMenuView()

    def handle_menu(self):
        """Handle the users menu loop"""
        # Double-check authorization
        if self.current_user.role != UserRole.GESTION:
            show_error("Accès non autorisé. Seule la gestion peut gérer les utilisateurs.")
            return

        while True:
            choice = self.view.show_users_menu()

            if choice == "1":
                self.list_users()
            elif choice == "2":
                self.create_user()
            elif choice == "3":
                self.update_user()
            elif choice == "4":
                self.delete_user()
            elif choice == "0":
                break
            else:
                show_error("Choix invalide.")

    def list_users(self):
        """List all users (GESTION only)"""
        db = SessionLocal()
        try:
            users = list_all_users(db)
            self.view.display_users_list(users)
        except Exception as e:
            show_error(f"Erreur lors de la récupération des utilisateurs: {str(e)}")
            sentry_sdk.capture_exception(e)
        finally:
            db.close()

    def create_user(self):
        """Create a new user (GESTION only)"""
        db = SessionLocal()
        try:
            # Get user data from view
            user_data = self.view.get_user_data()

            if not user_data:
                show_info("Création annulée.")
                return

            # Validate required fields
            if not all([user_data.get('name'), user_data.get('email'),
                        user_data.get('password'), user_data.get('role')]):
                show_error("Tous les champs sont requis.")
                return

            # Check if email already exists using service
            existing_user = get_user_by_email(db, user_data['email'])
            if existing_user:
                show_error("Un utilisateur avec cet email existe déjà.")
                return

            # Create user
            new_user = create_user(
                db=db,
                name=user_data['name'],
                email=user_data['email'],
                role=user_data['role'],
                password=user_data['password']
            )

            show_success(f"Utilisateur '{new_user.name}' créé avec succès.")
            sentry_sdk.capture_message(f"User '{new_user.name}' created successfully.", level="info")

        except Exception as e:
            show_error(f"Erreur lors de la création de l'utilisateur: {str(e)}")
            sentry_sdk.capture_exception(e)
        finally:
            db.close()

    def update_user(self):
        """Update an existing user (GESTION only)"""
        db = SessionLocal()
        try:
            # Get list of users using service
            users = list_all_users(db)

            if not users:
                show_info("Aucun utilisateur à modifier.")
                return

            # Let user select which user to update
            selected_user = self.view.get_user_selection(users, "modifier")

            if not selected_user:
                show_info("Modification annulée.")
                return

            # Prevent self-deletion of role if current user is the selected user
            if selected_user.id == self.current_user.id:
                show_warning("Vous modifiez votre propre compte. Soyez prudent avec les changements de rôle.")

            # Get updated data
            updated_data = self.view.get_user_update_data(selected_user)

            if not updated_data:
                show_info("Modification annulée.")
                return

            # Check if email is being changed and if it already exists using service
            if updated_data['email'] != selected_user.email:
                if email_exists_for_different_user(db, updated_data['email'], selected_user.id):
                    show_error("Un utilisateur avec cet email existe déjà.")
                    return

            # Prepare fields to update
            fields_to_update = {}

            if updated_data['name'] != selected_user.name:
                fields_to_update['name'] = updated_data['name']

            if updated_data['email'] != selected_user.email:
                fields_to_update['email'] = updated_data['email']

            if updated_data['password']:
                fields_to_update['password'] = hash_password(updated_data['password'])

            if updated_data['role'] != selected_user.role:
                fields_to_update['role'] = updated_data['role']

            if not fields_to_update:
                show_info("Aucune modification détectée.")
                return

            updated_user = update_user(db, selected_user.id, **fields_to_update)

            show_success(f"Utilisateur '{updated_user.name}' modifié avec succès.")
            sentry_sdk.capture_message(f"User '{updated_user.name}' updated successfully", level="info")

            # Warning if current user changed their own role
            if selected_user.id == self.current_user.id and 'role' in fields_to_update:
                show_warning("Vous avez modifié votre propre rôle."
                             " Veuillez vous reconnecter pour que les changements prennent effet.")

        except Exception as e:
            show_error(f"Erreur lors de la modification de l'utilisateur: {str(e)}")
            sentry_sdk.capture_exception(e)
        finally:
            db.close()

    def delete_user(self):
        """Delete a user (GESTION only)"""
        db = SessionLocal()
        try:
            # Get list of users using service
            users = list_all_users(db)

            if not users:
                show_info("Aucun utilisateur à supprimer.")
                return

            # Let user select which user to delete
            selected_user = self.view.get_user_selection(users, "supprimer")

            if not selected_user:
                show_info("Suppression annulée.")
                return

            # Prevent self-deletion
            if selected_user.id == self.current_user.id:
                show_error("Vous ne pouvez pas supprimer votre propre compte.")
                return

            # Show user details and confirm deletion
            self.view.show_user_details(selected_user)

            if not self.view.confirm_user_deletion(selected_user):
                show_info("Suppression annulée.")
                return

            # Check if user has associated data using service
            associations = check_user_associations(db, selected_user.id)

            if associations['has_associations']:
                show_error(
                    f"Impossible de supprimer cet utilisateur. Il est associé à:\n"
                    f"- {associations['clients_count']} client(s)\n"
                    f"- {associations['contracts_count']} contrat(s)\n"
                    f"- {associations['events_count']} événement(s)\n"
                    f"Veuillez d'abord réassigner ces éléments à un autre utilisateur."
                )
                return

            # Delete user
            user_name = selected_user.name
            delete_user(db, selected_user.id)

            show_success(f"Utilisateur '{user_name}' supprimé avec succès.")
            sentry_sdk.capture_message(f"User '{user_name}' deleted successfully", level="info")

        except Exception as e:
            show_error(f"Erreur lors de la suppression de l'utilisateur: {str(e)}")
            sentry_sdk.capture_exception(e)
        finally:
            db.close()
