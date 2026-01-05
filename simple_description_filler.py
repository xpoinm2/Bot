#!/usr/bin/env python3
"""
Упрощенное заполнение описаний: только голосовые файлы
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional

class SimpleDescriptionFiller:
    """Упрощенный инструмент для заполнения описаний голосовых файлов"""

    def __init__(self, user_id: int = 8412294171):
        self.user_id = user_id
        self.library_path = Path(f"library/{user_id}")

    def run_interactive_filler(self) -> None:
        """Интерактивное заполнение описаний"""
        print("🎵 ЗАПОЛНЕНИЕ ОПИСАНИЙ ГОЛОСОВЫХ ФАЙЛОВ")
        print("=" * 50)
        print("Выберите что заполнять:")
        print("1. Голосовые файлы")
        print("2. Показать статистику")
        print("3. Выход")

        while True:
            try:
                choice = input("\nВыберите опцию (1-5): ").strip()

                if choice == '1':
                    self._fill_voices_interactive()
                elif choice == '2':
                    self._show_stats()
                elif choice == '3':
                    break
                else:
                    print("Неверный выбор!")

            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Ошибка: {e}")

    def _fill_voices_interactive(self) -> None:
        """Интерактивное заполнение описаний голосовых файлов"""
        print("\n🎤 ЗАПОЛНЕНИЕ ГОЛОСОВЫХ ФАЙЛОВ")

        voices_without_desc = self._get_files_without_descriptions("voices", "*.ogg")

        if not voices_without_desc:
            print("✅ Все голосовые файлы уже имеют описания!")
            return

        print(f"Найдено {len(voices_without_desc)} файлов без описаний")
        print("\nДля каждого файла:")
        print("1. Прослушайте файл")
        print("2. Введите точный текст что говорится")
        print("3. Укажите эмоцию и контекст")
        print("\nНажмите Enter для пропуска файла")

        processed_count = 0

        for i, voice_file in enumerate(voices_without_desc, 1):
            print(f"\n[{i}/{len(voices_without_desc)}] 🎤 {voice_file.name}")

            # Показать текущее описание если есть
            desc_file = voice_file.parent / f"{voice_file.stem}.txt"
            if desc_file.exists():
                try:
                    current_desc = desc_file.read_text(encoding='utf-8')
                    if "ТОЧНЫЙ ТЕКСТ:" in current_desc:
                        print("Текущее описание:")
                        lines = current_desc.split('\n')
                        for line in lines:
                            if line.startswith("ТОЧНЫЙ ТЕКСТ:") and len(line) > 15:
                                print(f"  {line}")
                                break
                except:
                    pass

            # Запросить данные
            text = input("ТОЧНЫЙ текст (что говорится): ").strip()
            if not text:
                print("⏭️ Пропущено")
                continue

            emotion = self._choose_emotion()
            theme = self._choose_theme()
            desc_type = self._choose_type()
            context = input("Контекст использования: ").strip()

            # Создать полное описание
            description = f"""Название: {text[:50]}{'...' if len(text) > 50 else ''}
