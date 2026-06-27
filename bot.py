import os
import asyncio
import logging
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    FSInputFile,
    CallbackQuery,
)
from pytubefix import YouTube
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TDRC, TCON, COMM, APIC
import urllib.request

BOT_TOKEN = os.getenv("BOT_TOKEN")
MAX_FILE_SIZE = 50 * 1024 * 1024

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# {user_id: youtube_url}
user_links: dict[int, str] = {}


def create_download_folder() -> str:
    folder_name = os.path.join("Downloads", f"Downloads_{datetime.now().strftime('%d_%m_%Y')}")
    os.makedirs(folder_name, exist_ok=True)
    return folder_name


def set_mp3_metadata(file_path: str, yt: YouTube) -> None:
    try:
        audio = MP3(file_path, ID3=ID3)
        try:
            audio.add_tags()
        except Exception:
            pass
        tags = audio.tags
        tags.add(TIT2(encoding=3, text=yt.title or ""))
        tags.add(TPE1(encoding=3, text=yt.author or ""))
        tags.add(TALB(encoding=3, text=yt.author or ""))
        if yt.publish_date:
            tags.add(TDRC(encoding=3, text=str(yt.publish_date.year)))
        tags.add(TCON(encoding=3, text="YouTube"))
        tags.add(COMM(encoding=3, lang="rus", desc="", text=yt.watch_url or ""))
        if yt.thumbnail_url:
            try:
                with urllib.request.urlopen(yt.thumbnail_url, timeout=10) as resp:
                    cover_data = resp.read()
                tags.add(APIC(encoding=3, mime="image/jpeg", type=3, desc="Cover", data=cover_data))
            except Exception:
                pass
        audio.save()
    except Exception as e:
        logger.warning(f"Не удалось записать метаданные: {e}")


def download_mp3(link: str) -> str:
    yt = YouTube(link, client="WEB")
    stream = yt.streams.get_audio_only()
    folder = create_download_folder()
    out_file = stream.download(output_path=folder)
    base, _ = os.path.splitext(out_file)
    new_file = base + ".mp3"
    if os.path.exists(new_file):
        os.remove(new_file)
    os.rename(out_file, new_file)
    set_mp3_metadata(new_file, yt)
    return new_file


def get_available_resolutions(link: str) -> list[str]:
    """Возвращает список доступных разрешений (без дублей, по убыванию)."""
    yt = YouTube(link, client="WEB")
    resolutions = set()
    for stream in yt.streams.filter(progressive=True, file_extension="mp4"):
        if stream.resolution:
            resolutions.add(stream.resolution)
    # Сортируем по числу (720p -> 720)
    return sorted(resolutions, key=lambda r: int(r.replace("p", "")), reverse=True)


def download_video(link: str, resolution: str) -> str:
    yt = YouTube(link, client="WEB")
    stream = yt.streams.filter(
        progressive=True, file_extension="mp4", resolution=resolution
    ).first()
    # Если выбранное качество недоступно — берём наилучшее
    if not stream:
        stream = yt.streams.get_highest_resolution()
    folder = create_download_folder()
    return stream.download(output_path=folder)


# ─────────────────────────── Хендлеры ───────────────────────────

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer(
        "👋 Привет! Я бот для скачивания видео и музыки с YouTube.\n\n"
        "📎 Просто отправь мне ссылку на YouTube видео, "
        "и я предложу скачать его как MP3 🎵 или как видео 🎬."
    )


@dp.message(F.text.regexp(r"(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+"))
async def handle_youtube_link(message: types.Message):
    user_links[message.from_user.id] = message.text.strip()

    try:
        yt = YouTube(message.text.strip())
        title = yt.title
        minutes, seconds = divmod(yt.length, 60)
        info_text = (
            f"🎬 **{title}**\n"
            f"⏱ Длительность: {minutes}:{seconds:02d}\n\n"
            "Выбери формат загрузки:"
        )
    except Exception:
        info_text = "Выбери формат загрузки:"

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🎵 MP3", callback_data="download_mp3"),
                InlineKeyboardButton(text="🎬 Видео", callback_data="choose_quality"),
            ]
        ]
    )
    await message.answer(info_text, reply_markup=keyboard, parse_mode="Markdown")


