#!/usr/bin/env python3
"""
Тест строгой фильтрации рекомендаций
"""

import asyncio
from media_recommender import get_media_recommender

async def test_strict_filtering():
    """Тест строгой фильтрации"""
    recommender = get_media_recommender(8412294171)

    test_cases = [
        ("привет, как дела?", "Вопрос о самочувствии - должны найти подходящий ответ"),
        ("я сегодня устал", "Утверждение о состоянии - должны найти сочувствие"),
        ("спасибо за помощь", "Благодарность - должны найти ответ на благодарность"),
        ("что-то непонятное сообщение", "Несуществующая тема - должны отказаться от рекомендаций")
    ]

    print("🧪 Тест строгой фильтрации рекомендаций")
    print("=" * 60)

    for message, description in test_cases:
        print(f"\n💬 {description}")
        print(f"📨 '{message}'")

        # Тестируем обычную фильтрацию
        normal_recs = await recommender.recommend_media(message, strict_filtering=False)
        print(f"   Обычная фильтрация: {len(normal_recs)} рекомендаций")

        # Тестируем строгую фильтрацию
        strict_recs = await recommender.recommend_media(message, strict_filtering=True)
        print(f"   Строгая фильтрация: {len(strict_recs)} рекомендаций")

        if strict_recs:
            for i, rec in enumerate(strict_recs, 1):
                print(f"     {i}. {rec.filename} (уверенность: {rec.relevance_score:.1%})")
                print(f"        {rec.reason}")
        else:
            print("     ❌ Нет подходящих рекомендаций")

        print("-" * 40)

if __name__ == "__main__":
    asyncio.run(test_strict_filtering())
