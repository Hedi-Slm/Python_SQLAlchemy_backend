import sys
from app.controllers.main_controller import MainController


def main():
    try:
        controller = MainController()
        controller.run()
    except KeyboardInterrupt:
        print("\n👋 Application fermée par l'utilisateur.")
    except Exception as e:
        print(f"❌ Erreur critique: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
