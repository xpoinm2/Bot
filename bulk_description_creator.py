#!/usr/bin/env python3
"""
Массовое создание описаний для медиафайлов с шаблонами
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple

class BulkDescriptionCreator:
    """Инструмент для массового создания описаний медиафайлов"""

    def __init__(self, user_id: int = 8412294171):
        self.user_id = user_id
        self.library_path = Path(f"library/{user_id}")
        self.templates = self._load_templates()

    def _load_templates(self) -> Dict[str, Dict]:
        """Загружает шаблоны описаний по категориям"""
        return {
            'voice_question_greeting': {
                'title': 'Приветствие с вопросом',
                'context': 'Использовать при ответе на приветствие, когда нужно показать интерес к собеседнику',
                'emotion': 'happy',
                'theme': 'greeting',
                'type': 'question',
                'keywords': 'привет, здравствуй, как дела, как жизнь, как настроение',
                'usage': 'Когда собеседник пишет "привет" или "здравствуй"'
            },

            'voice_answer_wellbeing': {
                'title': 'Ответ на вопрос о самочувствии',
                'context': 'Прямой ответ на вопрос "как дела?" или "как самочувствие?"',
                'emotion': 'happy',
                'theme': 'wellbeing',
                'type': 'answer',
                'keywords': 'отлично, хорошо, замечательно, прекрасно, супер, отлично',
                'usage': 'Когда спрашивают "как дела?" и действительно все хорошо'
            },

            'voice_gratitude_answer': {
                'title': 'Благодарность за внимание',
                'context': 'Ответ на проявление заботы, комплимент или помощь',
                'emotion': 'grateful',
                'theme': 'gratitude',
                'type': 'answer',
                'keywords': 'спасибо, благодарю, приятно, рада, приятно слышать',
                'usage': 'Когда собеседник проявляет заботу или делает комплимент'
            },

            'voice_story_food': {
                'title': 'Рассказ о готовке',
                'context': 'Рассказать о любимых блюдах или умении готовить',
                'emotion': 'happy',
                'theme': 'food',
                'type': 'story',
                'keywords': 'готовка, кухня, рецепт, люблю готовить, умею готовить',
                'usage': 'Когда разговор заходит о еде или кулинарии'
            },

            'voice_story_travel': {
                'title': 'Рассказ о путешествиях',
                'context': 'Поделиться впечатлениями от поездок или путешествий',
                'emotion': 'excited',
                'theme': 'travel',
                'type': 'story',
                'keywords': 'путешествие, поездка, отпуск, море, пляж, отель',
                'usage': 'Когда собеседник спрашивает о путешествиях'
            },

            'voice_statement_about_me': {
                'title': 'Рассказ о себе',
                'context': 'Кратко рассказать о себе, работе, увлечениях',
                'emotion': 'neutral',
                'theme': 'about_me',
                'type': 'statement',
                'keywords': 'работаю, занимаюсь, люблю, интересуюсь, увлекаюсь',
                'usage': 'Когда спрашивают "кем ты работаешь?" или "чем занимаешься?"'
            },

            # Шаблоны для фото/видео
            'photo_food': {
                'title': 'Фото еды',
                'context': 'Показать приготовленное блюдо или процесс готовки',
                'emotion': 'happy',
                'theme': 'food',
                'type': 'statement',
                'keywords': 'еда, блюдо, готовка, кухня, рецепт',
                'usage': 'Когда разговор заходит о еде'
            },

            'photo_travel': {
                'title': 'Фото из путешествия',
                'context': 'Показать красивые места, пейзажи из поездок',
                'emotion': 'excited',
                'theme': 'travel',
                'type': 'statement',
                'keywords': 'путешествие, поездка, отпуск, море, пляж, отель',
                'usage': 'Когда спрашивают о путешествиях'
            },

            'video_story': {
                'title': 'Видео история',
                'context': 'Показать короткую историю или момент из жизни',
                'emotion': 'happy',
                'theme': 'story',
                'type': 'statement',
                'keywords': 'видео, история, момент, жизнь',
                'usage': 'Когда нужно рассказать о чем-то визуально'
            }
        }

    def analyze_file_content(self, file_path: str) -> Dict[str, str]:
        """Анализирует содержимое файла на основе расширения и названия"""
        path_obj = Path(file_path)
        filename = path_obj.name.lower()

        analysis = {
            'file_type': path_obj.suffix[1:],  # убираем точку
            'suggested_template': 'voice_answer_wellbeing',  # по умолчанию
            'detected_content': '',
            'needs_manual_check': True
        }

        # Анализ голосовых файлов
        if analysis['file_type'] == 'ogg':
            analysis.update(self._analyze_voice_file(filename))

        # Анализ фото/видео
        elif analysis['file_type'] in ['jpg', 'png', 'mp4', 'mov']:
            analysis.update(self._analyze_visual_file(filename))

        return analysis

    def _analyze_voice_file(self, filename: str) -> Dict[str, str]:
        """Анализирует голосовой файл"""
        # Здесь будут эвристики на основе названий
        if any(word in filename for word in ['привет', 'здравствуй']):
            return {
                'suggested_template': 'voice_question_greeting',
                'detected_content': 'Приветствие с вопросом о самочувствии',
                'needs_manual_check': True
            }
        elif any(word in filename for word in ['спасибо', 'благодар']):
            return {
                'suggested_template': 'voice_gratitude_answer',
                'detected_content': 'Ответ с благодарностью',
                'needs_manual_check': True
            }
        elif any(word in filename for word in ['готов', 'кухн', 'рецепт']):
            return {
                'suggested_template': 'voice_story_food',
                'detected_content': 'Рассказ о готовке или еде',
                'needs_manual_check': True
            }
        elif any(word in filename for word in ['путешеств', 'поездк', 'отпуск']):
            return {
                'suggested_template': 'voice_story_travel',
                'detected_content': 'Рассказ о путешествии',
                'needs_manual_check': True
            }
        elif any(word in filename for word in ['работ', 'занима', 'люблю']):
            return {
                'suggested_template': 'voice_statement_about_me',
                'detected_content': 'Рассказ о себе',
                'needs_manual_check': True
            }
        else:
            return {
                'suggested_template': 'voice_answer_wellbeing',
                'detected_content': 'Не удалось определить содержимое автоматически',
                'needs_manual_check': True
            }

    def _analyze_visual_file(self, filename: str) -> Dict[str, str]:
        """Анализирует визуальный файл"""
        if any(word in filename for word in ['еда', 'блюдо', 'готовк', 'кухн']):
            return {
                'suggested_template': 'photo_food',
                'detected_content': 'Фото еды или процесса готовки',
                'needs_manual_check': True
            }
        elif any(word in filename for word in ['путешеств', 'поездк', 'отпуск', 'море', 'пляж']):
            return {
                'suggested_template': 'photo_travel',
                'detected_content': 'Фото из путешествия',
                'needs_manual_check': True
            }
        else:
            return {
                'suggested_template': 'video_story',
                'detected_content': 'Фото или видео',
                'needs_manual_check': True
            }

    def create_description_template(self, file_path: str, template_key: str = None) -> str:
        """Создает шаблон описания для файла"""
        path_obj = Path(file_path)

        # Автоматический выбор шаблона если не указан
        if not template_key:
            analysis = self.analyze_file_content(file_path)
            template_key = analysis['suggested_template']

        template = self.templates.get(template_key, self.templates['voice_answer_wellbeing'])

        description = f"""Название: {template['title']}
