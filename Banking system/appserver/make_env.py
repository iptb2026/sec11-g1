"""
Creates appserver/.env from .env.example, so the backend can start.

    python make_env.py              # asks for the DB password
    python make_env.py 1234         # or pass it directly

A new random SECRET_KEY is generated each time. If .env already exists it
is left alone unless you add --force (that also logs everyone out, since
tokens signed with the old key stop working).
"""
import getpass
import secrets
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXAMPLE = HERE / ".env.example"
TARGET = HERE / ".env"


def main() -> None:
    args = [a for a in sys.argv[1:] if a != "--force"]
    force = "--force" in sys.argv[1:]

    if TARGET.exists() and not force:
        print(f"{TARGET} already exists, nothing changed. Use --force to replace it.")
        return

    password = args[0] if args else getpass.getpass("MySQL password for the backend: ")
    if not password:
        sys.exit("The DB password can't be empty.")

    lines = []
    for line in EXAMPLE.read_text(encoding="utf-8").splitlines():
        if line.startswith("DB_PASSWORD="):
            line = f"DB_PASSWORD={password}"
        elif line.startswith("SECRET_KEY="):
            line = f"SECRET_KEY={secrets.token_hex(32)}"
        lines.append(line)

    TARGET.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {TARGET}. Start the backend as usual.")


if __name__ == "__main__":
    main()
