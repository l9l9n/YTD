# YTD — YouTube Downloader

Инструмент для скачивания видео и аудио с YouTube. Работает в двух режимах: консольное приложение и Telegram-бот.

---

## Возможности

- Скачивание аудио в формате **MP3** с автоматической записью метаданных (название, автор, год, обложка)
- Скачивание **видео** с выбором качества (360p / 480p / 720p и т.д.)
- Telegram-бот с удобными кнопками — файл сразу приходит в чат
- Консольный режим — файлы сохраняются локально в папку `Downloads/Downloads_ДД_ММ_ГГГГ/`

---

## Стек

- [pytubefix](https://github.com/JuanBindez/pytubefix) — скачивание с YouTube
- [aiogram 3](https://docs.aiogram.dev/) — Telegram Bot API
- [mutagen](https://mutagen.readthedocs.io/) — запись ID3-тегов в MP3
- [python-dotenv](https://github.com/theskumar/python-dotenv) — загрузка токена из `.env`

---

## Структура проекта

```
ytd/
├── bot.py            # Telegram-бот
├── main.py           # Консольная версия
├── start.py          # Запуск консольной версии через venv
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env              # Токен бота (не в git)
```

---

## Установка и запуск

### 1. Клонировать репозиторий

```bash
git clone https://github.com/l9l9n/YTD.git
cd YTD
```

### 2. Создать файл `.env`

```env
BOT_TOKEN=ваш_токен_от_BotFather
```

Получить токен можно у [@BotFather](https://t.me/BotFather) в Telegram.

---

### Вариант A — через Python (вручную)

```bash
python -m venv venv
venv\Scripts\activate        # Windows
# или
source venv/bin/activate     # Linux / macOS

pip install -r requirements.txt
```

**Запуск Telegram-бота:**
```bash
python bot.py
```

**Запуск консольной версии:**
```bash
python main.py
# или
python start.py
```

---

### Вариант B — через Docker Compose

```bash
docker compose up -d
```

Бот запустится в фоне. Скачанные файлы (при консольном использовании) будут доступны в папке `Downloads/` на хосте.

Остановить:
```bash
docker compose down
```

---

## Использование

### Telegram-бот

1. Найди бота в Telegram и отправь `/start`
2. Скинь ссылку на YouTube видео
3. Нажми **MP3** или **Видео**
4. Если выбрал видео — выбери качество из доступных
5. Получи файл прямо в чате

> Ограничение Telegram: файлы до **50 МБ**. Для длинных видео выбирай качество пониже.

### Консоль

```
Введите ссылку: https://www.youtube.com/watch?v=...
1 — скачать MP3
2 — скачать видео
q — выход
```

Файлы сохраняются в `Downloads/Downloads_ДД_ММ_ГГГГ/`.
