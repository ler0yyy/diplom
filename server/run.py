import os

from server.app import app

if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    try:
        app.run(host="0.0.0.0", port=port, debug=True)
    except OSError as e:
        print(f"\n[ОШИБКА] Не удалось запустить сервер на порту {port}:", e)
        print("Закройте другую программу на этом порту или смените PORT в .env")
        raise
