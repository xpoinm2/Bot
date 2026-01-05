#!/usr/bin/env python3
"""
Простой тест системы рекомендаций
"""

import asyncio
from media_recommender import get_media_recommender

async def test_simple():
    """Простой тест"""
    recommender = get_media_recommender(8412294171)

    # Проверим анализ одного файла
    print("Проверяем метаданные файлов:")
    for file_path, metadata in list(recommender.file_metadata.items())[:5]:
        print(f"  {metadata.get('filename')}: themes={metadata.get('themes')}, content_types={metadata.get('content_types')}")

    # Тест анализ контекста
    test_messages = ["привет, как дела?", "я сегодня устал", "спасибо"]
    for msg in test_messages:
        context = recommender._analyze_message_context(msg)
        print(f"\nСообщение: '{msg}'")
        print(f"  Контекст: {context}")

if __name__ == "__main__":
    asyncio.run(test_simple())
