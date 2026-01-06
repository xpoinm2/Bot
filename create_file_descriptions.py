#!/usr/bin/env python3
"""
Создание и управление файлами описаний для медиафайлов
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional

class DescriptionManager:
    """Менеджер файлов описаний"""

    def __init__(self, user_id: int = 8412294171):
        self.user_id = user_id
        self.library_path = Path(f"library/{user_id}")
        self.templates = self._load_templates()

    def _load_templates(self) -> Dict[str, str]:
        """Загружает шаблоны описаний"""
        return {
            'voice_question_greeting': """Название: Приветствие с вопросом
Контекст: Использовать при ответе на приветствие, когда нужно показать интерес к собеседнику
Эмоция: happy
Тема: greeting
Тип: question
Ключевые слова: привет, здравствуй, как дела, как жизнь, как настроение
Пример использования: Когда собеседник пишет "привет" или "здравствуй"
""",

            'voice_answer_wellbeing': """Название: Ответ на вопрос о самочувствии
Контекст: Прямой ответ на вопрос "как дела?" или "как самочувствие?"
Эмоция: happy
Тема: wellbeing
Тип: answer
Ключевые слова: отлично, хорошо, замечательно, прекрасно, супер, отлично
Пример использования: Когда спрашивают "как дела?" и действительно все хорошо
""",

            'voice_gratitude_answer': """Название: Благодарность за внимание
Контекст: Ответ на проявление заботы, комплимент или помощь
Эмоция: grateful
Тема: gratitude
Тип: answer
Ключевые слова: спасибо, благодарю, приятно, рада, приятно слышать
Пример использования: Когда собеседник проявляет заботу или делает комплимент
""",

            'voice_story_food': """Название: Рассказ о готовке
Контекст: Рассказать о любимых блюдах или умении готовить
Эмоция: happy
Тема: food
Тип: story
Ключевые слова: готовка, кухня, рецепт, люблю готовить, умею готовить
Пример использования: Когда разговор заходит о еде или кулинарии
""",

            'voice_story_travel': """Название: Рассказ о путешествиях
Контекст: Поделиться впечатлениями от поездок или путешествий
Эмоция: excited
Тема: travel
Тип: story
Ключевые слова: путешествие, поездка, отпуск, море, пляж, отель
Пример использования: Когда собеседник спрашивает о путешествиях
""",

            'voice_statement_about_me': """Название: Рассказ о себе
Контекст: Кратко рассказать о себе, работе, увлечениях
Эмоция: neutral
Тема: about_me
Тип: statement
Ключевые слова: работаю, занимаюсь, люблю, интересуюсь, увлекаюсь
Пример использования: Когда спрашивают "кем ты работаешь?" или "чем занимаешься?"
"""
        }

    def create_description_for_file(self, file_path: str, template_key: Optional[str] = None) -> bool:
        """Создает файл описания для конкретного файла"""
        path_obj = Path(file_path)
        if not path_obj.exists():
            print(f"❌ Файл не существует: {file_path}")
            return False

        desc_file = path_obj.parent / f"{path_obj.stem}.txt"

        if desc_file.exists():
            overwrite = input(f"Файл описания уже существует: {desc_file.name}. Перезаписать? (y/N): ")
            if overwrite.lower() != 'y':
                return False

        # Определяем шаблон на основе имени файла
        if template_key and template_key in self.templates:
            content = self.templates[template_key]
        else:
            # Автоматически определяем шаблон
            filename_lower = path_obj.name.lower()
            template_key = self._guess_template(filename_lower)
            content = self.templates.get(template_key, self._create_basic_description(path_obj.name))

        try:
            with open(desc_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Создано описание: {desc_file.name}")
            return True
        except Exception as e:
            print(f"❌ Ошибка создания описания: {e}")
            return False

    def _guess_template(self, filename: str) -> str:
        """Определяет подходящий шаблон на основе имени файла"""
        filename_lower = filename.lower()

        # Анализ по ключевым словам
        if any(word in filename_lower for word in ['привет', 'здравствуй', 'как дела']):
            return 'voice_question_greeting'
        elif any(word in filename_lower for word in ['хорошо', 'отлично', 'замечательно']):
            return 'voice_answer_wellbeing'
        elif any(word in filename_lower for word in ['спасибо', 'благодар']):
            return 'voice_gratitude_answer'
        elif any(word in filename_lower for word in ['готов', 'кухн', 'рецепт']):
            return 'voice_story_food'
        elif any(word in filename_lower for word in ['путешеств', 'поездк', 'отпуск']):
            return 'voice_story_travel'
        elif any(word in filename_lower for word in ['работ', 'занима', 'люблю']):
            return 'voice_statement_about_me'
        else:
            return 'voice_answer_wellbeing'  # по умолчанию

    def _create_basic_description(self, filename: str) -> str:
        """Создает базовое описание для неизвестного файла"""
        return f"""Название: {filename}
