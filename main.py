#!/usr/bin/env python3

import os
import sys
import logging
from dotenv import load_dotenv

# Проверяем импорты
try:
    import numpy as np
    import pandas as pd
    from telegram import Update
    from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    sys.exit(1)

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

print("🚀 Запускаем бота для поиска торговых точек...")
print(f"📦 NumPy версия: {np.__version__}")
print(f"📦 pandas версия: {pd.__version__}")

# Загружаем переменные окружения
load_dotenv()

class TradingPointBot:
    def __init__(self):
        self.df = None
        self.load_data()
    
    def load_data(self):
        """Загрузка данных только с листа 'Север'"""
        try:
            print("📂 Загружаем данные из листа 'Север'...")
            
            # Читаем только лист 'Север'
            self.df = pd.read_excel('Test2-2.xlsx', sheet_name='Север', engine='openpyxl')
            
            # Очищаем и подготавливаем данные
            self.df['Название ТО'] = self.df['Название ТО'].astype(str).str.lower().str.strip()
            
            # Заполняем пустые значения
            self.df = self.df.fillna('Не указано')
            
            print(f"✅ Данные загружены: {len(self.df)} торговых точек")
            print(f"📊 Колонки: {list(self.df.columns)}")
            
            # Покажем несколько примеров для проверки
            print(f"\n🔍 Примеры торговых точек:")
            for i, name in enumerate(self.df['Название ТО'].head(5)):
                print(f"   {i+1}. {name.title()}")
            
        except Exception as e:
            print(f"❌ Ошибка загрузки данных: {e}")
            raise
    
    def search(self, name):
        """Поиск торговой точки по названию"""
        name = name.lower().strip()
        print(f"🔍 Ищем: '{name}'")
        
        # Поиск в данных
        result = self.df[self.df['Название ТО'] == name]
        
        if not result.empty:
            print(f"✅ Найдено: {len(result)} записей")
            return self.format_result(result.iloc[0])
        
        print(f"❌ Не найдено")
        return None
    
    def format_result(self, row):
        """Форматирование результата в читаемый вид"""
        try:
            # Функция для безопасного получения значений
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
            
        except Exception as e:
            print(f"❌ Ошибка форматирования: {e}")
            return "❌ Произошла ошибка при обработке данных"
    
    def get_similar_names(self, name, max_suggestions=5):
        """Поиск похожих названий"""
        name = name.lower()
        similar = []
        
        for store_name in self.df['Название ТО']:
            if name in store_name.lower():
                similar.append(store_name.title())
        
        return list(set(similar))[:max_suggestions]

# Инициализируем бота
try:
    bot = TradingPointBot()
    print("\n🤖 Бот успешно инициализирован и готов к работе!")
except Exception as e:
    print(f"❌ Ошибка инициализации бота: {e}")
    sys.exit(1)

async def start_command(update: Update, context: CallbackContext):
    """Обработчик команды /start"""
    text = """
👋 *Привет! Я бот для поиска информации о торговых точках*

Просто отправь мне *название магазина*, и я найду всю информацию о нём.

*Примеры названий для поиска:*
• Гульден
• Чалка
• Джонка
• Бакингем
• Буцина
• Амгунь
• Александер

*Как пользоваться:*
1. Напишите название магазина
2. Получите подробную информацию
3. Если магазин не найден - проверьте написание

*Доступные команды:*
/start - показать это сообщение
/help - помощь
/list - показать все доступные названия
    """
    await update.message.reply_text(text, parse_mode='Markdown')

async def help_command(update: Update, context: CallbackContext):
    """Обработчик команды /help"""
    help_text = """
*Помощь по использованию бота*

🤖 *Что делает бот:*
Ищет информацию о торговых точках в базе данных

🔍 *Как искать:*
Просто напишите название магазина в чат

📝 *Примеры названий:*
• Гульден
• Чалка
• Джонка
• Бакингем

⚡ *Команды:*
/start - начать работу
/help - эта справка
/list - показать все названия

💡 *Советы:*
• Названия чувствительны к регистру
• Проверяйте правильность написания
• Используйте команду /list для просмотра всех вариантов
    """
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def list_command(update: Update, context: CallbackContext):
    """Обработчик команды /list - показать все названия"""
    try:
        all_names = sorted([name.title() for name in bot.df['Название ТО'].unique()])
        
        # Разбиваем на части, чтобы не превысить лимит Telegram
        chunk_size = 50
        chunks = [all_names[i:i + chunk_size] for i in range(0, len(all_names), chunk_size)]
        
        for i, chunk in enumerate(chunks):
            chunk_text = "\n".join([f"• {name}" for name in chunk])
            message = f"📋 *Список торговых точек ({i+1}/{len(chunks)}):*\n\n{chunk_text}"
            await update.message.reply_text(message, parse_mode='Markdown')
        
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка при получении списка: {e}")

async def handle_message(update: Update, context: CallbackContext):
    """Обработчик текстовых сообщений"""
    user_text = update.message.text.strip()
    
    if not user_text:
        await update.message.reply_text("📝 Пожалуйста, введите название торговой точки")
        return
    
    # Ищем торговую точку
    result = bot.search(user_text)
    
    if result:
        await update.message.reply_text(result, parse_mode='Markdown')
    else:
        # Предлагаем похожие варианты
        similar = bot.get_similar_names(user_text)
        
        similar_text = ""
        if similar:
            similar_text = f"\n\n💡 *Похожие названия:*\n" + "\n".join([f"• {s}" for s in similar])
        
        error_text = f"""
❌ *Торговая точка \"{user_text}\" не найдена*

*Возможные причины:*
• Опечатка в названии
• Торговая точка отсутствует в базе
{similar_text}

*Попробуйте:*
• Проверить написание
• Использовать команду /list для просмотра всех названий
• Обратиться к администратору
        """
        await update.message.reply_text(error_text, parse_mode='Markdown')

def main():
    """Основная функция запуска бота"""
    token = os.getenv('BOT_TOKEN')
    
    if not token:
        print("❌ Токен бота не найден!")
        print("💡 Убедитесь, что файл .env существует и содержит BOT_TOKEN=ваш_токен")
        return
    
    try:
        # Создаем приложение бота
        application = Application.builder().token(token).build()
        
        # Добавляем обработчики команд
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("list", list_command))
        
        # Добавляем обработчик текстовых сообщений
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        # Запускаем бота
        print("\n🎯 Бот запущен и готов к работе!")
        print("📍 Для остановки нажмите Ctrl+C")
        print("🔗 Найдите бота в Telegram и отправьте ему /start")
        
        application.run_polling()
        
    except Exception as e:
        print(f"❌ Ошибка запуска бота: {e}")

if __name__ == '__main__':
    main()