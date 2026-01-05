#!/usr/bin/env python3
"""
Анализ существующих медиафайлов и предложения по переименованию
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple
import json

class FileAnalyzer:
    """Анализатор медиафайлов для предложения переименований"""

    def __init__(self, user_id: int = 8412294171):
        self.user_id = user_id
        self.library_path = Path(f"library/{user_id}")
        self.analysis_results = {}

        # Паттерны для анализа русских названий
        self.russian_patterns = {
            'questions': [
                r'как.*\?', r'что.*\?', r'где.*\?', r'когда.*\?', r'почему.*\?',
                r'расскажи', r'ты.*\?', r'вы.*\?', r'кем.*\?', r'чем.*\?'
            ],
            'greetings': [
                r'здравствуй', r'привет', r'добрый', r'доброе', r'доброго',
                r'доброй', r'хай', r'hello', r'hi'
            ],
            'wellbeing': [
                r'как.*дела', r'как.*самочувствие', r'как.*настроение',
                r'как.*жизнь', r'как.*поживаешь', r'хорошо', r'отлично',
                r'замечательно', r'прекрасно', r'нормально', r'плохо', r'так себе'
            ],
            'gratitude': [
                r'спасибо', r'благодар', r'спс', r'thank', r'thanks'
            ],
            'food': [
                r'еда', r'готов', r'кухн', r'рецепт', r'суп', r'борщ',
                r'паста', r'пицца', r'салат', r'мясо', r'рыба'
            ],
            'travel': [
                r'путешеств', r'поездк', r'отпуск', r'турция', r'италия',
                r'франция', r'дубай', r'питер', r'море', r'пляж', r'отель'
            ],
            'work': [
                r'работ', r'офис', r'компьютер', r'документ', r'папк'
            ],
            'pets': [
                r'кошк', r'собак', r'кот', r'пес', r'животн'
            ],
            'stories': [
                r'рассказ', r'история', r'был', r'езди', r'летал', r'видел'
            ]
        }

    def analyze_filename(self, filename: str) -> Dict[str, any]:
        """Анализирует имя файла и определяет его характеристики"""
        name_lower = filename.lower()
        analysis = {
            'original_name': filename,
            'detected_emotion': 'neutral',
            'detected_theme': 'unknown',
            'detected_type': 'statement',
            'confidence': 0,
            'issues': []
        }

        # Определяем тип контента
        is_question = False
        for pattern in self.russian_patterns['questions']:
            if re.search(pattern, name_lower):
                is_question = True
                break

        if is_question:
            analysis['detected_type'] = 'question'
        elif any(word in name_lower for word in ['хорошо', 'отлично', 'замечательно', 'прекрасно']):
            analysis['detected_type'] = 'answer'
        elif any(word in name_lower for word in ['спасибо', 'благодар']):
            analysis['detected_type'] = 'gratitude'

        # Определяем тему
        theme_scores = {}
        for theme, patterns in self.russian_patterns.items():
            score = 0
            for pattern in patterns:
                if re.search(pattern, name_lower):
                    score += 1
            theme_scores[theme] = score

        best_theme = max(theme_scores.items(), key=lambda x: x[1])
        if best_theme[1] > 0:
            analysis['detected_theme'] = best_theme[0]
            analysis['confidence'] = min(best_theme[1] * 20, 100)

        # Определяем эмоцию
        if any(word in name_lower for word in ['хорошо', 'отлично', 'замечательно', 'прекрасно', 'супер']):
            analysis['detected_emotion'] = 'happy'
        elif any(word in name_lower for word in ['плохо', 'устал', 'грустн', 'проблем']):
            analysis['detected_emotion'] = 'sad'
        elif any(word in name_lower for word in ['спасибо', 'благодар', 'мил', 'хорош']):
            analysis['detected_emotion'] = 'grateful'
        elif any(word in name_lower for word in ['взволнован', 'возбужден', 'класс', 'круто']):
            analysis['detected_emotion'] = 'excited'

        # Проверяем на проблемы
        if analysis['detected_theme'] == 'unknown':
            analysis['issues'].append("Не удалось определить тему файла")

        if analysis['confidence'] < 30:
            analysis['issues'].append(f"Низкая уверенность анализа ({analysis['confidence']}%)")

        if is_question and analysis['detected_type'] != 'question':
            analysis['issues'].append("Возможно, это вопрос, но определено как утверждение")

        return analysis

    def suggest_new_name(self, analysis: Dict) -> str:
        """Предлагает новое имя файла на основе анализа"""
        emotion = analysis['detected_emotion']
        theme = analysis['detected_theme']
        content_type = analysis['detected_type']

        # Создаем базовое имя
        base_name = f"{emotion}_{theme}_{content_type}"

        # Добавляем описание на основе оригинального имени
        original = analysis['original_name'].replace('.ogg', '').replace('.mp4', '').replace('.jpg', '').replace('.png', '')

        # Очищаем оригинальное имя от спецсимволов
        clean_desc = re.sub(r'[^\w\s-]', '', original)
        clean_desc = re.sub(r'\s+', '_', clean_desc.strip())

        # Ограничиваем длину описания
        if len(clean_desc) > 30:
            clean_desc = clean_desc[:27] + "..."

        new_name = f"{base_name}_{clean_desc}" if clean_desc else base_name

        return new_name

    def analyze_all_files(self) -> Dict[str, Dict]:
        """Анализирует все медиафайлы"""
        results = {}

        folders_to_check = ['voices', 'video', 'stickers', 'pastes']

        for folder in folders_to_check:
            folder_path = self.library_path / folder
            if not folder_path.exists():
                continue

            print(f"\nFOLDER: Анализ папки: {folder}")

            for file_path in folder_path.rglob('*'):
                if file_path.is_file() and file_path.suffix.lower() in ['.ogg', '.mp4', '.jpg', '.png', '.txt']:
                    filename = file_path.name

                    analysis = self.analyze_filename(filename)
                    analysis['file_path'] = str(file_path)
                    analysis['folder'] = folder
                    analysis['suggested_name'] = self.suggest_new_name(analysis)

                    results[str(file_path)] = analysis

                    # Выводим результат
                    status = "OK" if not analysis['issues'] else "ISSUE"
                    print(f"  {status} {filename}")
                    print(f"      -> {analysis['suggested_name']}{file_path.suffix}")
                    if analysis['issues']:
                        for issue in analysis['issues']:
                            print(f"      ISSUE: {issue}")
                    print()

        return results

    def save_analysis_report(self, results: Dict, output_file: str = "file_analysis_report.json"):
        """Сохраняет отчет анализа в файл"""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"REPORT: Отчет сохранен в {output_file}")

    def generate_renaming_script(self, results: Dict, output_file: str = "rename_files.py"):
        """Генерирует скрипт для переименования файлов"""
        script_content = '''#!/usr/bin/env python3
"""
Автоматическое переименование медиафайлов
"""

import os
import shutil
from pathlib import Path

def rename_files():
    """Переименовывает файлы согласно анализу"""
    renames = {
'''

        for file_path, analysis in results.items():
            old_path = Path(file_path)
            new_name = analysis['suggested_name'] + old_path.suffix
            new_path = old_path.parent / new_name

            script_content += f'        "{file_path}": "{new_path}",\n'

        script_content += '''
    }

    for old_path, new_path in renames.items():
        old_path = Path(old_path)
        new_path = Path(new_path)

        if old_path.exists() and not new_path.exists():
            print(f"Переименовываю: {old_path.name} → {new_path.name}")
            shutil.move(str(old_path), str(new_path))
        elif new_path.exists():
            print(f"WARNING: Файл уже существует: {new_path}")
        else:
            print(f"❌ Исходный файл не найден: {old_path}")

if __name__ == "__main__":
    rename_files()
    print("DONE: Переименование завершено")
'''

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(script_content)

        print(f"SCRIPT: Скрипт переименования создан: {output_file}")

def main():
    """Основная функция"""
    print("ANALYSIS: Анализ медиафайлов для переименования")
    print("=" * 50)

    analyzer = FileAnalyzer()
    results = analyzer.analyze_all_files()

    print(f"\n📊 Результаты анализа:")
    print(f"   Всего файлов: {len(results)}")

    issues_count = sum(len(analysis.get('issues', [])) for analysis in results.values())
    print(f"   Проблемных файлов: {issues_count}")

    # Сохраняем отчеты
    analyzer.save_analysis_report(results)
    analyzer.generate_renaming_script(results)

    print("\nDONE: Анализ завершен!")
    print("REPORT: file_analysis_report.json - подробный отчет")
    print("SCRIPT: rename_files.py - скрипт для переименования")

if __name__ == "__main__":
    main()