Контекст: {template['context']}
Эмоция: {template['emotion']}
Тема: {template['theme']}
Тип: {template['type']}
Ключевые слова: {template['keywords']}
Пример использования: {template['usage']}
Файл: {path_obj.name}
"""

        # Добавляем специальную секцию для ручного заполнения
        description += """
=== РУЧНОЕ ЗАПОЛНЕНИЕ ===

После прослушивания/просмотра файла укажите:
1. ТОЧНЫЙ текст (для голосовых)
2. Описание содержимого (для фото/видео)
3. Конкретный контекст использования
4. Дополнительные ключевые слова

ТОЧНЫЙ ТЕКСТ/СОДЕРЖИМОЕ:
[здесь напишите что именно говорится/показывается]

КОНКРЕТНЫЙ КОНТЕКСТ:
[в каких ситуациях использовать этот файл]

ДОПОЛНИТЕЛЬНЫЕ КЛЮЧЕВЫЕ СЛОВА:
[другие слова, по которым можно найти этот файл]
"""

        return description

    def create_batch_descriptions(self, file_paths: List[str], output_dir: str = "description_templates") -> None:
        """Создает шаблоны описаний для списка файлов"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)

        created_count = 0

        for file_path in file_paths:
            path_obj = Path(file_path)
            template_filename = f"{path_obj.stem}_template.txt"
            template_path = output_path / template_filename

            if template_path.exists():
                print(f"SKIP: Шаблон уже существует: {template_filename}")
                continue

            try:
                description = self.create_description_template(file_path)
                template_path.write_text(description, encoding='utf-8')
                created_count += 1
                print(f"CREATE: {template_filename}")
            except Exception as e:
                print(f"ERROR: Не удалось создать шаблон для {path_obj.name}: {e}")

        print(f"\nDONE: Создано {created_count} шаблонов описаний в папке {output_dir}")

    def create_descriptions_for_folder(self, folder_name: str, limit: int = None) -> None:
        """Создает шаблоны для всех файлов в папке"""
        folder_path = self.library_path / folder_name
        if not folder_path.exists():
            print(f"ERROR: Папка не существует: {folder_path}")
            return

        # Собираем файлы
        media_files = []
        for ext in ['*.ogg', '*.mp4', '*.jpg', '*.png']:
            media_files.extend(folder_path.glob(ext))

        if limit:
            media_files = media_files[:limit]

        print(f"Найдено {len(media_files)} файлов в папке {folder_name}")

        if not media_files:
            return

        # Создаем шаблоны
        output_dir = f"description_templates_{folder_name}"
        self.create_batch_descriptions([str(f) for f in media_files], output_dir)

    def interactive_description_creator(self) -> None:
        """Интерактивный режим создания описаний"""
        print("BULK DESCRIPTION CREATOR")
        print("=" * 40)
        print("Выберите режим:")
        print("1. Создать шаблоны для всех голосовых файлов")
        print("2. Создать шаблоны для всех фото/видео")
        print("3. Создать шаблон для конкретного файла")
        print("4. Показать доступные шаблоны")
        print("5. Выход")

        while True:
            try:
                choice = input("\nВыберите опцию (1-5): ").strip()

                if choice == '1':
                    limit = input("Сколько файлов обработать (Enter = все): ").strip()
                    limit = int(limit) if limit.isdigit() else None
                    self.create_descriptions_for_folder('voices', limit)

                elif choice == '2':
                    limit = input("Сколько файлов обработать (Enter = все): ").strip()
                    limit = int(limit) if limit.isdigit() else None
                    for folder in ['video', 'stickers']:
                        if (self.library_path / folder).exists():
                            self.create_descriptions_for_folder(folder, limit)

                elif choice == '3':
                    file_path = input("Введите путь к файлу: ").strip()
                    if file_path and Path(file_path).exists():
                        description = self.create_description_template(file_path)
                        print("\nШАБЛОН ОПИСАНИЯ:")
                        print("=" * 50)
                        print(description)
                        print("=" * 50)
                    else:
                        print("Файл не найден!")

                elif choice == '4':
                    print("\nДОСТУПНЫЕ ШАБЛОНЫ:")
                    for key, template in self.templates.items():
                        print(f"  {key}: {template['title']}")

                elif choice == '5':
                    break

                else:
                    print("Неверный выбор!")

            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Ошибка: {e}")