@dp.callback_query(F.data == "choose_quality")
async def handle_choose_quality(callback: CallbackQuery):
    user_id = callback.from_user.id
    link = user_links.get(user_id)

    if not link:
        await callback.answer("❌ Ссылка не найдена. Отправь ссылку заново.", show_alert=True)
        return

    await callback.answer()
    status_msg = await callback.message.answer("🔍 Получаю доступные качества...")

    try:
        loop = asyncio.get_running_loop()
        resolutions = await loop.run_in_executor(None, get_available_resolutions, link)

        if not resolutions:
            await status_msg.edit_text("❌ Не удалось получить доступные качества.")
            return

        buttons = [
            [InlineKeyboardButton(text=f"📹 {res}", callback_data=f"video_{res}")]
            for res in resolutions
        ]
        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
        await status_msg.edit_text("Выбери качество видео:", reply_markup=keyboard)

    except Exception as e:
        logger.error(f"Ошибка получения качеств: {e}")
        await status_msg.edit_text(f"❌ Ошибка: `{e}`", parse_mode="Markdown")


@dp.callback_query(F.data.startswith("video_"))
async def handle_video_quality(callback: CallbackQuery):
    user_id = callback.from_user.id
    link = user_links.get(user_id)
    resolution = callback.data.replace("video_", "")  # например "720p"

    if not link:
        await callback.answer("❌ Ссылка не найдена. Отправь ссылку заново.", show_alert=True)
        return

    await callback.answer()
    status_msg = await callback.message.answer(f"⏳ Скачиваю видео {resolution}... Подожди немного.")

    try:
        loop = asyncio.get_running_loop()
        file_path = await loop.run_in_executor(None, download_video, link, resolution)

        file_size = os.path.getsize(file_path)
        if file_size > MAX_FILE_SIZE:
            await status_msg.edit_text(
                f"❌ Файл слишком большой ({file_size // (1024*1024)} МБ). "
                f"Telegram позволяет отправлять файлы до 50 МБ.\n"
                f"Попробуй качество пониже."
            )
            os.remove(file_path)
            return

        input_file = FSInputFile(file_path)
        await callback.message.answer_document(
            document=input_file,
            caption=f"🎬 Вот твоё видео ({resolution})!",
        )
        await status_msg.delete()
        os.remove(file_path)

    except Exception as e:
        logger.error(f"Ошибка при скачивании видео: {e}")
        await status_msg.edit_text(
            f"❌ Произошла ошибка:\n`{e}`\n\nПопробуй другую ссылку.",
            parse_mode="Markdown",
        )

    user_links.pop(user_id, None)


@dp.callback_query(F.data == "download_mp3")
async def handle_download_mp3(callback: CallbackQuery):
    user_id = callback.from_user.id
    link = user_links.get(user_id)

    if not link:
        await callback.answer("❌ Ссылка не найдена. Отправь ссылку заново.", show_alert=True)
        return

    await callback.answer()
    status_msg = await callback.message.answer("⏳ Скачиваю MP3 🎵... Подожди немного.")

    try:
        loop = asyncio.get_running_loop()
        file_path = await loop.run_in_executor(None, download_mp3, link)

        file_size = os.path.getsize(file_path)
        if file_size > MAX_FILE_SIZE:
            await status_msg.edit_text(
                f"❌ Файл слишком большой ({file_size // (1024*1024)} МБ). "
                f"Telegram позволяет отправлять файлы до 50 МБ."
            )
            os.remove(file_path)
            return

        input_file = FSInputFile(file_path)
        await callback.message.answer_audio(audio=input_file, caption="🎵 Вот твой MP3!")
        await status_msg.delete()
        os.remove(file_path)

    except Exception as e:
        logger.error(f"Ошибка при скачивании MP3: {e}")
        await status_msg.edit_text(
            f"❌ Произошла ошибка:\n`{e}`\n\nПопробуй другую ссылку.",
            parse_mode="Markdown",
        )

    user_links.pop(user_id, None)


@dp.message()
async def handle_other(message: types.Message):
    await message.answer(
        "🤔 Я понимаю только ссылки на YouTube.\n"
        "Отправь мне ссылку вида:\n"
        "`https://www.youtube.com/watch?v=...`\n"
        "или\n"
        "`https://youtu.be/...`",
        parse_mode="Markdown",
    )


async def main():
    logger.info("🚀 Бот запускается...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
