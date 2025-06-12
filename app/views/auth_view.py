import click
from typing import Tuple


class AuthView:
    def show_welcome(self):
        """Display welcome message"""
        click.clear()
        click.echo("=" * 50)
        click.echo(click.style("EPIC EVENTS - SYSTÈME CRM"))
        click.echo("=" * 50)
        click.echo()

    def show_login_menu(self) -> str:
        """Display login menu and get user choice"""
        click.echo("📋 MENU PRINCIPAL")
        click.echo("-" * 20)
        click.echo("1. 🔐 Se connecter")
        click.echo("2. 🚪 Quitter")
        click.echo()

        return click.prompt(click.style("Votre choix"), type=str).strip()

    def get_login_credentials(self) -> Tuple[str, str]:
        """Get login credentials from user"""
        click.echo()
        click.echo("🔐 CONNEXION")
        click.echo("-" * 15)

        email = click.prompt(click.style("Email"),type=str).strip()

        password = click.prompt(click.style("Mot de passe"),type=str).strip()

        return email, password

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

    def show_goodbye(self):
        """Display goodbye message"""
        click.clear()
        click.echo()
        click.echo(click.style("👋 Merci d'avoir utilisé Epic Events CRM!"))
        click.echo(click.style("À bientôt !"))
        click.echo()

    def wait_for_user(self):
        """Wait for user to press Enter"""
        click.prompt(click.style("Appuyez sur Entrée pour continuer..."), default="", show_default=False)
