import logging
import pandas as pd
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
import re
import os
import json
from typing import Dict, List

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Токен бота из переменных окружения
BOT_TOKEN = os.environ.get('BOT_TOKEN')
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден в переменных окружения!")

# Файл для хранения языковых настроек пользователей
USER_LANGUAGE_FILE = "user_languages.json"

# Многоязычная поддержка
LANGUAGES = {
    'ru': {
        'welcome': '👋 Добро пожаловать в бот поиска студентов!\n\nВыберите действие:',
        'search_by_name': '🔍 Поиск по имени',
        'show_group': '👥 Показать группу',
        'change_language': '🌐 Сменить язык',
        'statistics': '📊 Статистика',
        'help': '❓ Помощь',
        'enter_name': 'Введите имя и фамилию студента:',
        'choose_group': 'Выберите группу:',
        'student_found': '✅ Найден студент:',
        'students_in_group': '👥 Студенты группы {group}:',
        'no_students_found': '❌ Студенты не найдены',
        'exam_passed': '✅ Экзамен сдан',
        'exam_failed': '❌ Экзамен не сдан',
        'phone': '📱 Телефон',
        'nickname': '👤 Никнейм',
        'certificates': '🏆 Сертификаты',
        'back_to_menu': '🔙 Главное меню',
        'language_changed': '✅ Язык изменен на Русский',
        'help_text': '''
🤖 Инструкция по использованию бота:

🔍 Поиск по имени - найти студента по имени и фамилии
👥 Показать группу - показать всех студентов выбранной группы  
📊 Статистика - общая статистика по группам
🌐 Сменить язык - переключение между языками

Для поиска просто введите имя и фамилию студента.
        ''',
        'total_students': 'Всего студентов: {count}',
        'passed_exam_count': 'Сдали экзамен: {count}',
        'failed_exam_count': 'Не сдали экзамен: {count}',
        'group': 'Группа',
        'status': 'Статус',
        'select_language': 'Выберите язык:',
        'has_certificate': 'есть сертификат',
        'no_certificate': 'нет сертификата'
    },
    'uz': {
        'welcome': '👋 Talabalar qidiruv botiga xush kelibsiz!\n\nAmalni tanlang:',
        'search_by_name': '🔍 Ism bo\'yicha qidirish',
        'show_group': '👥 Guruhni ko\'rsatish',
        'change_language': '🌐 Tilni o\'zgartirish',
        'statistics': '📊 Statistika',
        'help': '❓ Yordam',
        'enter_name': 'Talabaning ism va familiyasini kiriting:',
        'choose_group': 'Guruhni tanlang:',
        'student_found': '✅ Talaba topildi:',
        'students_in_group': '👥 {group} guruh talabalari:',
        'no_students_found': '❌ Talabalar topilmadi',
        'exam_passed': '✅ Imtihon topshirildi',
        'exam_failed': '❌ Imtihon topshirilmadi',
        'phone': '📱 Telefon',
        'nickname': '👤 Taxallus',
        'certificates': '🏆 Sertifikatlar',
        'back_to_menu': '🔙 Asosiy menyu',
        'language_changed': '✅ Til o\'zbekchaga o\'zgartirildi',
        'help_text': '''
🤖 Botdan foydalanish bo\'yicha ko\'rsatma:

🔍 Ism bo\'yicha qidirish - talabani ism va familiya bo\'yicha topish
👥 Guruhni ko\'rsatish - tanlangan guruhning barcha talabalarini ko\'rsatish
📊 Statistika - guruhlar bo\'yicha umumiy statistika
🌐 Tilni o\'zgartirish - tillar o\'rtasida almashtirish

Qidirish uchun talabaning ism va familiyasini kiriting.
        ''',
        'total_students': 'Jami talabalar: {count}',
        'passed_exam_count': 'Imtihon topshirganlar: {count}',
        'failed_exam_count': 'Imtihon topshirmaganlar: {count}',
        'group': 'Guruh',
        'status': 'Holat',
        'select_language': 'Tilni tanlang:',
        'has_certificate': 'sertifikat bor',
        'no_certificate': 'sertifikat yo\'q'
    },
    'en': {
        'welcome': '👋 Welcome to the Student Search Bot!\n\nChoose an action:',
        'search_by_name': '🔍 Search by name',
        'show_group': '👥 Show group',
        'change_language': '🌐 Change language',
        'statistics': '📊 Statistics',
        'help': '❓ Help',
        'enter_name': 'Enter student name and surname:',
        'choose_group': 'Choose a group:',
        'student_found': '✅ Student found:',
        'students_in_group': '👥 Students in group {group}:',
        'no_students_found': '❌ No students found',
        'exam_passed': '✅ Exam passed',
        'exam_failed': '❌ Exam failed',
        'phone': '📱 Phone',
        'nickname': '👤 Nickname',
        'certificates': '🏆 Certificates',
        'back_to_menu': '🔙 Main menu',
        'language_changed': '✅ Language changed to English',
        'help_text': '''
🤖 Bot usage instructions:

🔍 Search by name - find a student by name and surname
👥 Show group - show all students in the selected group
📊 Statistics - general statistics by groups
🌐 Change language - switch between languages

To search, simply enter the student's name and surname.
        ''',
        'total_students': 'Total students: {count}',
        'passed_exam_count': 'Passed exam: {count}',
        'failed_exam_count': 'Failed exam: {count}',
        'group': 'Group',
        'status': 'Status',
        'select_language': 'Select language:',
        'has_certificate': 'has certificate',
        'no_certificate': 'no certificate'
    }
}

