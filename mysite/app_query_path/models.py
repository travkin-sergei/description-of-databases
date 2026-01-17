# app_query_path/models.py
from django.db import models

from .apps import db_schema
from _common.models import BaseClass


class Article(BaseClass):
    title = models.CharField(max_length=255)
    content = models.TextField()

    def __str__(self):
        return self.title

    class Meta:
        db_table = f'{db_schema}"."article'
        verbose_name = '01 Статья'
        verbose_name_plural = '01 Статьи'


class Question(BaseClass):
    text = models.CharField(max_length=255)
    is_start = models.BooleanField(default=False)

    def __str__(self):
        return self.text

    class Meta:
        db_table = f'{db_schema}"."question'
        verbose_name = '02 Вопрос'
        verbose_name_plural = '02 Вопрос'


class AnswerOption(BaseClass):
    question = models.ForeignKey(Question, related_name="options", on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    # Какая статья связана с этим вариантом
    article = models.ForeignKey(Article, null=True, blank=True, on_delete=models.SET_NULL)
    # если выбран этот ответ → переход к следующему вопросу
    next_question = models.ForeignKey(
        Question,
        null=True,
        blank=True,
        related_name="prev_options",
        on_delete=models.SET_NULL,
    )

    def __str__(self):
        return f"{self.question.text} → {self.text}"

    class Meta:
        db_table = f'{db_schema}"."answer_option'
        verbose_name = '03 Вариант ответа'
        verbose_name_plural = '03 Вариант ответа'
