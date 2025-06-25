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
