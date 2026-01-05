#!/usr/bin/env python3
"""
Автоматическое улучшение медиафайлов: переименование + описания
"""

import os
import shutil
import json
from pathlib import Path
from typing import Dict, List, Optional

class AutoMediaImprover:
    """Автоматический улучшатель медиафайлов"""

    def __init__(self, user_id: int = 8412294171):
        self.user_id = user_id
        self.library_path = Path(f"library/{user_id}")
        self.analysis_file = "file_analysis_report.json"

        # Загружаем анализ если есть
        self.analysis_data = {}
        self._load_analysis()

    def _load_analysis(self) -> None:
        """Загружает данные анализа"""
        if Path(self.analysis_file).exists():
            try:
                with open(self.analysis_file, 'r', encoding='utf-8') as f:
                    self.analysis_data = json.load(f)
                print(f"LOAD: Загружен анализ {len(self.analysis_data)} файлов")
            except Exception as e:
                print(f"WARNING: Не удалось загрузить анализ: {e}")
                self.analysis_data = {}

    def run_full_improvement(self, max_files: int = 10) -> None:
        """Запускает полное улучшение для ограниченного количества файлов"""
        print("AUTO MEDIA IMPROVER")
        print("=" * 50)
        print(f"Будет обработано максимум {max_files} файлов из каждой категории")
        print()

        # 1. Анализируем файлы
        self._run_analysis()

        # 2. Автоматически переименовываем хорошие файлы
        self._auto_rename_good_files()

        # 3. Создаем шаблоны описаний
        self._create_description_templates(max_files)

        # 4. Показываем статистику
        self._show_improvement_stats()

        print("\nNEXT STEPS:")
        print("1. Просмотрите/прослушайте файлы и заполните шаблоны описаний")
        print("2. Используйте: python quick_description_filler.py --interactive")
        print("3. Проверьте работу: python test_strict_filtering.py")

    def _run_analysis(self) -> None:
        """Запускает анализ файлов"""
        print("STEP 1: Анализ файлов")
        if not self.analysis_data:
            print("Запускаю анализ файлов...")
            os.system("python analyze_current_files.py")
            self._load_analysis()  # Перезагружаем после анализа
        else:
            print("Анализ уже выполнен, пропускаю...")

    def _auto_rename_good_files(self) -> None:
        """Автоматически переименовывает файлы с высокой уверенностью"""
        print("\nSTEP 2: Автоматическое переименование")

        if not self.analysis_data:
            print("Нет данных анализа, пропускаю переименование")
            return

        good_files = []
        for file_path, analysis in self.analysis_data.items():
            # Переименовываем только файлы с уверенностью >80% и без проблем
            if analysis.get('confidence', 0) > 80 and not analysis.get('issues'):
                good_files.append(file_path)

        if not good_files:
            print("Нет файлов подходящих для автоматического переименования")
            return

        print(f"Найдено {len(good_files)} файлов для автоматического переименования")

        renamed_count = 0
        for file_path in good_files:
            if self._rename_file(file_path):
                renamed_count += 1

        print(f"Переименовано: {renamed_count}/{len(good_files)} файлов")

    def _rename_file(self, file_path: str) -> bool:
        """Переименовывает один файл"""
        if file_path not in self.analysis_data:
            return False

        analysis = self.analysis_data[file_path]
        old_path = Path(file_path)

        if not old_path.exists():
            return False

        # Создаем новое имя
        new_name = analysis['suggested_name'] + old_path.suffix
        new_path = old_path.parent / new_name

        # Проверяем, не существует ли уже
        if new_path.exists():
            return False

        try:
            # Создаем бэкап
            backup_path = old_path.parent / f"{old_path.stem}_backup{old_path.suffix}"
            if not backup_path.exists():
                shutil.copy2(str(old_path), str(backup_path))

            # Переименовываем
            shutil.move(str(old_path), str(new_path))

            # Обновляем данные анализа
            self.analysis_data[str(new_path)] = analysis
            self.analysis_data[str(new_path)]['original_name'] = new_name
            del self.analysis_data[file_path]

            return True
        except Exception as e:
            print(f"ERROR renaming {old_path.name}: {e}")
            return False

    def _create_description_templates(self, max_files: int) -> None:
        """Создает шаблоны описаний для файлов"""
        print(f"\nSTEP 3: Создание шаблонов описаний (макс {max_files} на категорию)")

        folders = ['voices', 'video', 'stickers']
        total_created = 0

        for folder in folders:
            folder_path = self.library_path / folder
            if not folder_path.exists():
                continue

            # Собираем файлы без описаний
            files_without_desc = []
            for ext in ['*.ogg', '*.mp4', '*.jpg', '*.png']:
                for media_file in folder_path.glob(ext):
                    desc_file = media_file.parent / f"{media_file.stem}.txt"
                    if not desc_file.exists():
                        files_without_desc.append(media_file)

            # Ограничиваем количество
            files_without_desc = files_without_desc[:max_files]

            if not files_without_desc:
                continue

            print(f"  {folder}: {len(files_without_desc)} файлов")

            # Создаем шаблоны
            output_dir = f"description_templates_{folder}"
            os.makedirs(output_dir, exist_ok=True)

            created_for_folder = 0
            for media_file in files_without_desc:
                template_file = Path(output_dir) / f"{media_file.stem}_template.txt"

                if template_file.exists():
                    continue

                try:
                    # Создаем простой шаблон
                    template_content = f"""Название: {media_file.stem}
Контекст: Автоматически созданное описание - нужно заполнить вручную
Эмоция: neutral
Тема: unknown
Тип: statement
Ключевые слова: {media_file.stem.replace('_', ', ')}
Пример использования: Когда подходит по описанию

=== РУЧНОЕ ЗАПОЛНЕНИЕ ===

После прослушивания/просмотра файла заполните:
1. ТОЧНЫЙ текст или описание содержимого
2. Конкретный контекст использования
3. Правильные эмоция/тема/тип
4. Ключевые слова

ТОЧНЫЙ ТЕКСТ/СОДЕРЖИМОЕ:
[здесь опишите что слышно/видно в файле]

КОНКРЕТНЫЙ КОНТЕКСТ:
[в каких ситуациях использовать этот файл]

ПРАВИЛЬНЫЕ ПАРАМЕТРЫ:
Эмоция: [happy/sad/neutral/excited/grateful]
Тема: [greeting/wellbeing/about_me/food/travel]
Тип: [question/answer/statement/story]
"""

                    template_file.write_text(template_content, encoding='utf-8')
                    created_for_folder += 1

                except Exception as e:
                    print(f"    ERROR creating template for {media_file.name}: {e}")

            print(f"    Создано шаблонов: {created_for_folder}")
            total_created += created_for_folder

        print(f"Всего создано шаблонов: {total_created}")

    def _show_improvement_stats(self) -> None:
        """Показывает статистику улучшений"""
        print("\nSTEP 4: Статистика улучшений")

        folders = ['voices', 'video', 'stickers']
        total_files = 0
        total_renamed = 0
        total_templates = 0

        for folder in folders:
            folder_path = self.library_path / folder
            if not folder_path.exists():
                continue

            files_count = 0
            renamed_count = 0
            templates_count = 0

            for ext in ['*.ogg', '*.mp4', '*.jpg', '*.png']:
                for media_file in folder_path.glob(ext):
                    files_count += 1

                    # Проверяем, переименован ли файл (содержит ли стандартный формат)
                    if any(media_file.name.startswith(prefix) for prefix in
                          ['happy_', 'sad_', 'neutral_', 'excited_', 'grateful_']):
                        renamed_count += 1

                    # Проверяем наличие шаблона описания
                    template_dir = Path(f"description_templates_{folder}")
                    template_file = template_dir / f"{media_file.stem}_template.txt"
                    if template_file.exists():
                        templates_count += 1

            if files_count > 0:
                print(f"  {folder}:")
                print(f"    Всего файлов: {files_count}")
                print(f"    Переименовано: {renamed_count} ({renamed_count/files_count*100:.1f}%)")
                print(f"    Шаблонов: {templates_count}")

                total_files += files_count
                total_renamed += renamed_count
                total_templates += templates_count

        if total_files > 0:
            print(f"\n  ОБЩАЯ СТАТИСТИКА:")
            print(f"    Всего файлов: {total_files}")
            print(f"    Переименовано: {total_renamed} ({total_renamed/total_files*100:.1f}%)")
            print(f"    Шаблонов описаний: {total_templates}")

    def cleanup_backups(self) -> None:
        """Удаляет резервные копии файлов"""
        print("CLEANUP: Удаление резервных копий")

        folders = ['voices', 'video', 'stickers']
        deleted_count = 0

        for folder in folders:
            folder_path = self.library_path / folder
            if not folder_path.exists():
                continue

            for file_path in folder_path.glob("*_backup.*"):
                try:
                    file_path.unlink()
                    deleted_count += 1
                    print(f"  DELETE: {file_path.name}")
                except Exception as e:
                    print(f"  ERROR deleting {file_path.name}: {e}")

        print(f"Удалено резервных копий: {deleted_count}")

def main():
    """Основная функция"""
    import argparse

    parser = argparse.ArgumentParser(description="Автоматическое улучшение медиафайлов")
    parser.add_argument('--full', action='store_true',
                       help='Полное автоматическое улучшение')
    parser.add_argument('--max-files', type=int, default=10,
                       help='Максимум файлов для обработки (по умолчанию: 10)')
    parser.add_argument('--cleanup', action='store_true',
                       help='Удалить резервные копии файлов')
    parser.add_argument('--stats', action='store_true',
                       help='Показать статистику улучшений')

    args = parser.parse_args()

    improver = AutoMediaImprover()

    if args.cleanup:
        improver.cleanup_backups()
    elif args.stats:
        improver._show_improvement_stats()
    elif args.full:
        improver.run_full_improvement(args.max_files)
    else:
        print("AUTO MEDIA IMPROVER")
        print("=" * 50)
        print("Автоматическое улучшение медиафайлов")
        print("\nИспользуйте --help для опций")
        print("\nПримеры:")
        print("  python auto_improve_media.py --full --max-files 20")
        print("  python auto_improve_media.py --stats")
        print("  python auto_improve_media.py --cleanup")

if __name__ == "__main__":
    main()
