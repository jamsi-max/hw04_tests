from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse

User = get_user_model()


class Post(models.Model):
    text = models.TextField(
        'Текст поста',
        help_text='Введите текст поста')
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор'
    )
    group = models.ForeignKey(
        'Group',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        verbose_name='Группа',
        help_text='Выберите группу'
    )

    class Meta:
        ordering = ['-pub_date']

    def get_absolute_url(self):
        return reverse('posts:profile', args=[self.author.username])

    def __str__(self):
        return self.text[:15]


class Group(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField()

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            new_slug = self.title.translate(
                str.maketrans(
                    "абвгдеёжзийклмнопрстуфхцчшщъыьэюя\
                        +АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ",
                    "abvgdeejzijklmnoprstufhzcss_y_eua\
                        +ABVGDEEJZIJKLMNOPRSTUFHZCSS_Y_EUA"
                )
            )
            self.slug = slugify(new_slug)[:200]
        if Group.objects.filter(slug=self.slug).exists():
            raise ValidationError(
                f'Адрес "{self.slug}" уже существует, '
                'придумайте уникальное значение'
            )
        super().save(*args, **kwargs)
