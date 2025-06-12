import click
from app.models.user import User, UserRole


class MainView:
    def show_main_menu(self, user: User) -> str:
        """Display main menu based on user role"""
        click.clear()
        click.echo("=" * 50)
        click.echo(click.style(f"EPIC EVENTS CRM - {user.name}"))
        click.echo(click.style(f"Rôle: {user.role.value.upper()}"))
        click.echo("=" * 50)
        click.echo()

        click.echo("📋 MENU PRINCIPAL")
        click.echo("-" * 20)
        click.echo("1. 👥 Gestion des clients")
        click.echo("2. 📄 Gestion des contrats")
        click.echo("3. 🎉 Gestion des événements")

        # Only show user management for GESTION role
        if user.role == UserRole.GESTION:
            click.echo("4. 👤 Gestion des utilisateurs")

        click.echo("0. 🚪 Se déconnecter")
        click.echo()

        return click.prompt(click.style("Votre choix"), type=str).strip()

    def show_success(self, message: str):
        """Display success message"""
        click.echo()
        click.echo(click.style(f"✅ {message}"))
        click.echo()
        self.wait_for_user()

    def show_error(self, message: str):
        """Display error message"""
        click.echo()
        click.echo(click.style(f"❌ {message}"))
        click.echo()
        self.wait_for_user()

    def show_info(self, message: str):
        """Display info message"""
        click.echo()
        click.echo(click.style(f"ℹ️  {message}"))
        click.echo()
        self.wait_for_user()

    def wait_for_user(self):
        """Wait for user to press Enter"""
        click.prompt(click.style("Appuyez sur Entrée pour continuer..."), default="", show_default=False)
