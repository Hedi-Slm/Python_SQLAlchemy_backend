import click
from app.models.user import UserRole


class UserMenuView:
    """View for user management (GESTION only)"""

    def show_users_menu(self):
        """Display users menu"""
        click.clear()
        click.echo("=" * 60)
        click.echo("👤 GESTION DES UTILISATEURS")
        click.echo("=" * 60)
        click.echo()

        click.echo("📋 MENU UTILISATEURS")
        click.echo("-" * 20)
        click.echo("1. 📋 Lister tous les utilisateurs")
        click.echo("2. ➕ Créer un nouvel utilisateur")
        click.echo("3. ✏️ Modifier un utilisateur")
        click.echo("4. 🗑️ Supprimer un utilisateur")
        click.echo("0. ⬅️ Retour au menu principal")
        click.echo()

        return click.prompt("Votre choix", type=str).strip()

    def get_user_data(self):
        """Get user data from user input"""
        click.echo()
        click.echo("📝 CRÉATION D'UN NOUVEL UTILISATEUR")
        click.echo("-" * 40)

        data = {}
        data['name'] = click.prompt("Nom complet", type=str).strip()
        data['email'] = click.prompt("Email", type=str).strip()

        # Password input
        data['password'] = click.prompt("Mot de passe", type=str).strip()
        password_confirm = click.prompt("Confirmer le mot de passe", type=str).strip()

        if data['password'] != password_confirm:
            click.echo("❌ Les mots de passe ne correspondent pas.")
            return None

        # Role selection
        data['role'] = self.get_role_selection()
        if not data['role']:
            return None

        return data

    def get_user_update_data(self, user):
        """Get updated user data from user input"""
        click.echo()
        click.echo(f"✏️ MODIFICATION DE L'UTILISATEUR: {user.name}")
        click.echo("-" * 60)

        data = {}
        data['name'] = click.prompt("Nom complet", default=user.name, type=str).strip()
        data['email'] = click.prompt("Email", default=user.email, type=str).strip()

        # Ask if user wants to change password
        if click.confirm("Voulez-vous changer le mot de passe ?", default=False):
            data['password'] = click.prompt("Nouveau mot de passe", type=str, hide_input=True).strip()
            password_confirm = click.prompt("Confirmer le nouveau mot de passe",
                                            type=str, hide_input=True).strip()

            if data['password'] != password_confirm:
                click.echo("❌ Les mots de passe ne correspondent pas.")
                return None
        else:
            data['password'] = None  # Don't change password if empty

        # Role selection
        current_role_display = user.role.value.title()
        click.echo(f"\nRôle actuel: {current_role_display}")

        if click.confirm("Voulez-vous changer le rôle ?", default=False):
            data['role'] = self.get_role_selection()
            if not data['role']:
                return None
        else:
            data['role'] = user.role

        return data

    def get_role_selection(self):
        """Get role selection from user"""
        click.echo()
        click.echo("👥 SÉLECTION DU RÔLE")
        click.echo("-" * 20)

        roles = [
            (UserRole.COMMERCIAL, "Gestion des clients et création d'événements"),
            (UserRole.SUPPORT, "Gestion des événements assignés"),
            (UserRole.GESTION, "Administration complète du système")
        ]

        for i, (role, description) in enumerate(roles, 1):
            click.echo(f"{i}. {role.value.title()} - {description}")

        click.echo("0. Annuler")

        try:
            choice = click.prompt("Sélectionnez un rôle", type=int)
            if choice == 0:
                return None
            if 1 <= choice <= len(roles):
                return roles[choice - 1][0]
            else:
                click.echo("Choix invalide.")
                return None
        except ValueError:
            click.echo("Veuillez entrer un nombre valide.")
            return None

    def display_users_list(self, users):
        """Display list of users"""
        click.echo()
        click.echo("📋 LISTE DES UTILISATEURS")
        click.echo("=" * 80)

        if not users:
            click.echo("Aucun utilisateur trouvé.")
            return

        for user in users:
            role_display = user.role.value.title()

            click.echo(f"ID: {user.id} | {user.name}")
            click.echo(f"   📧 {user.email}")
            click.echo(f"   👤 Rôle: {role_display}")
            click.echo("-" * 80)

        click.echo()
        click.pause("Appuyez sur Entrée pour continuer...")

    def get_user_selection(self, users, action="sélectionner"):
        """Get user selection from user"""
        if not users:
            click.echo("Aucun utilisateur disponible.")
            return None

        click.echo()
        click.echo(f"🔍 SÉLECTION D'UN UTILISATEUR ({action.upper()})")
        click.echo("-" * 40)

        for i, user in enumerate(users, 1):
            role_display = user.role.value.title()
            click.echo(f"{i}. {user.name} ({user.email}) - {role_display}")

        click.echo("0. Annuler")

        try:
            choice = click.prompt(f"Sélectionnez un utilisateur à {action}", type=int)
            if choice == 0:
                return None
            if 1 <= choice <= len(users):
                return users[choice - 1]
            else:
                click.echo("Choix invalide.")
                return None
        except ValueError:
            click.echo("Veuillez entrer un nombre valide.")
            return None

    def confirm_user_deletion(self, user):
        """Confirm user deletion"""
        click.echo()
        click.echo("⚠️ CONFIRMATION DE SUPPRESSION")
        click.echo("-" * 35)
        click.echo(f"Utilisateur: {user.name}")
        click.echo(f"Email: {user.email}")
        click.echo(f"Rôle: {user.role.value.title()}")
        click.echo()
        click.echo("⚠️ ATTENTION: Cette action est irréversible!")
        click.echo()

        return click.confirm("Êtes-vous sûr de vouloir supprimer cet utilisateur ?", default=False)

    def show_user_details(self, user):
        """Display detailed user information"""
        click.echo()
        click.echo("👤 DÉTAILS DE L'UTILISATEUR")
        click.echo("=" * 40)
        click.echo(f"ID: {user.id}")
        click.echo(f"Nom: {user.name}")
        click.echo(f"Email: {user.email}")
        click.echo(f"Rôle: {user.role.value.title()}")
        click.echo("=" * 40)
        click.echo()