Контекст: {context if context else 'Голосовое сообщение'}
Эмоция: {emotion}
Тема: {theme}
Тип: {desc_type}
Ключевые слова: {text.replace(' ', ', ').lower()[:100]}
Пример использования: {context if context else 'Когда подходит по контексту разговора'}
"""

            try:
                desc_file.write_text(description, encoding='utf-8')
                processed_count += 1
                print("✅ Описание сохранено")
            except Exception as e:
                print(f"❌ Ошибка сохранения: {e}")

        print(f"\n✅ Заполнено описаний: {processed_count}")


    def _choose_emotion(self) -> str:
        """Выбор эмоции"""
        emotions = {
            '1': 'happy',
            '2': 'sad',
            '3': 'neutral',
            '4': 'excited',
            '5': 'grateful',
            '6': 'sympathetic'
        }

        while True:
            print("Эмоция:")
            print("1. happy - радостный")
            print("2. sad - грустный")
            print("3. neutral - нейтральный")
            print("4. excited - восторженный")
            print("5. grateful - благодарный")
            print("6. sympathetic - сочувствующий")

            choice = input("Выберите (1-6) [3]: ").strip()
            if not choice:
                return 'neutral'
            if choice in emotions:
                return emotions[choice]

    def _choose_theme(self) -> str:
        """Выбор темы"""
        themes = {
            '1': 'greeting',
            '2': 'wellbeing',
            '3': 'about_me',
            '4': 'food',
            '5': 'travel',
            '6': 'work',
            '7': 'gratitude'
        }

        while True:
            print("Тема:")
            print("1. greeting - приветствие")
            print("2. wellbeing - самочувствие")
            print("3. about_me - о себе")
            print("4. food - еда")
            print("5. travel - путешествия")
            print("6. work - работа")
            print("7. gratitude - благодарность")

            choice = input("Выберите (1-7) [2]: ").strip()
            if not choice:
                return 'wellbeing'
            if choice in themes:
                return themes[choice]

    def _choose_type(self) -> str:
        """Выбор типа"""
        types = {
            '1': 'question',
            '2': 'answer',
            '3': 'statement',
            '4': 'story',
            '5': 'compliment',
            '6': 'gratitude'
        }

        while True:
            print("Тип:")
            print("1. question - вопрос")
            print("2. answer - ответ")
            print("3. statement - утверждение")
            print("4. story - рассказ")
            print("5. compliment - комплимент")
            print("6. gratitude - благодарность")

            choice = input("Выберите (1-6) [3]: ").strip()
            if not choice:
                return 'statement'
            if choice in types:
                return types[choice]

    def _get_files_without_descriptions(self, folder_name: str, pattern: str) -> List[Path]:
        """Получает файлы без описаний"""
        folder_path = self.library_path / folder_name
        if not folder_path.exists():
            return []

        files_without_desc = []

        for file_path in folder_path.glob(pattern):
            desc_file = file_path.parent / f"{file_path.stem}.txt"
            if not desc_file.exists():
                files_without_desc.append(file_path)

        return files_without_desc

    def _show_stats(self) -> None:
        """Показывает статистику"""
        print("\n📊 СТАТИСТИКА ГОТОВНОСТИ:")

        # Голосовые
        voices_path = self.library_path / "voices"
        if voices_path.exists():
            voice_files = list(voices_path.glob("*.ogg"))
            voice_descs = 0
            for vf in voice_files:
                desc_file = vf.parent / f"{vf.stem}.txt"
                if desc_file.exists():
                    try:
                        content = desc_file.read_text(encoding='utf-8')
                        # Проверяем что описание заполнено (не содержит шаблон)
                        if "ТОЧНЫЙ ТЕКСТ:" not in content and "РУЧНОЕ ЗАПОЛНЕНИЕ" not in content:
                            voice_descs += 1
                    except:
                        pass

            voice_percent = (voice_descs / len(voice_files) * 100) if voice_files else 0
            print(".1f")

        print("💡 Пасты: исключены из рекомендаций")

def main():
    """Основная функция"""
    import argparse

    parser = argparse.ArgumentParser(description="Упрощенное заполнение описаний голосовых файлов")
    parser.add_argument('--stats', action='store_true',
                       help='Показать статистику готовности')
    parser.add_argument('--voices', action='store_true',
                       help='Заполнить только голосовые')
    parser.add_argument('--interactive', action='store_true',
                       help='Интерактивный режим')

    args = parser.parse_args()

    filler = SimpleDescriptionFiller()

    if args.stats:
        filler._show_stats()
    elif args.voices:
        filler._fill_voices_interactive()
    elif args.interactive:
        filler.run_interactive_filler()
    else:
        print("Запуск интерактивного режима...")
        filler.run_interactive_filler()

if __name__ == "__main__":
    main()
