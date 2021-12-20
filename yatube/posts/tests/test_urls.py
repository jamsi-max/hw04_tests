# posts/tests/tests_url.py
from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post

User = get_user_model()


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user')

        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )

        cls.post = Post.objects.create(
            id=1,
            text='Текст тестового поста',
            author=cls.user
        )

    def test_homepage(self):
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_uses_correct_template_for_guest_client(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/': 'posts/index.html',
            '/group/test-slug/': 'posts/group_list.html',
            '/profile/test_user/': 'posts/profile.html',
            '/posts/1/': 'posts/post_detail.html',
        }

        for adress, template in templates_url_names.items():
            with self.subTest(adress=adress):
                response = self.guest_client.get(adress)
                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertTemplateUsed(response, template)

    def test_urls_uses_correct_template_authorized_client(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/posts/1/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
        }

        for adress, template in templates_url_names.items():
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertTemplateUsed(response, template)

    def test_post_edit_url_redirect_anonymous(self):
        """Страница /posts/1/edit/ перенаправляет анонимного пользователя."""
        response = self.guest_client.get('/posts/1/edit/')
        self.assertRedirects(
            response, reverse('users:login') + '?next=/posts/1/edit/'
        )

    def test_post_create_url_redirect_anonymous(self):
        """Страница /create/ перенаправляет анонимного пользователя."""
        response = self.guest_client.get('/create/')
        self.assertRedirects(
            response,
            reverse('users:login') + '?next=/create/'
        )

    def test_urls_404_for_guest_client(self):
        response = self.guest_client.get('unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_urls_404_for_authorized_client(self):
        response = self.authorized_client.get('unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
