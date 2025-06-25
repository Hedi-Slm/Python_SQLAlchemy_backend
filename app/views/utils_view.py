import click


def show_error(message):
    """Display error message"""
    click.echo()
    click.echo(click.style(f"❌ ERREUR: {message}", fg='red'))
    click.echo()


def show_success(message):
    """Display success message"""
    click.echo()
    click.echo(click.style(f"✅ SUCCÈS: {message}", fg='green'))
    click.echo()


def show_info(message):
    """Display info message"""
    click.echo()
    click.echo(click.style(f"ℹ️  INFO: {message}", fg='blue'))
    click.echo()


def show_warning(message):
    """Display warning message"""
    click.echo()
    click.echo(click.style(f"⚠️  ATTENTION: {message}", fg='yellow'))
    click.echo()


def wait_for_user():
    """Wait for user to press Enter"""
    click.prompt(click.style("Appuyez sur Entrée pour continuer..."), default="", show_default=False)