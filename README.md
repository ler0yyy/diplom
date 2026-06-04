```markdown
# 🎯 PollPoint — интерактивная система опросов для лекций

**PollPoint** объединяет веб-сайт, сервер на Flask, базу данных PostgreSQL и макросы PowerPoint (VBA) для проведения опросов в реальном времени. Преподаватель создаёт вопросы заранее, студенты отвечают через QR-код, а результаты мгновенно появляются на слайде презентации и в браузере.

> 🎓 Дипломный проект • ЮФУ ИММиКН • 2026

---

## 🚀 Возможности

- **Два типа опросов**
  - *Выбор варианта* (2–5 ответов) — столбчатая диаграмма с процентами
  - *Облако тегов* — студенты вводят ключевые слова, отображается частотный словарь
- **Роли пользователей** — преподаватель управляет контентом, студент только отвечает
- **Автоматизация в PowerPoint**
  - При показе слайда с QR-кодом VBA создаёт сессию опроса
  - При переходе на слайд статистики VBA запрашивает данные с сервера и обновляет текст
- **Живая статистика** — веб-страница результатов обновляется каждые 2.5 секунды
- **JWT-аутентификация**, безопасное хранение паролей (bcrypt)
- **Простое развёртывание** — всё поднимается одной командой (или двойным кликом)

---

## 🛠 Технологии

| Часть | Стек |
|-------|------|
| **Сервер** | Python 3 • Flask • SQLAlchemy • PostgreSQL • pg8000 |
| **Клиент (веб)** | HTML • CSS • JavaScript • Chart.js |
| **Клиент (PowerPoint)** | VBA • MSXML2.XMLHTTP • VBA-JSON |
| **Безопасность** | JWT • bcrypt |
| **Инструменты** | python‑dotenv • Flask‑CORS • Flask‑Migrate |

---

## 📂 Структура проекта

```
PollPoint/
├── web/                  # Сайт (HTML/CSS/JS)
│   ├── index.html        # Вход / регистрация
│   ├── teacher.html      # Кабинет преподавателя
│   ├── create-*          # Конструктор презентаций и слайдов
│   ├── poll*.html        # Опросы (choice / tags)
│   ├── results.html      # Статистика в реальном времени
│   └── js/               # API-клиент, авторизация, графики
├── server/               # Flask API + раздача сайта
│   ├── app.py            # Инициализация приложения
│   ├── models.py         # SQLAlchemy‑модели
│   ├── routes/           # auth, presentations, poll
│   ├── config.py         # Конфигурация из .env
│   ├── check_db.py       # Проверка подключения к БД
│   ├── init_db.py        # Создание таблиц
│   ├── seed.py           # Тестовые пользователи
│   └── run.py            # Точка входа
├── database/
│   └── database.sql      # SQL‑схема PostgreSQL
├── presentation/
│   ├── vba_macro.bas     # Макросы HTTP + сессии + статистика
│   └── ThisPresentation.txt # Код события смены слайда
├── start.bat             # Быстрый старт (Windows)
├── start.sh              # Быстрый старт (macOS / Linux)
└── README.md
```

---

## ⚡ Быстрый старт

### Windows

1. **Установите PostgreSQL** ([официальный сайт](https://www.postgresql.org/download/windows/)).  
   Придумайте пароль для пользователя `postgres` и запомните его.

2. **Дважды кликните `start.bat`**. Скрипт сам:
   - создаст виртуальное окружение
   - установит зависимости Python
   - проверит PostgreSQL, создаст базу `pollpoint`
   - создаст таблицы и тестовых пользователей
   - запустит сервер

3. При первом запуске скрипт попросит ввести пароль от PostgreSQL в файл `server/.env`.

4. Откройте в браузере **http://localhost:5001/** 🎉

### macOS / Linux

1. Установите PostgreSQL и запустите службу:
   ```bash
   # macOS
   brew install postgresql && brew services start postgresql

   # Ubuntu
   sudo apt update && sudo apt install postgresql && sudo service postgresql start
   ```

2. В терминале выполните:
   ```bash
   ./start.sh
   ```

3. Откройте **http://localhost:5001/**

---

## 🔐 Тестовые учётные записи

После запуска скрипта в базе уже будут пользователи:

| Роль           | Email                     | Пароль       |
|----------------|---------------------------|--------------|
| Преподаватель  | `teacher@pollpoint.local` | `teacher123` |
| Студент        | `student1@pollpoint.local`| `student123` |
| Студент        | `student2@pollpoint.local`| `student123` |

---

## 🖥 Ручная установка (если скрипты не работают)

### Windows (PowerShell)
```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r server\requirements.txt
copy server\.env.example server\.env
# отредактируйте server\.env, указав свой пароль PostgreSQL
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
# отредактируйте server/.env
python -m server.check_db
python -m server.init_db
python -m server.seed
python -m server.run
```

---

## 🎬 Сценарий демонстрации

1. **Преподаватель** входит в систему, создаёт презентацию и добавляет слайд (тип `choice` или `tags`).
2. Нажимает кнопку **«QR»** → получает QR‑код, вставляет его в слайд PowerPoint.
3. **Студенты** сканируют QR-код, регистрируются/входят и отвечают на вопрос.
4. **Результаты** отображаются в реальном времени:
   - на веб‑странице `results.html` (диаграмма обновляется каждые 2.5 с)
   - на следующем слайде PowerPoint (VBA‑макрос автоматически запрашивает статистику)

---

## 🧩 Интеграция с PowerPoint

1. Откройте `.pptm` файл и перейдите в редактор VBA (`Alt+F11`).
2. Импортируйте модуль `presentation/vba_macro.bas`.
3. Добавьте библиотеку [VBA‑JSON](https://github.com/VBA-tools/VBA-JSON).
4. Вставьте код из `presentation/ThisPresentation.txt` в объект `ThisPresentation`.
5. На слайдах создайте фигуры с именами:
   - QR‑слайд: **PollLink**
   - Статистика: **QuestionBox**, **TotalBox**, **Option1**…**Option5**, **TagsBox**
6. В заметках слайда укажите:
   - `[POLL slide_id=1]` — для слайда с QR
   - `[STATS]` — для слайда статистики

---

## ⚙️ Конфигурация

Параметры сервера и БД задаются в файле `server/.env` (пример в `.env.example`):

```
PORT=5001                   # порт, на котором работает сервер
PGHOST=127.0.0.1
PGPORT=5432
PGUSER=postgres
PGPASSWORD=your_password
PGDATABASE=pollpoint
```

---

## 📄 Лицензия

MIT © 2026 [ler0yyy/ ссылка на GitHub]

---

## 🤝 Контакты

Если есть вопросы или предложения, открывайте [issue](https://github.com/ler0yyy/diplom/issues) или пишите на почту.

> Сделано с ❤️ в рамках дипломного проекта
```
