# app_query_path/admin.py
from django.contrib import admin
from .models import Question, AnswerOption, Article


class AnswerOptionInline(admin.TabularInline):
    model = AnswerOption
    extra = 0
    fk_name = 'question'  # обязательно указать FK


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("id", "text")  # если is_start нет, убираем
    inlines = [AnswerOptionInline]


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("id", "title")


@admin.register(AnswerOption)
class AnswerOptionAdmin(admin.ModelAdmin):
    list_display = ("id", "text", "question", "next_question", "article")
