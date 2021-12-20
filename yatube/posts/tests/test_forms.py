# posts/tests/tests_form.py
import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.forms import PostForm
from posts.models import Group, Post

User = get_user_model()

# Создаем временную папку для медиа-файлов;
# на момент теста медиа папка будет переопределена
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


# Для сохранения media-файлов в тестах будет использоваться
# временная папка TEMP_MEDIA_ROOT, а потом удалится
@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='userTest')
        cls.group = Group.objects.create(
            slug='test_slug',
            title='Тестовая группа',
            description='Тестовое описание группы',
        )
        # Создаем запись в базе данных для проверки сушествующего slug
        cls.post = Post.objects.create(
            text='Тестовый текст поста',
            author=PostFormTests.user,
            group=PostFormTests.group
        )
        # Создаем форму
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        # Удаляем директорию и всё её содержимое
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        # Создаем авторизованный клиент
        self.authorized_client = Client()
        self.authorized_client.force_login(PostFormTests.user)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        # Подсчитаем количество записей в Post
        posts_count = Post.objects.count()
        form_data = {
            'text': '2 - Тестовый текст поста',
            'group': PostFormTests.group.id,
        }
        # Отправляем POST-запрос
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(
            response,
            reverse('posts:profile', kwargs={'username': 'userTest'})
        )
        # Проверяем, увеличилось ли число постов
        self.assertEqual(Post.objects.count(), posts_count + 1)
        # Проверяем, что создалась запись
        self.assertTrue(
            Post.objects.filter(
                text='2 - Тестовый текст поста',
                author=PostFormTests.user,
                group=PostFormTests.group.id,
            ).exists()
        )

    def test_edit_post(self):
        """Валидная форма изменяет запись в Post."""
        # Подсчитаем количество записей в Post
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Измененный текст тестового поста',
            'group': PostFormTests.group.id,
        }
        response = self.authorized_client.post(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': PostFormTests.post.id}
            ),
            data=form_data,
            follow=True
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(
            response,
            reverse('posts:post_detail', args=[PostFormTests.post.id])
        )
        # Проверяем, что число постов не увеличилось
        self.assertEqual(Post.objects.count(), posts_count)
        # Проверяем, что запись изменилась
        self.assertTrue(
            Post.objects.filter(
                text='Измененный текст тестового поста',
            ).exists()
        )

    # Тестирование лейблов
    def test_title_label(self):
        title_label = PostFormTests.form.fields['text'].label
        group_label = PostFormTests.form.fields['group'].label
        self.assertEqual(title_label, 'Текст поста')
        self.assertEqual(group_label, 'Выбор группы')

    def test_title_help_text(self):
        title_help_text = PostFormTests.form.fields['text'].help_text
        group_help_text = PostFormTests.form.fields['group'].help_text
        self.assertEqual(
            group_help_text, 'Группа, к которой будет относиться пост'
        )
        self.assertEqual(title_help_text, 'Текст нового поста')
