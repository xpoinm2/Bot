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
    file_type: str  # 'voice', 'video'
    relevance_score: float  # 0-1, насколько подходит
    reason: str  # почему именно этот файл
    metadata: Dict[str, Any]  # дополнительная информация

class MediaRecommender:
    """Рекомендатель медиафайлов на основе контекста"""

    def __init__(self, library_base_path: str):
        self.library_base_path = Path(library_base_path)
        self.allowed_extensions = {".ogg", ".mp4", ".jpg", ".jpeg", ".png"}
        self.media_types = {
            'voices': 'voice',
            'video': 'video'
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
                    if file_path.suffix.lower() not in self.allowed_extensions:
                        continue
                    self._analyze_and_cache_file(file_path, media_type)

        logger.info(f"Загружено метаданных для {len(self.file_metadata)} медиафайлов")

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
                'themes': [],
                'content_types': []
            }

            # Определяем темы и типы контента
            themes, content_types = self._infer_themes_from_filename(file_path.name)
            metadata['themes'] = themes
            metadata['content_types'] = content_types

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

    def _infer_themes_from_filename(self, filename: str) -> Tuple[List[str], List[str]]:
        """Определяет темы и типы контента на основе имени файла"""
        themes = []
        content_types = []
        filename_lower = filename.lower()

        # Анализ типа контента (вопрос/ответ/утверждение)
        question_words = ['как', 'что', 'где', 'когда', 'почему', 'зачем', 'кто', 'чей']
        if any(word in filename_lower for word in question_words) or filename_lower.endswith('?'):
            content_types.append('question')
        else:
            content_types.append('statement')

        # Приветствия и прощания
        if any(word in filename_lower for word in ['здравствуй', 'привет', 'добрый', 'доброе', 'доброго', 'спокойной', 'хай', 'hello', 'hi']):
            themes.append('greeting')
            if any(word in filename_lower for word in ['здравствуй', 'привет', 'добрый', 'доброе', 'хай', 'hello', 'hi']):
                content_types.append('greeting_start')
            else:
                content_types.append('farewell')

        # Вопросы о самочувствии
        if any(word in filename_lower for word in ['как', 'самочувствие', 'настроение', 'дела', 'жизнь', 'поживаешь']):
            themes.append('wellbeing')
            if 'как' in filename_lower and any(word in filename_lower for word in ['дела', 'самочувствие', 'настроение', 'жизнь', 'поживаешь']):
                content_types.append('wellbeing_question')

        # Ответы на вопросы о самочувствии
        if any(word in filename_lower for word in ['хорошо', 'отлично', 'нормально', 'плохо', 'так себе', 'прекрасно', 'замечательно', 'в порядке', 'неплохо']):
            themes.append('wellbeing')
            content_types.append('wellbeing_response')

        # О себе
        if any(word in filename_lower for word in ['о себе', 'расскажи', 'работаешь', 'кем']):
            themes.append('about_self')
            if 'расскажи' in filename_lower:
                content_types.append('about_self_question')
            else:
                content_types.append('about_self_statement')

        # Еда и готовка
        if any(word in filename_lower for word in ['еда', 'готовк', 'кухн', 'рецепт', 'суп', 'борщ', 'стол']):
            themes.append('food')
            if any(word in filename_lower for word in ['люблю', 'готов', 'ем', 'ела']):
                content_types.append('food_hobby')
            elif any(word in filename_lower for word in ['рецепт', 'как готов']):
                content_types.append('food_recipe')

        # Путешествия
        if any(word in filename_lower for word in ['путешеств', 'поездк', 'отпуск', 'турци', 'итали', 'франци', 'дубай', 'питер']):
            themes.append('travel')
            if any(word in filename_lower for word in ['был', 'езди', 'летал', 'видел']):
                content_types.append('travel_story')

        # Животные
        if any(word in filename_lower for word in ['кошк', 'собак', 'животн', 'кот', 'пес']):
            themes.append('pets')
            if any(word in filename_lower for word in ['моя', 'мой', 'наш']):
                content_types.append('pets_ownership')

        # Работа/офис
        if any(word in filename_lower for word in ['работ', 'офис', 'документ', 'папк', 'компьютер']):
            themes.append('work')
            if any(word in filename_lower for word in ['работа', 'офис', 'компания']):
                content_types.append('work_environment')

        # Благодарности
        if any(word in filename_lower for word in ['спасибо', 'благодар', 'спс']):
            themes.append('gratitude')
            content_types.append('gratitude')

        # Извинения
        if any(word in filename_lower for word in ['извин', 'прости', 'сорри']):
            themes.append('apology')
            content_types.append('apology')

        # Эмоциональные состояния
        if any(word in filename_lower for word in ['грустн', 'рад', 'счастлив', 'обижен']):
            themes.append('emotion')
            content_types.append('emotion_expression')

        return themes, content_types

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

        # Сначала фильтруем файлы по базовым критериям с учетом контекста
        context_text = incoming_message
        if history_context:
            recent_history = " ".join(history_context[-3:])
            if recent_history:
                context_text = f"{incoming_message} {recent_history}"
        candidate_files = self._filter_candidates_by_keywords(context_text.lower())

        if not candidate_files:
            if api_key and self.file_metadata:
                fallback_candidates = sorted(self.file_metadata.keys())
                return await self._rank_with_ai(
                    incoming_message,
                    fallback_candidates,
                    history_context or [],
                    max_recommendations,
                    api_key
                )
            candidate_files = sorted(self.file_metadata.keys())

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

    def _analyze_message_context(self, message: str) -> Dict[str, Any]:
        """Анализирует контекст входящего сообщения"""
        message_lower = message.lower().strip()

        context = {
            'is_question': False,
            'themes': [],
            'content_type_needed': 'statement',  # По умолчанию ищем ответы/утверждения
            'urgency': 'normal'
        }

        # Определяем, является ли сообщение вопросом
        question_indicators = ['?', 'как', 'что', 'где', 'когда', 'почему', 'зачем', 'кто', 'чей', 'расскажи', 'ты']
        context['is_question'] = (
            any(indicator in message_lower for indicator in question_indicators) or
            message_lower.endswith('?') or
            message_lower.startswith(('ты ', 'вы '))
        )

        # Если это вопрос, нам нужны ответы/утверждения
        if context['is_question']:
            context['content_type_needed'] = 'statement'
        else:
            # Если это утверждение, можем предлагать вопросы или продолжение разговора
            context['content_type_needed'] = 'question'

        # Определяем темы сообщения
        if any(word in message_lower for word in ['привет', 'здравствуй', 'добрый', 'доброе', 'хай', 'hello', 'hi']):
            context['themes'].append('greeting')

        if any(word in message_lower for word in ['как дела', 'как самочувствие', 'как настроение', 'что делаешь', 'как жизнь', 'как поживаешь']):
            context['themes'].append('wellbeing')

        if any(word in message_lower for word in ['о себе', 'расскажи о себе', 'кем работаешь', 'чем занимаешься', 'кто ты', 'откуда']):
            context['themes'].append('about_self')

        if any(word in message_lower for word in ['еда', 'готовить', 'кухня', 'рецепт', 'кушать', 'поесть', 'голоден']):
            context['themes'].append('food')

        if any(word in message_lower for word in ['спасибо', 'благодар', 'спс', 'thank', 'thanks']):
            context['themes'].append('gratitude')

        if any(word in message_lower for word in ['извин', 'прости', 'сорри', 'sorry', 'простите']):
            context['themes'].append('apology')

        if any(word in message_lower for word in ['любовь', 'нрав', 'симпат', 'красив', 'мил', 'хорош', 'замечательн']):
            context['themes'].append('affection')

        return context

    def _filter_candidates_by_keywords(self, message: str) -> List[str]:
        """Фильтрует файлы по ключевым словам с учетом контекста"""
        candidates = []
        context = self._analyze_message_context(message)

        for file_path, metadata in self.file_metadata.items():
            keywords = metadata.get('keywords', [])
            themes = metadata.get('themes', [])
            content_types = metadata.get('content_types', [])

            score = 0

            # Проверяем совпадения по ключевым словам
            keyword_matches = sum(1 for keyword in keywords if keyword in message.lower())
            if keyword_matches > 0:
                score += keyword_matches * 2

            # Проверяем совпадения по темам
            theme_matches = sum(1 for theme in context['themes'] if theme in themes)
            if theme_matches > 0:
                score += theme_matches * 3

            # Проверяем соответствие типа контента
            content_type_match = False
            if context['content_type_needed'] == 'statement':
                # Ищем ответы/утверждения, избегаем вопросов
                if 'question' not in content_types and any(ct in content_types for ct in ['statement', 'wellbeing_response', 'about_self_statement']):
                    content_type_match = True
                    score += 2
            elif context['content_type_needed'] == 'question':
                # Ищем вопросы для продолжения разговора
                if 'question' in content_types:
                    content_type_match = True
                    score += 1

            # Бонус за точные совпадения типов контента
            if context['is_question'] and 'wellbeing_response' in content_types:
                score += 3  # Отличный ответ на вопрос о самочувствии
            elif not context['is_question'] and 'gratitude' in content_types:
                score += 3  # Спасибо на утверждение

            # Только файлы с минимальным скором попадают в кандидаты
            if score >= 2:
                candidates.append((file_path, score))

        # Сортируем по релевантности и возвращаем только пути
        candidates.sort(key=lambda x: x[1], reverse=True)
        return [file_path for file_path, score in candidates[:20]]  # Ограничиваем количество кандидатов

    async def _rank_with_ai(
        self,
        message: str,
        candidate_files: List[str],
        history: List[str],
        max_recommendations: int,
        api_key: str
    ) -> List[MediaRecommendation]:
        """Ранжирует файлы с помощью AI с учетом контекста"""
        context = self._analyze_message_context(message)

        # Создаем промпт для AI
        file_descriptions = []
        for i, file_path in enumerate(candidate_files[:12]):  # немного больше для выбора
            metadata = self.file_metadata.get(file_path, {})
            desc = f"{i+1}. {metadata.get('filename', 'Неизвестный файл')} - тип: {metadata.get('type', 'неизвестный')}"

            themes = metadata.get('themes', [])
            content_types = metadata.get('content_types', [])

            if themes:
                desc += f", темы: {', '.join(themes)}"
            if content_types:
                desc += f", тип контента: {', '.join(content_types)}"

            file_descriptions.append(desc)

        # Определяем что нужно для ответа
        response_type_needed = "ответы/утверждения" if context['is_question'] else "вопросы или благодарности"

        prompt = f"""
Ты помогаешь выбрать подходящие медиафайлы для ответа в переписке девушки с парнем.

КОНТЕКСТ СООБЩЕНИЯ:
- Сообщение пользователя: "{message}"
- Это {'ВОПРОС' if context['is_question'] else 'УТВЕРЖДЕНИЕ'}
- Нам нужны: {response_type_needed}

ПРАВИЛА ВЫБОРА:
1. На ВОПРОС пользователя предлагай ОТВЕТЫ, а не новые вопросы
2. На УТВЕРЖДЕНИЕ можно предложить благодарность или вопрос для продолжения
3. Избегай предлагать вопросы в ответ на вопросы
4. Выбирай файлы, релевантные по темам и контенту

История переписки (последние сообщения):
{chr(10).join(history[-3:]) if history else "Нет истории"}

ДОСТУПНЫЕ ФАЙЛЫ:
{chr(10).join(file_descriptions)}

ВЫБЕРИ до {max_recommendations} наиболее подходящих файлов. Для КАЖДОГО укажи:
1. Номер файла
2. Оценку релевантности (0.0-1.0, где 1.0 - идеально подходит)
3. КРАТКУЮ причину выбора (почему именно этот файл подходит для этого сообщения)

Формат ответа:
Файл X: оценка - причина
Файл Y: оценка - причина

Если ни один файл не подходит, укажи "Нет подходящих файлов"
"""

        try:
            ai_response = await gpt_answer(
                prompt,
                system_prompt="Ты эксперт по выбору медиафайлов для романтической переписки. Всегда учитывай контекст и избегай логических ошибок.",
                api_key=api_key,
                model="gpt-4o-mini",
                temperature=0.2  # Более детерминированные ответы
            )

            if "Нет подходящих файлов" in ai_response:
                return []

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
        """Простое ранжирование по схожести с учетом контекста"""
        recommendations = []
        context = self._analyze_message_context(message)

        for file_path in candidate_files:
            metadata = self.file_metadata.get(file_path, {})
            keywords = metadata.get('keywords', [])
            themes = metadata.get('themes', [])
            content_types = metadata.get('content_types', [])

            score = 0
            reasons = []

            # Оценка по ключевым словам
            keyword_score = sum(1 for keyword in keywords if keyword in message.lower())
            if keyword_score > 0:
                score += keyword_score * 2
                reasons.append(f"{keyword_score} ключевых слов")

            # Оценка по темам
            theme_score = sum(1 for theme in context['themes'] if theme in themes)
            if theme_score > 0:
                score += theme_score * 3
                reasons.append(f"{theme_score} совпадений по темам")

            # Оценка по типу контента
            if context['is_question']:
                # На вопрос ищем ответы
                if 'question' not in content_types:
                    score += 2
                    reasons.append("ответ на вопрос")
                if 'wellbeing_response' in content_types:
                    score += 3
                    reasons.append("прямой ответ на вопрос о самочувствии")
            else:
                # На утверждение можем предлагать вопросы или благодарности
                if 'question' in content_types or 'gratitude' in content_types:
                    score += 1
                    reasons.append("продолжение разговора")

            # Специальные правила
            if 'gratitude' in content_types and not context['is_question']:
                score += 2
                reasons.append("подходит для ответа на утверждение")

            # Нормализуем оценку (0-1)
            relevance = min(score / 10.0, 1.0)

            if relevance > 0.15:  # повышенный порог
                recommendations.append(MediaRecommendation(
                    file_path=file_path,
                    file_type=metadata.get('type', 'unknown'),
                    relevance_score=relevance,
                    reason=f"Совпадения: {', '.join(reasons)}",
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
