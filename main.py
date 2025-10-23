#!/usr/bin/env python3

import os
import sys
import logging
from dotenv import load_dotenv

# Проверяем импорты
try:
    import pandas as pd
    from telegram import Update
    from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
    print("✅ Все модули успешно импортированы")
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    sys.exit(1)

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

print("🚀 Запускаем облачную версию бота...")
print(f"📦 pandas версия: {pd.__version__}")

# Загружаем переменные окружения
load_dotenv()

class TradingBot:
    def __init__(self):
        self.df = None
        self.load_data()
    
    def load_data(self):
        """Загрузка данных из Excel файла"""
        try:
            print("📂 Загружаем данные из Excel...")
            
            # Читаем Excel файл
            self.df = pd.read_excel('Test2-2.xlsx', sheet_name='Север', engine='openpyxl')
            
            # Очищаем и подготавливаем данные
            self.df['Название ТО'] = self.df['Название ТО'].astype(str).str.lower().str.strip()
            self.df = self.df.fillna('Не указано')
            
            print(f"✅ Данные загружены: {len(self.df)} торговых точек")
            
        except Exception as e:
            print(f"❌ Ошибка загрузки данных: {e}")
            raise
    
    def search(self, name):
        """Поиск торговой точки"""
        name = name.lower().strip()
        
        result = self.df[self.df['Название ТО'] == name]
        
        if not result.empty:
            return self.format_result(result.iloc[0])
        
        return None
    
    def format_result(self, row):
        """Форматирование результата"""
        def safe_get(col):
            val = row.get(col)
            if val is None or val == '' or str(val).lower() == 'nan':
                return 'Не указано'
            return str(val)
        
        result_text = f"""
🏪 *{safe_get('Название ТО').title()}*

📋 *Формат:* {safe_get('Формат')}
🏢 *Филиал:* {safe_get('Филиал')}
👨‍💼 *Менеджер:* {safe_get('Менеджер')}
👩‍💼 *ДФ:* {safe_get('ДФ')}
👨‍💼 *ДГ:* {safe_get('ДГ')}
📍 *Адрес:* {safe_get('Адрес')}
🔢 *Пин:* {safe_get('Пин')}
        """.strip()
        
        return result_text

# Инициализируем бота
try:
    bot = TradingBot()
    print("🤖 Бот успешно инициализирован!")
except Exception as e:
    print(f"❌ Ошибка инициализации бота: {e}")
    sys.exit(1)

async def start_command(update: Update, context: CallbackContext):
    text = """
👋 *Привет! Я бот для поиска информации о торговых точках*

Просто отправь мне *название магазина*, и я найду всю информацию.

*Примеры названий:*
• Гульден
• Чалка
• Джонка
• Бакингем

*Команды:*
/start - начать работу
/help - помощь
/status - статус бота
    """
    await update.message.reply_text(text, parse_mode='Markdown')

async def help_command(update: Update, context: CallbackContext):
    help_text = """
*Помощь по использованию бота*

🤖 *Что делает бот:*
Ищет информацию о торговых точках

🔍 *Как искать:*
Напишите название магазина в чат

⚡ *Команды:*
/start - начать работу
/help - эта справка
/status - статус бота
    """
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def status_command(update: Update, context: CallbackContext):
    status_text = f"""
🤖 *Статус бота*

✅ Бот работает исправно
📊 Загружено торговых точек: {len(bot.df)}
🔄 Версия: Облачная 2.0
📍 Хостинг: Render.com
    """
    await update.message.reply_text(status_text, parse_mode='Markdown')

async def handle_message(update: Update, context: CallbackContext):
    user_text = update.message.text.strip()
    
    if not user_text:
        await update.message.reply_text("📝 Введите название магазина")
        return
    
    result = bot.search(user_text)
    
    if result:
        await update.message.reply_text(result, parse_mode='Markdown')
    else:
        error_text = f"""
❌ *Магазин \"{user_text}\" не найден*

Проверьте правильность написания или попробуйте другое название.
        """
        await update.message.reply_text(error_text, parse_mode='Markdown')

def main():
    token = os.getenv('BOT_TOKEN')
    
    if not token:
        print("❌ Токен бота не найден!")
        return
    
    try:
        application = Application.builder().token(token).build()
        
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("status", status_command))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        print("🎯 Бот запущен в облаке!")
        print("📍 Бот будет работать 24/7")
        
        application.run_polling()
        
    except Exception as e:
        print(f"❌ Ошибка запуска бота: {e}")

if __name__ == '__main__':
    main()