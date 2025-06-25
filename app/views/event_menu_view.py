import click
from datetime import datetime
from app.models.user import UserRole


class EvenMenuView:
    """View for event management"""

    def show_events_menu(self, current_user):
        """Display events menu based on user role"""
        click.clear()
        click.echo("=" * 60)
        click.echo("🎉 GESTION DES ÉVÉNEMENTS")
        click.echo("=" * 60)
        click.echo()

        click.echo("📋 MENU ÉVÉNEMENTS")
        click.echo("-" * 20)
        click.echo("1. 📋 Lister tous les événements")

        # Only COMMERCIAL can create events
        if current_user.role == UserRole.COMMERCIAL:
            click.echo("2. ➕ Créer un nouvel événement")

        # SUPPORT and GESTION can update events
        if current_user.role in [UserRole.SUPPORT, UserRole.GESTION]:
            click.echo("3. ✏️  Modifier un événement")

        click.echo("4. 🔍 Filtrer les événements")
        click.echo("0. ⬅️  Retour au menu principal")
        click.echo()

        return click.prompt("Votre choix", type=str).strip()

    def get_event_data(self, signed_contracts):
        """Get event data from user input"""
        click.echo()
        click.echo("📝 CRÉATION D'UN NOUVEL ÉVÉNEMENT")
        click.echo("-" * 40)

        # Select contract (only signed contracts)
        contract = self.get_contract_selection(signed_contracts, "contrats signés")
        if not contract:
            return None

        data = {}
        data['contract_id'] = contract.id
        data['name'] = click.prompt("Nom de l'événement", type=str).strip()

        # Event dates
        click.echo("\n📅 Dates de l'événement:")
        data['start_date'] = self.get_datetime_input("Date et heure de début (DD/MM/YYYY HH:MM)")
        data['end_date'] = self.get_datetime_input("Date et heure de fin (DD/MM/YYYY HH:MM)")

        # Validate dates
        if data['end_date'] <= data['start_date']:
            click.echo("❌ La date de fin doit être postérieure à la date de début.")
            return None

        data['location'] = click.prompt("Lieu de l'événement", type=str).strip()
        data['attendees'] = click.prompt("Nombre de participants", type=int, default=0)
        data['notes'] = click.prompt("Notes (optionnel)", default="", type=str).strip()

        return data

    def get_event_update_data(self, event, support_users=None):
        """Get updated event data from user input"""
        click.echo()
        click.echo(f"✏️  MODIFICATION DE L'ÉVÉNEMENT: {event.name}")
        click.echo("-" * 60)

        data = {}
        data['name'] = click.prompt("Nom de l'événement", default=event.name, type=str).strip()

        # Event dates
        click.echo("\n📅 Dates de l'événement:")
        data['start_date'] = self.get_datetime_input("Date et heure de début (DD/MM/YYYY HH:MM)",
                                                     default=event.date_start)
        data['end_date'] = self.get_datetime_input("Date et heure de fin (DD/MM/YYYY HH:MM)",
                                                   default=event.date_end)

        # Validate dates
        if data['end_date'] <= data['start_date']:
            click.echo("❌ La date de fin doit être postérieure à la date de début.")
            return None

        data['location'] = click.prompt("Lieu de l'événement", default=event.location, type=str).strip()
        data['attendees'] = click.prompt("Nombre de participants", default=event.attendees, type=int)
        data['notes'] = click.prompt("Notes", default=event.notes or "", type=str).strip()

        # Support assignment (only for GESTION role)
        if support_users:
            support_contact = self.get_support_selection(support_users, event.support_contact)
            if support_contact:
                data['support_contact_id'] = support_contact.id

        return data

    def get_datetime_input(self, prompt_text, default=None):
        """Get datetime input from user"""
        while True:
            try:
                if default:
                    default_str = default.strftime("%d/%m/%Y %H:%M")
                    date_str = click.prompt(prompt_text, default=default_str, type=str).strip()
                else:
                    date_str = click.prompt(prompt_text, type=str).strip()

                return datetime.strptime(date_str, "%d/%m/%Y %H:%M")
            except ValueError:
                click.echo("❌ Format invalide. Utilisez le format DD/MM/YYYY HH:MM (ex: 25/12/2023 14:30)")

    def display_events_list(self, events):
        """Display list of events"""
        click.echo()
        click.echo("📋 LISTE DES ÉVÉNEMENTS")
        click.echo("=" * 120)

        if not events:
            click.echo("Aucun événement trouvé.")
            return

        for event in events:
            support_name = event.support_contact.name if event.support_contact else "Non assigné"
            support_status = "👤" if event.support_contact else "⚠️"

            click.echo(f"ID: {event.id} | {event.name}")
            click.echo(f"   Client: {event.contract.client.full_name} | Contrat ID: {event.contract.id}")
            click.echo(
                f"   📅 {event.date_start.strftime('%d/%m/%Y %H:%M')} → {event.date_end.strftime('%d/%m/%Y %H:%M')}")
            click.echo(f"   📍 {event.location} | 👥 {event.attendees} participants")
            click.echo(f"   {support_status} Support: {support_name}")
            if event.notes:
                click.echo(f"   📝 Notes: {event.notes}")
            click.echo("-" * 120)

        click.echo()
        click.pause("Appuyez sur Entrée pour continuer...")

    def get_event_selection(self, events):
        """Get event selection from user"""
        if not events:
            click.echo("Aucun événement disponible.")
            return None

        click.echo()
        click.echo("🔍 SÉLECTION D'UN ÉVÉNEMENT")
        click.echo("-" * 30)

        for i, event in enumerate(events, 1):
            support_info = f"Support: {event.support_contact.name}" if event.support_contact else "Sans support"
            click.echo(f"{i}. {event.name} - {event.contract.client.full_name} ({support_info})")

        click.echo("0. Annuler")

        try:
            choice = click.prompt("Sélectionnez un événement", type=int)
            if choice == 0:
                return None
            if 1 <= choice <= len(events):
                return events[choice - 1]
            else:
                click.echo("Choix invalide.")
                return None
        except ValueError:
            click.echo("Veuillez entrer un nombre valide.")
            return None

    def get_contract_selection(self, contracts, contract_type="contrats"):
        """Get contract selection from user"""
        if not contracts:
            click.echo(f"Aucun {contract_type} disponible.")
            return None

        click.echo()
        click.echo(f"🔍 SÉLECTION D'UN CONTRAT ({contract_type.upper()})")
        click.echo("-" * 40)

        for i, contract in enumerate(contracts, 1):
            click.echo(f"{i}. ID:{contract.id} - {contract.client.full_name} ({contract.client.company_name})")

        click.echo("0. Annuler")

        try:
            choice = click.prompt("Sélectionnez un contrat", type=int)
            if choice == 0:
                return None
            if 1 <= choice <= len(contracts):
                return contracts[choice - 1]
            else:
                click.echo("Choix invalide.")
                return None
        except ValueError:
            click.echo("Veuillez entrer un nombre valide.")
            return None

    def get_support_selection(self, support_users, current_support=None):
        """Get support user selection"""
        click.echo()
        click.echo("👤 ASSIGNATION DU SUPPORT")
        click.echo("-" * 25)

        current_text = f" (actuellement: {current_support.name})" if current_support else ""
        click.echo(f"Choisissez un membre du support{current_text}:")

        for i, user in enumerate(support_users, 1):
            current_indicator = " ← ACTUEL" if current_support and user.id == current_support.id else ""
            click.echo(f"{i}. {user.name}{current_indicator}")

        click.echo("0. Ne pas modifier")

        try:
            choice = click.prompt("Sélectionnez un support", type=int)
            if choice == 0:
                return None
            if 1 <= choice <= len(support_users):
                return support_users[choice - 1]
            else:
                click.echo("Choix invalide.")
                return None
        except ValueError:
            click.echo("Veuillez entrer un nombre valide.")
            return None

    def get_event_filter(self, current_user):
        """Get event filter criteria based on user role"""
        click.echo()
        click.echo("🔍 FILTRAGE DES ÉVÉNEMENTS")
        click.echo("-" * 30)

        if current_user.role == UserRole.SUPPORT:
            click.echo("1. Mes événements (assignés à moi)")
            click.echo("2. Événements sans support assigné")
            click.echo("0. Tous les événements")

            choice = click.prompt("Type de filtre", type=str).strip()

            filters = {
                "1": {"support_contact_id": current_user.id},
                "2": {"support_contact_id": None},
                "0": {}
            }

        elif current_user.role == UserRole.GESTION:
            click.echo("1. Événements sans support assigné")
            click.echo("2. Événements avec support assigné")
            click.echo("3. Événements à venir")
            click.echo("4. Événements passés")
            click.echo("0. Tous les événements")

            choice = click.prompt("Type de filtre", type=str).strip()

            filters = {
                "1": {"support_contact_id": None},
                "2": {"support_contact_id_not_null": True},
                "3": {"start_date_gte": datetime.now()},
                "4": {"end_date_lt": datetime.now()},
                "0": {}
            }

        else:  # COMMERCIAL
            click.echo("1. Mes événements (mes clients)")
            click.echo("2. Événements à venir")
            click.echo("3. Événements passés")
            click.echo("0. Tous les événements")

            choice = click.prompt("Type de filtre", type=str).strip()

            filters = {
                "1": {"commercial_contact_id": current_user.id},
                "2": {"start_date_gte": datetime.now()},
                "3": {"end_date_lt": datetime.now()},
                "0": {}
            }

        return filters.get(choice, {})
