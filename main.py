import sys
import os
from dotenv import load_dotenv
import sentry_sdk
from app.controllers.main_controller import MainController


load_dotenv()

SENTRY_DSN = os.getenv("SENTRY_DSN")

# Initialize Sentry if DSN is present
if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        traces_sample_rate=1.0,
        environment=os.getenv("ENV", "development"),
    )
    print("✅ Sentry initialized")
else:
    print("⚠️ Sentry not initialized (missing SENTRY_DSN)")


def main():
    try:
        controller = MainController()
        controller.run()
    except KeyboardInterrupt:
        print("\n👋 Application fermée par l'utilisateur.")
    except Exception as e:
        print(f"❌ Erreur critique: {e}")
        if SENTRY_DSN:
            sentry_sdk.capture_exception(e)
        sys.exit(1)


if __name__ == "__main__":
    main()
