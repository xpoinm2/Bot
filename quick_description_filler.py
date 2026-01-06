#!/usr/bin/env python3
"""
Быстрое заполнение описаний медиафайлов
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional

class QuickDescriptionFiller:
    """Инструмент для быстрого заполнения описаний"""

    def __init__(self, user_id: int = 8412294171):
        self.user_id = user_id
        self.library_path = Path(f"library/{user_id}")

    def get_files_without_descriptions(self, folder_name: str) -> List[Path]:
        """Получает список файлов без описаний"""
        folder_path = self.library_path / folder_name
        if not folder_path.exists():
            return []

        files_without_desc = []

        for ext in ['*.ogg', '*.mp4', '*.jpg', '*.png']:
            for media_file in folder_path.glob(ext):
                desc_file = media_file.parent / f"{media_file.stem}.txt"
                if not desc_file.exists():
                    files_without_desc.append(media_file)

        return files_without_desc

    def create_quick_description(self, file_path: str, content_description: str,
                               context: str = "", keywords: str = "") -> bool:
        """Создает быстрое описание файла"""
        path_obj = Path(file_path)
        desc_file = path_obj.parent / f"{path_obj.stem}.txt"

        # Определяем базовые параметры по типу файла
        if path_obj.suffix == '.ogg':
            emotion = 'neutral'
            theme = 'unknown'
            desc_type = 'statement'
        elif path_obj.suffix in ['.jpg', '.png']:
            emotion = 'neutral'
            theme = 'unknown'
            desc_type = 'statement'
        elif path_obj.suffix in ['.mp4', '.mov']:
            emotion = 'neutral'
            theme = 'unknown'
            desc_type = 'statement'
        else:
            emotion = 'neutral'
            theme = 'unknown'
            desc_type = 'statement'

        description = f"""Название: {content_description}
