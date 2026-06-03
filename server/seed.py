"""
Создание тестовых пользователей.

Запуск из корня проекта:
  python -m server.seed
"""
from server.app import bcrypt, create_app, db
from server.models import User


def seed():
    app = create_app()
    with app.app_context():
        db.create_all()

        users = [
            ("teacher@pollpoint.local", "teacher123", "Иван Преподаватель", "teacher"),
            ("student1@pollpoint.local", "student123", "Анна Студент", "student"),
            ("student2@pollpoint.local", "student123", "Пётр Студент", "student"),
        ]

        for email, password, name, role in users:
            if User.query.filter_by(email=email).first():
                print(f"skip: {email}")
                continue
            pw_hash = bcrypt.generate_password_hash(password).decode("utf-8")
            db.session.add(User(email=email, password_hash=pw_hash, name=name, role=role))
            print(f"created: {email} / {password} ({role})")

        db.session.commit()
        print("Done.")


if __name__ == "__main__":
    seed()