def main():
    """Основная функция"""
    import argparse

    parser = argparse.ArgumentParser(description="Массовое создание описаний медиафайлов")
    parser.add_argument('--voices', action='store_true',
                       help='Создать шаблоны для всех голосовых файлов')
    parser.add_argument('--visual', action='store_true',
                       help='Создать шаблоны для всех фото/видео файлов')
    parser.add_argument('--file', type=str,
                       help='Создать шаблон для конкретного файла')
    parser.add_argument('--limit', type=int,
                       help='Ограничить количество файлов')
    parser.add_argument('--interactive', action='store_true',
                       help='Интерактивный режим')

    args = parser.parse_args()

    creator = BulkDescriptionCreator()

    if args.interactive:
        creator.interactive_description_creator()
    elif args.voices:
        creator.create_descriptions_for_folder('voices', args.limit)
    elif args.visual:
        for folder in ['video', 'stickers']:
            if (creator.library_path / folder).exists():
                creator.create_descriptions_for_folder(folder, args.limit)
    elif args.file:
        if Path(args.file).exists():
            description = creator.create_description_template(args.file)
            print(description)
        else:
            print(f"Файл не найден: {args.file}")
    else:
        print("Используйте --help для списка опций или --interactive для интерактивного режима")
        print("\nПримеры:")
        print("  python bulk_description_creator.py --voices --limit 5")
        print("  python bulk_description_creator.py --interactive")

if __name__ == "__main__":
    main()

