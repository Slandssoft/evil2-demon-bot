"""
Злой Демон 3.0 — Полная версия для Render.com
"""

import asyncio
import logging
import random
from datetime import datetime
from typing import Dict, List, Any

from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

# ========== ТВОИ ДАННЫЕ ==========
BOT_TOKEN = "8611498047:AAF4IGy-mV-GN4MfvDBrzGDuiotPqWLMyqE"
OWNER_ID = 6376163988
# ================================

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# ========== БАЗА ДАННЫХ ==========
class Database:
    def __init__(self):
        self.enemies: List[int] = []
        self.saved_messages: Dict[int, Dict] = {}
        self.stats: Dict[str, int] = {
            "evil_responses": 0,
            "deleted_saved": 0,
            "osint_requests": 0,
            "messages_processed": 0
        }
        self.settings: Dict[str, Any] = {
            "evil_mode": True,
            "save_deleted": True,
            "delay_min": 2,
            "delay_max": 7,
            "work_in_groups": True,
            "work_in_pm": True
        }
    
    def add_enemy(self, user_id: int) -> bool:
        if user_id not in self.enemies:
            self.enemies.append(user_id)
            return True
        return False
    
    def remove_enemy(self, user_id: int) -> bool:
        if user_id in self.enemies:
            self.enemies.remove(user_id)
            return True
        return False
    
    def save_message(self, message_id: int, data: Dict):
        self.saved_messages[message_id] = data
        self.stats["deleted_saved"] += 1
        if len(self.saved_messages) > 500:
            keys = sorted(self.saved_messages.keys())
            for k in keys[:100]:
                del self.saved_messages[k]
    
    def toggle_setting(self, key: str) -> Any:
        if key in self.settings:
            self.settings[key] = not self.settings[key]
        return self.settings.get(key)

db = Database()

# ========== FSM СОСТОЯНИЯ ==========
class EnemyStates(StatesGroup):
    waiting_for_id = State()

class OSINTStates(StatesGroup):
    waiting_for_username = State()
    waiting_for_email = State()
    waiting_for_phone = State()

# ========== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ==========
def generate_insult(user_message: str = "") -> str:
    templates = [
        f"ты ебливая тапочка вонючего деревенского жителя",
        f"ты поломоечный аппарат до советского производства, закрой рот",
        f"ты грязный подстаканник из электрички",
        f"у тебя мозгов как у дохлой крысы в консервной банке",
        f"ты даже {user_message[:20]} написать нормально не смог, дебил",
        f"слушай, {user_message[:15]}? сам ты петух гамбургский",
        f"закрой хлебало, {random.choice(['тупой', 'ебучий', 'вонючий'])} {random.choice(['козёл', 'баран', 'осел'])}"
    ]
    return random.choice(templates)

def get_main_keyboard():
    kb = ReplyKeyboardBuilder()
    kb.button(text="👿 Враги")
    kb.button(text="⚙️ Настройки")
    kb.button(text="🔍 OSINT")
    kb.button(text="📊 Статистика")
    kb.button(text="📁 Удалёнки")
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)

def get_enemy_keyboard():
    kb = InlineKeyboardBuilder()
    kb.button(text="➕ Добавить врага", callback_data="enemy_add")
    kb.button(text="📋 Список врагов", callback_data="enemy_list")
    kb.button(text="🗑 Удалить врага", callback_data="enemy_remove_menu")
    kb.button(text="🔙 Назад", callback_data="back_to_main")
    kb.adjust(1)
    return kb.as_markup()

def get_settings_keyboard():
    kb = InlineKeyboardBuilder()
    kb.button(
        text=f"{'✅' if db.settings['evil_mode'] else '❌'} Злой режим",
        callback_data="toggle_evil"
    )
    kb.button(
        text=f"{'✅' if db.settings['save_deleted'] else '❌'} Сохранять удалёнки",
        callback_data="toggle_save"
    )
    kb.button(text="🔙 Назад", callback_data="back_to_main")
    kb.adjust(1)
    return kb.as_markup()

def get_osint_keyboard():
    kb = InlineKeyboardBuilder()
    kb.button(text="👤 Поиск по username", callback_data="osint_username")
    kb.button(text="📧 Поиск по email", callback_data="osint_email")
    kb.button(text="📱 Поиск по номеру", callback_data="osint_phone")
    kb.button(text="🔙 Назад", callback_data="back_to_main")
    kb.adjust(1)
    return kb.as_markup()

# ========== ОБРАБОТЧИКИ КОМАНД ==========
@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        f"👋 Привет, {message.from_user.first_name}!\n"
        f"Я твой цифровой демон 😈\n\n"
        f"Выбери раздел в меню ниже:",
        reply_markup=get_main_keyboard()
    )