Контекст: {context if context else 'Автоматически созданное описание'}
Эмоция: {emotion}
Тема: {theme}
Тип: {desc_type}
Ключевые слова: {keywords if keywords else content_description.replace(' ', ', ')}
Пример использования: Когда подходит по описанию
"""

        try:
            desc_file.write_text(description, encoding='utf-8')
            return True
        except Exception as e:
            print(f"ERROR: Не удалось создать описание: {e}")
            return False

    def batch_quick_fill(self, folder_name: str) -> None:
        """Пакетное быстрое заполнение описаний"""
        files = self.get_files_without_descriptions(folder_name)

        if not files:
            print(f"Все файлы в папке {folder_name} уже имеют описания!")
            return

        print(f"Найдено {len(files)} файлов без описаний в папке {folder_name}")
        print("\nДля каждого файла введите краткое описание содержимого.")
        print("Примеры:")
        print("- Голосовые: 'Привет, как дела?'")
        print("- Фото: 'Мое фото с пляжа'")
        print("- Видео: 'Видео приготовления пасты'")
        print("\nНажмите Enter для пропуска файла")

        processed_count = 0

        for i, file_path in enumerate(files, 1):
            print(f"\n[{i}/{len(files)}] {file_path.name}")

            # Предлагаем шаблон на основе названия файла
            suggestion = self._suggest_description(file_path.name)
            if suggestion:
                print(f"Подсказка: {suggestion}")

            description = input("Описание: ").strip()

            if not description:
                print("SKIP: Пропущено")
                continue

            # Запрашиваем дополнительную информацию
            context = input("Контекст использования (опционально): ").strip()
            keywords = input("Ключевые слова (опционально): ").strip()

            if self.create_quick_description(str(file_path), description, context, keywords):
                processed_count += 1
                print("OK: Описание создано")
            else:
                print("ERROR: Не удалось создать описание")

        print(f"\nDONE: Создано {processed_count} описаний из {len(files)} файлов")

    def _suggest_description(self, filename: str) -> str:
        """Предлагает описание на основе названия файла"""
        filename_lower = filename.lower()

        suggestions = {
            'привет': 'Приветствие с вопросом о самочувствии',
            'здравствуй': 'Приветствие с вопросом о самочувствии',
            'спасибо': 'Благодарность за помощь',
            'как дела': 'Вопрос о самочувствии',
            'как самочувствие': 'Вопрос о самочувствии',
            'хорошо': 'Положительный ответ на вопрос о самочувствии',
            'отлично': 'Положительный ответ на вопрос о самочувствии',
            'замечательно': 'Положительный ответ на вопрос о самочувствии',
            'еда': 'Фото приготовленной еды',
            'блюдо': 'Фото блюда',
            'море': 'Фото с моря или пляжа',
            'пляж': 'Фото с пляжа',
            'путешествие': 'Фото из путешествия',
            'поездка': 'Фото из поездки',
            'готовк': 'Процесс приготовления еды',
            'кухн': 'В кухне за приготовлением'
        }

        for key, suggestion in suggestions.items():
            if key in filename_lower:
                return suggestion

        return ""

    def show_statistics(self) -> None:
        """Показывает статистику по описаниям"""
        folders = ['voices', 'video', 'stickers', 'pastes']

        print("STATISTICS: Состояние описаний файлов")
        print("=" * 50)

        total_files = 0
        total_descriptions = 0

        for folder in folders:
            folder_path = self.library_path / folder
            if not folder_path.exists():
                continue

            files_count = 0
            descriptions_count = 0

            for ext in ['*.ogg', '*.mp4', '*.jpg', '*.png']:
                for media_file in folder_path.glob(ext):
                    files_count += 1
                    desc_file = media_file.parent / f"{media_file.stem}.txt"
                    if desc_file.exists():
                        descriptions_count += 1

            if files_count > 0:
                percentage = (descriptions_count / files_count) * 100
                status = "GOOD" if percentage >= 80 else "NEED WORK" if percentage >= 50 else "URGENT"
                print("15")

                total_files += files_count
                total_descriptions += descriptions_count

        if total_files > 0:
            total_percentage = (total_descriptions / total_files) * 100
            print("15"
    def export_descriptions_to_json(self, output_file: str = "media_descriptions.json") -> None:
        """Экспортирует все описания в JSON файл"""
        descriptions = {}

        folders = ['voices', 'video', 'stickers', 'pastes']

        for folder in folders:
            folder_path = self.library_path / folder
            if not folder_path.exists():
                continue

            folder_descriptions = {}

            for ext in ['*.ogg', '*.mp4', '*.jpg', '*.png']:
                for media_file in folder_path.glob(ext):
                    desc_file = media_file.parent / f"{media_file.stem}.txt"

                    if desc_file.exists():
                        try:
                            content = desc_file.read_text(encoding='utf-8')
                            folder_descriptions[media_file.name] = {
                                'description_file': str(desc_file),
                                'content': content,
                                'size': media_file.stat().st_size,
                                'modified': media_file.stat().st_mtime
                            }
                        except Exception as e:
                            print(f"ERROR reading {desc_file}: {e}")

            if folder_descriptions:
                descriptions[folder] = folder_descriptions

        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(descriptions, f, ensure_ascii=False, indent=2)
            print(f"EXPORT: Описания экспортированы в {output_file}")
        except Exception as e:
            print(f"ERROR: Не удалось экспортировать: {e}")

    def interactive_mode(self) -> None:
        """Интерактивный режим заполнения описаний"""
        print("QUICK DESCRIPTION FILLER")
        print("=" * 40)
        print("Быстрое создание описаний для медиафайлов")
        print("\nВыберите действие:")
        print("1. Заполнить описания для голосовых файлов")
        print("2. Заполнить описания для фото/видео файлов")
        print("3. Показать статистику")
        print("4. Экспортировать описания в JSON")
        print("5. Выход")

        while True:
            try:
                choice = input("\nВыберите опцию (1-5): ").strip()

                if choice == '1':
                    self.batch_quick_fill('voices')

                elif choice == '2':
                    for folder in ['video', 'stickers']:
                        if (self.library_path / folder).exists():
                            self.batch_quick_fill(folder)

                elif choice == '3':
                    self.show_statistics()

                elif choice == '4':
                    filename = input("Имя файла для экспорта (Enter = media_descriptions.json): ").strip()
                    filename = filename if filename else "media_descriptions.json"
                    self.export_descriptions_to_json(filename)

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

    parser = argparse.ArgumentParser(description="Быстрое заполнение описаний медиафайлов")
    parser.add_argument('--voices', action='store_true',
                       help='Заполнить описания для голосовых файлов')
    parser.add_argument('--visual', action='store_true',
                       help='Заполнить описания для фото/видео файлов')
    parser.add_argument('--stats', action='store_true',
                       help='Показать статистику описаний')
    parser.add_argument('--export', type=str, nargs='?', const='media_descriptions.json',
                       help='Экспортировать описания в JSON файл')
    parser.add_argument('--interactive', action='store_true',
                       help='Интерактивный режим')

    args = parser.parse_args()

    filler = QuickDescriptionFiller()

    if args.interactive:
        filler.interactive_mode()
    elif args.voices:
        filler.batch_quick_fill('voices')
    elif args.visual:
        for folder in ['video', 'stickers']:
            if (filler.library_path / folder).exists():
                filler.batch_quick_fill(folder)
    elif args.stats:
        filler.show_statistics()
    elif args.export:
        filler.export_descriptions_to_json(args.export)
    else:
        print("Используйте --help для списка опций или --interactive для интерактивного режима")
        print("\nПримеры:")
        print("  python quick_description_filler.py --voices")
        print("  python quick_description_filler.py --stats")
        print("  python quick_description_filler.py --interactive")

if __name__ == "__main__":
    main()

