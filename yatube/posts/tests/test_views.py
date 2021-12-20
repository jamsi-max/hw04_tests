# posts/tests/test_views.py
from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from yatube.settings import COUNT_PAGINATOR_PAGE

from posts.models import Group, Post

User = get_user_model()


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_1 = User.objects.create_user(
            username='test_user_1'
        )
        cls.user_2 = User.objects.create_user(
            username='test_user_2'
        )
        cls.user_for_3_task = User.objects.create_user(
            username='user_for_3_task'
        )
        cls.group = Group.objects.create(
            slug='test_slug',
            title='1 -Тестовая группа',
            description='1 - Тестовое описание',
        )
        cls.group_2 = Group.objects.create(
            slug='2_test_slug',
            title='2 - Тестовая группа',
            description='2- Тестовое описание',
        )
        cls.group_3 = Group.objects.create(
            slug='test_task_3',
            title='Проверка для 3-го задания',
            description='Группа для проверки тестов из 3-го задания',
        )
        for i in range(30):
            Post.objects.create(
                text='Текст новошо поста',
                author=PostPagesTests.user_1 if i % 2
                else PostPagesTests.user_2,
                group=PostPagesTests.group if i % 2
                else PostPagesTests.group_2
            )
        cls.test_post_for_task_3 = Post.objects.create(
            text='Пост для проверки 3-го задания',
            author=PostPagesTests.user_for_3_task,
            group=PostPagesTests.group_3
        )

    def setUp(self):
        self.user = User.objects.create_user(username='StasBasov')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.guest_client = Client()

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            'posts/index.html': reverse('posts:main'),
            'posts/group_list.html': (
                reverse('posts:group_list', kwargs={'slug': 'test_slug'})
            ),
            'posts/profile.html': (
                reverse('posts:profile', kwargs={'username': 'test_user_1'})
            ),
            'posts/post_detail.html': (
                reverse(
                    'posts:post_detail',
                    kwargs={'post_id': PostPagesTests.group.id}
                )
            ),
            'posts/create_post.html': (
                reverse('posts:post_create'),
                reverse(
                    'posts:post_edit',
                    kwargs={'post_id': PostPagesTests.group.id}
                )
            ),
        }
        for template, reverse_name in templates_pages_names.items():
            if isinstance(reverse_name, tuple):
                for item in reverse_name:
                    response = self.authorized_client.get(item)
                    self.assertTemplateUsed(response, template)
            else:
                with self.subTest(reverse_name=reverse_name):
                    response = self.authorized_client.get(reverse_name)
                    self.assertTemplateUsed(response, template)

    def test_index_correct_post_paginator(self):
        response = self.authorized_client.get(reverse('posts:main'))
        self.assertEqual(
            response.context['object_list'].count(),
            COUNT_PAGINATOR_PAGE
        )

    def test_group_list_correct_group_and_paginator(self):
        response = self.authorized_client.get(reverse(
            'posts:group_list', kwargs={'slug': '2_test_slug'})
        )
        self.assertEqual(
            str(response.context['object_list'][0].group),
            '2 - Тестовая группа'
        )
        self.assertEqual(
            response.context['object_list'].count(),
            COUNT_PAGINATOR_PAGE
        )

    def test_profile_list_correct_user_and_paginator(self):
        response = self.authorized_client.get(reverse(
            'posts:profile', kwargs={'username': 'test_user_2'})
        )
        self.assertEqual(
            str(response.context['object_list'][0].author.username),
            'test_user_2'
        )
        self.assertEqual(
            response.context['object_list'].count(),
            COUNT_PAGINATOR_PAGE
        )

    def test_post_detail_correct_post_list_is_1(self):
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': 1})
        )
        post_expected = Post.objects.get(id=1)
        self.assertEqual(response.context['post'], post_expected)

    def test_post_create_and_edit_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response_create = self.authorized_client.get(
            reverse('posts:post_create')
        )
        response_edit = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': 1})
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

        post_expected = Post.objects.get(id=1)
        self.assertEqual(response_edit.context['post'], post_expected)

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field_creat = (
                    response_create.context.get('form').fields.get(value)
                )
                form_field_edit = (
                    response_edit.context.get('form').fields.get(value)
                )
                if response_create.context['is_edit']:
                    self.assertIsInstance(form_field_edit, expected)
                self.assertIsInstance(form_field_creat, expected)

    def test_post_with_group_correct_view(self):
        page_list = (
            self.authorized_client.get(reverse(
                'posts:main'
            )),
            self.authorized_client.get(reverse(
                'posts:group_list',
                kwargs={'slug': PostPagesTests.test_post_for_task_3.group.slug}
            )),
            self.authorized_client.get(reverse(
                'posts:profile', kwargs={'username': 'user_for_3_task'}
            )),
        )

        for page in page_list:
            self.assertTrue(PostPagesTests.test_post_for_task_3 in (
                page.context['object_list']
            ))

        self.assertFalse(
            PostPagesTests.test_post_for_task_3 in (
                self.authorized_client.get(
                    reverse('posts:group_list', kwargs={'slug': 'test_slug'})
                ).context['object_list']
            )
        )