@dp.message(F.text == "👿 Враги")
async def menu_enemies(message: Message):
    await message.answer(
        "👿 **Управление врагами**\n\n"
        "Выбери действие:",
        reply_markup=get_enemy_keyboard(),
        parse_mode="Markdown"
    )

@dp.message(F.text == "⚙️ Настройки")
async def menu_settings(message: Message):
    await message.answer(
        "⚙️ **Настройки**\n\n"
        f"Злой режим: {'✅ Вкл' if db.settings['evil_mode'] else '❌ Выкл'}\n"
        f"Сохранять удалёнки: {'✅ Вкл' if db.settings['save_deleted'] else '❌ Выкл'}\n"
        f"Задержка: {db.settings['delay_min']}-{db.settings['delay_max']} сек",
        reply_markup=get_settings_keyboard(),
        parse_mode="Markdown"
    )

@dp.message(F.text == "🔍 OSINT")
async def menu_osint(message: Message):
    await message.answer(
        "🔍 **OSINT-поиск**\n\n"
        "Выбери тип поиска:",
        reply_markup=get_osint_keyboard(),
        parse_mode="Markdown"
    )

@dp.message(F.text == "📊 Статистика")
async def menu_stats(message: Message):
    stats = db.stats
    await message.answer(
        "📊 **Статистика работы**\n\n"
        f"👿 Злых ответов: {stats['evil_responses']}\n"
        f"📥 Сохранено удалёнок: {stats['deleted_saved']}\n"
        f"🔍 OSINT-запросов: {stats['osint_requests']}\n"
        f"💬 Всего сообщений: {stats['messages_processed']}",
        parse_mode="Markdown"
    )

@dp.message(F.text == "📁 Удалёнки")
async def menu_saved(message: Message):
    saved = db.saved_messages
    if not saved:
        await message.answer("📁 Нет сохранённых сообщений")
        return
    
    items = list(saved.items())[-5:]
    text = "📁 **Последние сохранённые сообщения:**\n\n"
    for msg_id, data in items:
        text += f"• {data.get('text', '[медиа]')[:50]}\n"
        text += f"  от {data.get('from_name', data.get('from'))}\n\n"
    
    await message.answer(text, parse_mode="Markdown")

