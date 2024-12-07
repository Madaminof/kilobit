import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.default import DefaultBotProperties
from db import init_db, save_kino  # `save_kino` va `init_db` ni import qilamiz

# Bot tokeningizni kiriting
TOKEN = "7907590797:AAH6yrkSbxeay0KfRuxdwFTpzqY23J9qzKM"

# Dispatcher yaratamiz
dp = Dispatcher()

# Video yuborish uchun o'zgaruvchilar
video_id = None
waiting_for_code = False
db_pool = None  # Ma'lumotlar bazasi havzasi

@dp.message(Command("start"))
async def command_start_handler(message: Message) -> None:
    """Botga start buyrug‘ini jo‘natganda ishlaydi."""
    await message.answer(
        "Botga xush kelibsiz! Avval video yuboring, keyin esa kino kodi yuborishingizni so'rayman."
    )


@dp.message()
async def handle_video(message: Message) -> None:
    """Video yuborish uchun handler."""
    global video_id, waiting_for_code

    if message.video:
        # Foydalanuvchi video yuborgan bo'lsa
        video_id = message.video.file_id
        waiting_for_code = True
        await message.answer("Kino kodi yuboring.")
    elif waiting_for_code:
        # Kino kodi yuborilsa, video va kodi kanalga yuboriladi
        caption = message.text.strip()
        if video_id:
            sent_message = await message.bot.send_video(
                chat_id='@kinotopbot01',
                video=video_id,
                caption=f"Kino kodi: {caption}"
            )
            # Kino kodi va message_id ni bazaga saqlash
            if db_pool:
                await save_kino(db_pool, caption, sent_message.message_id)

            await message.answer(f"Video va kino kodi kanalga yuborildi. Message ID: {sent_message.message_id}")
            # Video va kod yuborilganidan so'ng, navbatni tozalash
            video_id = None
            waiting_for_code = False
        else:
            await message.answer("Iltimos, avval video yuboring.")
    else:
        await message.answer("Avval video yuboring, so'ngra kino kodi yuborishingizni kutyapman.")


async def main():
    logging.basicConfig(level=logging.INFO)

    # Bot obyektini to'g'ri konfiguratsiya qilamiz
    bot = Bot(
        token=TOKEN,
        session=AiohttpSession(),
        default=DefaultBotProperties(parse_mode="HTML")  # Yangi usulda parse_mode
    )

    # Ma'lumotlar bazasini sozlash
    global db_pool
    db_pool = await init_db()

    # Start polling
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
