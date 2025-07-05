import sentry_sdk
from datetime import date

from app.views.contract_menu_view import ContractMenuView
from app.services.contract_service import *
from app.db.connection import SessionLocal
from app.views.utils_view import show_error, show_success


class ContractMenuController:
    """Handle contracts menu navigation"""

    def __init__(self, current_user):
        self.current_user = current_user
        self.view = ContractMenuView()

    def handle_menu(self):
        """Handle the contracts menu loop"""
        while True:
            choice = self.view.show_contracts_menu(self.current_user)

            if choice == "1":
                self.list_contracts()
            elif choice == "2" and self.current_user.role == UserRole.GESTION:
                self.create_contract()
            elif choice == "3" and self.current_user.role in [UserRole.COMMERCIAL, UserRole.GESTION]:
                self.update_contract()
            elif choice == "4":
                self.filter_contracts()
            elif choice == "0":
                break
            else:
                show_error("Choix invalide ou non autorisé.")

    def list_contracts(self):
        """List all contracts"""
        db = SessionLocal()
        try:
            contracts = get_all_contracts(db)
            self.view.display_contracts_list(contracts)
        except Exception as e:
            show_error(f"Erreur lors de la récupération des contrats: {str(e)}")
            sentry_sdk.capture_exception(e)
        finally:
            db.close()

    def create_contract(self):
        """Create a new contract (GESTION only)"""
        if self.current_user.role != UserRole.GESTION:
            show_error("Accès non autorisé. Seule la gestion peut créer des contrats.")
            return

        db = SessionLocal()
        try:
            # Get all clients
            clients = get_all_clients(db)
            if not clients:
                show_error("Aucun client disponible. Créez d'abord des clients.")
                return

            # Get contract data from user
            contract_data = self.view.get_contract_data(clients)
            if not contract_data:
                return

            # Get commercial users for assignment
            commercials = get_commercial_users(db)

            if not commercials:
                show_error("Aucun commercial disponible.")
                return

            # Let user select commercial
            commercial = self.view.get_commercial_selection(commercials)
            if not commercial:
                return

            # Create the contract
            contract = create_contract(
                db=db,
                client_id=contract_data['client_id'],
                commercial_id=commercial.id,
                total_amount=contract_data['total_amount']
            )

            # Update additional fields if provided
            if 'is_signed' in contract_data:
                contract.is_signed = contract_data['is_signed']
            if 'amount_due' in contract_data:
                contract.amount_due = contract_data['amount_due']

            contract.date_created = date.today()
            db.commit()

            show_success(f"Contrat créé avec succès (ID: {contract.id})")
            sentry_sdk.capture_message(f"Contract created successfully (ID: {contract.id})", level="info")

        except Exception as e:
            db.rollback()
            show_error(f"Erreur lors de la création du contrat: {str(e)}")
            sentry_sdk.capture_exception(e)
        finally:
            db.close()

    def update_contract(self):
        """Update an existing contract (COMMERCIAL and GESTION)"""
        if self.current_user.role not in [UserRole.COMMERCIAL, UserRole.GESTION]:
            show_error("Accès non autorisé. Seuls les commerciaux et la gestion peuvent modifier des contrats.")
            return

        db = SessionLocal()
        try:
            # Get contracts that user can modify
            contracts = get_contracts_by_user(db, self.current_user)
            if not contracts:
                show_error("Aucun contrat disponible pour modification.")
                return

            # Let user select contract
            contract = self.view.get_contract_selection(contracts)
            if not contract:
                return

            # Check permissions for COMMERCIAL role
            if (self.current_user.role == UserRole.COMMERCIAL and
                    contract.commercial_id != self.current_user.id):
                show_error("Vous ne pouvez modifier que vos propres contrats.")
                return

            # Get updated data
            update_data = self.view.get_contract_update_data(contract)
            if not update_data:
                return

            # Update the contract
            updated_contract = update_contract(
                db=db,
                contract_id=contract.id,
                updater=self.current_user,
                **update_data
            )

            show_success(f"Contrat {updated_contract.id} modifié avec succès.")
            sentry_sdk.capture_message(f"Contract {updated_contract.id} modified successfully", level="info")

        except PermissionError as e:
            show_error(str(e))
        except Exception as e:
            db.rollback()
            show_error(f"Erreur lors de la modification du contrat: {str(e)}")
        finally:
            db.close()

    def filter_contracts(self):
        """Filter contracts (available to all users)"""
        db = SessionLocal()
        try:
            # Get filter criteria
            filter_choice = self.view.get_contract_filter()

            if filter_choice == "unsigned":
                contracts = list_unsigned_contracts(db)
            elif filter_choice == "unpaid":
                contracts = list_unpaid_contracts(db)
            elif filter_choice == "signed":
                contracts = list_signed_contracts(db)
            elif filter_choice == "paid":
                contracts = list_paid_contracts(db)
            else:
                # Show all contracts based on user role
                contracts = get_contracts_by_user(db, self.current_user)

            # Filter by user role permissions
            if self.current_user.role == UserRole.COMMERCIAL:
                contracts = [c for c in contracts if c.commercial_id == self.current_user.id]

            self.view.display_contracts_list(contracts)

        except Exception as e:
            show_error(f"Erreur lors du filtrage des contrats: {str(e)}")
            sentry_sdk.capture_exception(e)
        finally:
            db.close()
