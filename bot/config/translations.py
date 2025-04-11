import gettext
import os

LOCALE_DIR = os.path.join(os.path.dirname(__file__), "locales")
LANGUAGE = "uk"

translation = gettext.translation(
    domain="messages",
    localedir=LOCALE_DIR,
    languages=[LANGUAGE],
    fallback=True
)
_ = translation.gettext

if __name__ == "__main__":
    print(_("Welcome to our application!"))