class StudentBot:
    def __init__(self):
        self.students_data = {}
        self.user_languages = self.load_user_languages()
        self.load_data()
    
    def load_user_languages(self) -> Dict[str, str]:
        """Загрузка языковых настроек пользователей из файла"""
        if os.path.exists(USER_LANGUAGE_FILE):
            try:
                with open(USER_LANGUAGE_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Ошибка загрузки языковых настроек: {e}")
        return {}
    
    def save_user_languages(self):
        """Сохранение языковых настроек пользователей в файл"""
        try:
            with open(USER_LANGUAGE_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.user_languages, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Ошибка сохранения языковых настроек: {e}")
    
    def has_certificate(self, row: pd.Series) -> bool:
        """Проверка наличия сертификата у студента"""
        # Ищем колонки, которые могут содержать информацию о сертификатах
        cert_columns = []
        
        for col in row.index:
            col_lower = str(col).lower()
            if any(keyword in col_lower for keyword in ['sertifikat', 'certificate', 'cert']):
                cert_columns.append(col)
        
        # Если нашли колонки с сертификатами, проверяем их
        for col in cert_columns:
            value = row[col]
            if pd.notna(value):
                value_str = str(value).strip()
                # Проверяем, что значение не пустое и не является стандартными "пустыми" значениями
                if value_str and value_str.lower() not in ['', 'nan', 'none', 'null', '-', 'n/a']:
                    return True
        
        return False
    
    def load_data(self):
        """Загрузка данных студентов из CSV файлов"""
        urls = {
            'D1': 'https://hebbkx1anhila5yf.public.blob.vercel-storage.com/group_d1-PV7nQS7IQwFS9e2ps8nTKOBoGIv2br.csv',
            'D2': 'https://hebbkx1anhila5yf.public.blob.vercel-storage.com/group_d2-WQjbXhJy4zuB1uPnTEYsP27kTALVq0.csv',
            'D3': 'https://hebbkx1anhila5yf.public.blob.vercel-storage.com/group_d3-uPiNK14aokZuaaFV8DjGlyE94Qkkl9.csv',
            'D4': 'https://hebbkx1anhila5yf.public.blob.vercel-storage.com/group_d4-ln5jYKnT5nlI7UQxO2xBBdXrvtMHV9.csv'
        }
        
        for group, url in urls.items():
            try:
                response = requests.get(url, timeout=30)
                content = response.content.decode('utf-8', errors='ignore')
                
                # Создаем временный файл
                temp_file = f'temp_{group.lower()}.csv'
                with open(temp_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                # Пробуем разные способы чтения CSV
                df = None
                
                # Сначала пробуем с разделителем ;
                try:
                    df = pd.read_csv(temp_file, delimiter=';')
                    logger.info(f"Группа {group} загружена с разделителем ';'")
                except:
                    pass
                
                # Если не получилось, пробуем с запятой
                if df is None or df.empty:
                    try:
                        df = pd.read_csv(temp_file, delimiter=',')
                        logger.info(f"Группа {group} загружена с разделителем ','")
                    except:
                        pass
                
                # Если все еще не получилось, пробуем автоопределение
                if df is None or df.empty:
                    try:
                        df = pd.read_csv(temp_file)
                        logger.info(f"Группа {group} загружена с автоопределением разделителя")
                    except Exception as e:
                        logger.error(f"Не удалось загрузить группу {group}: {e}")
                        continue
                
                if df is not None and not df.empty:
                    # Очищаем данные
                    df = df.dropna(how='all')  # Удаляем полностью пустые строки
                    
                    # Логируем информацию о колонках
                    logger.info(f"Группа {group}: колонки = {list(df.columns)}")
                    
                    # Проверяем наличие сертификатов для отладки
                    cert_count = 0
                    for _, row in df.iterrows():
                        if self.has_certificate(row):
                            cert_count += 1
                    
                    logger.info(f"Группа {group}: {len(df)} студентов, {cert_count} с сертификатами")
                    
                    self.students_data[group] = df
                
                # Удаляем временный файл
                if os.path.exists(temp_file):
                    os.remove(temp_file)
                    
            except Exception as e:
                logger.error(f"Ошибка загрузки группы {group}: {e}")
    
    def get_user_language(self, user_id: int) -> str:
        """Получить язык пользователя"""
        user_id_str = str(user_id)
        return self.user_languages.get(user_id_str, 'ru')
    
    def set_user_language(self, user_id: int, language: str):
        """Установить язык пользователя"""
        user_id_str = str(user_id)
        self.user_languages[user_id_str] = language
        self.save_user_languages()
    
    def get_text(self, user_id: int, key: str, **kwargs) -> str:
        """Получить текст на языке пользователя"""
        lang = self.get_user_language(user_id)
        text = LANGUAGES[lang].get(key, key)
        if kwargs:
            text = text.format(**kwargs)
        return text
    
    def create_main_menu(self, user_id: int) -> ReplyKeyboardMarkup:
        """Создать главное меню"""
        keyboard = [
            [KeyboardButton(self.get_text(user_id, 'search_by_name'))],
            [KeyboardButton(self.get_text(user_id, 'show_group'))],
            [KeyboardButton(self.get_text(user_id, 'statistics')), 
             KeyboardButton(self.get_text(user_id, 'help'))],
            [KeyboardButton(self.get_text(user_id, 'change_language'))]
        ]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    def search_student(self, query: str) -> List[Dict]:
        """Поиск студента по имени и фамилии"""
        results = []
        query_lower = query.lower()
        
        for group, df in self.students_data.items():
            if df.empty:
                continue
                
            # Ищем по всем колонкам, которые могут содержать имена
            for index, row in df.iterrows():
                row_text = ' '.join(str(val) for val in row.values if pd.notna(val))
                
                # Проверяем, содержит ли строка поисковый запрос
                if query_lower in row_text.lower():
                    student_info = {
                        'group': group,
                        'data': row,
                        'index': index
                    }
                    results.append(student_info)
        
        return results
    
    def format_student_info(self, student: Dict, user_id: int) -> str:
        """Форматирование информации о студенте"""
        row = student['data']
        group = student['group']
        
        # Определяем статус экзамена по наличию сертификатов
        has_cert = self.has_certificate(row)
        exam_status = self.get_text(user_id, 'exam_passed') if has_cert else self.get_text(user_id, 'exam_failed')
        
        # Получаем ФИО студента
        name = self.get_student_name(row)
        
        # Форматируем информацию на языке пользователя
        info = f"┌{'─' * 35}┐\n"
        info += f"│ 👤 **{name}**\n"
        info += f"│ 🏫 {self.get_text(user_id, 'group')}: **{group}**\n"
        info += f"│ 📋 {self.get_text(user_id, 'status')}: {exam_status}\n"
        
        # Добавляем дополнительную информацию если есть
        phone = self.get_student_phone(row)
        if phone:
            info += f"│ {self.get_text(user_id, 'phone')}: {phone}\n"
        
        nickname = self.get_student_nickname(row)
        if nickname:
            info += f"│ {self.get_text(user_id, 'nickname')}: {nickname}\n"
        
        certificates = self.get_student_certificates(row)
        if certificates:
            info += f"│ {self.get_text(user_id, 'certificates')}: {certificates}\n"
        
        info += f"└{'─' * 35}┘"
        
        return info
    
    def get_student_name(self, row: pd.Series) -> str:
        """Получить имя студента из строки данных"""
        # Проверяем различные возможные колонки с именами
        name_columns = ['F.I.Sh', 'ФИО', 'Name', 'Имя', 'Full Name']
        
        for col in name_columns:
            if col in row and pd.notna(row[col]):
                return str(row[col]).strip()
        
        # Если не нашли по названию колонки, берем вторую колонку (обычно там имя)
        if len(row) > 1 and pd.notna(row.iloc[1]):
            return str(row.iloc[1]).strip()
        
        return "Не указано"
    
    def get_student_phone(self, row: pd.Series) -> str:
        """Получить телефон студента"""
        phone_columns = ['Telefon nomeri', 'Phone', 'Телефон']
        
        for col in phone_columns:
            if col in row and pd.notna(row[col]):
                phone = str(row[col]).strip()
                if phone and phone != '':
                    return phone
        
        return ""
    
    def get_student_nickname(self, row: pd.Series) -> str:
        """Получить никнейм студента"""
        nickname_columns = ['Nick name', 'Nickname', 'Никнейм']
        
        for col in nickname_columns:
            if col in row and pd.notna(row[col]):
                nickname = str(row[col]).strip()
                if nickname and nickname != '':
                    return nickname
        
        return ""
    
    def get_student_certificates(self, row: pd.Series) -> str:
        """Получить информацию о сертификатах студента"""
        cert_columns = []
        
        for col in row.index:
            col_lower = str(col).lower()
            if any(keyword in col_lower for keyword in ['sertifikat', 'certificate', 'cert']):
                cert_columns.append(col)
        
        certificates = []
        for col in cert_columns:
            if pd.notna(row[col]):
                cert = str(row[col]).strip()
                if cert and cert.lower() not in ['', 'nan', 'none', 'null', '-', 'n/a']:
                    certificates.append(cert)
        
        return ', '.join(certificates) if certificates else ""
    
    def get_group_students(self, group: str) -> pd.DataFrame:
        """Получить студентов группы"""
        return self.students_data.get(group, pd.DataFrame())
    
    def get_statistics(self, user_id: int) -> str:
        """Получить статистику"""
        total_students = 0
        passed_exam = 0
        failed_exam = 0
        
        group_stats = {}
        
        for group, df in self.students_data.items():
            if df.empty:
                continue
                
            group_total = len(df)
            total_students += group_total
            
            # Подсчитываем сдавших экзамен (у кого есть сертификаты)
            group_passed = 0
            for _, row in df.iterrows():
                if self.has_certificate(row):
                    group_passed += 1
            
            group_failed = group_total - group_passed
            passed_exam += group_passed
            failed_exam += group_failed
            
            group_stats[group] = {
                'total': group_total,
                'passed': group_passed,
                'failed': group_failed
            }
        
        stats = f"📊 **{self.get_text(user_id, 'statistics')}**\n\n"
        stats += f"{self.get_text(user_id, 'total_students', count=total_students)}\n"
        stats += f"{self.get_text(user_id, 'passed_exam_count', count=passed_exam)}\n"
        stats += f"{self.get_text(user_id, 'failed_exam_count', count=failed_exam)}\n\n"
        
        # Статистика по группам
        for group, group_stat in group_stats.items():
            stats += f"**{group}:** {group_stat['total']} ({self.get_text(user_id, 'has_certificate')}: {group_stat['passed']})\n"
        
        return stats

# Создаем экземпляр бота
bot = StudentBot()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    user_id = update.effective_user.id
    welcome_text = bot.get_text(user_id, 'welcome')
    main_menu = bot.create_main_menu(user_id)
    
    await update.message.reply_text(
        welcome_text,
        reply_markup=main_menu,
        parse_mode='Markdown'
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик текстовых сообщений"""
    user_id = update.effective_user.id
    text = update.message.text
    
    # Получаем все возможные варианты команд на всех языках
    search_commands = [LANGUAGES[lang]['search_by_name'] for lang in LANGUAGES]
    show_group_commands = [LANGUAGES[lang]['show_group'] for lang in LANGUAGES]
    statistics_commands = [LANGUAGES[lang]['statistics'] for lang in LANGUAGES]
    help_commands = [LANGUAGES[lang]['help'] for lang in LANGUAGES]
    change_language_commands = [LANGUAGES[lang]['change_language'] for lang in LANGUAGES]
    
    if text in search_commands:
        await update.message.reply_text(bot.get_text(user_id, 'enter_name'))
        context.user_data['waiting_for'] = 'student_name'
        
    elif text in show_group_commands:
        keyboard = [
            [InlineKeyboardButton("D1", callback_data="group_D1"),
             InlineKeyboardButton("D2", callback_data="group_D2")],
            [InlineKeyboardButton("D3", callback_data="group_D3"),
             InlineKeyboardButton("D4", callback_data="group_D4")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            bot.get_text(user_id, 'choose_group'),
            reply_markup=reply_markup
        )
        
    elif text in statistics_commands:
        stats = bot.get_statistics(user_id)
        await update.message.reply_text(stats, parse_mode='Markdown')
        
    elif text in help_commands:
        help_text = bot.get_text(user_id, 'help_text')
        await update.message.reply_text(help_text)
        
    elif text in change_language_commands:
        keyboard = [
            [InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru"),
             InlineKeyboardButton("🇺🇿 O'zbek", callback_data="lang_uz")],
            [InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            bot.get_text(user_id, 'select_language'),
            reply_markup=reply_markup
        )
        
    elif context.user_data.get('waiting_for') == 'student_name':
        # Поиск студента
        results = bot.search_student(text)
        
        if results:
            response = f"{bot.get_text(user_id, 'student_found')}\n\n"
            for i, student in enumerate(results[:5]):  # Показываем максимум 5 результатов
                response += f"{bot.format_student_info(student, user_id)}\n\n"
        else:
            response = bot.get_text(user_id, 'no_students_found')
        
        await update.message.reply_text(response, parse_mode='Markdown')
        context.user_data['waiting_for'] = None
    else:
        # Если текст не распознан как команда, пробуем искать студента
        results = bot.search_student(text)
        
        if results:
            response = f"{bot.get_text(user_id, 'student_found')}\n\n"
            for i, student in enumerate(results[:5]):  # Показываем максимум 5 результатов
                response += f"{bot.format_student_info(student, user_id)}\n\n"
            await update.message.reply_text(response, parse_mode='Markdown')
        else:
            # Если ничего не найдено, показываем главное меню
            main_menu = bot.create_main_menu(user_id)
            await update.message.reply_text(
                bot.get_text(user_id, 'welcome'),
                reply_markup=main_menu,
                parse_mode='Markdown'
            )

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик callback запросов"""
    query = update.callback_query
    user_id = query.from_user.id
    data = query.data
    
    await query.answer()
    
    if data.startswith('group_'):
        group = data.split('_')[1]
        df = bot.get_group_students(group)
        
        if df.empty:
            await query.edit_message_text(bot.get_text(user_id, 'no_students_found'))
            return
        
        response = bot.get_text(user_id, 'students_in_group', group=group) + "\n\n"
        
        for index, row in df.iterrows():
            if index >= 20:  # Ограничиваем вывод 20 студентами
                response += f"\n... и еще {len(df) - 20} студентов"
                break
                
            name = bot.get_student_name(row)
            has_cert = bot.has_certificate(row)
            status = "✅" if has_cert else "❌"
            
            response += f"{index + 1}. {status} {name}\n"
        
        # Добавляем кнопку "Назад"
        keyboard = [[InlineKeyboardButton(bot.get_text(user_id, 'back_to_menu'), callback_data="back_to_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(response, reply_markup=reply_markup, parse_mode='Markdown')
        
    elif data.startswith('lang_'):
        lang = data.split('_')[1]
        bot.set_user_language(user_id, lang)
        
        await query.edit_message_text(bot.get_text(user_id, 'language_changed'))
        
        # Обновляем главное меню
        main_menu = bot.create_main_menu(user_id)
        await context.bot.send_message(
            chat_id=user_id,
            text=bot.get_text(user_id, 'welcome'),
            reply_markup=main_menu,
            parse_mode='Markdown'
        )
        
    elif data == 'back_to_menu':
        main_menu = bot.create_main_menu(user_id)
        await context.bot.send_message(
            chat_id=user_id,
            text=bot.get_text(user_id, 'welcome'),
            reply_markup=main_menu,
            parse_mode='Markdown'
        )

def main():
    """Запуск бота"""
    try:
        # Создаем приложение
        application = Application.builder().token(BOT_TOKEN).build()
        
        # Добавляем обработчики
        application.add_handler(CommandHandler("start", start))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        application.add_handler(CallbackQueryHandler(handle_callback))
        
        # Запускаем бота
        logger.info("Бот запущен на Railway...")
        application.run_polling(allowed_updates=Update.ALL_TYPES)
        
    except Exception as e:
        logger.error(f"Ошибка запуска бота: {e}")
        raise

if __name__ == '__main__':
    main()
