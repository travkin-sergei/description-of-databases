from django.db import models
from django.utils.text import slugify


class Article(models.Model):
    """
    Список статей для описания приложения и документирования проекта.
    Получить статью можно по slug.
    Стандартные slug
    """
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='дата изменения')
    is_active = models.BooleanField(default=True, verbose_name='запись активна')
    slug = models.SlugField(max_length=200, unique=True, verbose_name='Слаг', blank=True)
    title = models.CharField(max_length=200, )
    content = models.TextField()

    def __str__(self):
        return self.slug

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'doc_article'
        verbose_name = '01 Статья'
        verbose_name_plural = '01 Статьи'
