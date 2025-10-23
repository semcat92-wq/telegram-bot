#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import platform

# Проверяем версию Python
print(f"🚀 Запуск бота...")
print(f"📋 Python версия: {sys.version}")
print(f"💻 Операционная система: {platform.system()} {platform.release()}")

try:
    import pandas as pd
    import logging
    from telegram import Update
    from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
    from dotenv import load_dotenv
    print("✅ Все необходимые модули успешно импортированы")
except ImportError as e:
    print(f"❌ Ошибка импорта модулей: {e}")
    print("📦 Установите недостающие модули командой:")
    print("   python3 -m pip install pandas openpyxl python-telegram-bot python-dotenv")
    sys.exit(1)

# Загружаем переменные окружения из файла .env
load_dotenv()

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TradingPointBot:
    def __init__(self, excel_file_path):
        """Инициализация бота с загрузкой данных из Excel"""
        self.excel_file = excel_file_path
        self.df_north = None
        self.df_center = None
        print(f"📂 Загружаем данные из файла: {excel_file_path}")
        self.load_data()
    
    def load_data(self):
        """Загрузка данных из Excel файла"""
        try:
            # Проверяем существование файла
            if not os.path.exists(self.excel_file):
                raise FileNotFoundError(f"Файл {self.excel_file} не найден!")
            
            print("📖 Читаем лист 'Север'...")
            self.df_north = pd.read_excel(self.excel_file, sheet_name='Север')
            
            print("📖 Читаем лист 'Центр'...")
            self.df_center = pd.read_excel(self.excel_file, sheet_name='Центр')
            
            # Преобразуем названия в нижний регистр для удобства поиска
            self.df_north['Название ТО'] = self.df_north['Название ТО'].astype(str).str.lower().str.strip()
            self.df_center['Название ТО'] = self.df_center['Название ТО'].astype(str).str.lower().str.strip()
            
            print(f"✅ Загружено {len(self.df_north)} записей с листа 'Север'")
            print(f"✅ Загружено {len(self.df_center)} записей с листа 'Центр'")
            logger.info("Данные успешно загружены из Excel файла")
            
        except Exception as e:
            print(f"❌ Ошибка загрузки данных: {e}")
            logger.error(f"Ошибка загрузки данных: {e}")
            raise
    
    def search_trading_point(self, name):
        """Поиск торговой точки по названию"""
        name = name.strip().lower()
        logger.info(f"🔍 Поиск торговой точки: '{name}'")
        
        # Ищем в листе "Север"
        result_north = self.df_north[self.df_north['Название ТО'] == name]
        
        # Ищем в листе "Центр"  
        result_center = self.df_center[self.df_center['Название ТО'] == name]
        
        if not result_north.empty:
            logger.info(f"✅ Найдено в листе 'Север': {len(result_north)} записей")
            return self.format_result(result_north.iloc[0], 'Север')
        elif not result_center.empty:
            logger.info(f"✅ Найдено в листе 'Центр': {len(result_center)} записей")
            return self.format_result(result_center.iloc[0], 'Центр')
        else:
            logger.info(f"❌ Торговая точка '{name}' не найдена")
            return None
    
    def format_result(self, row, sheet_name):
        """Форматирование найденных данных"""
        try:
            # Функция для безопасного получения значений
            def get_value(column_name, default='Не указано'):
                value = row.get(column_name)
                if pd.isna(value) or value == '':
                    return default
                return str(value)
            
            if sheet_name == 'Север':
                result_text = f"""
🏪 *{get_value('Название ТО').title()}* ({sheet_name})

📋 *Формат:* {get_value('Формат')}
🏢 *Филиал:* {get_value('Филиал')}
👨‍💼 *Менеджер:* {get_value('Менеджер')}
👩‍💼 *ДФ:* {get_value('ДФ')}  
👨‍💼 *ДГ:* {get_value('ДГ')}
📍 *Адрес:* {get_value('Адрес')}
🔢 *Пин:* {get_value('Пин')}
                """
            else:  # Центр
                result_text = f"""
🏪 *{get_value('Название ТО').title()}* ({sheet_name})

📋 *Формат:* {get_value('Формат')}
👨‍💼 *ВССБ:* {get_value('ВССБ')}
👩‍💼 *ССБ:* {get_value('ССБ')}
📍 *Адрес:* {get_value('Адрес')}
🔢 *Пин:* {get_value('Пин')}
👨‍💼 *Директор Группы:* {get_value('Директор Группы')}
                """
            
            return result_text.strip()
            
        except Exception as e:
            logger.error(f"Ошибка форматирования результата: {e}")
            return "❌ Произошла ошибка при обработке данных"

