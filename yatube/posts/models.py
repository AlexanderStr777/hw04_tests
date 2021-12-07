# posts/models.py
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    title = models.CharField('Заголовок', max_length=200)
    slug = models.SlugField('URL', unique=True)
    description = models.TextField('Описание')

    class Meta:
        verbose_name = 'Группа постов'
        verbose_name_plural = 'Группы постов'

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField('Содержание')
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор'
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        related_name='group',
        blank=True,
        null=True,
        verbose_name='Сообщество',
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def __str__(self):
        return self.text[:15]
