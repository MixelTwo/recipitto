# Рецепитто

> Всем приятного Рецепитто!

Книга рецептов с возможностью находить рецепты по наличию или отсутствию в них конкретных ингредиентов

## Описание проекта

Рецепитто — это веб-приложение для управления кулинарными рецептами. Пользователи могут просматривать, искать, добавлять и оценивать рецепты, а также фильтровать их по ингредиентам.

Проект состоит из двух основных частей:
- **Backend**: Python-сервер на фреймворке Bafser, предоставляющий REST API для работы с рецептами, ингредиентами, пользователями и т.д.
- **Frontend**: Клиентское приложение на TypeScript, которое компилируется в статические файлы и обслуживается бэкендом.

## Структура проекта

```
project/
├── backend/               # Python-бэкенд
│   ├── blueprints/        # Эндпоинты API
│   ├── data/              # Модели данных и операции с БД
│   ├── utils/             # Вспомогательные скрипты
│   ├── alembic/           # Миграции базы данных
│   ├── main.py            # Точка входа сервера
│   ├── requirements.txt   # Зависимости Python
│   └── run.bat            # Скрипт запуска (Windows)
├── frontend/              # TypeScript-фронтенд
│   ├── src/               # Исходный код TypeScript
│   ├── wwwroot/           # Статические файлы (HTML, CSS, JS)
│   │   ├── index.html     # Главная страница
│   │   └── dist/          # Скомпилированные JS-файлы (генерируется)
│   ├── tsconfig.json      # Конфигурация TypeScript
│   └── build.bat          # Скрипт сборки (Windows)
└── README.md              # Этот файл
```

## Зависимости

### Backend (Python 3.11+)
Основные зависимости перечислены в `backend/requirements.txt`:
- `bafser==2.8.7` — веб-фреймворк
- `gunicorn` — WSGI-сервер (для продакшена)
- `python-dotenv` — загрузка переменных окружения
- `transliterate` — транслитерация текста

Для разработки также используются инструменты из `backend/requirements-dev.txt` (black, isort, flake8, pytest, coverage и др.).

### Frontend
- TypeScript (компилятор `tsc`)
- Современный JavaScript (ES2022+)
- Браузерные API (DOM, Fetch и т.д.)

## Система сборки Python-пакета

Backend часть проекта упакована как Python-пакет с использованием `setuptools`. Это позволяет устанавливать его через `pip` и распространять в виде архива.

### Файлы конфигурации

- `backend/setup.py` — основная конфигурация пакета (имя, версия, зависимости, точки входа)
- `requirements.txt` — список зависимостей (дублирует `backend/requirements.txt`)
- `backend/pyproject.toml` — настройки линтеров и форматирования

### Сборка пакета

Чтобы создать дистрибутив (исходный архив), выполните в директории `backend`:

```bash
python setup.py sdist
```

Архив будет помещён в `backend/dist/recipitto-backend-1.0.0.tar.gz`.

### Установка пакета в режиме разработки

Для разработки можно установить пакет в editable-режиме:

```bash
pip install -e backend/
```

Это позволит вносить изменения в код без переустановки.

### Установка зависимостей через pip

Все зависимости можно установить одной командой:

```bash
pip install -r requirements.txt
```

## Сборка и запуск

### 1. Подготовка окружения

#### Backend
```bash
cd backend
# Создание виртуального окружения (автоматически в run.bat)
python -m venv .venv
# Активация окружения
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate
# Установка зависимостей
pip install -r requirements.txt
```

#### Frontend
Установите TypeScript глобально (если ещё не установлен):
```bash
npm install -g typescript
```
Или используйте локальный tsc из node_modules (не требуется, если tsc доступен в PATH).

### 2. Сборка проекта

Для сборки необходимо скомпилировать TypeScript и скопировать содержимое `frontend/wwwroot` в папку `backend/build`.

Выполните следующие команды из корня проекта:

```bash
# Компиляция TypeScript
cd frontend
tsc
# или используйте скрипт (Windows)
build.bat

# Копирование статических файлов в backend/build
cd ..
mkdir -p backend/build
cp -r frontend/wwwroot/* backend/build/
```

На Windows можно использовать `xcopy` или `robocopy`. Пример скрипта:
```batch
xcopy /E /I frontend\wwwroot backend\build
```

### 3. Запуск сервера

#### Режим разработки (с автоматической перезагрузкой)
```bash
cd backend
python main.py dev
```
Или используйте готовый скрипт (Windows):
```bash
run.bat
```

Сервер будет доступен по адресу: [http://localhost:5000](http://localhost:5000)

#### Продакшен-режим (с использованием gunicorn)
```bash
cd backend
gunicorn main:app --workers 4 --bind 0.0.0.0:5000
```

### 4. Доступ к приложению

Откройте браузер и перейдите по адресу [http://localhost:5000](http://localhost:5000). Бэкенд автоматически обслуживает статические файлы из папки `build` (если они были скопированы).
