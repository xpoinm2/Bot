#!/usr/bin/env python3
"""
Упрощенное улучшение медиа: только голосовые файлы
"""

import os
import shutil
import json
from pathlib import Path
from typing import Dict, List, Optional

class SimpleMediaImprover:
    """Упрощенный улучшатель только для голосовых файлов"""

    def __init__(self, user_id: int = 8412294171):
        self.user_id = user_id
        self.library_path = Path(f"library/{user_id}")

    def run_simple_improvement(self, max_files: int = 20) -> None:
        """Запускает упрощенное улучшение только для голосовых файлов"""
        print("🎵 УПРОЩЕННОЕ УЛУЧШЕНИЕ ГОЛОСОВЫХ ФАЙЛОВ")
        print("=" * 50)
        print(f"Будет обработано максимум {max_files} голосовых файлов")
        print("Фото/видео/пасты пропускаются (названия понятны или не рекомендуются)")
        print()

        # 1. Создать описания для голосовых
        self._create_voice_descriptions(max_files)

        # 2. Показать статистику
        self._show_simple_stats()

        print("\n✅ ГОТОВО!")
        print("\n📝 Заполните описания:")
        print("python simple_description_filler.py --voices")
        print("\n🔍 Проверьте результат:")
        print("python simple_description_filler.py --stats")

    def _create_voice_descriptions(self, max_files: int) -> None:
        """Создает описания для голосовых файлов"""
        print("🎤 Создание описаний для голосовых файлов...")

        voices_path = self.library_path / "voices"
        if not voices_path.exists():
            print("❌ Папка voices не найдена")
            return

        # Получить все .ogg файлы
        voice_files = list(voices_path.glob("*.ogg"))[:max_files]
        created_count = 0

        for voice_file in voice_files:
            desc_file = voice_file.parent / f"{voice_file.stem}.txt"

            if desc_file.exists():
                continue

            # Создать базовое описание
            description = f"""Название: {voice_file.stem}
Контекст: Автоматически созданное описание - нужно прослушать и заполнить
Эмоция: neutral
Тема: unknown
Тип: statement
Ключевые слова: {voice_file.stem.replace('_', ', ')}
Пример использования: Когда подходит по описанию

=== РУЧНОЕ ЗАПОЛНЕНИЕ ===

После ПРОСЛУШИВАНИЯ файла заполните:
1. ТОЧНЫЙ текст что говорится (обязательно!)
2. Эмоция говорящего: happy/sad/neutral/excited/grateful/sympathetic
3. Тема разговора: greeting/wellbeing/about_me/food/travel/work/gratitude
4. Тип: question/answer/statement/story/compliment
5. Конкретный контекст использования

ПРИМЕРЫ:
- Если файл содержит вопрос "как дела?": Тип = question, Тема = wellbeing
- Если файл содержит ответ "хорошо, спасибо": Тип = answer, Тема = wellbeing
- Если файл содержит рассказ "я работаю в IT": Тип = statement, Тема = about_me

ТОЧНЫЙ ТЕКСТ:
[здесь напишите что именно говорится в голосовом файле]

ЭМОЦИЯ: [happy/sad/neutral/excited/grateful/sympathetic]
ТЕМА: [greeting/wellbeing/about_me/food/travel/work/gratitude]
ТИП: [question/answer/statement/story/compliment]

КОНКРЕТНЫЙ КОНТЕКСТ:
[когда именно использовать этот голосовой файл]
"""

            try:
                desc_file.write_text(description, encoding='utf-8')
                created_count += 1
                print(f"  ✓ {voice_file.name}")
            except Exception as e:
                print(f"  ❌ Ошибка создания описания для {voice_file.name}: {e}")

        print(f"  Создано описаний для голосовых: {created_count}")


    def _show_simple_stats(self) -> None:
        """Показывает упрощенную статистику"""
        print("\n📊 СТАТИСТИКА:")

        # Статистика голосовых
        voices_path = self.library_path / "voices"
        if voices_path.exists():
            voice_files = list(voices_path.glob("*.ogg"))
            voice_descs = list(voices_path.glob("*.txt"))
            voice_ready = len([d for d in voice_descs if not d.name.endswith('.ogg.txt')])

            print(f"🎤 Голосовые: {len(voice_files)} файлов, {voice_ready} описаний")

        print(f"\n💡 Пасты: исключены из рекомендаций")
        print(f"💡 Фото/видео: названия уже понятны")

def main():
    """Основная функция"""
    import argparse

    parser = argparse.ArgumentParser(description="Упрощенное улучшение медиа (только голосовые файлы)")
    parser.add_argument('--max-files', type=int, default=20,
                       help='Максимум файлов для обработки (по умолчанию: 20)')
    parser.add_argument('--stats', action='store_true',
                       help='Показать статистику готовности')

    args = parser.parse_args()

    improver = SimpleMediaImprover()

    if args.stats:
        improver._show_simple_stats()
    else:
        improver.run_simple_improvement(args.max_files)

if __name__ == "__main__":
    main()
