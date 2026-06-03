import os

from server.app import create_app, db
import server.models  # noqa: F401

app = create_app()

# Для Flask-Migrate:
#   set FLASK_APP=server.manage
#   flask db init
#   flask db migrate -m "init"
#   flask db upgrade

if __name__ == "__main__":
    # удобный запуск
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=True)

