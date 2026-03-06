"""
Злой Демон 3.0 — Полная версия для Render.com
Инструкция: замени BOT_TOKEN и OWNER_ID на свои
"""

import asyncio
import logging
import random
import os
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

# Настройка логирования (ОДИН РАЗ!)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Инициализация бота (ОДИН РАЗ!)
bot = Bot(token=BOT_TOKEN)

# ✨ УДАЛЯЕМ ВЕБХУК, ЕСЛИ БЫЛ ✨
async def delete_webhook():
    await bot.delete_webhook(drop_pending_updates=True)
    logger.info("✅ Webhook удалён (если был)")
asyncio.run(delete_webhook())

# Инициализация диспетчера (ОДИН РАЗ!)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# ========== БАЗА ДАННЫХ ==========
# ... (весь остальной код БЕЗ ИЗМЕНЕНИЙ, начиная с класса Database)
