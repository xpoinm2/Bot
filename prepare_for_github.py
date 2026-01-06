#!/usr/bin/env python3
"""
Скрипт для подготовки кода к отправке на GitHub.
Заменяет реальный API ключ на заглушку.
"""

import re

def prepare_for_github():
    """Заменяет реальный API ключ на заглушку"""
    file_path = "run_bot.bat"

    print("PREPARING: Подготовка кода для GitHub...")

    try:
        # Читаем файл
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Ищем строку с API ключом (в bat файле)
        pattern = r'set\s+"OPENAI_API_KEY=([^"]*)"'
        match = re.search(pattern, content)

        if not match:
            print("ERROR: Не найден OPENAI_API_KEY в коде")
            return False

        real_key = match.group(1)

        # Проверяем, что это не заглушка уже
        if real_key == "your-openai-api-key-here":
            print("WARNING: API ключ уже заменен на заглушку")
            return True

        # Заменяем на заглушку
        new_content = content.replace(real_key, "your-openai-api-key-here\"")

        # Записываем обратно
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

        print("SUCCESS: API ключ заменен на заглушку")
        print(f"   Старый ключ: {real_key[:20]}...")
        print("   Новый ключ: your-openai-api-key-here")
        print("\nINFO: После коммита на GitHub верните реальный ключ обратно!")

        return True

    except Exception as e:
        print(f"ERROR: Ошибка: {e}")
        return False

def restore_api_key():
    """Восстанавливает реальный API ключ (нужен ваш ключ)"""
    print("RESTORING: Восстановление API ключа...")

    # Здесь нужно ввести реальный ключ
    real_key = input("Введите ваш реальный OpenAI API ключ: ").strip()

    if not real_key:
        print("ERROR: Ключ не введен")
        return False

    file_path = "run_bot.bat"

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Заменяем заглушку на реальный ключ
        new_content = content.replace("your-openai-api-key-here\"", real_key + "\"")

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

        print("SUCCESS: API ключ восстановлен")
        print(f"   Ключ: {real_key[:20]}...")

        return True

    except Exception as e:
        print(f"ERROR: Ошибка: {e}")
        return False

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--restore":
        restore_api_key()
    else:
        prepare_for_github()
        print("\nNEXT STEPS:")
        print("1. git add .")
        print("2. git commit -m 'Replace API key with placeholder'")
        print("3. git push")
        print("4. python prepare_for_github.py --restore  # вернуть ключ обратно")
