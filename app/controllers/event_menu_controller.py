from app.models.user import User, UserRole
from app.models.contract import Contract
from app.models.event import Event
from app.views.event_menu_view import EvenMenuView
from app.views.utils_view import show_error, show_success, show_info
from app.services.event_service import create_event, update_event,get_filtered_events, get_events_with_details
from app.db.connection import SessionLocal
from sqlalchemy.orm import joinedload


class EventMenuController:
    """Handle events menu navigation"""

    def __init__(self, current_user):
        self.current_user = current_user
        self.view = EvenMenuView()

    def handle_menu(self):
        """Handle the events menu loop"""
        while True:
            choice = self.view.show_events_menu(self.current_user)

            if choice == "1":
                self.list_events()
            elif choice == "2" and self.current_user.role == UserRole.COMMERCIAL:
                self.create_event()
            elif choice == "3" and self.current_user.role in [UserRole.SUPPORT, UserRole.GESTION]:
                self.update_event()
            elif choice == "4":
                self.filter_events()
            elif choice == "0":
                break
            else:
                show_error("Choix invalide ou non autorisé.")

    def list_events(self):
        """List all events"""
        db = SessionLocal()
        try:
            events = get_events_with_details(db)
            self.view.display_events_list(events)
        except Exception as e:
            show_error(f"Erreur lors de la récupération des événements: {str(e)}")
        finally:
            db.close()

    def filter_events(self):
        """Filter events (available to all users)"""
        db = SessionLocal()
        try:
            filter_criteria = self.view.get_event_filter(self.current_user)
            filtered_events = get_filtered_events(db, filter_criteria)

            if filtered_events:
                show_info(f"{len(filtered_events)} événement(s) trouvé(s) avec les critères sélectionnés.")
                self.view.display_events_list(filtered_events)
            else:
                show_info("Aucun événement ne correspond aux critères de filtrage.")
        except Exception as e:
            show_error(f"Erreur lors du filtrage des événements: {str(e)}")
        finally:
            db.close()

    def create_event(self):
        """Create a new event (COMMERCIAL only)"""
        if self.current_user.role != UserRole.COMMERCIAL:
            show_error("Accès non autorisé. Seuls les commerciaux peuvent créer des événements.")
            return

        db = SessionLocal()
        try:
            # Get signed contracts for this commercial
            signed_contracts = db.query(Contract).filter(
                Contract.commercial_id == self.current_user.id,
                Contract.is_signed is True
            ).options(joinedload(Contract.client)).all()

            if not signed_contracts:
                show_error("Aucun contrat signé disponible pour créer un événement.")
                return

            # Get event data from user
            event_data = self.view.get_event_data(signed_contracts)
            if not event_data:
                show_info("Création d'événement annulée.")
                return

            # Get the contract to access client_id
            contract = db.query(Contract).filter_by(id=event_data['contract_id']).first()

            # Create the event
            new_event = create_event(
                db=db,
                client_id=contract.client_id,
                contract_id=event_data['contract_id'],
                start=event_data['start_date'],
                end=event_data['end_date'],
                location=event_data['location'],
                attendees=event_data['attendees'],
                notes=event_data['notes'],
                name=event_data['name']
            )

            show_success(f"Événement créé avec succès (ID: {new_event.id})")

        except Exception as e:
            show_error(f"Erreur lors de la création de l'événement: {str(e)}")
        finally:
            db.close()

    def update_event(self):
        """Update an existing event (SUPPORT and GESTION)"""
        if self.current_user.role not in [UserRole.SUPPORT, UserRole.GESTION]:
            show_error("Accès non autorisé. Seuls le support et la gestion peuvent modifier des événements.")
            return

        db = SessionLocal()
        try:
            # Get events based on user role
            if self.current_user.role == UserRole.SUPPORT:
                # Support users can only update their assigned events or unassigned ones
                events = db.query(Event).filter(
                    (Event.support_id == self.current_user.id) |
                    (Event.support_id is None)
                ).options(
                    joinedload(Event.contract).joinedload(Contract.client),
                    joinedload(Event.support_contact)
                ).all()
            else:
                # Gestion can update all events
                events = db.query(Event).options(
                    joinedload(Event.contract).joinedload(Contract.client),
                    joinedload(Event.support_contact)
                ).all()

            if not events:
                show_error("Aucun événement disponible pour modification.")
                return

            # Select event to update
            selected_event = self.view.get_event_selection(events)
            if not selected_event:
                show_info("Modification annulée.")
                return

            # Get support users for assignment (only for GESTION)
            support_users = None
            if self.current_user.role == UserRole.GESTION:
                support_users = db.query(User).filter_by(role=UserRole.SUPPORT).all()

            # Get updated data
            update_data = self.view.get_event_update_data(selected_event, support_users)
            if not update_data:
                show_info("Modification annulée.")
                return

            # Update the event
            updated_fields = {
                'name': update_data['name'],
                'date_start': update_data['start_date'],
                'date_end': update_data['end_date'],
                'location': update_data['location'],
                'attendees': update_data['attendees'],
                'notes': update_data['notes']
            }

            # Handle support assignment for GESTION
            if 'support_contact_id' in update_data:
                updated_fields['support_id'] = update_data['support_contact_id']

            updated_event = update_event(
                db=db,
                event_id=selected_event.id,
                updater=self.current_user,
                **updated_fields
            )

            show_success(f"Événement ID {updated_event.id} modifié avec succès.")

        except PermissionError as e:
            show_error(str(e))
        except Exception as e:
            show_error(f"Erreur lors de la modification de l'événement: {str(e)}")
        finally:
            db.close()
