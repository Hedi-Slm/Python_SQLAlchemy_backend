import click
from app.models.user import UserRole


class ContractMenuView:
    """View for contract management"""

    def show_contracts_menu(self, current_user):
        """Display contracts menu based on user role"""
        click.clear()
        click.echo("=" * 60)
        click.echo("📄 GESTION DES CONTRATS")
        click.echo("=" * 60)
        click.echo()

        click.echo("📋 MENU CONTRATS")
        click.echo("-" * 20)
        click.echo("1. 📋 Lister tous les contrats")

        # Only GESTION can create contracts
        if current_user.role == UserRole.GESTION:
            click.echo("2. ➕ Créer un nouveau contrat")

        # COMMERCIAL and GESTION can update contracts
        if current_user.role in [UserRole.COMMERCIAL, UserRole.GESTION]:
            click.echo("3. ✏️  Modifier un contrat")

        click.echo("4. 🔍 Filtrer les contrats")
        click.echo("0. ⬅️  Retour au menu principal")
        click.echo()

        return click.prompt("Votre choix", type=str).strip()

    def get_contract_data(self, clients):
        """Get contract data from user input"""
        click.echo()
        click.echo("📝 CRÉATION D'UN NOUVEAU CONTRAT")
        click.echo("-" * 40)

        # Select client
        client = self.get_client_selection(clients)
        if not client:
            return None

        try:
            data = {}
            data['client_id'] = client.id
            data['total_amount'] = click.prompt("Montant total du contrat (€)", type=float)

            # Amount due defaults to total amount
            default_amount_due = data['total_amount']
            data['amount_due'] = click.prompt(
                "Montant restant à payer (€)",
                type=float,
                default=default_amount_due
            )

            data['is_signed'] = click.confirm("Le contrat est-il signé ?", default=False)

            return data
        except (ValueError, click.Abort):
            click.echo("Création annulée.")
            return None

    def get_contract_update_data(self, contract):
        """Get updated contract data from user input"""
        click.echo()
        click.echo(f"✏️  MODIFICATION DU CONTRAT ID: {contract.id}")
        click.echo(f"    Client: {contract.client.full_name}")
        click.echo("-" * 50)

        try:
            data = {}
            data['total_amount'] = click.prompt(
                "Montant total du contrat (€)",
                default=float(contract.total_amount),
                type=float
            )
            data['amount_due'] = click.prompt(
                "Montant restant à payer (€)",
                default=float(contract.amount_due),
                type=float
            )
            data['is_signed'] = click.confirm(
                "Le contrat est-il signé ?",
                default=contract.is_signed
            )

            return data
        except (ValueError, click.Abort):
            click.echo("Modification annulée.")
            return None

    def display_contracts_list(self, contracts):
        """Display list of contracts"""
        click.echo()
        click.echo("📋 LISTE DES CONTRATS")
        click.echo("=" * 100)

        if not contracts:
            click.echo("Aucun contrat trouvé.")
            return

        for contract in contracts:
            status = "✅ Signé" if contract.is_signed else "⏳ En attente"
            amount_due_status = "💰 Payé" if contract.amount_due == 0 else f"💸 Reste {contract.amount_due}€"

            click.echo(f"ID: {contract.id} | Client: {contract.client.full_name}")
            click.echo(f"   Montant total: {contract.total_amount}€ | {amount_due_status}")
            click.echo(f"   Statut: {status} | Commercial: {contract.commercial.name}")

            if contract.date_created:
                click.echo(f"   Créé le: {contract.date_created.strftime('%d/%m/%Y')}")
            else:
                click.echo(f"   Créé le: Non renseigné")

            click.echo("-" * 100)

    def get_contract_selection(self, contracts):
        """Get contract selection from user"""
        if not contracts:
            click.echo("Aucun contrat disponible.")
            return None

        click.echo()
        click.echo("🔍 SÉLECTION D'UN CONTRAT")
        click.echo("-" * 30)

        for i, contract in enumerate(contracts, 1):
            status = "Signé" if contract.is_signed else "En attente"
            click.echo(f"{i}. ID:{contract.id} - {contract.client.full_name} ({status})")

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
        except (ValueError, click.Abort):
            click.echo("Sélection annulée.")
            return None

    def get_client_selection(self, clients):
        """Get client selection from user"""
        if not clients:
            click.echo("Aucun client disponible.")
            return None

        click.echo()
        click.echo("🔍 SÉLECTION D'UN CLIENT")
        click.echo("-" * 25)

        for i, client in enumerate(clients, 1):
            company_info = f" ({client.company_name})" if client.company_name else ""
            click.echo(f"{i}. {client.full_name}{company_info}")

        click.echo("0. Annuler")

        try:
            choice = click.prompt("Sélectionnez un client", type=int)
            if choice == 0:
                return None
            if 1 <= choice <= len(clients):
                return clients[choice - 1]
            else:
                click.echo("Choix invalide.")
                return None
        except (ValueError, click.Abort):
            click.echo("Sélection annulée.")
            return None

    def get_commercial_selection(self, commercials):
        """Get commercial selection from user"""
        if not commercials:
            click.echo("Aucun commercial disponible.")
            return None

        click.echo()
        click.echo("🔍 SÉLECTION D'UN COMMERCIAL")
        click.echo("-" * 30)

        for i, commercial in enumerate(commercials, 1):
            click.echo(f"{i}. {commercial.name} ({commercial.email})")

        click.echo("0. Annuler")

        try:
            choice = click.prompt("Sélectionnez un commercial", type=int)
            if choice == 0:
                return None
            if 1 <= choice <= len(commercials):
                return commercials[choice - 1]
            else:
                click.echo("Choix invalide.")
                return None
        except (ValueError, click.Abort):
            click.echo("Sélection annulée.")
            return None

    def get_contract_filter(self):
        """Get contract filter criteria"""
        click.echo()
        click.echo("🔍 FILTRAGE DES CONTRATS")
        click.echo("-" * 25)
        click.echo("1. Contrats non signés")
        click.echo("2. Contrats au payement partiel")
        click.echo("3. Contrats signés")
        click.echo("4. Contrats entièrement payés")
        click.echo("0. Tous les contrats")

        choice = click.prompt("Type de filtre", type=str).strip()

        filter_map = {
            "1": "unsigned",
            "2": "unpaid",
            "3": "signed",
            "4": "paid",
            "0": "all"
        }

        return filter_map.get(choice, "all")
