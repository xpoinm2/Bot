#!/usr/bin/env python3
"""
Интерактивное переименование медиафайлов
"""

import os
import shutil
import json
from pathlib import Path
from typing import Dict, List, Optional

class FileRenamer:
    """Интерактивный инструмент для переименования медиафайлов"""

    def __init__(self, analysis_file: str = "file_analysis_report.json"):
        self.analysis_file = analysis_file
        self.analysis_data = {}
        self.load_analysis()

    def load_analysis(self):
        """Загружает данные анализа"""
        try:
            with open(self.analysis_file, 'r', encoding='utf-8') as f:
                self.analysis_data = json.load(f)
            print(f"✅ Загружен анализ {len(self.analysis_data)} файлов")
        except FileNotFoundError:
            print(f"❌ Файл анализа не найден: {self.analysis_file}")
            print("Запустите сначала: python analyze_current_files.py")
            exit(1)

    def show_file_info(self, file_path: str) -> None:
        """Показывает информацию о файле"""
        if file_path not in self.analysis_data:
            print(f"❌ Файл не найден в анализе: {file_path}")
            return

        analysis = self.analysis_data[file_path]
        print(f"\n📁 Файл: {analysis['original_name']}")
        print(f"📂 Папка: {analysis['folder']}")
        print(f"🎭 Эмоция: {analysis['detected_emotion']}")
        print(f"📋 Тема: {analysis['detected_theme']}")
        print(f"💬 Тип: {analysis['detected_type']}")
        print(f"📊 Уверенность: {analysis['confidence']}%")

        print(f"\n💡 Предлагаемое имя: {analysis['suggested_name']} ")

        if analysis.get('issues'):
            print(f"\n⚠️ Проблемы:")
            for issue in analysis['issues']:
                print(f"   • {issue}")

    def rename_file(self, file_path: str, new_name: str, create_backup: bool = True) -> bool:
        """Переименовывает файл"""
        if file_path not in self.analysis_data:
            print(f"❌ Файл не найден в анализе: {file_path}")
            return False

        old_path = Path(file_path)
        if not old_path.exists():
            print(f"❌ Файл не существует: {file_path}")
            return False

        # Добавляем расширение если его нет
        if not new_name.endswith(old_path.suffix):
            new_name += old_path.suffix

        new_path = old_path.parent / new_name

        # Проверяем, не существует ли уже файл с таким именем
        if new_path.exists():
            print(f"⚠️ Файл уже существует: {new_path}")
            overwrite = input("Перезаписать? (y/N): ").lower().strip()
            if overwrite != 'y':
                return False

        try:
            # Создаем бэкап если нужно
            if create_backup and old_path.exists():
                backup_path = old_path.parent / f"{old_path.stem}_backup{old_path.suffix}"
                shutil.copy2(str(old_path), str(backup_path))
                print(f"📋 Создан бэкап: {backup_path.name}")

            # Переименовываем
            shutil.move(str(old_path), str(new_path))
            print(f"✅ Переименовано: {old_path.name} → {new_path.name}")

            # Обновляем данные анализа
            self.analysis_data[str(new_path)] = self.analysis_data[file_path]
            self.analysis_data[str(new_path)]['original_name'] = new_name
            del self.analysis_data[file_path]

            return True

        except Exception as e:
            print(f"❌ Ошибка переименования: {e}")
            return False

    def auto_rename_good_files(self, min_confidence: int = 70) -> None:
        """Автоматически переименовывает файлы с высокой уверенностью"""
        good_files = []
        for file_path, analysis in self.analysis_data.items():
            if analysis['confidence'] >= min_confidence and not analysis.get('issues'):
                good_files.append(file_path)

        if not good_files:
            print(f"❌ Нет файлов с уверенностью ≥ {min_confidence}%")
            return

        print(f"🤖 Найдено {len(good_files)} файлов для автоматического переименования")
        confirm = input("Продолжить? (y/N): ").lower().strip()

        if confirm != 'y':
            return

        renamed_count = 0
        for file_path in good_files:
            analysis = self.analysis_data[file_path]
            new_name = analysis['suggested_name']
            if self.rename_file(file_path, new_name, create_backup=True):
                renamed_count += 1

        print(f"✅ Автоматически переименовано: {renamed_count}/{len(good_files)} файлов")

    def interactive_rename(self) -> None:
        """Интерактивное переименование"""
        files_list = list(self.analysis_data.keys())

        if not files_list:
            print("❌ Нет файлов для переименования")
            return

        print(f"\n🎯 Интерактивное переименование ({len(files_list)} файлов)")
        print("Команды:")
        print("  'list' - показать все файлы")
        print("  'auto' - автоматическое переименование хороших файлов")
        print("  'skip' - пропустить файл")
        print("  'quit' - выход")
        print("  или введите новый имя файла")

        current_index = 0

        while current_index < len(files_list):
            file_path = files_list[current_index]
            analysis = self.analysis_data[file_path]

            print(f"\n{'='*50}")
            print(f"Файл {current_index + 1}/{len(files_list)}")
            self.show_file_info(file_path)

            while True:
                choice = input("\nВыберите действие: ").strip()

                if choice.lower() in ['q', 'quit', 'exit']:
                    return
                elif choice.lower() == 'list':
                    print("\n📋 Список файлов:")
                    for i, fp in enumerate(files_list, 1):
                        status = "✅" if self.analysis_data[fp]['confidence'] >= 70 else "⚠️"
                        print(f"  {i}. {status} {Path(fp).name}")
                    continue
                elif choice.lower() == 'auto':
                    self.auto_rename_good_files()
                    continue
                elif choice.lower() == 'skip':
                    break
                elif choice:
                    # Пользователь ввел новое имя
                    if self.rename_file(file_path, choice):
                        break
                    else:
                        continue
                else:
                    print("❌ Введите команду или новое имя файла")

            current_index += 1

        print("\n🎉 Интерактивное переименование завершено!")

    def create_description_files(self) -> None:
        """Создает файлы описаний для всех медиафайлов"""
        descriptions_created = 0

        for file_path, analysis in self.analysis_data.items():
            path_obj = Path(file_path)
            desc_file = path_obj.parent / f"{path_obj.stem}.txt"

            if desc_file.exists():
                continue

            # Создаем базовое описание
            description = f"""Название: {analysis['original_name']}
Контекст: {self._get_context_description(analysis)}
Эмоция: {analysis['detected_emotion']}
Тема: {analysis['detected_theme']}
Тип: {analysis['detected_type']}
Ключевые слова: {self._get_keywords(analysis)}
"""

            try:
                with open(desc_file, 'w', encoding='utf-8') as f:
                    f.write(description)
                descriptions_created += 1
                print(f"📝 Создано описание: {desc_file.name}")
            except Exception as e:
                print(f"❌ Ошибка создания описания для {path_obj.name}: {e}")

        print(f"✅ Создано описаний: {descriptions_created}")

    def _get_context_description(self, analysis: Dict) -> str:
        """Генерирует описание контекста использования файла"""
        emotion = analysis['detected_emotion']
        theme = analysis['detected_theme']
        content_type = analysis['detected_type']

        context_map = {
            ('question', 'greeting'): "Приветствие с вопросом о самочувствии",
            ('question', 'wellbeing'): "Вопрос о самочувствии или делах",
            ('answer', 'wellbeing'): "Ответ на вопрос о самочувствии",
            ('gratitude', 'gratitude'): "Благодарность за помощь или внимание",
            ('statement', 'about_me'): "Рассказ о себе, увлечениях или работе",
            ('story', 'food'): "Рассказ о готовке или любимой еде",
            ('story', 'travel'): "Рассказ о путешествиях или поездках"
        }

        key = (content_type, theme)
        return context_map.get(key, f"Контент на тему {theme} с эмоциональным окрасом {emotion}")

    def _get_keywords(self, analysis: Dict) -> str:
        """Генерирует ключевые слова для файла"""
        original = analysis['original_name'].lower()
        words = []

        # Извлекаем значимые слова из оригинального имени
        for word in original.replace('_', ' ').replace('-', ' ').split():
            word = word.strip()
            if len(word) > 3 and not word.endswith(('.ogg', '.mp4', '.jpg', '.png')):
                words.append(word)

        # Добавляем тематические ключевые слова
        theme_keywords = {
            'greeting': ['привет', 'здравствуй', 'добрый'],
            'wellbeing': ['дела', 'самочувствие', 'настроение', 'хорошо', 'отлично'],
            'gratitude': ['спасибо', 'благодарность', 'спс'],
            'food': ['еда', 'готовка', 'кухня', 'рецепт'],
            'travel': ['путешествие', 'поездка', 'отпуск']
        }

        if analysis['detected_theme'] in theme_keywords:
            words.extend(theme_keywords[analysis['detected_theme']])

        return ', '.join(set(words))

def main():
    """Основная функция"""
    import argparse

    parser = argparse.ArgumentParser(description="Инструмент переименования медиафайлов")
    parser.add_argument('--analysis-file', default='file_analysis_report.json',
                       help='Файл с анализом (по умолчанию: file_analysis_report.json)')
    parser.add_argument('--auto', action='store_true',
                       help='Автоматическое переименование хороших файлов')
    parser.add_argument('--create-descriptions', action='store_true',
                       help='Создать файлы описаний для всех файлов')
    parser.add_argument('--interactive', action='store_true',
                       help='Интерактивный режим переименования')

    args = parser.parse_args()

    renamer = FileRenamer(args.analysis_file)

    if args.create_descriptions:
        print("📝 Создание файлов описаний...")
        renamer.create_description_files()
    elif args.auto:
        print("🤖 Автоматическое переименование...")
        renamer.auto_rename_good_files()
    elif args.interactive:
        renamer.interactive_rename()
    else:
        print("🎯 Запуск интерактивного режима...")
        print("Используйте --help для списка опций")
        renamer.interactive_rename()

if __name__ == "__main__":
    main()

