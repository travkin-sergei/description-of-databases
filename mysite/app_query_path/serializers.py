# app_query_path/serializers.py

from rest_framework import serializers
from .models import Article, Question, AnswerOption


class ArticleSerializer(serializers.ModelSerializer):
    """Сериализатор для статей (решений)."""

    class Meta:
        model = Article
        fields = ['id', 'title', 'content', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class AnswerOptionSerializer(serializers.ModelSerializer):
    """Сериализатор для вариантов ответов."""

    # Вложенные представления для связанных объектов (только для чтения)
    article_title = serializers.CharField(source='article.title', read_only=True)
    next_question_text = serializers.CharField(source='next_question.text', read_only=True)

    class Meta:
        model = AnswerOption
        fields = [
            'id',
            'question',
            'text',
            'article',
            'article_title',
            'next_question',
            'next_question_text',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class QuestionSerializer(serializers.ModelSerializer):
    """Сериализатор для вопросов с вложенными вариантами ответов."""

    options = AnswerOptionSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = [
            'id',
            'text',
            'is_start',
            'options',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class QuestionStartSerializer(serializers.Serializer):
    """Сериализатор для получения первого вопроса."""

    question_id = serializers.IntegerField(read_only=True)
    text = serializers.CharField(read_only=True)
    options = AnswerOptionSerializer(many=True, read_only=True)

    def to_representation(self, instance):
        return {
            'question_id': instance.id,
            'text': instance.text,
            'options': AnswerOptionSerializer(
                instance.options.all(), many=True, context=self.context
            ).data
        }