Контекст: Автоматически созданное описание
Эмоция: neutral
Тема: unknown
Тип: statement
Ключевые слова: {filename.replace('_', ', ')}
Пример использования: Когда подходит по контексту разговора
"""

    def create_descriptions_for_all(self, folders: List[str] = None) -> None:
        """Создает описания для всех файлов в указанных папках"""
        if folders is None:
            folders = ['voices', 'video', 'stickers', 'pastes']

        total_created = 0

        for folder in folders:
            folder_path = self.library_path / folder
            if not folder_path.exists():
                print(f"⚠️ Папка не существует: {folder}")
                continue

            print(f"\n📁 Обработка папки: {folder}")

            media_files = []
            for ext in ['*.ogg', '*.mp4', '*.jpg', '*.png', '*.txt']:
                media_files.extend(folder_path.glob(ext))

            for file_path in media_files:
                desc_file = file_path.parent / f"{file_path.stem}.txt"

                if not desc_file.exists():
                    if self.create_description_for_file(str(file_path)):
                        total_created += 1
                else:
                    print(f"⏭️ Описание уже существует: {desc_file.name}")

        print(f"\n✅ Создано описаний: {total_created}")

    def validate_descriptions(self) -> None:
        """Проверяет корректность файлов описаний"""
        folders = ['voices', 'video', 'stickers', 'pastes']
        issues = []

        for folder in folders:
            folder_path = self.library_path / folder
            if not folder_path.exists():
                continue

            media_files = []
            for ext in ['*.ogg', '*.mp4', '*.jpg', '*.png', '*.txt']:
                media_files.extend(folder_path.glob(ext))

            for file_path in media_files:
                desc_file = file_path.parent / f"{file_path.stem}.txt"

                if not desc_file.exists():
                    issues.append(f"Отсутствует описание: {file_path.name}")
                else:
                    # Проверяем корректность описания
                    try:
                        with open(desc_file, 'r', encoding='utf-8') as f:
                            content = f.read()

                        required_fields = ['Название:', 'Контекст:', 'Эмоция:', 'Тема:', 'Тип:']
                        missing_fields = []

                        for field in required_fields:
                            if field not in content:
                                missing_fields.append(field)

                        if missing_fields:
                            issues.append(f"Некорректное описание {desc_file.name}: отсутствуют поля {', '.join(missing_fields)}")

                    except Exception as e:
                        issues.append(f"Ошибка чтения описания {desc_file.name}: {e}")

        if issues:
            print("⚠️ Найдены проблемы с описаниями:")
            for issue in issues:
                print(f"   • {issue}")
        else:
            print("✅ Все описания корректны!")

    def interactive_mode(self) -> None:
        """Интерактивный режим создания описаний"""
        print("🎯 Интерактивное создание описаний")
        print("Команды:")
        print("  'all' - создать описания для всех файлов")
        print("  'validate' - проверить существующие описания")
        print("  'file <путь>' - создать описание для конкретного файла")
        print("  'quit' - выход")

        while True:
            command = input("\nВведите команду: ").strip()

            if command.lower() in ['q', 'quit', 'exit']:
                break
            elif command.lower() == 'all':
                self.create_descriptions_for_all()
            elif command.lower() == 'validate':
                self.validate_descriptions()
            elif command.startswith('file '):
                file_path = command[5:].strip()
                self.create_description_for_file(file_path)
            else:
                print("❌ Неизвестная команда")

def main():
    """Основная функция"""
    import argparse

    parser = argparse.ArgumentParser(description="Управление файлами описаний медиа")
    parser.add_argument('--all', action='store_true',
                       help='Создать описания для всех файлов')
    parser.add_argument('--validate', action='store_true',
                       help='Проверить корректность описаний')
    parser.add_argument('--file', type=str,
                       help='Создать описание для конкретного файла')
    parser.add_argument('--template', action='store_true',
                       help='Использовать шаблоны для создания описаний')
    parser.add_argument('--interactive', action='store_true',
                       help='Интерактивный режим')

    args = parser.parse_args()

    manager = DescriptionManager()

    if args.all:
        manager.create_descriptions_for_all()
    elif args.validate:
        manager.validate_descriptions()
    elif args.file:
        manager.create_description_for_file(args.file)
    elif args.interactive:
        manager.interactive_mode()
    else:
        print("🎯 Запуск интерактивного режима...")
        print("Используйте --help для списка опций")
        manager.interactive_mode()

if __name__ == "__main__":
    main()

