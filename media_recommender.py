import os
import json
import logging
from typing import List, Dict, Optional, Tuple, Any
from pathlib import Path
from dataclasses import dataclass

from OpenAi_helper import gpt_answer, OpenAIModel

logger = logging.getLogger(__name__)

@dataclass
class MediaRecommendation:
    """Рекомендация медиафайла для ответа"""
    file_path: str
    file_type: str  # 'voice', 'video', 'sticker', 'paste'
    relevance_score: float  # 0-1, насколько подходит
    reason: str  # почему именно этот файл
    metadata: Dict[str, Any]  # дополнительная информация

class MediaRecommender:
    """Рекомендатель медиафайлов на основе контекста"""

    def __init__(self, library_base_path: str):
        self.library_base_path = Path(library_base_path)
        self.media_types = {
            'voices': 'voice',
            'video': 'video',
            'stickers': 'sticker',
            'pastes': 'paste'
        }
        self._load_file_metadata()

    def _load_file_metadata(self) -> None:
        """Загружает или создает метаданные для медиафайлов"""
        self.file_metadata = {}

        for folder_name, media_type in self.media_types.items():
            folder_path = self.library_base_path / folder_name
            if not folder_path.exists():
                continue

            for file_path in folder_path.rglob('*'):
                if file_path.is_file():
                    self._analyze_and_cache_file(file_path, media_type)

    def _analyze_and_cache_file(self, file_path: Path, media_type: str) -> None:
        """Анализирует файл и кэширует его метаданные"""
        try:
            # Получаем базовую информацию из имени файла
            filename = file_path.stem.lower()

            # Создаем базовые метаданные
            metadata = {
                'filename': file_path.name,
                'path': str(file_path),
                'type': media_type,
                'size': file_path.stat().st_size,
                'keywords': self._extract_keywords_from_filename(filename),
                'themes': self._infer_themes_from_filename(filename)
            }

            self.file_metadata[str(file_path)] = metadata

        except Exception as e:
            logger.warning(f"Не удалось проанализировать файл {file_path}: {e}")

    def _extract_keywords_from_filename(self, filename: str) -> List[str]:
        """Извлекает ключевые слова из имени файла"""
        # Удаляем расширения и специальные символы
        clean_name = filename.replace('_', ' ').replace('-', ' ').replace('.ogg', '').replace('.mp4', '').replace('.jpg', '')

        # Разбиваем на слова
        words = clean_name.split()

        # Фильтруем и нормализуем
        keywords = []
        for word in words:
            word = word.strip().lower()
            if len(word) > 2:  # игнорируем слишком короткие слова
                keywords.append(word)

        return keywords

    def _infer_themes_from_filename(self, filename: str) -> List[str]:
        """Определяет темы на основе имени файла"""
        themes = []

        # Приветствия и прощания
        if any(word in filename for word in ['здравствуй', 'привет', 'добрый', 'доброе', 'доброго', 'спокойной']):
            themes.append('greeting')

        # Вопросы о самочувствии
        if any(word in filename for word in ['как', 'самочувствие', 'настроение', 'дела']):
            themes.append('wellbeing')

        # О себе
        if any(word in filename for word in ['о себе', 'расскажи', 'работаешь', 'кем']):
            themes.append('about_self')

        # Еда и готовка
        if any(word in filename for word in ['еда', 'готовк', 'кухн', 'рецепт', 'суп', 'борщ']):
            themes.append('food')

        # Путешествия
        if any(word in filename for word in ['путешеств', 'поездк', 'отпуск', 'турци', 'итали', 'франци']):
            themes.append('travel')

        # Животные
        if any(word in filename for word in ['кошк', 'собак', 'животн']):
            themes.append('pets')

        # Работа/офис
        if any(word in filename for word in ['работ', 'офис', 'документ', 'папк']):
            themes.append('work')

        return themes

    async def recommend_media(
        self,
        incoming_message: str,
        history_context: Optional[List[str]] = None,
        max_recommendations: int = 3,
        api_key: Optional[str] = None
    ) -> List[MediaRecommendation]:
        """
        Рекомендует подходящие медиафайлы на основе входящего сообщения

        Args:
            incoming_message: текст входящего сообщения
            history_context: предыдущие сообщения для контекста
            max_recommendations: максимальное количество рекомендаций
            api_key: ключ OpenAI API

        Returns:
            список рекомендаций медиафайлов
        """

        # Сначала фильтруем файлы по базовым критериям
        candidate_files = self._filter_candidates_by_keywords(incoming_message.lower())

        if not candidate_files:
            return []

        # Если кандидатов много, используем AI для ранжирования
        if len(candidate_files) > max_recommendations * 2 and api_key:
            return await self._rank_with_ai(
                incoming_message,
                candidate_files,
                history_context or [],
                max_recommendations,
                api_key
            )

        # Иначе ранжируем по простым критериям
        return self._rank_by_similarity(
            incoming_message.lower(),
            candidate_files,
            max_recommendations
        )

    def _filter_candidates_by_keywords(self, message: str) -> List[str]:
        """Фильтрует файлы по ключевым словам"""
        candidates = []

        for file_path, metadata in self.file_metadata.items():
            # Проверяем ключевые слова
            keywords = metadata.get('keywords', [])
            themes = metadata.get('themes', [])

            # Ищем совпадения в ключевых словах
            keyword_matches = any(keyword in message for keyword in keywords)

            # Ищем совпадения в темах
            theme_matches = any(theme in message for theme in ['greeting', 'wellbeing', 'about_self', 'food', 'travel', 'pets', 'work']
                              if theme in themes)

            if keyword_matches or theme_matches:
                candidates.append(file_path)

        return candidates

    async def _rank_with_ai(
        self,
        message: str,
        candidate_files: List[str],
        history: List[str],
        max_recommendations: int,
        api_key: str
    ) -> List[MediaRecommendation]:
        """Ранжирует файлы с помощью AI"""

        # Создаем промпт для AI
        file_descriptions = []
        for i, file_path in enumerate(candidate_files[:10]):  # ограничиваем для экономии токенов
            metadata = self.file_metadata.get(file_path, {})
            desc = f"{i+1}. {metadata.get('filename', 'Неизвестный файл')} - тип: {metadata.get('type', 'неизвестный')}"
            if metadata.get('themes'):
                desc += f", темы: {', '.join(metadata['themes'])}"
            file_descriptions.append(desc)

        prompt = f"""
Анализируй входящее сообщение пользователя и выбери наиболее подходящие медиафайлы для ответа.

Входящее сообщение: "{message}"

История переписки:
{chr(10).join(history[-5:]) if history else "Нет истории"}

Доступные файлы:
{chr(10).join(file_descriptions)}

Выбери до {max_recommendations} наиболее подходящих файлов. Для каждого укажи:
1. Номер файла
2. Оценку релевантности (0.0-1.0)
3. Причину выбора

Формат ответа:
Файл X: оценка - причина
Файл Y: оценка - причина
"""

        try:
            ai_response = await gpt_answer(
                prompt,
                system_prompt="Ты эксперт по выбору подходящих медиафайлов для ответов в переписке.",
                api_key=api_key,
                model="gpt-4o-mini",
                temperature=0.3
            )

            return self._parse_ai_ranking(ai_response, candidate_files, max_recommendations)

        except Exception as e:
            logger.warning(f"Ошибка AI-ранжирования: {e}")
            # Fallback к простому ранжированию
            return self._rank_by_similarity(message, candidate_files, max_recommendations)

    def _parse_ai_ranking(
        self,
        ai_response: str,
        candidate_files: List[str],
        max_recommendations: int
    ) -> List[MediaRecommendation]:
        """Парсит ответ AI и создает рекомендации"""
        recommendations = []

        for line in ai_response.split('\n'):
            line = line.strip()
            if not line:
                continue

            # Ищем паттерн "Файл X: оценка - причина"
            import re
            match = re.match(r'Файл\s+(\d+):\s*([0-9.]+)\s*-\s*(.+)', line, re.IGNORECASE)
            if match:
                file_idx = int(match.group(1)) - 1
                score = float(match.group(2))
                reason = match.group(3).strip()

                if 0 <= file_idx < len(candidate_files) and 0 <= score <= 1:
                    file_path = candidate_files[file_idx]
                    metadata = self.file_metadata.get(file_path, {})

                    recommendations.append(MediaRecommendation(
                        file_path=file_path,
                        file_type=metadata.get('type', 'unknown'),
                        relevance_score=min(score, 1.0),
                        reason=reason,
                        metadata=metadata
                    ))

        # Сортируем по релевантности и ограничиваем количество
        recommendations.sort(key=lambda x: x.relevance_score, reverse=True)
        return recommendations[:max_recommendations]

    def _rank_by_similarity(
        self,
        message: str,
        candidate_files: List[str],
        max_recommendations: int
    ) -> List[MediaRecommendation]:
        """Простое ранжирование по схожести"""
        recommendations = []

        for file_path in candidate_files:
            metadata = self.file_metadata.get(file_path, {})
            keywords = metadata.get('keywords', [])
            themes = metadata.get('themes', [])

            # Считаем совпадения
            keyword_score = sum(1 for keyword in keywords if keyword in message)
            theme_score = sum(1 for theme in themes if theme in message)

            # Нормализуем оценку
            total_words = len(message.split())
            if total_words > 0:
                relevance = min((keyword_score + theme_score * 2) / total_words, 1.0)
            else:
                relevance = 0.0

            if relevance > 0.1:  # минимальный порог
                recommendations.append(MediaRecommendation(
                    file_path=file_path,
                    file_type=metadata.get('type', 'unknown'),
                    relevance_score=relevance,
                    reason=f"Найдено совпадений: {keyword_score} ключевых слов, {theme_score} тем",
                    metadata=metadata
                ))

        # Сортируем и ограничиваем
        recommendations.sort(key=lambda x: x.relevance_score, reverse=True)
        return recommendations[:max_recommendations]

# Глобальный экземпляр рекомендатора
_media_recommender: Optional[MediaRecommender] = None

def get_media_recommender(user_id: int) -> MediaRecommender:
    """Получает или создает экземпляр рекомендатора для пользователя"""
    global _media_recommender

    library_path = f"library/{user_id}"
    if not os.path.exists(library_path):
        # Создаем пустую директорию если не существует
        os.makedirs(library_path, exist_ok=True)

    if _media_recommender is None or str(_media_recommender.library_base_path) != library_path:
        _media_recommender = MediaRecommender(library_path)

    return _media_recommender
