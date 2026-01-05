#!/usr/bin/env python3
"""
Тест системы на английском для проверки логики
"""

import asyncio
from media_recommender import get_media_recommender

async def test_english():
    """Тест на английском"""
    # Создадим тестовые файлы с английскими именами
    test_library_path = "library/8412294171"
    import os
    os.makedirs(f"{test_library_path}/pastes", exist_ok=True)

    # Создаем тестовые файлы
    test_files = [
        ("hello_how_are_you.txt", "Hello! How are you doing?"),
        ("im_doing_great.txt", "I'm doing great! Full of energy!"),
        ("tell_me_about_yourself.txt", "Tell me more about yourself!"),
        ("i_work_in_it.txt", "I work in IT, I love traveling and cooking."),
        ("thank_you_so_much.txt", "Thank you so much! You're such a good person!"),
    ]

    for filename, content in test_files:
        with open(f"{test_library_path}/pastes/{filename}", 'w', encoding='utf-8') as f:
            f.write(content)

    # Пересоздаем рекомендатор
    recommender = get_media_recommender(8412294171)

    # Тестируем
    test_messages = ["hello, how are you?", "tell me about yourself", "thank you"]
    for msg in test_messages:
        context = recommender._analyze_message_context(msg)
        print(f"\nMessage: '{msg}'")
        print(f"  Context: {context}")

        # Ищем рекомендации
        recommendations = await recommender.recommend_media(msg, api_key=None)  # Без AI
        if recommendations:
            print("  RECOMMENDATIONS:")
            for i, rec in enumerate(recommendations, 1):
                print(f"    {i}. {rec.filename} (score: {rec.relevance_score:.2f}) - {rec.reason}")
        else:
            print("  No recommendations found")

if __name__ == "__main__":
    asyncio.run(test_english())