# ========== INLINE КНОПКИ ==========
@dp.callback_query(F.data == "back_to_main")
async def callback_back(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(
        "Главное меню:",
        reply_markup=get_main_keyboard()
    )
    await callback.answer()

@dp.callback_query(F.data == "enemy_add")
async def callback_enemy_add(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "👿 Отправь ID пользователя (только цифры):"
    )
    await state.set_state(EnemyStates.waiting_for_id)
    await callback.answer()

@dp.callback_query(F.data == "enemy_list")
async def callback_enemy_list(callback: CallbackQuery):
    if not db.enemies:
        await callback.message.edit_text("👿 Список врагов пуст")
        await callback.answer()
        return
    
    text = "👿 **Список врагов:**\n\n"
    for i, enemy_id in enumerate(db.enemies, 1):
        text += f"{i}. `{enemy_id}`\n"
    
    await callback.message.edit_text(text, parse_mode="Markdown")
    await callback.answer()

@dp.callback_query(F.data == "enemy_remove_menu")
async def callback_enemy_remove_menu(callback: CallbackQuery):
    if not db.enemies:
        await callback.message.edit_text("👿 Список врагов пуст")
        await callback.answer()
        return
    
    kb = InlineKeyboardBuilder()
    for enemy_id in db.enemies[:10]:
        kb.button(text=f"❌ {enemy_id}", callback_data=f"enemy_remove_{enemy_id}")
    kb.button(text="🔙 Назад", callback_data="back_to_main")
    kb.adjust(1)
    
    await callback.message.edit_text(
        "Выбери врага для удаления:",
        reply_markup=kb.as_markup()
    )
    await callback.answer()

@dp.callback_query(F.data.startswith("enemy_remove_"))
async def callback_enemy_remove(callback: CallbackQuery):
    enemy_id = int(callback.data.replace("enemy_remove_", ""))
    if db.remove_enemy(enemy_id):
        await callback.message.edit_text(f"✅ Враг {enemy_id} удалён!")
    else:
        await callback.message.edit_text(f"❌ Враг {enemy_id} не найден")
    await callback.answer()

@dp.callback_query(F.data == "toggle_evil")
async def callback_toggle_evil(callback: CallbackQuery):
    new_value = db.toggle_setting("evil_mode")
    status = "включён" if new_value else "выключен"
    await callback.message.edit_text(f"✅ Злой режим {status}")
    await callback.answer()

@dp.callback_query(F.data == "toggle_save")
async def callback_toggle_save(callback: CallbackQuery):
    new_value = db.toggle_setting("save_deleted")
    status = "включено" if new_value else "выключено"
    await callback.message.edit_text(f"✅ Сохранение удалёнок {status}")
    await callback.answer()

@dp.callback_query(F.data == "osint_username")
async def callback_osint_username(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "🔍 Введи username для поиска (без @):"
    )
    await state.set_state(OSINTStates.waiting_for_username)
    await callback.answer()

@dp.callback_query(F.data == "osint_email")
async def callback_osint_email(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "🔍 Введи email для поиска:"
    )
    await state.set_state(OSINTStates.waiting_for_email)
    await callback.answer()

@dp.callback_query(F.data == "osint_phone")
async def callback_osint_phone(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "🔍 Введи номер телефона для поиска (в любом формате):"
    )
    await state.set_state(OSINTStates.waiting_for_phone)
    await callback.answer()

# ========== FSM ОБРАБОТЧИКИ ==========
@dp.message(EnemyStates.waiting_for_id)
async def process_enemy_id(message: Message, state: FSMContext):
    try:
        enemy_id = int(message.text)
        if db.add_enemy(enemy_id):
            await message.answer(f"✅ Враг {enemy_id} добавлен!")
        else:
            await message.answer(f"❌ Враг {enemy_id} уже в списке")
    except ValueError:
        await message.answer("❌ Это не число. Отправь ID цифрами.")
    
    await state.clear()
    await message.answer("Главное меню:", reply_markup=get_main_keyboard())

@dp.message(OSINTStates.waiting_for_username)
async def process_osint_username(message: Message, state: FSMContext):
    username = message.text.strip().replace("@", "")
    await message.answer(f"🔍 Ищу `{username}`...", parse_mode="Markdown")
    db.stats["osint_requests"] += 1
    await asyncio.sleep(1)
    await message.answer(
        f"🔍 **Результаты для @{username}**\n\n"
        f"(Здесь будет реальный поиск по 700+ сайтам)\n"
        f"Пока это демо-версия",
        parse_mode="Markdown"
    )
    await state.clear()

@dp.message(OSINTStates.waiting_for_email)
async def process_osint_email(message: Message, state: FSMContext):
    email = message.text.strip()
    await message.answer(f"🔍 Ищу `{email}`...", parse_mode="Markdown")
    db.stats["osint_requests"] += 1
    await asyncio.sleep(1)
    await message.answer(
        f"🔍 **Результаты для {email}**\n\n"
        f"(Здесь будет реальный поиск по утечкам)",
        parse_mode="Markdown"
    )
    await state.clear()

@dp.message(OSINTStates.waiting_for_phone)
async def process_osint_phone(message: Message, state: FSMContext):
    phone = message.text.strip()
    await message.answer(f"🔍 Ищу `{phone}`...", parse_mode="Markdown")
    db.stats["osint_requests"] += 1
    await asyncio.sleep(1)
    await message.answer(
        f"🔍 **Результаты для {phone}**\n\n"
        f"(Здесь будет реальный поиск по Telegram и утечкам)",
        parse_mode="Markdown"
    )
    await state.clear()

# ========== ГЛАВНЫЙ ОБРАБОТЧИК СООБЩЕНИЙ ==========
@dp.message()
async def handle_all_messages(message: Message):
    if message.text and message.text.startswith("/"):
        return
    if message.from_user.id == bot.id:
        return
    
    db.stats["messages_processed"] += 1
    
    if db.settings["save_deleted"] and message.text:
        db.save_message(
            message.message_id,
            {
                "text": message.text,
                "from": message.from_user.id,
                "from_name": message.from_user.full_name,
                "chat": message.chat.id,
                "time": datetime.now().isoformat()
            }
        )
    
    is_enemy = message.from_user.id in db.enemies
    
    if is_enemy and db.settings["evil_mode"]:
        is_group = message.chat.type in ["group", "supergroup"]
        if is_group and not db.settings["work_in_groups"]:
            return
        if not is_group and not db.settings["work_in_pm"]:
            return
        
        await bot.send_chat_action(message.chat.id, "typing")
        delay = random.randint(db.settings["delay_min"], db.settings["delay_max"])
        await asyncio.sleep(delay)
        insult = generate_insult(message.text or "")
        await message.reply(insult)
        db.stats["evil_responses"] += 1

# ========== УДАЛЕНИЕ ВЕБХУКА И ЗАПУСК ==========
async def on_startup():
    """Действия при запуске"""
    await bot.delete_webhook(drop_pending_updates=True)
    logger.info("✅ Webhook удалён")

async def main():
    """Главная функция запуска"""
    await on_startup()
    logger.info("🚀 Бот запускается...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