# Создаем глобальный экземпляр бота
try:
    bot_instance = TradingPointBot('Test2-2.xlsx')
    print("🤖 Бот успешно инициализирован!")
except Exception as e:
    print(f"❌ Не удалось инициализировать бота: {e}")
    bot_instance = None

async def start_command(update: Update, context: CallbackContext):
    """Обработчик команды /start"""
    welcome_text = """
👋 *Привет! Я бот для поиска информации о торговых точках*

Просто отправь мне *название магазина*, и я найду всю информацию о нём.

*Примеры названий для поиска:*
• Гульден
• Чалка  
• Авинда
• Бакингем
• Джонка

*Как пользоваться:*
1. Напишите название магазина
2. Получите подробную информацию
3. Если магазин не найден - проверьте написание

*Доступные команды:*
/start - показать это сообщение
/help - помощь
/reload - перезагрузить данные
    """
    await update.message.reply_text(welcome_text, parse_mode='Markdown')

async def help_command(update: Update, context: CallbackContext):
    """Обработчик команды /help"""
    help_text = """
*Помощь по использованию бота*

🤖 *Что делает бот:*
Ищет информацию о торговых точках в базе данных Excel

🔍 *Как искать:*
Просто напишите название магазина в чат

📝 *Примеры названий:*
• Гульден
• Чалка
• Авинда
• Бакингем

⚡ *Команды:*
/start - начать работу
/help - эта справка  
/reload - перезагрузить данные
    """
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def reload_command(update: Update, context: CallbackContext):
    """Обработчик команды /reload - перезагрузка данных из Excel"""
    global bot_instance
    try:
        bot_instance.load_data()
        await update.message.reply_text("✅ *Данные успешно перезагружены из Excel файла!*", parse_mode='Markdown')
        logger.info("Данные перезагружены по команде пользователя")
    except Exception as e:
        await update.message.reply_text(f"❌ *Ошибка перезагрузки данных:* {e}", parse_mode='Markdown')
        logger.error(f"Ошибка перезагрузки данных: {e}")

async def handle_message(update: Update, context: CallbackContext):
    """Обработчик всех текстовых сообщений"""
    if bot_instance is None:
        await update.message.reply_text("❌ *Бот не инициализирован. Проверьте наличие файла данных*", parse_mode='Markdown')
        return
    
    user_message = update.message.text.strip()
    
    # Игнорируем пустые сообщения
    if not user_message:
        await update.message.reply_text("📝 *Пожалуйста, введите название магазина для поиска*", parse_mode='Markdown')
        return
    
    # Ищем торговую точку
    result = bot_instance.search_trading_point(user_message)
    
    if result:
        await update.message.reply_text(result, parse_mode='Markdown')
    else:
        error_message = f"""
❌ *Торговая точка "{user_message}" не найдена*

*Возможные причины:*
• Опечатка в названии
• Магазин отсутствует в базе
• Неправильный регистр букв

*Попробуйте:*
• Проверить написание
• Использовать другое название
• Обратиться к администратору
        """
        await update.message.reply_text(error_message, parse_mode='Markdown')

async def error_handler(update: Update, context: CallbackContext):
    """Обработчик ошибок"""
    logger.error(f"Ошибка при обработке сообщения: {context.error}")
    
    if update and update.message:
        await update.message.reply_text(
            "❌ *Произошла непредвиденная ошибка. Пожалуйста, попробуйте позже*",
            parse_mode='Markdown'
        )

def main():
    """Основная функция запуска бота"""
    # Получаем токен бота из переменных окружения
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    
    if not BOT_TOKEN:
        print("❌ ОШИБКА: Токен бота не найден!")
        print("Создайте файл .env и добавьте туда: BOT_TOKEN=ваш_токен_бота")
        print("Или установите переменную окружения: export BOT_TOKEN='ваш_токен'")
        return
    
    # Проверяем инициализацию бота
    if bot_instance is None:
        print("❌ ОШИБКА: Бот не инициализирован! Проверьте наличие файла Test2-2.xlsx")
        return
    
    try:
        # Создаем приложение бота
        application = Application.builder().token(BOT_TOKEN).build()
        
        # Добавляем обработчики команд
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("reload", reload_command))
        
        # Добавляем обработчик текстовых сообщений
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        # Добавляем обработчик ошибок
        application.add_error_handler(error_handler)
        
        # Запускаем бота
        print("🤖 Бот запускается...")
        print("📍 Для остановки нажмите Ctrl+C")
        
        application.run_polling()
        
    except Exception as e:
        logger.error(f"Ошибка запуска бота: {e}")
        print(f"❌ ОШИБКА ЗАПУСКА: {e}")

if __name__ == '__main__':
    main()