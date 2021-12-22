# posts/tests/tests_form.py
import shutil
import tempfile
from http import HTTPStatus

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse
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

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        # Удаляем директорию и всё её содержимое
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        # Создаем авторизованный клиент
        self.authorized_client = Client()
        self.authorized_client.force_login(PostFormTests.user)

        # Создаем не авторизованный клиент
        self.guest_client = Client()

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        # Подсчитаем количество записей в Post
        posts_count = Post.objects.count()
        form_data_create = {
            'text': '2 - Тестовый текст поста',
            'group': PostFormTests.group.id,
        }
        # Проверяем что не авторизованый клиент не может создать пост
        response = self.guest_client.post(
            reverse('posts:post_create'),
            data=form_data_create,
            follow=True
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(
            response,
            reverse('users:login')
            + '?next=/create/'
        )
        # Проверяем, что число постов не увеличилось
        self.assertNotEqual(Post.objects.count(), posts_count + 1)
        # Проверяем что пост не создан
        self.assertFalse(
            Post.objects.filter(
                text=form_data_create['text']).exists()
        )

        # Отправляем POST-запрос
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data_create,
            follow=True
        )
        # Проверяем статус ответа
        self.assertEqual(response.status_code, HTTPStatus.OK)
        # Проверяем, сработал ли редирект
        self.assertRedirects(
            response,
            reverse('posts:profile', kwargs={'username': PostFormTests.user})
        )
        # Проверяем, увеличилось ли число постов
        self.assertEqual(Post.objects.count(), posts_count + 1)
        # Проверяем, что создалась запись и по очередно поля
        new_post = Post.objects.get(text=form_data_create['text'])
        self.assertEqual(form_data_create['text'], new_post.text)
        self.assertEqual(form_data_create['group'], new_post.group.id)
        self.assertEqual(PostFormTests.user, new_post.author)

        # Проверяем что не авторизованый клиент не может создать пост
        response = self.guest_client.post(
            reverse('posts:post_create'),
            data=form_data_create,
            follow=True
        )
        # Проверяем статус ответа
        self.assertEqual(response.status_code, HTTPStatus.OK)
        # Проверяем, сработал ли редирект
        self.assertRedirects(
            response,
            reverse('users:login') + '?next=/create/'
        )

    def test_edit_post(self):
        """Валидная форма изменяет запись в Post."""
        # Подсчитаем количество записей в Post
        posts_count = Post.objects.count()
        form_data_edit = {
            'text': 'Измененный текст тестового поста',
            'group': PostFormTests.group.id,
        }
        # Проверяем что не авторизованый клиент не может изменить пост
        response = self.guest_client.post(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': PostFormTests.post.id}
            ),
            data=form_data_edit,
            follow=True
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(
            response,
            reverse('users:login')
            + f'?next=/posts/{PostFormTests.post.id}/edit/'
        )
        # Проверяем изменился ли пост
        self.assertNotEqual(form_data_edit['text'], PostFormTests.post.text)

        # Проверка для авторизованного пользователя
        response = self.authorized_client.post(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': PostFormTests.post.id}
            ),
            data=form_data_edit,
            follow=True
        )
        # Проверяем статус ответа
        self.assertEqual(response.status_code, HTTPStatus.OK)
        # Проверяем, сработал ли редирект
        self.assertRedirects(
            response,
            reverse('posts:post_detail', args=[PostFormTests.post.id])
        )
        # Проверяем, что число постов не увеличилось
        self.assertEqual(Post.objects.count(), posts_count)
        # Проверяем, что запись изменилась и по очередно поля
        new_post = Post.objects.get(text=form_data_edit['text'])
        self.assertEqual(form_data_edit['text'], new_post.text)
        self.assertEqual(form_data_edit['group'], new_post.group.id)
        self.assertEqual(PostFormTests.user, new_post.author)
