from datetime import date
from app.models.user import UserRole
from app.views.client_menu_view import ClientMenuView
from app.views.utils_view import show_error, show_success, show_info
from app.services.client_service import create_client, update_client, get_clients_by_user
from app.db.connection import SessionLocal


class ClientMenuController:
    """Handle clients menu navigation"""

    def __init__(self, current_user):
        self.current_user = current_user
        self.view = ClientMenuView()

    def handle_menu(self):
        """Handle the clients menu loop"""
        while True:
            choice = self.view.show_clients_menu(self.current_user)

            if choice == "1":
                self.list_clients()
            elif choice == "2" and self.current_user.role == UserRole.COMMERCIAL:
                self.create_client()
            elif choice == "3" and self.current_user.role == UserRole.COMMERCIAL:
                self.update_client()
            elif choice == "0":
                break
            else:
                show_error("Choix invalide ou non autorisé.")

    def list_clients(self):
        """List all clients based on user role"""
        try:
            db = SessionLocal()
            clients = get_clients_by_user(db, self.current_user)

            if clients:
                self.view.display_clients_list(clients)
            else:
                show_info("Aucun client trouvé.")

        except Exception as e:
            show_error(f"Erreur lors de la récupération des clients: {str(e)}")
        finally:
            db.close()

    def create_client(self):
        """Create a new client (COMMERCIAL only)"""
        if self.current_user.role != UserRole.COMMERCIAL:
            show_error("Accès non autorisé. Seuls les commerciaux peuvent créer des clients.")
            return

        try:
            client_data = self.view.get_client_data()

            if not client_data:
                show_info("Création annulée.")
                return

            # Validate required fields
            if not client_data.get('full_name') or not client_data.get('email'):
                show_error("Le nom complet et l'email sont obligatoires.")
                return

            client_data['date_created'] = date.today()
            client_data['last_contact'] = date.today()

            # Create client in database
            db = SessionLocal()
            client = create_client(db, self.current_user.id, **client_data)

            show_success(f"Client '{client.full_name}' créé avec succès (ID: {client.id})")

        except Exception as e:
            show_error(f"Erreur lors de la création du client: {str(e)}")
        finally:
            db.close()

    def update_client(self):
        """Update an existing client COMMERCIAL"""
        if self.current_user.role != UserRole.COMMERCIAL:
            show_error(
                "Accès non autorisé. Seuls les commerciaux et la gestion peuvent modifier des clients.")
            return

        try:
            # Get list of clients user can modify
            db = SessionLocal()
            clients = get_clients_by_user(db, self.current_user)

            if not clients:
                show_info("Aucun client disponible pour modification.")
                return

            # Let user select a client
            selected_client = self.view.get_client_selection(clients)

            if not selected_client:
                show_info("Modification annulée.")
                return

            # Check permissions for COMMERCIAL role
            if (self.current_user.role == UserRole.COMMERCIAL and
                    selected_client.commercial_id != self.current_user.id):
                show_error("Vous ne pouvez modifier que vos propres clients.")
                return

            # Get updated data
            updated_data = self.view.get_client_update_data(selected_client)

            if not updated_data:
                show_info("Modification annulée.")
                return

            # Validate required fields
            if not updated_data.get('full_name') or not updated_data.get('email'):
                show_error("Le nom complet et l'email sont obligatoires.")
                return

            # Add last contact update
            updated_data['last_contact'] = date.today()

            # Update client in database
            updated_client = update_client(db, selected_client.id, self.current_user, **updated_data)

            show_success(f"Client '{updated_client.full_name}' modifié avec succès.")

        except PermissionError as e:
            show_error(str(e))
        except Exception as e:
            show_error(f"Erreur lors de la modification du client: {str(e)}")
        finally:
            db.close()