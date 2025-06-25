import click
from app.models.user import UserRole


class ClientMenuView:
    """View for client management"""

    def show_clients_menu(self, current_user):
        """Display clients menu based on user role"""
        click.clear()
        click.echo("=" * 60)
        click.echo("👥 GESTION DES CLIENTS")
        click.echo("=" * 60)
        click.echo()

        click.echo("📋 MENU CLIENTS")
        click.echo("-" * 20)
        click.echo("1. 📋 Lister tous les clients")

        # Only COMMERCIAL can create clients
        if current_user.role == UserRole.COMMERCIAL:
            click.echo("2. ➕ Créer un nouveau client")

        # COMMERCIAL can update clients
        if current_user.role == UserRole.COMMERCIAL:
            click.echo("3. ✏️  Modifier un client")

        click.echo("0. ⬅️  Retour au menu principal")
        click.echo()

        return click.prompt("Votre choix", type=str).strip()

    def get_client_data(self):
        """Get client data from user input"""
        click.echo()
        click.echo("📝 CRÉATION D'UN NOUVEAU CLIENT")
        click.echo("-" * 35)

        try:
            data = {}
            data['full_name'] = click.prompt("Nom complet", type=str).strip()

            if not data['full_name']:
                click.echo("❌ Le nom complet est obligatoire.")
                return None

            data['email'] = click.prompt("Email", type=str).strip()

            if not data['email']:
                click.echo("❌ L'email est obligatoire.")
                return None

            # Validate basic email format
            if '@' not in data['email'] or '.' not in data['email']:
                click.echo("❌ Format d'email invalide.")
                return None

            data['phone'] = click.prompt("Téléphone (optionnel)", default="", type=str).strip()
            data['company_name'] = click.prompt("Nom de l'entreprise (optionnel)", default="", type=str).strip()

            # Confirm creation
            click.echo()
            click.echo("📋 RÉCAPITULATIF")
            click.echo("-" * 15)
            click.echo(f"Nom: {data['full_name']}")
            click.echo(f"Email: {data['email']}")
            click.echo(f"Téléphone: {data['phone'] or 'Non renseigné'}")
            click.echo(f"Entreprise: {data['company_name'] or 'Non renseignée'}")
            click.echo()

            if click.confirm("Confirmer la création de ce client ?"):
                return data
            else:
                return None

        except (KeyboardInterrupt, click.Abort):
            return None

    def get_client_update_data(self, client):
        """Get updated client data from user input"""
        click.echo()
        click.echo(f"✏️  MODIFICATION DU CLIENT: {client.full_name}")
        click.echo("-" * 50)
        click.echo()
        click.echo("ℹ️  Laissez vide pour conserver la valeur actuelle")
        click.echo()

        try:
            data = {}

            current_name = getattr(client, 'full_name', '')
            new_name = click.prompt("Nom complet", default=current_name, type=str).strip()
            if new_name and new_name != current_name:
                data['full_name'] = new_name
            elif not new_name:
                click.echo("❌ Le nom complet ne peut pas être vide.")
                return None
            else:
                data['full_name'] = current_name

            current_email = getattr(client, 'email', '')
            new_email = click.prompt("Email", default=current_email, type=str).strip()
            if new_email and new_email != current_email:
                # Validate basic email format
                if '@' not in new_email or '.' not in new_email:
                    click.echo("❌ Format d'email invalide.")
                    return None
                data['email'] = new_email
            elif not new_email:
                click.echo("❌ L'email ne peut pas être vide.")
                return None
            else:
                data['email'] = current_email

            current_phone = getattr(client, 'phone', '') or ''
            new_phone = click.prompt("Téléphone", default=current_phone, type=str).strip()
            data['phone'] = new_phone

            current_company = getattr(client, 'company_name', '') or ''
            new_company = click.prompt("Nom de l'entreprise", default=current_company, type=str).strip()
            data['company_name'] = new_company

            # Show summary of changes
            click.echo()
            click.echo("📋 MODIFICATIONS À APPORTER")
            click.echo("-" * 30)

            changes_made = False
            if data['full_name'] != current_name:
                click.echo(f"Nom: {current_name} → {data['full_name']}")
                changes_made = True

            if data['email'] != current_email:
                click.echo(f"Email: {current_email} → {data['email']}")
                changes_made = True

            if data['phone'] != current_phone:
                click.echo(f"Téléphone: {current_phone or 'Non renseigné'} → {data['phone'] or 'Non renseigné'}")
                changes_made = True

            if data['company_name'] != current_company:
                click.echo(
                    f"Entreprise: {current_company or 'Non renseignée'} → {data['company_name'] or 'Non renseignée'}")
                changes_made = True

            if not changes_made:
                click.echo("Aucune modification détectée.")
                return None

            click.echo()
            if click.confirm("Confirmer les modifications ?"):
                return data
            else:
                return None

        except (KeyboardInterrupt, click.Abort):
            return None

    def display_clients_list(self, clients):
        """Display list of clients"""
        click.echo()
        click.echo("📋 LISTE DES CLIENTS")
        click.echo("=" * 100)

        if not clients:
            click.echo("Aucun client trouvé.")
            return

        for i, client in enumerate(clients, 1):
            click.echo(f"{i}. ID: {client.id}")
            click.echo(f"   👤 {client.full_name}")
            click.echo(f"   🏢 {client.company_name or 'Entreprise non renseignée'}")
            click.echo(f"   📧 {client.email}")
            click.echo(f"   📞 {client.phone or 'Téléphone non renseigné'}")

            # Display commercial contact
            commercial_name = getattr(client.commercial, 'name', 'Non assigné') \
                if hasattr(client, 'commercial') else 'Non assigné'

            click.echo(f"   👨‍💼 Commercial: {commercial_name}")

            # Display dates if available
            if hasattr(client, 'date_created') and client.date_created:
                click.echo(f"   📅 Créé le: {client.date_created.strftime('%d/%m/%Y')}")
            if hasattr(client, 'last_contact') and client.last_contact:
                click.echo(f"   📞 Dernier contact: {client.last_contact.strftime('%d/%m/%Y')}")

            click.echo("-" * 100)

        click.echo(f"\n Total: {len(clients)} client(s)")

    def get_client_selection(self, clients):
        """Get client selection from user"""
        if not clients:
            click.echo("Aucun client disponible.")
            return None

        click.echo()
        click.echo("🔍 SÉLECTION D'UN CLIENT")
        click.echo("-" * 25)

        # Display simplified list for selection
        for i, client in enumerate(clients, 1):
            company_info = f" ({client.company_name})" if client.company_name else ""
            click.echo(f"{i}. {client.full_name}{company_info}")

        click.echo("0. ❌ Annuler")
        click.echo()

        try:
            choice = click.prompt("Sélectionnez un client", type=int)
            if choice == 0:
                return None
            if 1 <= choice <= len(clients):
                return clients[choice - 1]
            else:
                click.echo("❌ Choix invalide.")
                return None
        except (ValueError, KeyboardInterrupt, click.Abort):
            click.echo("❌ Sélection annulée.")
            return None