## PollPoint server (Flask + PostgreSQL)

### 1) Подготовка PostgreSQL

Создайте базу `pollpoint` и примените схему:

```bash
psql -U postgres -c "CREATE DATABASE pollpoint;"
psql -U postgres -d pollpoint -f ..\\database\\database.sql
```

### 2) Настройка окружения

Скопируйте `.env.example` в `.env` и поправьте `DATABASE_URL`, пароль, и т.д.

### 3) Установка зависимостей

```bash
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
```

### 4) Запуск сервера

```bash
python -m server.run
```

или

```bash
python -m server.manage
```

Сервер слушает `http://localhost:5000/` и **отдаёт статический сайт** из `../web`.

### 5) API endpoints (основные)

- `POST /api/auth/register`
- `POST /api/auth/login`
- `GET /api/presentations` (JWT + teacher)
- `POST /api/presentations` (JWT + teacher)
- `PUT /api/presentations/{id}` (JWT + teacher)
- `DELETE /api/presentations/{id}` (JWT + teacher)
- `GET /api/presentations/{id}/slides` (пока без JWT — для просмотра)
- `POST /api/presentations/{id}/slides` (JWT + teacher)
- `PUT /api/slides/{id}` (JWT + teacher)
- `DELETE /api/slides/{id}` (JWT + teacher)
- `POST /api/sessions` (без JWT)
- `POST /api/responses` (JWT)
- `GET /api/sessions/{id}/poll` (без JWT)
- `GET /api/sessions/{id}/stats` (без JWT)

### 6) Миграции (Flask-Migrate / Alembic)

Если хотите именно миграциями (как в требованиях), используйте:

```bash
set FLASK_APP=server.manage
flask db init
flask db migrate -m \"init\"
flask db upgrade
```

На старте для диплома можно оставить `database/database.sql` как «базовую миграцию».

