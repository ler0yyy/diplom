# PollPoint — инструкция по запуску

## Что где лежит

| Папка | Назначение |
|-------|------------|
| `web/` | Сайт (HTML/CSS/JS) |
| `server/` | Python API (Flask) |
| `database/` | SQL-схема PostgreSQL |
| `presentation/` | VBA-макросы для PowerPoint |

## Быстрый старт

### Windows

1. **Установите PostgreSQL** (один раз):
   - Скачай с https://www.postgresql.org/download/windows/
   - Установи с паролем для пользователя `postgres`
   - Запомни этот пароль — он понадобится на шаге 3

2. Двойной клик **`start.bat`** — скрипт всё сделает автоматически:
   - Создаст виртуальное окружение
   - Установит зависимости
   - Проверит PostgreSQL и создаст базу `pollpoint`
   - Создаст таблицы и тестовых пользователей
   - Запустит сервер

3. Открой **http://localhost:5001/**

**Примечание:** При первом запуске скрипт создаст `server/.env` и попросит указать `PGPASSWORD` — пароль от PostgreSQL, который ты вводил при установке.

### macOS / Linux

1. **Установите PostgreSQL** (один раз):
   ```bash
   # macOS
   brew install postgresql
   brew services start postgresql
   
   # Ubuntu/Debian
   sudo apt update && sudo apt install postgresql
   sudo service postgresql start
   ```

2. В терминале запусти:
   ```bash
   ./start.sh
   ```
3. Открой **http://localhost:5001/**

## Настройка

### Порт сервера

По умолчанию сервер использует порт **5001** (чтобы избежать конфликта на macOS). Если нужно изменить, открой `server/.env`:
```
PORT=5001
```

### Настройка PostgreSQL

Открой `server/.env` и укажи свои параметры:
```
PGHOST=127.0.0.1
PGPORT=5432
PGUSER=postgres
PGPASSWORD=твой_пароль
PGDATABASE=pollpoint
```

Если подключение не работает, скрипт попросит исправить пароль и попробует снова.

## Тестовые пользователи

После запуска скрипта `start.bat` / `start.sh` будут созданы:

| Роль | Email | Пароль |
|------|-------|--------|
| Преподаватель | `teacher@pollpoint.local` | `teacher123` |
| Студент | `student1@pollpoint.local` | `student123` |
| Студент | `student2@pollpoint.local` | `student123` |

## Ручная установка (если скрипт не работает)

### Windows
```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r server\requirements.txt
copy server\.env.example server\.env
# Редактируй server\.env — укажи PGPASSWORD
python -m server.check_db
python -m server.init_db
python -m server.seed
python -m server.run
```

### macOS / Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r server/requirements.txt
cp server/.env.example server/.env
# Редактируй server/.env — укажи PGPASSWORD
python -m server.check_db
python -m server.init_db
python -m server.seed
python -m server.run
```

## 3. PowerPoint (VBA)

1. Откройте `.pptm` → Alt+F11 (редактор VBA).
2. Импортируйте модуль `presentation/vba_macro.bas`.
3. Подключите **VBA-JSON** (JsonConverter) — скачайте с GitHub и добавьте модуль.
4. Вставьте код из `presentation/ThisPresentation.txt` в объект **ThisPresentation**.
5. На слайдах создайте фигуры с именами:
   - QR-слайд: `PollLink`
   - Stats-слайд: `QuestionBox`, `TotalBox`, `Option1`…`Option5`, `TagsBox`
6. В **заметках слайда** (Notes) напишите:
   - `[POLL slide_id=1]` — на слайде с QR (создаст сессию)
   - `[STATS]` — на слайде статистики (обновит данные)

## 4. Сценарий демонстрации

1. Войти как преподаватель → создать презентацию → добавить слайд (choice или tags).
2. Нажать **QR** → скопировать/скачать QR → вставить в PowerPoint.
3. Нажать **Результаты** (или открыть `results.html?session=...`) — диаграмма обновляется каждые 2.5 сек.
4. Студент сканирует QR → регистрируется/логинится → отвечает.
5. На следующем слайде PowerPoint показывается статистика через VBA.
