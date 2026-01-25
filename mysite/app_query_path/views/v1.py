# app_query_path/views/v1.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiParameter

from ..models import Question, Article, AnswerOption
from ..serializers import (
    QuestionSerializer,
    QuestionStartSerializer,
    ArticleSerializer,
)


@extend_schema(
    tags=['app_query_path'],
    summary="Получить стартовый вопрос",
    description="Возвращает первый вопрос с флагом is_start=True.",
    responses={200: QuestionStartSerializer}
)
class StartQuestionAPIView(APIView):
    """
    Эндпоинт для получения начального вопроса диалога.
    """

    def get(self, request):
        try:
            start_question = Question.objects.get(is_start=True)
        except Question.DoesNotExist:
            return Response(
                {"error": "Стартовый вопрос не настроен."},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = QuestionStartSerializer(start_question, context={'request': request})
        return Response(serializer.data)


@extend_schema(
    tags=['app_query_path'],
    summary="Получить следующий вопрос или статью по выбранному ответу",
    parameters=[
        OpenApiParameter(
            name='answer_id',
            type=int,
            required=True,
            description="ID варианта ответа (AnswerOption)"
        )
    ],
    responses={
        200: {
            'description': 'Следующий шаг: либо новый вопрос, либо статья',
            'content': {
                'application/json': {
                    'examples': {
                        'next_question': {
                            'summary': 'Следующий вопрос',
                            'value': {
                                "type": "question",
                                "data": {
                                    "id": 2,
                                    "text": "Какая у вас ОС?",
                                    "options": [
                                        {"id": 3, "text": "Windows"},
                                        {"id": 4, "text": "Linux"}
                                    ]
                                }
                            }
                        },
                        'final_article': {
                            "summary": "Найдено решение",
                            "value": {
                                "type": "article",
                                "data": {
                                    "id": 5,
                                    "title": "Инструкция по установке",
                                    "content": "Скачайте файл..."
                                }
                            }
                        }
                    }
                }
            }
        },
        404: {"description": "Ответ не найден"}
    }
)
class NextStepAPIView(APIView):
    """
    По ID варианта ответа определяет следующий шаг:
    - если есть next_question → возвращает вопрос;
    - если есть article → возвращает статью;
    - если ничего нет → завершает диалог.
    """

    def get(self, request):
        answer_id = request.query_params.get('answer_id')
        if not answer_id:
            return Response(
                {'error': 'Требуется параметр answer_id'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            answer = AnswerOption.objects.select_related(
                'next_question', 'article'
            ).get(id=answer_id)
        except AnswerOption.DoesNotExist:
            return Response(
                {'error': 'Вариант ответа не найден'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Случай 1: есть связанная статья — возвращаем её
        if answer.article:
            article_serializer = ArticleSerializer(answer.article)
            return Response({
                'type': 'article',
                'data': article_serializer.data
            })

        # Случай 2: есть следующий вопрос — возвращаем его
        if answer.next_question:
            question_serializer = QuestionSerializer(answer.next_question)
            return Response({
                'type': 'question',
                'data': question_serializer.data
            })

        # Случай 3: ни статьи, ни вопроса — диалог завершён
        return Response({
            'type': 'end',
            'data': {'message': 'Диалог завершён. Решение не найдено.'}
        })


# === Дополнительно: полные списки (для админки или отладки) ===

@extend_schema(tags=['app_query_path'])
class QuestionListView(APIView):
    def get(self, request):
        questions = Question.objects.prefetch_related('options').all()
        serializer = QuestionSerializer(questions, many=True)
        return Response(serializer.data)


@extend_schema(tags=['app_query_path'])
class ArticleListView(APIView):
    def get(self, request):
        articles = Article.objects.all()
        serializer = ArticleSerializer(articles, many=True)
        return Response(serializer.data)
